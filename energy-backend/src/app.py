# app.py
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from model import New_Site, db, User, ThermalBattery, SiteWaterTreatmentPlant,SiteHydrogenBasedCPHS, SiteCombinedHeatPower, WaterTreatmentPlant, HydrogenBasedCPHS, CombinedHeatPower, SiteThermalBattery, FlywheelEnergyStorage, HydrogenEnergyStorage, SiteHydrogenEnergyStorage, SiteFlywheelEnergyStorage, PVArray, SteamMethaneReformer, SiteSteamMethaneReformer, Generator, SiteGenerator, Hydropower, SiteHydropower, Biomass, GeoThermal, SiteGeoThermal, WindTurbine, HydrogenFuelCell, ElectricBattery, SiteElectricBattery, ConverterInverter, Electrolyzer, Load, GeoLocation, Site, SitePVArray, SiteWindTurbine, SiteBiomass, SiteConverterInverter, SiteHydrogenFuelCell, SiteElectrolyzer
import itertools
import random
import pandas as pd
import io
import matplotlib
import pulp
from flask import Flask, jsonify, request ,render_template
import pulp
import pandas as pd
import numpy as np

matplotlib.use('Agg')  # Use Agg backend for non-interactive plotting
import matplotlib.pyplot as plt

app = Flask(__name__)
username="root"
password="12345"
database_name="energy_project"
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{username}:{password}@localhost/{database_name}' #REPLACE 'root' with your username and 'password' with your password, and 'esnew' with the name of your database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
LCOE=0

db.init_app(app)
CORS(app) # Enable CORS for all routes by default

######################################################################################################################
################################################### MG Optimization ##################################################
######################################################################################################################
def define_parameters_durham_home():
    params = {
        'capacity_wind': [0.25, 0.23, 0.2, 0.18, 0.15, 0.13, 0.1, 0.12, 0.15, 0.2,
                          0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.48, 0.45, 0.4, 0.35, 0.3, 0.28, 0.27, 0.26],
        'capacity_pv': [0, 0, 0, 0, 0, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6,
                        0.65, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.05, 0, 0, 0, 0],
        ######################################################################################################
        ######################################################################################################
        ######################################################################################################
        
        'cost_grid': [ 60.8  ] * 24, ########### Enter the Elec Price per KWh ############

        ######################################################################################################
        ######################################################################################################
        ######################################################################################################
        
        'emissions_grid': 0.025, # kg per kw
        'fuel_cell_efficiency': 0.6,
        'electric_load': [0.8, 0.7, 0.6, 0.5, 0.5, 0.7, 1.0, 1.5, 1.8, 1.5, 1.2, 1.1, 
                          1.2, 1.3, 1.4, 1.5, 1.8, 2.0, 2.2, 2.0, 1.8, 1.5, 1.2, 1.0], # the total demand is 30
        
        # System capacities
        'pv_capacity': 5,  # kW
        'wind_capacity': 3,  # kW
        'fuel_cell_capacity': 5,  # kW
        
        # PV System Costs
        'pv_capital_cost': 2000,  # $/kW
        # 'pv_replacement_cost': 1500,  # $/kW
        'pv_installation_cost': 500,  # $/kW
        'pv_om_cost': 20,  # $/kW/year
        'pv_lifetime': 25,  # years
        
        # Wind Turbine Costs
        'wind_capital_cost': 3000,  # $/kW
        # 'wind_replacement_cost': 2500,  # $/kW
        'wind_installation_cost': 1000,  # $/kW
        'wind_om_cost': 40,  # $/kW/year
        'wind_lifetime': 20,  # years
        
        # # Fuel Cell Costs
        # 'fuel_cell_capital_cost': 1000,  # $/kW
        # 'fuel_cell_replacement_cost': 800,  # $/kW
        # 'fuel_cell_installation_cost': 200,  # $/kW
        # 'fuel_cell_om_cost': 0.02,  # $/kWh generated
        # 'fuel_cell_lifetime': 10,  # years
        
        # Grid Connection Costs
        # 'grid_connection_cost': 1000,  # $ (one-time fee)
        'grid_fixed_charge': 25,  # $/month
        
        # Other parameters
        'project_lifetime': 25,  # years
        'discount_rate': 0.05,  # 5% annual discount rate
        
        # Targets (unchanged)
        'cost_reduction_target': 0.2,
        'emission_reduction_target': 0.3,
        'renewable_fraction_target': 0.5,
        
        'surplus_energy_value': 0.39,  # $/kWh, assuming a feed-in tariff or net metering rate
    }
    return params
import logging

logging.basicConfig(level=logging.WARNING)



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

    
    # objective function
    prob += (
        pulp.lpSum([params['cost_grid'][hour] * energy_grid[hour] /100 for hour in range(24)]) +
        pv_annualized * params['pv_capacity'] +
        wind_annualized * params['wind_capacity'] +
        # fuel_cell_annualized * params['fuel_cell_capacity'] +
        # pulp.lpSum([params['fuel_cell_om_cost'] * fuel_cell_output[hour] for hour in range(24)]) +
        pulp.lpSum([params['emissions_grid'] * energy_grid[hour] for hour in range(24)]) - 
        pulp.lpSum([params['surplus_energy_value'] * surplus_energy[hour] for hour in range(24)])  # Subtract the value of surplus energy

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
    total_grid_cost = sum(params['cost_grid'][hour] * energy_grid[hour].varValue / 100 for hour in range(24))
    total_pv_cost = calculate_annualized_cost(
        params['pv_capital_cost'], params['pv_installation_cost'],
        params['pv_om_cost'], params['pv_lifetime'], params['discount_rate']) * params['pv_capacity']
    total_wind_cost = calculate_annualized_cost(
        params['wind_capital_cost'], params['wind_installation_cost'],
        params['wind_om_cost'], params['wind_lifetime'], params['discount_rate']) * params['wind_capacity']
    
    total_surplus_value = sum(params['surplus_energy_value'] * surplus_energy[hour].varValue for hour in range(24))
    
    # Actual cost without renewable energy
    load = [i * 30 for i in params['electric_load']]
    actual_cost_without_renewable = sum([load[i] * params["cost_grid"][i] / 100 for i in range(len(load))]) / 30
    
    total_cost = total_grid_cost + total_pv_cost / 365 + total_wind_cost / 365
    total_revenue = total_surplus_value - total_cost

    total_energy = df['Grid'].sum() + df['PV'].sum() + df['Wind'].sum()
    elec_price = np.mean(params['cost_grid']) / 100  # Average electricity price in $/kWh
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

    # Convert DataFrame to JSON serializable format (list of dictionaries)
    results_json = df.to_dict(orient='records')

    return results_json, kpi_data



@app.route('/RunMGOP', methods=['GET'])
def Run_MG_OpTimizer():

    user_id = request.args.get('user_id') 


    try:
        # Your optimization logic here
        #params = define_parameters_durham_home()
        
        ####################################################### Passing the data to MG Optimizer######################################################################
        #prob, energy_grid, energy_pv, energy_wind, surplus_energy = create_optimization_model(params)
        #results_df, kpi_data = solve_and_print_results(prob, energy_grid, energy_pv, energy_wind, surplus_energy, params)

        # Your optimization logic here use the db data
        data=get_sites_with_id(id =user_id)
        print("#########################################################################################################")
        print(f"############### {LCOE} ################")
        print("#########################################################################################################")

        params = {
        'capacity_wind': [0.25, 0.23, 0.2, 0.18, 0.15, 0.13, 0.1, 0.12, 0.15, 0.2,
                          0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.48, 0.45, 0.4, 0.35, 0.3, 0.28, 0.27, 0.26],
        'capacity_pv': [0, 0, 0, 0, 0, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6,
                        0.65, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.05, 0, 0, 0, 0],
        ######################################################################################################
        ######################################################################################################
        ######################################################################################################
        
        'cost_grid': [ LCOE * 100  ] * 24, ########### Enter the Elec Price per KWh ############

        ######################################################################################################
        ######################################################################################################
        ######################################################################################################
        
        'emissions_grid': 0.025, # kg per kw
        'electric_load': [0.8, 0.7, 0.6, 0.5, 0.5, 0.7, 1.0, 1.5, 1.8, 1.5, 1.2, 1.1, 
                          1.2, 1.3, 1.4, 1.5, 1.8, 2.0, 2.2, 2.0, 1.8, 1.5, 1.2, 1.0], # the total demand is 30
        
        # System capacities
        'pv_capacity': data[0]["energy_sources"]['pv_array']["capacity"],  # kW
        'wind_capacity': data[0]["energy_sources"]['wind_turbine']["capacity"],  # kW
        
        # PV System Costs
        'pv_capital_cost': data[0]["energy_sources"]['pv_array']["Capital_cost"],  # $/kW
        # 'pv_replacement_cost': 1500,  # $/kW
        'pv_installation_cost': data[0]["energy_sources"]['pv_array']["Installation_cost"],
        'pv_om_cost': data[0]["energy_sources"]['pv_array']["Operation_Maintenance_cost"],  # $/kW/year
        'pv_lifetime': data[0]["energy_sources"]['pv_array']["lifespan"],  # years
        
        # Wind Turbine Costs
        'wind_capital_cost': data[0]["energy_sources"]['wind_turbine']["Capital_cost"],  # $/kW
        # 'wind_replacement_cost': 2500,  # $/kW
        'wind_installation_cost': data[0]["energy_sources"]['wind_turbine']["Installation_cost"],  # $/kW
        'wind_om_cost': data[0]["energy_sources"]['wind_turbine']["Operation_Maintenance_cost"],  # $/kW/year
        'wind_lifetime': data[0]["energy_sources"]['wind_turbine']["lifespan"],  # years
        

        
        # Grid Connection Costs
        # 'grid_connection_cost': 1000,  # $ (one-time fee)
        'grid_fixed_charge': 25,  # $/month
        
        # Other parameters
        'project_lifetime': 25,  # years
        'discount_rate': 0.05,  # 5% annual discount rate
        
        # Targets (unchanged)
        'cost_reduction_target': 0.2,
        'emission_reduction_target': 0.3,
        'renewable_fraction_target': 0.5,
        
        'surplus_energy_value': 0.39,  # $/kWh, assuming a feed-in tariff or net metering rate
    }
        
        ####################################################### Passing the data to MG Optimizer######################################################################
        prob, energy_grid, energy_pv, energy_wind, surplus_energy = create_optimization_model(params)
        results_df, kpi_data = solve_and_print_results(prob, energy_grid, energy_pv, energy_wind, surplus_energy, params)
        if not kpi_data:
            print("Warning: KPI data was not generated correctly")

        return jsonify({'message': 'MG Optimizer Run successfully', 'results_df': results_df, 'kpi_data': kpi_data}), 200 
        # Return the result as JSON, without logging additional details to the console
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        return jsonify({'message': 'An error occurred'}), 500
 
def get_sites_with_id(id =10):
    
    # Retrieve all sites associated with the given user ID
    sites = New_Site.query.filter_by(user_id=id).all()

    # If no sites are found, return an empty list
    if not sites:
        return jsonify({'message': 'No sites found for the user', 'sites': []}), 404

    # Convert the site objects to a list of dictionaries for easy JSON conversion
    sites_data = []
    for site in sites:
        # Only include non-null energy sources and join with their full data
        energy_sources = {}

        if site.pv_array_id:
            pv_array = PVArray.query.get(site.pv_array_id)
            energy_sources['pv_array'] = {
                'id': pv_array.id,
                'name': pv_array.name,
                'rated_power': str(pv_array.rated_power),
                'efficiency': str(pv_array.efficiency),
                'area': str(pv_array.area),
                'module': pv_array.module,
                'description': pv_array.description,
                'location': pv_array.location,
                'capacity':float(pv_array.capacity),
                'lifespan': pv_array.lifespan,
                'Installation_cost': float(pv_array.operational_cost),
                'Capital_cost': float(pv_array.installation_cost),
                'Operation_Maintenance_cost': float(pv_array.maintenance_cost)
            }

        if site.wind_turbine_id:
            wind_turbine = WindTurbine.query.get(site.wind_turbine_id)
            energy_sources['wind_turbine'] = {
                'id': wind_turbine.id,
                'name': wind_turbine.name,
                
                'hub_height': str(wind_turbine.hub_height),
                'rotor_diameter': str(wind_turbine.rotor_diameter),
                'turbine_model': wind_turbine.turbine_model,
                'description': wind_turbine.description,
                'location': wind_turbine.location,
                'capacity': 5, #float(wind_turbine.capacity),
                'lifespan': wind_turbine.lifespan,
                'Installation_cost': float(wind_turbine.operational_cost),
                'Capital_cost': float(wind_turbine.installation_cost),
                'Operation_Maintenance_cost': float(wind_turbine.maintenance_cost)
            }

        if site.hydrogen_fuel_cell_id:
            hydrogen_fuel_cell = HydrogenFuelCell.query.get(site.hydrogen_fuel_cell_id)
            energy_sources['hydrogen_fuel_cell'] = {
                'id': hydrogen_fuel_cell.id,
                'name': hydrogen_fuel_cell.name,
                
                'efficiency': str(hydrogen_fuel_cell.efficiency),
                'lifespan': hydrogen_fuel_cell.lifespan,
                'description': hydrogen_fuel_cell.description,
                'location': hydrogen_fuel_cell.location,
                'Capactiy':float(hydrogen_fuel_cell.capacity),
                'Installation_cost': float(hydrogen_fuel_cell.operational_cost),
                'Capital_cost': float(hydrogen_fuel_cell.installation_cost),
                'Operation_Maintenance_cost': float(hydrogen_fuel_cell.maintenance_cost)
            }


        site_data = {
            'id': site.id,
            'name': site.name,
            'site_type': site.site_type,
            'demand': str(site.demand),
            'daily_consumption': str(site.daily_consumption),
            'surplus': str(site.surplus),
            'number_of_occupants': site.number_of_occupants,
            'size': str(site.size),
            'location': site.location,
            'energy_sources': energy_sources  # Include non-null energy sources with their full data
        }

        sites_data.append(site_data)

    # Return the site data as JSON
    return  sites_data


######################################################################################################################
######################################################################################################################
######################################################################################################################




energy_systems = []

def findsubsets_with_level(set, level=1):
    return list(itertools.combinations(set, level))

def get_all_combinations(set):
    combinations = []
    for i in range(1, len(set) + 1):
        combinations.extend(findsubsets_with_level(set, i))
    return combinations

def create_precentage_for_secnario(Energy_System):
    Num_Energy_System = len(Energy_System)
    precentage = [random.randint(1, 100) for _ in range(Num_Energy_System)]
    precentage_Sum = sum(precentage)
    for i in range(Num_Energy_System):
        precentage[i] = round((precentage[i] / precentage_Sum) * 100, 2)
    E_dict = {}
    for i in range(len(precentage)):
        E_dict[Energy_System[i]] = precentage[i]
    return E_dict

def generate_energy_strategies(energy_models):
    Energy_System_combinations = get_all_combinations(energy_models)
    existing_data = []
    for E_Ss in Energy_System_combinations:
        Energy_sources = []
        if len(E_Ss) > 1:
            for e_s in E_Ss:
                Energy_sources.append(e_s)
            startegy = {"Energy Sources": Energy_sources}
            my_json_object = {"Startegy": create_precentage_for_secnario(Energy_sources)}
            existing_data.append(my_json_object)
    return existing_data


def convert_to_decimal(value, default=0.0):
    try:
        return float(value)
    except (ValueError, TypeError):
        return default
    
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    user = User(
        name = data['username'],
        password=data['password'], # Replace with hashed password
        role=data['role']
        )
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully!'})

@app.route('/old_retrieve', methods=['GET'])
def Old_retrieve_user_data():
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400

    user = User.query.filter_by(id=user_id).first()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    try:

        # Pv array table 

        # Get PV Arrays where pv_array_id matches user_id
        pv_arrays = PVArray.query.join(SitePVArray).filter(PVArray.id == SitePVArray.pv_array_id)
        wind_turbines = WindTurbine.query.join(SiteWindTurbine).filter(SiteWindTurbine.site_id == user_id).all()

        # Serialize PV Arrays
        serialized_pv_arrays = [{
            'id': pv_array.id,
            'name': pv_array.name,
            'location': pv_array.location,
            'rated_power': str(pv_array.rated_power),
            'efficiency': str(pv_array.efficiency),
            'area': str(pv_array.area),
            'module': pv_array.module,
            'module_type': pv_array.module_type,
            'capacity': str(pv_array.capacity),
            'lifespan': pv_array.lifespan,
            'dc_ac_out': pv_array.dc_ac_out,
            'description': pv_array.description,
            'size': pv_array.size,
            'model_type': pv_array.model_type,
            'operational_cost': str(pv_array.operational_cost),
            'installation_cost': str(pv_array.installation_cost),
            'maintenance_cost': str(pv_array.maintenance_cost),
            'capacity_factor': str(pv_array.capacity_factor),
            'unit': pv_array.unit,
            'generation_type': pv_array.generation_type,
            'environmental_impact': pv_array.environmental_impact,
            'renewable_sources': pv_array.renewable_sources
        } for pv_array in pv_arrays]

        # Serialize Wind Turbines
        serialized_wind_turbines = [{
            'id': wind_turbine.id,
            'name': wind_turbine.name,
            'location': wind_turbine.location,
            'rated_power': str(wind_turbine.rated_power),
            'capacity': str(wind_turbine.capacity),
            'hub_height': wind_turbine.hub_height,
            'description': wind_turbine.description,
            'model_type': wind_turbine.model_type,
            'operational_cost': str(wind_turbine.operational_cost),
            'installation_cost': str(wind_turbine.installation_cost),
            'maintenance_cost': str(wind_turbine.maintenance_cost),
            'environmental_impact': wind_turbine.environmental_impact
        } for wind_turbine in wind_turbines]

        # Combine User Data
        user_data = {
            'id': user.id,
            'name': user.name,
            'role': user.role,
            'pv_arrays': serialized_pv_arrays,
            'wind_turbines': serialized_wind_turbines
        }

        return jsonify(user_data), 200

    except Exception as e:
        return jsonify({'error': 'Failed to retrieve user data: ' + str(e)}), 500

@app.route('/retrieve', methods=['GET'])
def get_sites():
    user_id = request.args.get('user_id') 
    # Retrieve all sites associated with the given user ID
    sites = New_Site.query.filter_by(user_id=user_id).all()

    # If no sites are found, return an empty list
    if not sites:
        return jsonify({'message': 'No sites found for the user', 'sites': []}), 404

    # Convert the site objects to a list of dictionaries for easy JSON conversion
    sites_data = []
    for site in sites:
        # Only include non-null energy sources and join with their full data
        energy_sources = {}

        if site.pv_array_id:
            pv_array = PVArray.query.get(site.pv_array_id)
            energy_sources['pv_array'] = {
                'id': pv_array.id,
                'name': pv_array.name,
                'rated_power': str(pv_array.rated_power),
                'efficiency': str(pv_array.efficiency),
                'area': str(pv_array.area),
                'module': pv_array.module,
                'description': pv_array.description,
                'location': pv_array.location,
                'capacity':float(pv_array.capacity),
                'lifespan': pv_array.lifespan,
                'Installation_cost': float(pv_array.operational_cost),
                'Capital_cost': float(pv_array.installation_cost),
                'Operation_Maintenance_cost': float(pv_array.maintenance_cost)
            }

        if site.wind_turbine_id:
            wind_turbine = WindTurbine.query.get(site.wind_turbine_id)
            energy_sources['wind_turbine'] = {
                'id': wind_turbine.id,
                'name': wind_turbine.name,
                
                'hub_height': str(wind_turbine.hub_height),
                'rotor_diameter': str(wind_turbine.rotor_diameter),
                'turbine_model': wind_turbine.turbine_model,
                'description': wind_turbine.description,
                'location': wind_turbine.location,
                'capacity': 5, #float(wind_turbine.capacity),
                'lifespan': wind_turbine.lifespan,
                'Installation_cost': float(wind_turbine.operational_cost),
                'Capital_cost': float(wind_turbine.installation_cost),
                'Operation_Maintenance_cost': float(wind_turbine.maintenance_cost)
            }

        if site.hydrogen_fuel_cell_id:
            hydrogen_fuel_cell = HydrogenFuelCell.query.get(site.hydrogen_fuel_cell_id)
            energy_sources['hydrogen_fuel_cell'] = {
                'id': hydrogen_fuel_cell.id,
                'name': hydrogen_fuel_cell.name,
                
                'efficiency': str(hydrogen_fuel_cell.efficiency),
                'lifespan': hydrogen_fuel_cell.lifespan,
                'description': hydrogen_fuel_cell.description,
                'location': hydrogen_fuel_cell.location,
                'Capactiy':float(hydrogen_fuel_cell.capacity),
                'Installation_cost': float(hydrogen_fuel_cell.operational_cost),
                'Capital_cost': float(hydrogen_fuel_cell.installation_cost),
                'Operation_Maintenance_cost': float(hydrogen_fuel_cell.maintenance_cost)
            }

        if site.biomass_id:
            biomass = Biomass.query.get(site.biomass_id)
            energy_sources['biomass'] = {
                'id': biomass.id,
                'name': biomass.name,
                'capacity': str(biomass.capacity),
                'efficiency': str(biomass.efficiency),
                'fuel_type': biomass.fuel_type,
                'description': biomass.description,
                'location': biomass.location,
                'Capactiy':float(biomass.capacity),
                'Installation_cost': float(biomass.operational_cost),
                'Capital_cost': float(biomass.installation_cost),
                'Operation_Maintenance_cost': float(biomass.maintenance_cost)
            }

        if site.geothermal_id:
            geothermal = GeoThermal.query.get(site.geothermal_id)
            energy_sources['geothermal'] = {
                'id': geothermal.id,
                'name': geothermal.name,
                'capacity': str(geothermal.capacity),
                'efficiency': str(geothermal.efficiency),
                'geothermal_gradient': str(geothermal.geothermal_gradient),
                'depth': str(geothermal.depth),
                'description': geothermal.description,
                'location': geothermal.location,
                'Installation_cost': float(geothermal.operational_cost),
                'Capital_cost': float(geothermal.installation_cost),
                'Operation_Maintenance_cost': float(geothermal.maintenance_cost)
            }

        if site.hydropower_id:
            hydropower = Hydropower.query.get(site.hydropower_id)
            energy_sources['hydropower'] = {
                'id': hydropower.id,
                'name': hydropower.name,
                'capacity': str(hydropower.capacity),
                'turbine_efficiency': str(hydropower.turbine_efficiency),
                'description': hydropower.description,
                'location': hydropower.location,
                'operational_cost': str(hydropower.operational_cost),
                'installation_cost': str(hydropower.installation_cost),
                'maintenance_cost': str(hydropower.maintenance_cost)
            }

        if site.electric_battery_id:
            electric_battery = ElectricBattery.query.get(site.electric_battery_id)
            energy_sources['electric_battery'] = {
                'id': electric_battery.id,
                'name': electric_battery.name,
                'capacity': str(electric_battery.capacity),
                'efficiency': str(electric_battery.storage_efficiency),
                'description': electric_battery.description,
                'location': electric_battery.location,
                'operational_cost': str(electric_battery.operational_cost),
                'installation_cost': str(electric_battery.installation_cost),
                'maintenance_cost': str(electric_battery.maintenance_cost)
            }

        if site.flywheel_energy_storage_id:
            flywheel_energy_storage = FlywheelEnergyStorage.query.get(site.flywheel_energy_storage_id)
            energy_sources['flywheel_energy_storage'] = {
                'id': flywheel_energy_storage.id,
                'name': flywheel_energy_storage.name,
                'capacity': str(flywheel_energy_storage.capacity),
                'efficiency': str(flywheel_energy_storage.storage_efficiency),
                'description': flywheel_energy_storage.description,
                'location': flywheel_energy_storage.location,
                'operational_cost': str(flywheel_energy_storage.operational_cost),
                'installation_cost': str(flywheel_energy_storage.installation_cost),
                'maintenance_cost': str(flywheel_energy_storage.maintenance_cost)
            }

        if site.hydrogen_energy_storage_id:
            hydrogen_energy_storage = HydrogenEnergyStorage.query.get(site.hydrogen_energy_storage_id)
            energy_sources['hydrogen_energy_storage'] = {
                'id': hydrogen_energy_storage.id,
                'name': hydrogen_energy_storage.name,
                'capacity': str(hydrogen_energy_storage.capacity),
                'efficiency': str(hydrogen_energy_storage.storage_efficiency),
                'description': hydrogen_energy_storage.description,
                'location': hydrogen_energy_storage.location,
                'operational_cost': str(hydrogen_energy_storage.operational_cost),
                'installation_cost': str(hydrogen_energy_storage.installation_cost),
                'maintenance_cost': str(hydrogen_energy_storage.maintenance_cost)
            }

        if site.thermal_battery_id:
            thermal_battery = ThermalBattery.query.get(site.thermal_battery_id)
            energy_sources['thermal_battery'] = {
                'id': thermal_battery.id,
                'name': thermal_battery.name,
                'capacity': str(thermal_battery.capacity),
                'efficiency': str(thermal_battery.storage_efficiency),
                'description': thermal_battery.description,
                'location': thermal_battery.location,
                'operational_cost': str(thermal_battery.operational_cost),
                'installation_cost': str(thermal_battery.installation_cost),
                'maintenance_cost': str(thermal_battery.maintenance_cost)
            }

        if site.combined_heat_power_id:
            combined_heat_power = CombinedHeatPower.query.get(site.combined_heat_power_id)
            energy_sources['combined_heat_power'] = {
                'id': combined_heat_power.id,
                'name': combined_heat_power.name,
                'capacity': str(combined_heat_power.capacity),
                'efficiency': str(combined_heat_power.efficiency),
                'description': combined_heat_power.description,
                'location': combined_heat_power.location,
                'operational_cost': str(combined_heat_power.operational_cost),
                'installation_cost': str(combined_heat_power.installation_cost),
                'maintenance_cost': str(combined_heat_power.maintenance_cost)
            }

        if site.generator_id:
            generator = Generator.query.get(site.generator_id)
            energy_sources['generator'] = {
                'id': generator.id,
                'name': generator.name,
                'capacity': str(generator.capacity),
                'efficiency': str(generator.efficiency),
                'description': generator.description,
                'location': generator.location,
                'operational_cost': str(generator.operational_cost),
                'installation_cost': str(generator.installation_cost),
                'maintenance_cost': str(generator.maintenance_cost)
            }

        if site.steam_methane_reformer_id:
            steam_methane_reformer = SteamMethaneReformer.query.get(site.steam_methane_reformer_id)
            energy_sources['steam_methane_reformer'] = {
                'id': steam_methane_reformer.id,
                'name': steam_methane_reformer.name,
                'capacity': str(steam_methane_reformer.capacity),
                'description': steam_methane_reformer.description,
                'location': steam_methane_reformer.location,
                'operational_cost': str(steam_methane_reformer.operational_cost),
                'installation_cost': str(steam_methane_reformer.installation_cost),
                'maintenance_cost': str(steam_methane_reformer.maintenance_cost)
            }

        if site.hydrogen_based_cphs_id:
            hydrogen_based_cphs = HydrogenBasedCPHS.query.get(site.hydrogen_based_cphs_id)
            energy_sources['hydrogen_based_cphs'] = {
                'id': hydrogen_based_cphs.id,
                'name': hydrogen_based_cphs.name,
                'capacity': str(hydrogen_based_cphs.capacity),
                'description': hydrogen_based_cphs.description,
                'location': hydrogen_based_cphs.location,
                'operational_cost': str(hydrogen_based_cphs.operational_cost),
                'installation_cost': str(hydrogen_based_cphs.installation_cost),
                'maintenance_cost': str(hydrogen_based_cphs.maintenance_cost)
            }

        if site.water_treatment_plant_id:
            water_treatment_plant = WaterTreatmentPlant.query.get(site.water_treatment_plant_id)
            energy_sources['water_treatment_plant'] = {
                'id': water_treatment_plant.id,
                'name': water_treatment_plant.name,
                'capacity': str(water_treatment_plant.capacity),
                'description': water_treatment_plant.description,
                'location': water_treatment_plant.location,
                'operational_cost': str(water_treatment_plant.operational_cost),
                'installation_cost': str(water_treatment_plant.installation_cost),
                'maintenance_cost': str(water_treatment_plant.maintenance_cost)
            }

        if site.power_plant_id:
            power_plant = PowerPlant.query.get(site.power_plant_id)
            energy_sources['power_plant'] = {
                'id': power_plant.id,
                'name': power_plant.name,
                'capacity': str(power_plant.capacity),
                'description': power_plant.description,
                'location': power_plant.location,
                'operational_cost': str(power_plant.operational_cost),
                'installation_cost': str(power_plant.installation_cost),
                'maintenance_cost': str(power_plant.maintenance_cost)
            }

        site_data = {
            'id': site.id,
            'name': site.name,
            'site_type': site.site_type,
            'demand': str(site.demand),
            'daily_consumption': str(site.daily_consumption),
            'surplus': str(site.surplus),
            'number_of_occupants': site.number_of_occupants,
            'size': str(site.size),
            'location': site.location,
            'energy_sources': energy_sources  # Include non-null energy sources with their full data
        }

        sites_data.append(site_data)

    # Return the site data as JSON
    return jsonify({'message': 'Sites retrieved successfully', 'sites': sites_data}), 200



@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    name = data['username']
    password = data['password'] # Replace with hashed password
    user = User.query.filter_by(name=name, password=password).first()
    if user:
        print(user.id)
        return jsonify({'userID': user.id})
    return jsonify({'message': 'Invalid credentials!'})

@app.route('/api/old_save_model', methods=['POST'])
def old_save_model():
    energy_systems.clear()
    data = request.get_json()
    nodes = data['nodes']
    edges = data['edges']
    user_data = data.get('userData', {})  # Assuming user data may be included
    userID = data.get('userID')  # Assuming user ID may be included
    location_data = data.get('locationData', {})  # Assuming location data may be included

    # Save location data
    location = GeoLocation(
        longitude=convert_to_decimal(location_data.get('longitude', 0)),
        latitude=convert_to_decimal(location_data.get('latitude', 0)),
        altitude=convert_to_decimal(location_data.get('altitude', 0)),
        name=location_data.get('name', ''),
        description=location_data.get('description', ''),
        country=location_data.get('country', ''),
        city=location_data.get('city', ''),
        address=location_data.get('address', '')
    )
    db.session.add(location)
    db.session.commit()

    # Save site data
    site = Site(
        name=user_data.get('siteName'),  # Replace with actual site name
        site_type=user_data.get('siteType'),  # Replace with actual site type
        demand=user_data.get('demand'),  # Replace with actual demand
        daily_consumption=user_data.get('dailyConsumption'),  # Replace with actual daily consumption
        surplus=user_data.get('surplus'),  # Replace with actual surplus
        number_of_occupants=user_data.get('numberOfOccupants'),  # Replace with actual number of occupants
        size=user_data.get('size'),  # Replace with actual size
        location=location.name,
        user_id=userID,  # Replace with actual user ID
        location_id=location.id
    )
    db.session.add(site)
    db.session.commit()




    # Save nodes and create join table entries
    for node in nodes:
        node_type = node['type']
        if node_type == 'renewableEnergySources.elecGeneration':
            if node['name'] == 'PVArray':
                new_node = PVArray(
                    name=node['name'],
                    location=location.name,
                    rated_power=convert_to_decimal(get_parameter_value(node['parameters'], 'rated_power')),
                    efficiency=convert_to_decimal(get_parameter_value(node['parameters'], 'efficiency')),
                    area=convert_to_decimal(get_parameter_value(node['parameters'], 'area')),
                    module=get_parameter_value(node['parameters'], 'module'),
                    module_type=get_parameter_value(node['parameters'], 'module_type'),
                    module_parameters=get_parameter_value(node['parameters'], 'module_parameters'),
                    temperature_model_parameters=get_parameter_value(node['parameters'], 'temperature_model_parameters'),
                    capacity=convert_to_decimal(get_parameter_value(node['parameters'], 'capacity')),
                    lifespan=get_parameter_value(node['parameters'], 'lifespan'),
                    dc_ac_out=get_parameter_value(node['parameters'], 'dc_ac_out'),
                    description=get_parameter_value(node['parameters'], 'description'),
                    size=get_parameter_value(node['parameters'], 'size'),
                    model_type=get_parameter_value(node['parameters'], 'model_type'),
                    operational_cost=convert_to_decimal(get_parameter_value(node['parameters'], 'operational_cost')),
                    installation_cost=convert_to_decimal(get_parameter_value(node['parameters'], 'installation_cost')),
                    maintenance_cost=convert_to_decimal(get_parameter_value(node['parameters'], 'maintenance_cost')),
                    capacity_factor=convert_to_decimal(get_parameter_value(node['parameters'], 'capacity_factor')),
                    unit=get_parameter_value(node['parameters'], 'unit'),
                    generation_type=get_parameter_value(node['parameters'], 'generation_type'),
                    environmental_impact=get_parameter_value(node['parameters'], 'environmental_impact'),
                    renewable_sources=get_parameter_value(node['parameters'], 'renewable_sources')
                )

                db.session.add(new_node)
                db.session.commit()
                # Create join table entry
                site_pv_array = SitePVArray(
                    site_id=site.id,
                    pv_array_id=new_node.id
                )
                db.session.add(site_pv_array)
                energy_systems.append(new_node.name)
            elif node['name'] == 'WT':
                new_node = WindTurbine(
                    name=node['name'],
                    location=location.name,
                    capacity=convert_to_decimal(get_parameter_value(node['parameters'], 'capacity')),
                    hub_height=convert_to_decimal(get_parameter_value(node['parameters'], 'hub_height')),
                    rotor_diameter=convert_to_decimal(get_parameter_value(node['parameters'], 'rotor_diameter')),
                    turbine_model=get_parameter_value(node['parameters'], 'turbine_model'),
                    power_curve=get_parameter_value(node['parameters'], 'power_curve'),
                    power_coefficient_curve=get_parameter_value(node['parameters'], 'power_coefficient_curve'),
                    efficiency=convert_to_decimal(get_parameter_value(node['parameters'], 'efficiency')),
                    len_unit=get_parameter_value(node['parameters'], 'len_unit'),
                    spd_unit=get_parameter_value(node['parameters'], 'spd_unit'),
                    pwr_unit=get_parameter_value(node['parameters'], 'pwr_unit'),
                    ctl_mode=get_parameter_value(node['parameters'], 'ctl_mode'),
                    rotor_ht=convert_to_decimal(get_parameter_value(node['parameters'], 'rotor_ht')),
                    sensr_ht=convert_to_decimal(get_parameter_value(node['parameters'], 'sensr_ht')),
                    sher_exp=convert_to_decimal(get_parameter_value(node['parameters'], 'sher_exp')),
                    turb_int=convert_to_decimal(get_parameter_value(node['parameters'], 'turb_int')),
                    air_dens=convert_to_decimal(get_parameter_value(node['parameters'], 'air_dens')),
                    pwr_ratd=convert_to_decimal(get_parameter_value(node['parameters'], 'pwr_ratd')),
                    spd_ratd=convert_to_decimal(get_parameter_value(node['parameters'], 'spd_ratd')),
                    num_pair=convert_to_decimal(get_parameter_value(node['parameters'], 'num_pair')),
                    lifespan=convert_to_decimal(get_parameter_value(node['parameters'], 'lifespan')),
                    dc_ac_out=get_parameter_value(node['parameters'], 'dc_ac_out'),
                    description=get_parameter_value(node['parameters'], 'description'),
                    size=get_parameter_value(node['parameters'], 'size'),
                    model_type=get_parameter_value(node['parameters'], 'model_type'),
                    operational_cost=convert_to_decimal(get_parameter_value(node['parameters'], 'operational_cost')),
                    installation_cost=convert_to_decimal(get_parameter_value(node['parameters'], 'installation_cost')),
                    maintenance_cost=convert_to_decimal(get_parameter_value(node['parameters'], 'maintenance_cost')),
                    capacity_factor=convert_to_decimal(get_parameter_value(node['parameters'], 'capacity_factor')),
                    unit=get_parameter_value(node['parameters'], 'unit'),
                    generation_type=get_parameter_value(node['parameters'], 'generation_type'),
                    environmental_impact=get_parameter_value(node['parameters'], 'environmental_impact'),
                    renewable_sources=get_parameter_value(node['parameters'], 'renewable_sources')
                )
                db.session.add(new_node)
                db.session.commit()
                # Create join table entry
                site_wind_turbine = SiteWindTurbine(
                    site_id=site.id,
                    wind_turbine_id=new_node.id
                )
                db.session.add(site_wind_turbine)
                energy_systems.append(new_node.name)
            
            elif node['name'] == 'FC':
                new_node = HydrogenFuelCell(
                    name=node['name'],
                    capacity=convert_to_decimal(get_parameter_value(node['parameters'], 'capacity')),
                    lifespan=convert_to_decimal(get_parameter_value(node['parameters'], 'lifespan')),
                    dc_ac_out=get_parameter_value(node['parameters'], 'dc_ac_out'),
                    location=get_parameter_value(node['parameters'], 'location'),
                    description=get_parameter_value(node['parameters'], 'description'),
                    size=get_parameter_value(node['parameters'], 'size'),
                    model_type=get_parameter_value(node['parameters'], 'model_type'),
                    efficiency=convert_to_decimal(get_parameter_value(node['parameters'], 'efficiency')),
                    operational_cost=convert_to_decimal(get_parameter_value(node['parameters'], 'operational_cost')),
                    installation_cost=convert_to_decimal(get_parameter_value(node['parameters'], 'installation_cost')),
                    maintenance_cost=convert_to_decimal(get_parameter_value(node['parameters'], 'maintenance_cost')),
                    capacity_factor=convert_to_decimal(get_parameter_value(node['parameters'], 'capacity_factor')),
                    unit=get_parameter_value(node['parameters'], 'unit'),
                    generation_type=get_parameter_value(node['parameters'], 'generation_type'),
                    environmental_impact=get_parameter_value(node['parameters'], 'environmental_impact'),
                    renewable_sources=get_parameter_value(node['parameters'], 'renewable_sources'),
                    hydrogen_consumption_rate=convert_to_decimal(get_parameter_value(node['parameters'], 'hydrogen_consumption_rate')),
                    operating_temperature=convert_to_decimal(get_parameter_value(node['parameters'], 'operating_temperature')),
                    operating_pressure=convert_to_decimal(get_parameter_value(node['parameters'], 'operating_pressure')),
                    power_output_curve=get_parameter_value(node['parameters'], 'power_output_curve'),
                    cathode_oxidant_type=convert_to_decimal(get_parameter_value(node['parameters'], 'cathode_oxidant_type')),
                    modules_in_series_per_stack=convert_to_decimal(get_parameter_value(node['parameters'], 'modules_in_series_per_stack')),
                    stacks_in_parallel=convert_to_decimal(get_parameter_value(node['parameters'], 'stacks_in_parallel')),
                    electrode_area=convert_to_decimal(get_parameter_value(node['parameters'], 'electrode_area')),
                    faraday_efficiency=convert_to_decimal(get_parameter_value(node['parameters'], 'faraday_efficiency')),
                    operating_voltage=convert_to_decimal(get_parameter_value(node['parameters'], 'operating_voltage')),
                    tafel_slope=convert_to_decimal(get_parameter_value(node['parameters'], 'tafel_slope')),
                    ohmic_resistance=convert_to_decimal(get_parameter_value(node['parameters'], 'ohmic_resistance')),
                    min_cell_voltage=convert_to_decimal(get_parameter_value(node['parameters'], 'min_cell_voltage'))
                )

                db.session.add(new_node)
                db.session.commit()

                site_hydrogen_fuel_cell = SiteHydrogenFuelCell(
                    site_id=site.id,
                    hydrogen_fuel_cell_id=new_node.id
                )
                db.session.add(site_hydrogen_fuel_cell)
                energy_systems.append(new_node.name)

            elif node['name'] == 'Geothermal':
                new_node = GeoThermal(
                    name=node['name'],
                    size=get_parameter_value(node['parameters'], 'size'),
                    model_type=get_parameter_value(node['parameters'], 'model_type'),
                    capacity=convert_to_decimal(get_parameter_value(node['parameters'], 'capacity')),
                    efficiency=convert_to_decimal(get_parameter_value(node['parameters'], 'efficiency')),
                    unit=get_parameter_value(node['parameters'], 'unit'),
                    operational_cost=convert_to_decimal(get_parameter_value(node['parameters'], 'operational_cost')),
                    installation_cost=convert_to_decimal(get_parameter_value(node['parameters'], 'installation_cost')),
                    maintenance_cost=convert_to_decimal(get_parameter_value(node['parameters'], 'maintenance_cost')),
                    lifespan=convert_to_decimal(get_parameter_value(node['parameters'], 'lifespan')),
                    capacity_factor=convert_to_decimal(get_parameter_value(node['parameters'], 'capacity_factor')),
                    dc_ac_out=get_parameter_value(node['parameters'], 'dc_ac_out'),
                    location=get_parameter_value(node['parameters'], 'location'),
                    description=get_parameter_value(node['parameters'], 'description'),
                    renewable_sources=get_parameter_value(node['parameters'], 'renewable_sources'),
                    generation_type=get_parameter_value(node['parameters'], 'generation_type'),
                    environmental_impact=get_parameter_value(node['parameters'], 'environmental_impact'),
                    geothermal_gradient=convert_to_decimal(get_parameter_value(node['parameters'], 'geothermal_gradient')),
                    depth=convert_to_decimal(get_parameter_value(node['parameters'], 'depth')),
                    flow_rate=convert_to_decimal(get_parameter_value(node['parameters'], 'flow_rate'))
                )

                db.session.add(new_node)
                db.session.commit()

                site_geothermal = SiteGeoThermal(
                    site_id=site.id,
                    geothermal_id=new_node.id
                )
                db.session.add(site_geothermal)
                energy_systems.append(new_node.name)

            elif node['name'] == 'Biomass':
                new_node = Biomass(
                    name=node['name'],
                    size=get_parameter_value(node['parameters'], 'size'),
                    model_type=get_parameter_value(node['parameters'], 'model_type'),
                    capacity=convert_to_decimal(get_parameter_value(node['parameters'], 'capacity')),
                    efficiency=convert_to_decimal(get_parameter_value(node['parameters'], 'efficiency')),
                    unit=get_parameter_value(node['parameters'], 'unit'),
                    operational_cost=convert_to_decimal(get_parameter_value(node['parameters'], 'operational_cost')),
                    installation_cost=convert_to_decimal(get_parameter_value(node['parameters'], 'installation_cost')),
                    maintenance_cost=convert_to_decimal(get_parameter_value(node['parameters'], 'maintenance_cost')),
                    lifespan=convert_to_decimal(get_parameter_value(node['parameters'], 'lifespan')),
                    capacity_factor=convert_to_decimal(get_parameter_value(node['parameters'], 'capacity_factor')),
                    dc_ac_out=get_parameter_value(node['parameters'], 'dc_ac_out'),
                    location=get_parameter_value(node['parameters'], 'location'),
                    description=get_parameter_value(node['parameters'], 'description'),
                    generation_type=get_parameter_value(node['parameters'], 'generation_type'),
                    environmental_impact=get_parameter_value(node['parameters'], 'environmental_impact'),
                    fuel_type=get_parameter_value(node['parameters'], 'fuel_type'),
                    feedstock_characteristics=(get_parameter_value(node['parameters'], 'feedstock_characteristics')),
                    emission_rate=convert_to_decimal(get_parameter_value(node['parameters'], 'emission_rate')),
                    renewable_sources=get_parameter_value(node['parameters'], 'renewable_sources')
                )

                db.session.add(new_node)
                db.session.commit()

                site_biomass = SiteBiomass(
                    site_id=site.id,
                    biomass_id=new_node.id
                )
                db.session.add(site_biomass)
                energy_systems.append(new_node.name)

            elif node['name'] == 'Hydro':
                new_node = Hydropower(
                    name=node['name'],
                    size=get_parameter_value(node['parameters'], 'size'),
                    model_type=get_parameter_value(node['parameters'], 'model_type'),
                    capacity=convert_to_decimal(get_parameter_value(node['parameters'], 'capacity')),
                    efficiency=convert_to_decimal(get_parameter_value(node['parameters'], 'efficiency')),
                    unit=get_parameter_value(node['parameters'], 'unit'),
                    operational_cost=convert_to_decimal(get_parameter_value(node['parameters'], 'operational_cost')),
                    installation_cost=convert_to_decimal(get_parameter_value(node['parameters'], 'installation_cost')),
                    maintenance_cost=convert_to_decimal(get_parameter_value(node['parameters'], 'maintenance_cost')),
                    lifespan=convert_to_decimal(get_parameter_value(node['parameters'], 'lifespan')),
                    capacity_factor=convert_to_decimal(get_parameter_value(node['parameters'], 'capacity_factor')),
                    dc_ac_out=get_parameter_value(node['parameters'], 'dc_ac_out'),
                    location=get_parameter_value(node['parameters'], 'location'),
                    description=get_parameter_value(node['parameters'], 'description'),
                    renewable_sources=get_parameter_value(node['parameters'], 'renewable_sources'),
                    generation_type=get_parameter_value(node['parameters'], 'generation_type'),
                    environmental_impact=get_parameter_value(node['parameters'], 'environmental_impact'),
                    water_flow_rate=convert_to_decimal(get_parameter_value(node['parameters'], 'water_flow_rate')),
                    head_height=convert_to_decimal(get_parameter_value(node['parameters'], 'head_height')),
                    turbine_efficiency=convert_to_decimal(get_parameter_value(node['parameters'], 'turbine_efficiency'))
                )

                db.session.add(new_node)
                db.session.commit()

                site_hydro = SiteHydropower(
                    site_id=site.id,
                    hydropower_id=new_node.id
                )
                db.session.add(site_hydro)
                energy_systems.append(new_node.name)

            elif node['name'] == "WaterTreatmentPlant":
                new_node = WaterTreatmentPlant(
                    name = node['name'],
                    capacity = convert_to_decimal(get_parameter_value(node['parameters'], 'capacity')),
                    lifespan = convert_to_decimal(get_parameter_value(node['parameters'], 'lifespan')),
                    dc_ac_out = get_parameter_value(node['parameters'], 'dc_ac_out'),
                    location = get_parameter_value(node['parameters'], 'location'),
                    description = get_parameter_value(node['parameters'], 'description'),
                    size = get_parameter_value(node['parameters'], 'size'),
                    model_type = get_parameter_value(node['parameters'], 'model_type'),
                    efficiency = convert_to_decimal(get_parameter_value(node['parameters'], 'efficiency')),
                    operational_cost = convert_to_decimal(get_parameter_value(node['parameters'], 'operational_cost')),
                    installation_cost = convert_to_decimal(get_parameter_value(node['parameters'], 'installation_cost')),
                    maintenance_cost = convert_to_decimal(get_parameter_value(node['parameters'], 'maintenance_cost')),
                    capacity_factor = convert_to_decimal(get_parameter_value(node['parameters'], 'capacity_factor')),
                    unit = get_parameter_value(node['parameters'], 'unit'),
                    generation_type = get_parameter_value(node['parameters'], 'generation_type'),
                    environmental_impact = get_parameter_value(node['parameters'], 'environmental_impact'),
                    renewable_sources = get_parameter_value(node['parameters'], 'renewable_sources'),
                    power_consumption_per_m3 = convert_to_decimal(get_parameter_value(node['parameters'], 'power_consumption_per_m3')),
                )

                db.session.add(new_node)
                db.session.commit()

                site_water = SiteWaterTreatmentPlant(
                    site_id=site.id,
                    water_treatment_plant_id=new_node.id
                )
                db.session.add(site_water)
                energy_systems.append(new_node.name)

            elif node['name'] == "CHP":
                new_node = CombinedHeatPower(
                    name = node['name'],
                    capacity = convert_to_decimal(get_parameter_value(node['parameters'], 'capacity')),
                    lifespan = convert_to_decimal(get_parameter_value(node['parameters'], 'lifespan')),
                    dc_ac_out = get_parameter_value(node['parameters'], 'dc_ac_out'),
                    location = get_parameter_value(node['parameters'], 'location'),
                    description = get_parameter_value(node['parameters'], 'description'),
                    size = get_parameter_value(node['parameters'], 'size'),
                    model_type = get_parameter_value(node['parameters'], 'model_type'),
                    efficiency = convert_to_decimal(get_parameter_value(node['parameters'], 'efficiency')),
                    operational_cost = convert_to_decimal(get_parameter_value(node['parameters'], 'operational_cost')),
                    installation_cost = convert_to_decimal(get_parameter_value(node['parameters'], 'installation_cost')),
                    maintenance_cost = convert_to_decimal(get_parameter_value(node['parameters'], 'maintenance_cost')),
                    capacity_factor = convert_to_decimal(get_parameter_value(node['parameters'], 'capacity_factor')),
                    unit = get_parameter_value(node['parameters'], 'unit'),
                    fuel_type = get_parameter_value(node['parameters'], 'fuel_type'),
                    generation_type = get_parameter_value(node['parameters'], 'generation_type'),
                    emissions_rate = convert_to_decimal(get_parameter_value(node['parameters'], 'emissions_rate')),
                    thermal_efficiency = convert_to_decimal(get_parameter_value(node['parameters'], 'thermal_efficiency')),
                    electrical_efficiency = convert_to_decimal(get_parameter_value(node['parameters'], 'electrical_efficiency')),
                    heat_output = convert_to_decimal(get_parameter_value(node['parameters'], 'heat_output')),
                    power_output = convert_to_decimal(get_parameter_value(node['parameters'], 'power_output'))
                )

                db.session.add(new_node)
                db.session.commit()

                site_chp = SiteCombinedHeatPower(
                    site_id=site.id,
                    combined_heat_power_id=new_node.id
                )
                db.session.add(site_chp)
                energy_systems.append(new_node.name)

            elif node['name'] == "HydrogenBasedCPHS":
                new_node = HydrogenBasedCPHS(
                    name = node['name'],
                    capacity = convert_to_decimal(get_parameter_value(node['parameters'], 'capacity')),
                    lifespan = convert_to_decimal(get_parameter_value(node['parameters'], 'lifespan')),
                    dc_ac_out = get_parameter_value(node['parameters'], 'dc_ac_out'),
                    location = get_parameter_value(node['parameters'], 'location'),
                    description = get_parameter_value(node['parameters'], 'description'),
                    size = get_parameter_value(node['parameters'], 'size'),
                    model_type = get_parameter_value(node['parameters'], 'model_type'),
                    efficiency = convert_to_decimal(get_parameter_value(node['parameters'], 'efficiency')),
                    operational_cost = convert_to_decimal(get_parameter_value(node['parameters'], 'operational_cost')),
                    installation_cost = convert_to_decimal(get_parameter_value(node['parameters'], 'installation_cost')),
                    maintenance_cost = convert_to_decimal(get_parameter_value(node['parameters'], 'maintenance_cost')),
                    capacity_factor = convert_to_decimal(get_parameter_value(node['parameters'], 'capacity_factor')),
                    unit = get_parameter_value(node['parameters'], 'unit'),
                    generation_type = get_parameter_value(node['parameters'], 'generation_type'),
                    environmental_impact = get_parameter_value(node['parameters'], 'environmental_impact'),
                    renewable_sources = get_parameter_value(node['parameters'], 'renewable_sources'),
                    hydrogen_consumption_rate = convert_to_decimal(get_parameter_value(node['parameters'], 'hydrogen_consumption_rate')),
                    water_consumption_rate = convert_to_decimal(get_parameter_value(node['parameters'], 'water_consumption_rate')),
                )

                db.session.add(new_node)
                db.session.commit()

                site_hydrogen_cphs = SiteHydrogenBasedCPHS(
                    site_id=site.id,
                    hydrogen_based_cphs_id=new_node.id
                )
                db.session.add(site_hydrogen_cphs)
                energy_systems.append(new_node.name)

        elif node_type == 'renewableEnergySources.h2Generation':
            if node['name'] == 'Electrolyzer':
                new_node = Electrolyzer(
                    name=node['name'],
                    location=get_parameter_value(node['parameters'], 'location'),
                    capacity=convert_to_decimal(get_parameter_value(node['parameters'], 'capacity')),
                    efficiency=convert_to_decimal(get_parameter_value(node['parameters'], 'efficiency')),
                    hydrogen_production_rate=convert_to_decimal(get_parameter_value(node['parameters'], 'hydrogen_production_rate')),
                    operating_temperature=convert_to_decimal(get_parameter_value(node['parameters'], 'operating_temperature')),
                    operating_pressure=convert_to_decimal(get_parameter_value(node['parameters'], 'operating_pressure')),
                    power_to_hydrogen_curve=(get_parameter_value(node['parameters'], 'power_to_hydrogen_curve')),
                    temperature_mode=get_parameter_value(node['parameters'], 'temperature_mode'),
                    electrode_area=convert_to_decimal(get_parameter_value(node['parameters'], 'electrode_area')),
                    cells_in_series=convert_to_decimal(get_parameter_value(node['parameters'], 'cells_in_series')),
                    stacks_in_parallel=convert_to_decimal(get_parameter_value(node['parameters'], 'stacks_in_parallel')),
                    max_current_density=convert_to_decimal(get_parameter_value(node['parameters'], 'max_current_density')),
                    max_operating_temperature=convert_to_decimal(get_parameter_value(node['parameters'], 'max_operating_temperature')),
                    min_cell_voltage=convert_to_decimal(get_parameter_value(node['parameters'], 'min_cell_voltage')),
                    thermal_resistance=convert_to_decimal(get_parameter_value(node['parameters'], 'thermal_resistance')),
                    thermal_time_constant=convert_to_decimal(get_parameter_value(node['parameters'], 'thermal_time_constant')),
                    electrolyzer_type=convert_to_decimal(get_parameter_value(node['parameters'], 'electrolyzer_type')),
                    logical_unit=convert_to_decimal(get_parameter_value(node['parameters'], 'logical_unit')),
                    size=get_parameter_value(node['parameters'], 'size'),
                    model_type=get_parameter_value(node['parameters'], 'model_type'),
                    lifespan=convert_to_decimal(get_parameter_value(node['parameters'], 'lifespan')),
                    dc_ac_out=get_parameter_value(node['parameters'], 'dc_ac_out'),
                    operational_cost=convert_to_decimal(get_parameter_value(node['parameters'], 'operational_cost')),
                    installation_cost=convert_to_decimal(get_parameter_value(node['parameters'], 'installation_cost')),
                    maintenance_cost=convert_to_decimal(get_parameter_value(node['parameters'], 'maintenance_cost')),
                    capacity_factor=convert_to_decimal(get_parameter_value(node['parameters'], 'capacity_factor')),
                    unit=get_parameter_value(node['parameters'], 'unit'),
                    generation_type=get_parameter_value(node['parameters'], 'generation_type'),
                    environmental_impact=get_parameter_value(node['parameters'], 'environmental_impact'),
                    renewable_sources=get_parameter_value(node['parameters'], 'renewable_sources'),
                    description=get_parameter_value(node['parameters'], 'description')
                )
                db.session.add(new_node)
                db.session.commit()
                # Create join table entry
                site_electrolyzer = SiteElectrolyzer(
                    site_id=site.id,
                    electrolyzer_id=new_node.id
                )
                db.session.add(site_electrolyzer)
                energy_systems.append(new_node.name)

        elif node_type == 'nonRenewableEnergySources.elecGeneration':
            if node['name'] == 'Generator':
                new_node = Generator(
                    name=node['name'],
                    capacity=convert_to_decimal(get_parameter_value(node['parameters'], 'capacity')),
                    lifespan=convert_to_decimal(get_parameter_value(node['parameters'], 'lifespan')),
                    dc_ac_out=get_parameter_value(node['parameters'], 'dc_ac_out'),
                    location=get_parameter_value(node['parameters'], 'location'),
                    description=get_parameter_value(node['parameters'], 'description'),
                    size=get_parameter_value(node['parameters'], 'size'),
                    model_type=get_parameter_value(node['parameters'], 'model_type'),
                    efficiency=convert_to_decimal(get_parameter_value(node['parameters'], 'efficiency')),
                    operational_cost=convert_to_decimal(get_parameter_value(node['parameters'], 'operational_cost')),
                    installation_cost=convert_to_decimal(get_parameter_value(node['parameters'], 'installation_cost')),
                    maintenance_cost=convert_to_decimal(get_parameter_value(node['parameters'], 'maintenance_cost')),
                    capacity_factor=convert_to_decimal(get_parameter_value(node['parameters'], 'capacity_factor')),
                    unit=get_parameter_value(node['parameters'], 'unit'),
                    fuel_type=get_parameter_value(node['parameters'], 'fuel_type'),
                    generation_type=get_parameter_value(node['parameters'], 'generation_type'),
                    emissions_rate=convert_to_decimal(get_parameter_value(node['parameters'], 'emissions_rate')),
                    generator_efficiency=convert_to_decimal(get_parameter_value(node['parameters'], 'generator_efficiency')),
                    power_output=convert_to_decimal(get_parameter_value(node['parameters'], 'power_output')),
                    operating_hours=convert_to_decimal(get_parameter_value(node['parameters'], 'operating_hours'))
                )
                db.session.add(new_node)
                db.session.commit()
                # Create join table entry
                site_generator = SiteGenerator(
                    site_id=site.id,
                    generator_id=new_node.id
                )
                db.session.add(site_generator)
                energy_systems.append(new_node.name)
        
        elif node_type == 'nonRenewableEnergySources.h2Generation':
            if node['name'] == 'SteamMethane':
                new_node = SteamMethaneReformer(
                    name=node['name'],
                    capacity=convert_to_decimal(get_parameter_value(node['parameters'], 'capacity')),
                    lifespan=convert_to_decimal(get_parameter_value(node['parameters'], 'lifespan')),
                    dc_ac_out=get_parameter_value(node['parameters'], 'dc_ac_out'),
                    location=get_parameter_value(node['parameters'], 'location'),
                    description=get_parameter_value(node['parameters'], 'description'),
                    size=get_parameter_value(node['parameters'], 'size'),
                    model_type=get_parameter_value(node['parameters'], 'model_type'),
                    efficiency=convert_to_decimal(get_parameter_value(node['parameters'], 'efficiency')),
                    operational_cost=convert_to_decimal(get_parameter_value(node['parameters'], 'operational_cost')),
                    installation_cost=convert_to_decimal(get_parameter_value(node['parameters'], 'installation_cost')),
                    maintenance_cost=convert_to_decimal(get_parameter_value(node['parameters'], 'maintenance_cost')),
                    capacity_factor=convert_to_decimal(get_parameter_value(node['parameters'], 'capacity_factor')),
                    unit=get_parameter_value(node['parameters'], 'unit'),
                    fuel_type=get_parameter_value(node['parameters'], 'fuel_type'),
                    generation_type=get_parameter_value(node['parameters'], 'generation_type'),
                    emissions_rate=convert_to_decimal(get_parameter_value(node['parameters'], 'emissions_rate')),
                    reformer_efficiency=convert_to_decimal(get_parameter_value(node['parameters'], 'reformer_efficiency')),
                    hydrogen_production_rate=convert_to_decimal(get_parameter_value(node['parameters'], 'hydrogen_production_rate')),
                    operating_hours=convert_to_decimal(get_parameter_value(node['parameters'], 'operating_hours'))
                )
                db.session.add(new_node)
                db.session.commit()
                # Create join table entry
                site_steam_methane_reformer = SiteSteamMethaneReformer(
                    site_id=site.id,
                    steam_methane_reformer_id=new_node.id
                )
                db.session.add(site_steam_methane_reformer)
                energy_systems.append(new_node.name)

        elif node_type == 'energyStorage':
            if node['name'] == 'Battery':
                new_node = ElectricBattery(
                    name=node['name'],
                    capacity=convert_to_decimal(get_parameter_value(node['parameters'], 'capacity')),
                    dc_ac_out=get_parameter_value(node['parameters'], 'dc_ac_out'),
                    storage_efficiency=convert_to_decimal(get_parameter_value(node['parameters'], 'storage_efficiency')),
                    charge_efficiency=convert_to_decimal(get_parameter_value(node['parameters'], 'charge_efficiency')),
                    discharge_efficiency=convert_to_decimal(get_parameter_value(node['parameters'], 'discharge_efficiency')),
                    state_of_charge=convert_to_decimal(get_parameter_value(node['parameters'], 'state_of_charge')),
                    type=get_parameter_value(node['parameters'], 'type'),
                    max_current_charge=convert_to_decimal(get_parameter_value(node['parameters'], 'max_current_charge')),
                    max_current_discharge=convert_to_decimal(get_parameter_value(node['parameters'], 'max_current_discharge')),
                    max_charge_voltage=convert_to_decimal(get_parameter_value(node['parameters'], 'max_charge_voltage')),
                    cells_in_parallel=convert_to_decimal(get_parameter_value(node['parameters'], 'cells_in_parallel')),
                    cells_in_series=convert_to_decimal(get_parameter_value(node['parameters'], 'cells_in_series')),
                    location=get_parameter_value(node['parameters'], 'location'),
                    lifespan=convert_to_decimal(get_parameter_value(node['parameters'], 'lifespan')),
                    description=get_parameter_value(node['parameters'], 'description')
                )
                db.session.add(new_node)
                db.session.commit()
                # Create join table entry
                site_battery = SiteElectricBattery(
                    site_id=site.id,
                    electric_battery_id=new_node.id
                )
                db.session.add(site_battery)
                energy_systems.append(new_node.name)

            if node['name'] == 'H2Tank':
                new_node = HydrogenEnergyStorage(
                    name = node['name'],
                    capacity=convert_to_decimal(get_parameter_value(node['parameters'], 'capacity')),
                    dc_ac_out=get_parameter_value(node['parameters'], 'dc_ac_out'),
                    storage_efficiency=convert_to_decimal(get_parameter_value(node['parameters'], 'storage_efficiency')),
                    charge_efficiency=convert_to_decimal(get_parameter_value(node['parameters'], 'charge_efficiency')),
                    discharge_efficiency=convert_to_decimal(get_parameter_value(node['parameters'], 'discharge_efficiency')),
                    state_of_charge=convert_to_decimal(get_parameter_value(node['parameters'], 'state_of_charge')),
                    lifetime_cycles=convert_to_decimal(get_parameter_value(node['parameters'], 'lifetime_cycles')),
                    max_charge_rate=convert_to_decimal(get_parameter_value(node['parameters'], 'max_charge_rate')),
                    max_discharge_rate=convert_to_decimal(get_parameter_value(node['parameters'], 'max_discharge_rate')),
                    storage_pressure=convert_to_decimal(get_parameter_value(node['parameters'], 'storage_pressure')),
                    location=get_parameter_value(node['parameters'], 'location'),
                    lifespan=convert_to_decimal(get_parameter_value(node['parameters'], 'lifespan')),
                    description=get_parameter_value(node['parameters'], 'description')
                )
                db.session.add(new_node)
                db.session.commit()

                site_h2_storage = SiteHydrogenEnergyStorage(
                    site_id=site.id,
                    hydrogen_energy_storage_id=new_node.id
                )
                db.session.add(site_h2_storage)
                energy_systems.append(new_node.name)
            
            if node['name'] == 'Flywheel':
                new_node = FlywheelEnergyStorage(
                    name=node['name'],
                    capacity=convert_to_decimal(get_parameter_value(node['parameters'], 'capacity')),
                    dc_ac_out=get_parameter_value(node['parameters'], 'dc_ac_out'),
                    storage_efficiency=convert_to_decimal(get_parameter_value(node['parameters'], 'storage_efficiency')),
                    charge_efficiency=convert_to_decimal(get_parameter_value(node['parameters'], 'charge_efficiency')),
                    discharge_efficiency=convert_to_decimal(get_parameter_value(node['parameters'], 'discharge_efficiency')),
                    state_of_charge=convert_to_decimal(get_parameter_value(node['parameters'], 'state_of_charge')),
                    rotational_speed=convert_to_decimal(get_parameter_value(node['parameters'], 'rotational_speed')),
                    moment_of_inertia=convert_to_decimal(get_parameter_value(node['parameters'], 'moment_of_inertia')),
                    mechanical_losses=convert_to_decimal(get_parameter_value(node['parameters'], 'mechanical_losses')),
                    location=get_parameter_value(node['parameters'], 'location'),
                    lifespan=convert_to_decimal(get_parameter_value(node['parameters'], 'lifespan')),
                    description=get_parameter_value(node['parameters'], 'description')
                )
                db.session.add(new_node)
                db.session.commit()

                site_flywheel = SiteFlywheelEnergyStorage(
                    site_id=site.id,
                    flywheel_energy_storage_id=new_node.id
                )
                db.session.add(site_flywheel)
                energy_systems.append(new_node.name)

            if node['name'] == 'Thermal':
                new_node = ThermalBattery(
                    name=node['name'],
                    capacity=convert_to_decimal(get_parameter_value(node['parameters'], 'capacity')),
                    dc_ac_out=get_parameter_value(node['parameters'], 'dc_ac_out'),
                    storage_efficiency=convert_to_decimal(get_parameter_value(node['parameters'], 'storage_efficiency')),
                    charge_efficiency=convert_to_decimal(get_parameter_value(node['parameters'], 'charge_efficiency')),
                    discharge_efficiency=convert_to_decimal(get_parameter_value(node['parameters'], 'discharge_efficiency')),
                    state_of_charge=convert_to_decimal(get_parameter_value(node['parameters'], 'state_of_charge')),
                    thermal_conductivity=convert_to_decimal(get_parameter_value(node['parameters'], 'thermal_conductivity')),
                    temperature_range=(get_parameter_value(node['parameters'], 'temperature_range')),
                    heat_loss_coefficient=convert_to_decimal(get_parameter_value(node['parameters'], 'heat_loss_coefficient')),
                    lifespan=convert_to_decimal(get_parameter_value(node['parameters'], 'lifespan')),
                    location=get_parameter_value(node['parameters'], 'location'),
                    description=get_parameter_value(node['parameters'], 'description')
                )
                db.session.add(new_node)
                db.session.commit()

                site_thermal_battery = SiteThermalBattery(
                    site_id=site.id,
                    thermal_battery_id=new_node.id
                )
                db.session.add(site_thermal_battery)
                energy_systems.append(new_node.name)


        elif node_type == 'invertersConverters':
            new_node = ConverterInverter(
                name=node['name'],
                type=get_parameter_value(node['parameters'], 'type'),
                capacity=convert_to_decimal(get_parameter_value(node['parameters'], 'capacity')),
                efficiency=convert_to_decimal(get_parameter_value(node['parameters'], 'efficiency')),
                unit=get_parameter_value(node['parameters'], 'unit'),
                installation_cost=convert_to_decimal(get_parameter_value(node['parameters'], 'installation_cost')),
                maintenance_cost=convert_to_decimal(get_parameter_value(node['parameters'], 'maintenance_cost')),
                lifespan=convert_to_decimal(get_parameter_value(node['parameters'], 'lifespan')),
                dc_ac_out=get_parameter_value(node['parameters'], 'dc_ac_out'),
                location=get_parameter_value(node['parameters'], 'location'),
                description=get_parameter_value(node['parameters'], 'description')
            )
            db.session.add(new_node)
            db.session.commit()
            # Create join table entry
            site_converter_inverter = SiteConverterInverter(
                site_id=site.id,
                converter_inverter_id=new_node.id
            )
            db.session.add(site_converter_inverter)
            # Add more conditions for other converters

        elif node_type == 'energyLoad':
            new_node = Load(
                name=node['name'],
                load_type=get_parameter_value(node['parameters'], 'Load Type'),
                demand=convert_to_decimal(get_parameter_value(node['parameters'], 'Demand')),
                site_id=site.id
            )
            db.session.add(new_node)
            # Add more conditions for other loads

        # Add additional conditions for other node types
            # Save site data
    New_site = New_site(
        name=user_data.get('siteName'),  # Replace with actual site name
        site_type=user_data.get('siteType'),  # Replace with actual site type
        demand=user_data.get('demand'),  # Replace with actual demand
        daily_consumption=user_data.get('dailyConsumption'),  # Replace with actual daily consumption
        surplus=user_data.get('surplus'),  # Replace with actual surplus
        number_of_occupants=user_data.get('numberOfOccupants'),  # Replace with actual number of occupants
        size=user_data.get('size'),  # Replace with actual size
        location=location.name,  # Location name
        user_id=userID,  # Replace with actual user ID
        location_id=location.id,  # Geolocation ID
        
        # Energy sources foreign keys
        pv_array_id=user_data.get('pvArrayId'),  # Replace with actual PV array ID
        wind_turbine_id=user_data.get('windTurbineId'),  # Replace with actual wind turbine ID
        hydrogen_fuel_cell_id=user_data.get('hydrogenFuelCellId'),  # Replace with actual hydrogen fuel cell ID
        biomass_id=user_data.get('biomassId'),  # Replace with actual biomass ID
        geothermal_id=user_data.get('geothermalId'),  # Replace with actual geothermal ID
        hydropower_id=user_data.get('hydropowerId'),  # Replace with actual hydropower ID
        electric_battery_id=user_data.get('electricBatteryId'),  # Replace with actual electric battery ID
        flywheel_energy_storage_id=user_data.get('flywheelEnergyStorageId'),  # Replace with actual flywheel energy storage ID
        hydrogen_energy_storage_id=user_data.get('hydrogenEnergyStorageId'),  # Replace with actual hydrogen energy storage ID
        thermal_battery_id=user_data.get('thermalBatteryId'),  # Replace with actual thermal battery ID
        combined_heat_power_id=user_data.get('combinedHeatPowerId'),  # Replace with actual combined heat power ID
        generator_id=user_data.get('generatorId'),  # Replace with actual generator ID
        steam_methane_reformer_id=user_data.get('steamMethaneReformerId'),  # Replace with actual steam methane reformer ID
        hydrogen_based_cphs_id=user_data.get('hydrogenBasedCphsId'),  # Replace with actual hydrogen-based CPHS ID
        water_treatment_plant_id=user_data.get('waterTreatmentPlantId'),  # Replace with actual water treatment plant ID
        power_plant_id=user_data.get('powerPlantId')  # Replace with actual power plant ID
    )
    db.session.add(site)
        

    db.session.commit()
    return jsonify({'message': 'Model saved successfully!'})

@app.route('/api/save_model', methods=['POST'])
def save_model():
    energy_systems.clear()
    data = request.get_json()
    nodes = data['nodes']
    edges = data['edges']
    user_data = data.get('userData', {})  # Assuming user data may be included
    userID = data.get('userID')  # Assuming user ID may be included
    location_data = data.get('locationData', {})  # Assuming location data may be included

    # Save location data
    location = GeoLocation(
        longitude=convert_to_decimal(location_data.get('longitude', 0)),
        latitude=convert_to_decimal(location_data.get('latitude', 0)),
        altitude=convert_to_decimal(location_data.get('altitude', 0)),
        name=location_data.get('name', ''),
        description=location_data.get('description', ''),
        country=location_data.get('country', ''),
        city=location_data.get('city', ''),
        address=location_data.get('address', '')
    )
    db.session.add(location)
    db.session.commit()

    # Initialize energy source IDs
    pv_array_id = None
    wind_turbine_id = None
    hydrogen_fuel_cell_id = None
    biomass_id = None
    geothermal_id = None
    hydropower_id = None
    electric_battery_id = None
    flywheel_energy_storage_id = None
    hydrogen_energy_storage_id = None
    thermal_battery_id = None
    combined_heat_power_id = None
    generator_id = None
    steam_methane_reformer_id = None
    hydrogen_based_cphs_id = None
    water_treatment_plant_id = None
    power_plant_id = None

    # Helper function to handle empty string for integer fields
    def convert_to_int(value, default=None):
        try:
            return int(value) if value else default
        except ValueError:
            return default

    # Save nodes and create join table entries
    for node in nodes:
        node_type = node['type']
        if node_type == 'renewableEnergySources.elecGeneration':
            if node['name'] == 'PVArray':
                new_node = PVArray(
                    name=node['name'],
                    location=location.name,
                    rated_power=convert_to_decimal(get_parameter_value(node['parameters'], 'rated_power')),
                    efficiency=convert_to_decimal(get_parameter_value(node['parameters'], 'efficiency')),
                    area=convert_to_decimal(get_parameter_value(node['parameters'], 'area')),
                    module=get_parameter_value(node['parameters'], 'module'),
                    module_type=get_parameter_value(node['parameters'], 'module_type'),
                    module_parameters=get_parameter_value(node['parameters'], 'module_parameters'),
                    temperature_model_parameters=get_parameter_value(node['parameters'], 'temperature_model_parameters'),
                    capacity=convert_to_decimal(get_parameter_value(node['parameters'], 'capacity')),
                    lifespan=convert_to_int(get_parameter_value(node['parameters'], 'lifespan')),  # Convert lifespan
                    dc_ac_out=get_parameter_value(node['parameters'], 'dc_ac_out'),
                    description=get_parameter_value(node['parameters'], 'description'),
                    size=get_parameter_value(node['parameters'], 'size'),
                    model_type=get_parameter_value(node['parameters'], 'model_type'),
                    operational_cost=convert_to_decimal(get_parameter_value(node['parameters'], 'operational_cost')),
                    installation_cost=convert_to_decimal(get_parameter_value(node['parameters'], 'installation_cost')),
                    maintenance_cost=convert_to_decimal(get_parameter_value(node['parameters'], 'maintenance_cost')),
                    capacity_factor=convert_to_decimal(get_parameter_value(node['parameters'], 'capacity_factor')),
                    unit=get_parameter_value(node['parameters'], 'unit'),
                    generation_type=get_parameter_value(node['parameters'], 'generation_type'),
                    environmental_impact=get_parameter_value(node['parameters'], 'environmental_impact'),
                    renewable_sources=get_parameter_value(node['parameters'], 'renewable_sources')
                )

                db.session.add(new_node)
                db.session.commit()
                pv_array_id = new_node.id  # Set the PVArray ID for the site

            elif node['name'] == 'WT':
                new_node = WindTurbine(
                    name=node['name'],
                    location=location.name,
                    capacity=convert_to_decimal(get_parameter_value(node['parameters'], 'capacity')),
                    hub_height=convert_to_decimal(get_parameter_value(node['parameters'], 'hub_height')),
                    rotor_diameter=convert_to_decimal(get_parameter_value(node['parameters'], 'rotor_diameter')),
                    turbine_model=get_parameter_value(node['parameters'], 'turbine_model'),
                    power_curve=get_parameter_value(node['parameters'], 'power_curve'),
                    power_coefficient_curve=get_parameter_value(node['parameters'], 'power_coefficient_curve'),
                    efficiency=convert_to_decimal(get_parameter_value(node['parameters'], 'efficiency')),
                    len_unit=get_parameter_value(node['parameters'], 'len_unit'),
                    spd_unit=get_parameter_value(node['parameters'], 'spd_unit'),
                    pwr_unit=get_parameter_value(node['parameters'], 'pwr_unit'),
                    ctl_mode=get_parameter_value(node['parameters'], 'ctl_mode'),
                    rotor_ht=convert_to_decimal(get_parameter_value(node['parameters'], 'rotor_ht')),
                    sensr_ht=convert_to_decimal(get_parameter_value(node['parameters'], 'sensr_ht')),
                    sher_exp=convert_to_decimal(get_parameter_value(node['parameters'], 'sher_exp')),
                    turb_int=convert_to_decimal(get_parameter_value(node['parameters'], 'turb_int')),
                    air_dens=convert_to_decimal(get_parameter_value(node['parameters'], 'air_dens')),
                    pwr_ratd=convert_to_decimal(get_parameter_value(node['parameters'], 'pwr_ratd')),
                    spd_ratd=convert_to_decimal(get_parameter_value(node['parameters'], 'spd_ratd')),
                    num_pair=convert_to_decimal(get_parameter_value(node['parameters'], 'num_pair')),
                    lifespan=convert_to_int(get_parameter_value(node['parameters'], 'lifespan')),  # Convert lifespan
                    dc_ac_out=get_parameter_value(node['parameters'], 'dc_ac_out'),
                    description=get_parameter_value(node['parameters'], 'description'),
                    size=get_parameter_value(node['parameters'], 'size'),
                    model_type=get_parameter_value(node['parameters'], 'model_type'),
                    operational_cost=convert_to_decimal(get_parameter_value(node['parameters'], 'operational_cost')),
                    installation_cost=convert_to_decimal(get_parameter_value(node['parameters'], 'installation_cost')),
                    maintenance_cost=convert_to_decimal(get_parameter_value(node['parameters'], 'maintenance_cost')),
                    capacity_factor=convert_to_decimal(get_parameter_value(node['parameters'], 'capacity_factor')),
                    unit=get_parameter_value(node['parameters'], 'unit'),
                    generation_type=get_parameter_value(node['parameters'], 'generation_type'),
                    environmental_impact=get_parameter_value(node['parameters'], 'environmental_impact'),
                    renewable_sources=get_parameter_value(node['parameters'], 'renewable_sources')
                )
                db.session.add(new_node)
                db.session.commit()
                wind_turbine_id = new_node.id  # Set the WindTurbine ID for the site

            
            elif node['name'] == 'FC':
                new_node = HydrogenFuelCell(
                    name=node['name'],
                    capacity=convert_to_decimal(get_parameter_value(node['parameters'], 'capacity')),
                    lifespan=convert_to_int(get_parameter_value(node['parameters'], 'lifespan')),  # Convert lifespan
                    dc_ac_out=get_parameter_value(node['parameters'], 'dc_ac_out'),
                    location=get_parameter_value(node['parameters'], 'location'),
                    description=get_parameter_value(node['parameters'], 'description'),
                    size=get_parameter_value(node['parameters'], 'size'),
                    model_type=get_parameter_value(node['parameters'], 'model_type'),
                    efficiency=convert_to_decimal(get_parameter_value(node['parameters'], 'efficiency')),
                    operational_cost=convert_to_decimal(get_parameter_value(node['parameters'], 'operational_cost')),
                    installation_cost=convert_to_decimal(get_parameter_value(node['parameters'], 'installation_cost')),
                    maintenance_cost=convert_to_decimal(get_parameter_value(node['parameters'], 'maintenance_cost')),
                    capacity_factor=convert_to_decimal(get_parameter_value(node['parameters'], 'capacity_factor')),
                    unit=get_parameter_value(node['parameters'], 'unit'),
                    generation_type=get_parameter_value(node['parameters'], 'generation_type'),
                    environmental_impact=get_parameter_value(node['parameters'], 'environmental_impact'),
                    renewable_sources=get_parameter_value(node['parameters'], 'renewable_sources'),
                    hydrogen_consumption_rate=convert_to_decimal(get_parameter_value(node['parameters'], 'hydrogen_consumption_rate')),
                    operating_temperature=convert_to_decimal(get_parameter_value(node['parameters'], 'operating_temperature')),
                    operating_pressure=convert_to_decimal(get_parameter_value(node['parameters'], 'operating_pressure')),
                    power_output_curve=get_parameter_value(node['parameters'], 'power_output_curve'),
                    cathode_oxidant_type=convert_to_decimal(get_parameter_value(node['parameters'], 'cathode_oxidant_type')),
                    modules_in_series_per_stack=convert_to_decimal(get_parameter_value(node['parameters'], 'modules_in_series_per_stack')),
                    stacks_in_parallel=convert_to_decimal(get_parameter_value(node['parameters'], 'stacks_in_parallel')),
                    electrode_area=convert_to_decimal(get_parameter_value(node['parameters'], 'electrode_area')),
                    faraday_efficiency=convert_to_decimal(get_parameter_value(node['parameters'], 'faraday_efficiency')),
                    operating_voltage=convert_to_decimal(get_parameter_value(node['parameters'], 'operating_voltage')),
                    tafel_slope=convert_to_decimal(get_parameter_value(node['parameters'], 'tafel_slope')),
                    ohmic_resistance=convert_to_decimal(get_parameter_value(node['parameters'], 'ohmic_resistance')),
                    min_cell_voltage=convert_to_decimal(get_parameter_value(node['parameters'], 'min_cell_voltage'))
                )

                db.session.add(new_node)
                db.session.commit()
                hydrogen_fuel_cell_id = new_node.id  # Set the HydrogenFuelCell ID for the site



            elif node['name'] == 'Geothermal':
                new_node = GeoThermal(
                    name=node['name'],
                    size=get_parameter_value(node['parameters'], 'size'),
                    model_type=get_parameter_value(node['parameters'], 'model_type'),
                    capacity=convert_to_decimal(get_parameter_value(node['parameters'], 'capacity')),
                    efficiency=convert_to_decimal(get_parameter_value(node['parameters'], 'efficiency')),
                    unit=get_parameter_value(node['parameters'], 'unit'),
                    operational_cost=convert_to_decimal(get_parameter_value(node['parameters'], 'operational_cost')),
                    installation_cost=convert_to_decimal(get_parameter_value(node['parameters'], 'installation_cost')),
                    maintenance_cost=convert_to_decimal(get_parameter_value(node['parameters'], 'maintenance_cost')),
                    lifespan=convert_to_int(get_parameter_value(node['parameters'], 'lifespan')),  # Convert lifespan
                    capacity_factor=convert_to_decimal(get_parameter_value(node['parameters'], 'capacity_factor')),
                    dc_ac_out=get_parameter_value(node['parameters'], 'dc_ac_out'),
                    location=get_parameter_value(node['parameters'], 'location'),
                    description=get_parameter_value(node['parameters'], 'description'),
                    renewable_sources=get_parameter_value(node['parameters'], 'renewable_sources'),
                    generation_type=get_parameter_value(node['parameters'], 'generation_type'),
                    environmental_impact=get_parameter_value(node['parameters'], 'environmental_impact'),
                    geothermal_gradient=convert_to_decimal(get_parameter_value(node['parameters'], 'geothermal_gradient')),
                    depth=convert_to_decimal(get_parameter_value(node['parameters'], 'depth')),
                    flow_rate=convert_to_decimal(get_parameter_value(node['parameters'], 'flow_rate'))
                )

                db.session.add(new_node)
                db.session.commit()

                geothermal_id = new_node.id

            elif node['name'] == 'Biomass':
                new_node = Biomass(
                    name=node['name'],
                    size=get_parameter_value(node['parameters'], 'size'),
                    model_type=get_parameter_value(node['parameters'], 'model_type'),
                    capacity=convert_to_decimal(get_parameter_value(node['parameters'], 'capacity')),
                    efficiency=convert_to_decimal(get_parameter_value(node['parameters'], 'efficiency')),
                    unit=get_parameter_value(node['parameters'], 'unit'),
                    operational_cost=convert_to_decimal(get_parameter_value(node['parameters'], 'operational_cost')),
                    installation_cost=convert_to_decimal(get_parameter_value(node['parameters'], 'installation_cost')),
                    maintenance_cost=convert_to_decimal(get_parameter_value(node['parameters'], 'maintenance_cost')),
                    lifespan=convert_to_int(get_parameter_value(node['parameters'], 'lifespan')),  # Convert lifespan
                    capacity_factor=convert_to_decimal(get_parameter_value(node['parameters'], 'capacity_factor')),
                    dc_ac_out=get_parameter_value(node['parameters'], 'dc_ac_out'),
                    location=get_parameter_value(node['parameters'], 'location'),
                    description=get_parameter_value(node['parameters'], 'description'),
                    generation_type=get_parameter_value(node['parameters'], 'generation_type'),
                    environmental_impact=get_parameter_value(node['parameters'], 'environmental_impact'),
                    fuel_type=get_parameter_value(node['parameters'], 'fuel_type'),
                    feedstock_characteristics=(get_parameter_value(node['parameters'], 'feedstock_characteristics')),
                    emission_rate=convert_to_decimal(get_parameter_value(node['parameters'], 'emission_rate')),
                    renewable_sources=get_parameter_value(node['parameters'], 'renewable_sources')
                )

                db.session.add(new_node)
                db.session.commit()

                biomass_id=new_node.id
        

        # Add additional conditions for other node types   ######################################## dont forget  to add the other energy sources ##########################


            # Save site data
    # Save the site with all relevant energy sources
    site = New_Site(
        name=user_data.get('siteName'),  # Replace with actual site name
        site_type=user_data.get('siteType'),  # Replace with actual site type
        demand=user_data.get('demand'),  # Replace with actual demand
        daily_consumption=user_data.get('dailyConsumption'),  # Replace with actual daily consumption
        surplus=user_data.get('surplus'),  # Replace with actual surplus
        number_of_occupants=user_data.get('numberOfOccupants'),  # Replace with actual number of occupants
        size=user_data.get('size'),  # Replace with actual size
        location=location.name,  # Location name
        user_id=userID,  # Replace with actual user ID
        location_id=location.id,  # Geolocation ID
        
        # Set foreign keys for energy sources
        pv_array_id=pv_array_id,
        wind_turbine_id=wind_turbine_id,
        hydrogen_fuel_cell_id=hydrogen_fuel_cell_id,
        biomass_id=biomass_id,
        geothermal_id=geothermal_id,
        hydropower_id=hydropower_id,
        electric_battery_id=electric_battery_id,
        flywheel_energy_storage_id=flywheel_energy_storage_id,
        hydrogen_energy_storage_id=hydrogen_energy_storage_id,
        thermal_battery_id=thermal_battery_id,
        combined_heat_power_id=combined_heat_power_id,
        generator_id=generator_id,
        steam_methane_reformer_id=steam_methane_reformer_id,
        hydrogen_based_cphs_id=hydrogen_based_cphs_id,
        water_treatment_plant_id=water_treatment_plant_id,
        power_plant_id=power_plant_id
    )
    print("############################################")
    print(f"PV Array ID: {pv_array_id}")
    print(f"Wind Turbine ID: {wind_turbine_id}")
    print(f"Hydrogen Fuel Cell ID: {hydrogen_fuel_cell_id}")

    db.session.add(site)
    db.session.commit()
    return jsonify({'message': 'Model saved successfully!'})



@app.route('/api/generate_strategies', methods=['GET'])
def generate_strategies():
    strategies = generate_energy_strategies(energy_systems)
    return jsonify({'strategies': strategies})

@app.route('/api/get_data', methods=['GET'])
def get_data():
    data_frames = []

    # Query all data from each table
    tables = [User, GeoLocation, Site, Load, PVArray, WindTurbine, HydrogenFuelCell, GeoThermal, Biomass, Hydropower, WaterTreatmentPlant, CombinedHeatPower, HydrogenBasedCPHS, SteamMethaneReformer, ElectricBattery, HydrogenEnergyStorage, FlywheelEnergyStorage, ThermalBattery, ConverterInverter, Generator, Electrolyzer]
    for table in tables:
        data = table.query.all()
        df = pd.DataFrame([item.__dict__ for item in data])
        df = df.drop(columns=['_sa_instance_state'])  # Remove SQLAlchemy's internal attribute
        df['source_table'] = table.__tablename__  # Add a column to indicate the source table
        data_frames.append(df)

    combined_df = pd.concat(data_frames, ignore_index=True)

    output = io.StringIO()
    combined_df.to_csv(output, index=False)
    output.seek(0)

    return send_file(io.BytesIO(output.getvalue().encode()), mimetype='text/csv', as_attachment=True, download_name='all_data.csv')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400

    # Read the CSV file
    df = pd.read_csv(file)

    # Generate plot
    plt.figure(figsize=(10, 6))
    for column in df.columns[1:]:
        plt.plot(df.iloc[:, 0], df[column], marker='o', label=column)
    plt.title('CSV Data Plot')
    plt.xlabel(df.columns[0])
    plt.ylabel('Values')
    plt.legend()
    plt.grid(True)

    # Save the plot to a bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    return send_file(buf, mimetype='image/png', as_attachment=True, download_name='plot.png')
    
@app.route('/lcoe', methods=['POST'])
def get_lcoe():
    if 'file' not in request.files:
        return jsonify({"message": "No file provided"}), 400

    file = request.files['file']

    if not file.filename.endswith('.csv'):
        return jsonify({"message": "Invalid file format. Please upload a CSV file."}), 400

    try:
        df = pd.read_csv(file)

        for k, i in enumerate(df['Cost/Operating cost ($/yr)']):
            if i >= 1:
                global LCOE
                LCOE=df['Cost/LCOE ($/kWh)'][k]
                return jsonify({"LCOE": df['Cost/LCOE ($/kWh)'][k]})
        
        return jsonify({"message": "No valid LCOE found"}), 404

    except Exception as e:
        return jsonify({"message": str(e)}), 500
    
def get_parameter_value(parameters, parameter_name):
    for param in parameters:
        if param['name'] == parameter_name:
            return param['value']
    return None

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
