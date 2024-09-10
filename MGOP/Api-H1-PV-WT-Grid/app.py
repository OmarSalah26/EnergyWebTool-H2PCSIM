from flask import Flask, jsonify, request ,render_template
import pulp
import pandas as pd
import numpy as np

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def create_energy_variables(prefix, hours):
    return [pulp.LpVariable(f'{prefix}_{hour}'.replace(' ', '_'), lowBound=0, cat='Continuous') for hour in range(24)]

def calculate_annualized_cost(capital_cost, installation_cost, om_cost, lifetime, discount_rate):
    total_initial_cost = capital_cost + installation_cost
    annuity_factor = discount_rate * (1 + discount_rate)**lifetime / ((1 + discount_rate)**lifetime - 1)
    annualized_capital = total_initial_cost * annuity_factor
    return annualized_capital + om_cost

def create_optimization_model(params):
    prob = pulp.LpProblem("Optimize House Microgrid", pulp.LpMinimize)
    
    energy_grid = create_energy_variables('energy_grid', 24)
    energy_pv = create_energy_variables('energy_pv', 24)
    energy_wind = create_energy_variables('energy_wind', 24)
    surplus_energy = create_energy_variables('surplus_energy', 24)

    # Calculate annualized costs
    pv_annualized = calculate_annualized_cost(
        params['pv_capital_cost'], params['pv_installation_cost'],
        params['pv_om_cost'], params['pv_lifetime'], params['discount_rate'])
    
    wind_annualized = calculate_annualized_cost(
        params['wind_capital_cost'], params['wind_installation_cost'],
        params['wind_om_cost'], params['wind_lifetime'], params['discount_rate'])

    # Objective function
    prob += (
        pulp.lpSum([params['cost_grid'] * energy_grid[hour] / 100 for hour in range(24)]) +
        pv_annualized * params['pv_capacity'] +
        wind_annualized * params['wind_capacity'] +
        pulp.lpSum([params['emissions_grid'] * energy_grid[hour] for hour in range(24)]) - 
        pulp.lpSum([params['surplus_energy_value'] * surplus_energy[hour] for hour in range(24)])
    )
    
    # Constraints
    for hour in range(24):
        prob += (energy_grid[hour] + energy_pv[hour] + energy_wind[hour]
                 == params['electric_load'][hour] + surplus_energy[hour], f"Energy_Balance_{hour}")
        prob += energy_pv[hour] <= params['pv_capacity'] * params['capacity_pv'][hour], f"PV_Capacity_{hour}"
        prob += energy_wind[hour] <= params['wind_capacity'] * params['capacity_wind'][hour], f"Wind_Capacity_{hour}"

    return prob, energy_grid, energy_pv, energy_wind, surplus_energy

def solve_and_print_results(prob, energy_grid, energy_pv, energy_wind, surplus_energy, params):
    prob.solve()

    results = []
    for hour in range(24):
        results.append({
            'Hour': hour,
            'Grid': energy_grid[hour].varValue,
            'PV': energy_pv[hour].varValue,
            'Wind': energy_wind[hour].varValue,
            'Surplus': surplus_energy[hour].varValue,
        })

    df = pd.DataFrame(results)
    
    # Calculate totals and KPIs
    total_grid_cost = sum(params['cost_grid'] * energy_grid[hour].varValue / 100 for hour in range(24))
    total_pv_cost = calculate_annualized_cost(
        params['pv_capital_cost'], params['pv_installation_cost'],
        params['pv_om_cost'], params['pv_lifetime'], params['discount_rate']) * params['pv_capacity']
    total_wind_cost = calculate_annualized_cost(
        params['wind_capital_cost'], params['wind_installation_cost'],
        params['wind_om_cost'], params['wind_lifetime'], params['discount_rate']) * params['wind_capacity']
    
    total_surplus_value = sum(params['surplus_energy_value'] * surplus_energy[hour].varValue for hour in range(24))
    
    # Actual cost without renewable energy
    load = [i * 30 for i in params['electric_load']]
    actual_cost_without_renewable = sum([load[i] * params["cost_grid"] / 100 for i in range(len(load))]) / 30
    
    total_cost = total_grid_cost + total_pv_cost / 365 + total_wind_cost / 365
    total_revenue = total_surplus_value - total_cost

    total_energy = df['Grid'].sum() + df['PV'].sum() + df['Wind'].sum()
    elec_price = params['cost_grid'] / 100  # Average electricity price in $/kWh
    ghg_emissions = df['Grid'].sum() * params['emissions_grid']
    total_surplus = df['Surplus'].sum()

    cost_reduction = 1 - (df['Grid'].sum() * elec_price) / (sum(params['electric_load']) * elec_price)
    emission_reduction = 1 - ghg_emissions / (sum(params['electric_load']) * params['emissions_grid'])
    renewable_fraction = (df['PV'].sum() + df['Wind'].sum()) / total_energy

    # Prepare output data
    kpi_data = {
        'total_grid_cost': total_grid_cost,
        'total_pv_cost': total_pv_cost,
        'total_wind_cost': total_wind_cost,
        'total_surplus_value': total_surplus_value,
        'actual_cost_without_renewable': actual_cost_without_renewable,
        'total_cost': total_cost,
        'total_revenue': total_revenue,
        'electricity_price': elec_price,
        'ghg_emissions': ghg_emissions,
        'total_surplus': total_surplus,
        'total_grid_power': df['Grid'].sum(),
        'cost_reduction': cost_reduction,
        'emission_reduction': emission_reduction,
        'renewable_fraction': renewable_fraction,
    }

    return df, kpi_data

@app.route('/optimize', methods=['POST'])
def optimize_energy_system():
    params = request.json

    # Set default values for 'capacity_pv' and 'capacity_wind' if they are missing
    if 'capacity_pv' not in params:
        params['capacity_pv'] = [0, 0, 0, 0, 0, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 
                                 0.65, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.05, 0, 0, 0, 0]

    if 'capacity_wind' not in params:
        params['capacity_wind'] = [0.25, 0.23, 0.2, 0.18, 0.15, 0.13, 0.1, 0.12, 0.15, 0.2, 0.25, 
                                   0.3, 0.35, 0.4, 0.45, 0.5, 0.48, 0.45, 0.4, 0.35, 0.3, 0.28, 
                                   0.27, 0.26]

    prob, energy_grid, energy_pv, energy_wind, surplus_energy = create_optimization_model(params)
    results_df, kpi_data = solve_and_print_results(prob, energy_grid, energy_pv, energy_wind, surplus_energy, params)

    # Convert results to JSON format
    results = results_df.to_dict(orient='records')

    # Include KPI data in the response
    return jsonify({'results': results, 'kpi': kpi_data})


if __name__ == "__main__":
    app.run(debug=True)