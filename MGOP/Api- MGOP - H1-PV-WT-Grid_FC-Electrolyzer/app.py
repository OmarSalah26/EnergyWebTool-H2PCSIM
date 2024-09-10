from flask import Flask, jsonify, request, render_template
import pulp
import pandas as pd
import numpy as np

app = Flask(__name__)

# Create energy variables for 24 hours
def create_energy_variables(prefix, hours):
    return [pulp.LpVariable(f'{prefix}_{hour}', lowBound=0, cat='Continuous') for hour in range(hours)]

# Function to calculate annualized cost
def calculate_annualized_cost(capital_cost, installation_cost, om_cost, lifetime, discount_rate):
    total_initial_cost = capital_cost + installation_cost
    annuity_factor = discount_rate * (1 + discount_rate)**lifetime / ((1 + discount_rate)**lifetime - 1)
    annualized_capital = total_initial_cost * annuity_factor
    return annualized_capital + om_cost

# Optimization model with new parameters
def create_optimization_model(params):
    prob = pulp.LpProblem("Optimize House Microgrid", pulp.LpMinimize)
    
    # Energy variables for each hour
    energy_grid = create_energy_variables('energy_grid', 24)
    energy_pv = create_energy_variables('energy_pv', 24)
    energy_wind = create_energy_variables('energy_wind', 24)
    surplus_energy = create_energy_variables('surplus_energy', 24)
    
    fuel_cell_output = create_energy_variables('fuel_cell_output', 24)
    electrolyzer_input = create_energy_variables('electrolyzer_input', 24)
    hydrogen_produced = create_energy_variables('hydrogen_produced', 24)
    hydrogen_sold = create_energy_variables('hydrogen_sold', 24)
    ev_charging = create_energy_variables('ev_charging', 24)
    ev_battery_level = create_energy_variables('ev_battery_level', 25)  # Include initial and final level
    
    # Calculate annualized costs
    pv_annualized = calculate_annualized_cost(
        params['pv_capital_cost'], params['pv_installation_cost'],
        params['pv_om_cost'], params['pv_lifetime'], params['discount_rate']
    )
    
    wind_annualized = calculate_annualized_cost(
        params['wind_capital_cost'], params['wind_installation_cost'],
        params['wind_om_cost'], params['wind_lifetime'], params['discount_rate']
    )
    
    fuel_cell_annualized = calculate_annualized_cost(
        params['fuel_cell_capital_cost'], params['fuel_cell_installation_cost'],
        0, params['fuel_cell_lifetime'], params['discount_rate']
    )
    
    electrolyzer_annualized = calculate_annualized_cost(
        params['electrolyzer_capital_cost'], params['electrolyzer_installation_cost'],
        0, params['electrolyzer_lifetime'], params['discount_rate']
    )
    
    # Objective function: Minimize costs (energy, installation, maintenance) and maximize surplus and hydrogen revenue
    prob += (
        pulp.lpSum([params['cost_grid'] * energy_grid[hour] / 100 for hour in range(24)]) +
        pv_annualized * params['pv_capacity'] +
        wind_annualized * params['wind_capacity'] +
        fuel_cell_annualized * params['fuel_cell_capacity'] +
        electrolyzer_annualized * params['electrolyzer_capacity'] +
        pulp.lpSum([params['fuel_cell_om_cost'] * fuel_cell_output[hour] for hour in range(24)]) +
        pulp.lpSum([params['electrolyzer_om_cost'] * electrolyzer_input[hour] for hour in range(24)]) +
        pulp.lpSum([params['water_price'] * params['water_consumption_rate'] * hydrogen_produced[hour] for hour in range(24)]) -
        pulp.lpSum([params['hydrogen_selling_price'] * hydrogen_sold[hour] for hour in range(24)]) -
        pulp.lpSum([params['surplus_energy_value'] * surplus_energy[hour] for hour in range(24)])
    )
    
    # Constraints
    for hour in range(24):
        # Energy balance constraint
        prob += (
            energy_grid[hour] + energy_pv[hour] + energy_wind[hour] + fuel_cell_output[hour]
            == params['electric_load'][hour] + surplus_energy[hour] + electrolyzer_input[hour] + ev_charging[hour], f"Energy_Balance_{hour}"
        )
        
        # Capacity constraints
        prob += energy_pv[hour] <= params['pv_capacity'] * params['capacity_pv'][hour], f"PV_Capacity_{hour}"
        prob += energy_wind[hour] <= params['wind_capacity'] * params['capacity_wind'][hour], f"Wind_Capacity_{hour}"
        prob += fuel_cell_output[hour] <= params['fuel_cell_capacity'], f"Fuel_Cell_Capacity_{hour}"
        prob += electrolyzer_input[hour] <= params['electrolyzer_capacity'], f"Electrolyzer_Capacity_{hour}"
        
        # Hydrogen production and sales constraints
        prob += hydrogen_produced[hour] == electrolyzer_input[hour] * params['electrolyzer_efficiency'], f"Hydrogen_Produced_{hour}"
        prob += hydrogen_sold[hour] * (params['hydrogen_energy_density'] * params['fuel_cell_efficiency']) == hydrogen_produced[hour] * (params['hydrogen_energy_density'] * params['fuel_cell_efficiency']) - fuel_cell_output[hour], f"Hydrogen_Sold_{hour}"
        
        # EV charging and battery constraints
        prob += ev_charging[hour] <= params['ev_max_charging_rate'], f"EV_Max_Charging_{hour}"
        if hour >= params['ev_arrival_time'] or hour < params['ev_departure_time']:
            prob += ev_charging[hour] >= 0, f"EV_Charging_Allowed_{hour}"
        else:
            prob += ev_charging[hour] == 0, f"EV_Charging_Not_Allowed_{hour}"
        
        # EV battery level constraints
        if hour == 0:
            prob += ev_battery_level[hour] == params['ev_battery_capacity'] - params['ev_daily_energy_need'], f"EV_Battery_Level_Start_{hour}"
        else:
            prob += ev_battery_level[hour] == ev_battery_level[hour - 1] + ev_charging[hour - 1] * params['ev_charging_efficiency'], f"EV_Battery_Level_{hour}"
        prob += ev_battery_level[hour] <= params['ev_battery_capacity'], f"EV_Max_Battery_{hour}"

    # Ensure EV is fully charged by departure time
    prob += ev_battery_level[params['ev_departure_time']] >= params['ev_battery_capacity'], "EV_Fully_Charged"

    return prob, energy_grid, energy_pv, energy_wind, surplus_energy, fuel_cell_output, electrolyzer_input, hydrogen_produced, hydrogen_sold, ev_charging, ev_battery_level

def solve_and_print_results(prob, energy_grid, energy_pv, energy_wind, surplus_energy, fuel_cell_output, electrolyzer_input, hydrogen_produced, hydrogen_sold, ev_charging, ev_battery_level, params):
    prob.solve()
    
    results = []
    for hour in range(24):
        results.append({
            'Hour': hour,
            'Grid': energy_grid[hour].varValue,
            'PV': energy_pv[hour].varValue,
            'Wind': energy_wind[hour].varValue,
            'Fuel_Cell_Output': fuel_cell_output[hour].varValue,
            'Surplus': surplus_energy[hour].varValue,
            'Electrolyzer_Input': electrolyzer_input[hour].varValue,
            'Hydrogen_Produced': hydrogen_produced[hour].varValue,
            'Hydrogen_Sold': hydrogen_sold[hour].varValue,
            'EV_Charging': ev_charging[hour].varValue,
            'EV_Battery_Level': ev_battery_level[hour].varValue,
        })
    
    df = pd.DataFrame(results)
    
    total_grid_cost = sum(params['cost_grid'] * energy_grid[hour].varValue / 100 for hour in range(24))
    total_pv_cost = params['pv_capacity'] * (params['pv_capital_cost'] + params['pv_installation_cost']) * params['discount_rate'] / (1 - (1 + params['discount_rate'])**(-params['pv_lifetime'])) + params['pv_om_cost']
    total_wind_cost = params['wind_capacity'] * (params['wind_capital_cost'] + params['wind_installation_cost']) * params['discount_rate'] / (1 - (1 + params['discount_rate'])**(-params['wind_lifetime'])) + params['wind_om_cost']
    total_fuel_cell_cost = params['fuel_cell_capacity'] * (params['fuel_cell_capital_cost'] + params['fuel_cell_installation_cost']) * params['discount_rate'] / (1 - (1 + params['discount_rate'])**(-params['fuel_cell_lifetime'])) + sum(params['fuel_cell_om_cost'] * fuel_cell_output[hour].varValue for hour in range(24))
    total_electrolyzer_cost = params['electrolyzer_capacity'] * (params['electrolyzer_capital_cost'] + params['electrolyzer_installation_cost']) * params['discount_rate'] / (1 - (1 + params['discount_rate'])**(-params['electrolyzer_lifetime'])) + sum(params['electrolyzer_om_cost'] * electrolyzer_input[hour].varValue for hour in range(24))
    total_water_cost = sum(params['water_price'] * params['water_consumption_rate'] * hydrogen_produced[hour].varValue for hour in range(24))
    total_hydrogen_sales = sum(params['hydrogen_selling_price'] * hydrogen_sold[hour].varValue for hour in range(24))
    total_surplus_value = sum(params['surplus_energy_value'] * surplus_energy[hour].varValue for hour in range(24))
    total_energy_from_grid = sum(energy_grid[hour].varValue for hour in range(24))
    total_energy = df['Grid'].sum() + df['PV'].sum() + df['Wind'].sum() + df['Fuel_Cell_Output'].sum()
    total_emissions = sum(energy_grid[hour].varValue * params['emissions_grid'] for hour in range(24))
    
    # EV charging cost and efficiency
    total_ev_charging = sum(ev_charging[hour].varValue for hour in range(24))
    avg_energy_cost = sum(params['cost_grid'] * energy_grid[hour].varValue / 100 for hour in range(24)) / total_energy if total_energy > 0 else 0
    total_ev_charging_cost = total_ev_charging * avg_energy_cost
    
    # Cost and emission reductions
    cost_reduction = 1 - (total_grid_cost + total_pv_cost + total_wind_cost + total_fuel_cell_cost + total_electrolyzer_cost - total_surplus_value - total_hydrogen_sales) / (sum(params['electric_load']) * avg_energy_cost)
    emission_reduction = 1 - total_emissions / (sum(params['electric_load']) * params['emissions_grid'])
    renewable_fraction = (df['PV'].sum() + df['Wind'].sum() + df['Fuel_Cell_Output'].sum()) / total_energy if total_energy > 0 else 0

    total_cost = total_grid_cost + total_pv_cost + total_wind_cost + total_fuel_cell_cost + total_electrolyzer_cost + total_water_cost
    total_revenue = total_surplus_value + total_hydrogen_sales - total_cost

    kpi_data = {
        'total_grid_cost': total_grid_cost,
        'total_pv_cost': total_pv_cost,
        'total_wind_cost': total_wind_cost,
        'total_fuel_cell_cost': total_fuel_cell_cost,
        'total_electrolyzer_cost': total_electrolyzer_cost,
        'total_water_cost': total_water_cost,
        'total_hydrogen_sales': total_hydrogen_sales,
        'total_surplus_value': total_surplus_value,
        'electricity_without_renewables': total_grid_cost / avg_energy_cost if avg_energy_cost > 0 else 0,
        'total_cost': total_cost,
        'total_revenue': total_revenue,
        'electricity_price': avg_energy_cost,
        'total_hydrogen_produced': sum(hydrogen_produced[hour].varValue for hour in range(24)),
        'total_hydrogen_sold': sum(hydrogen_sold[hour].varValue for hour in range(24)),
        'ghg_emissions': total_emissions,
        'total_surplus_energy': df['Surplus'].sum(),
        'total_grid_power_after_optimization': total_energy_from_grid,
        'ev_charging_cost': total_ev_charging_cost,
        'cost_reduction': cost_reduction,
        'emission_reduction': emission_reduction,
        'renewable_fraction': renewable_fraction
    }
    
    return df, kpi_data


# Flask routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/optimize', methods=['POST'])
def optimize_energy_system():
    params = request.json
    
    # Set default values for parameters if missing
    if 'capacity_pv' not in params:
        params['capacity_pv'] = [0, 0, 0, 0, 0, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.65, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.05, 0, 0, 0, 0]
    if 'capacity_wind' not in params:
        params['capacity_wind'] = [0.25, 0.23, 0.2, 0.18, 0.15, 0.13, 0.1, 0.12, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.48, 0.45, 0.4, 0.35, 0.3, 0.28, 0.27, 0.26]
    
    # Set default for EV max charging rate
    if 'ev_max_charging_rate' not in params:
        params['ev_max_charging_rate'] = 7  # Default value
    # Set default values for 'ev_arrival_time' and 'ev_departure_time' if they are missing
    if 'ev_arrival_time' not in params:
        params['ev_arrival_time'] = 18  # Set default to 6 PM
    if 'ev_departure_time' not in params:
        params['ev_departure_time'] = 7  # Set default to 7 AM
    prob, energy_grid, energy_pv, energy_wind, surplus_energy, fuel_cell_output, electrolyzer_input, hydrogen_produced, hydrogen_sold, ev_charging, ev_battery_level = create_optimization_model(params)
    results_df, kpi_data = solve_and_print_results(prob, energy_grid, energy_pv, energy_wind, surplus_energy, fuel_cell_output, electrolyzer_input, hydrogen_produced, hydrogen_sold, ev_charging, ev_battery_level, params)

    # Convert results to JSON format
    results = results_df.to_dict(orient='records')
    return jsonify({'results': results, 'kpi': kpi_data})


if __name__ == "__main__":
    app.run(debug=True)
