# app.py
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from model import db, User, ThermalBattery, SiteWaterTreatmentPlant,SiteHydrogenBasedCPHS, SiteCombinedHeatPower, WaterTreatmentPlant, HydrogenBasedCPHS, CombinedHeatPower, SiteThermalBattery, FlywheelEnergyStorage, HydrogenEnergyStorage, SiteHydrogenEnergyStorage, SiteFlywheelEnergyStorage, PVArray, SteamMethaneReformer, SiteSteamMethaneReformer, Generator, SiteGenerator, Hydropower, SiteHydropower, Biomass, GeoThermal, SiteGeoThermal, WindTurbine, HydrogenFuelCell, ElectricBattery, SiteElectricBattery, ConverterInverter, Electrolyzer, Load, GeoLocation, Site, SitePVArray, SiteWindTurbine, SiteBiomass, SiteConverterInverter, SiteHydrogenFuelCell, SiteElectrolyzer
import itertools
import random
import pandas as pd
import io
import matplotlib
matplotlib.use('Agg')  # Use Agg backend for non-interactive plotting
import matplotlib.pyplot as plt

app = Flask(__name__)
username="root"
password="12345"
database_name="energy_project"
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{username}:{password}@localhost:3000/{database_name}' #REPLACE 'root' with your username and 'password' with your password, and 'esnew' with the name of your database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
CORS(app)

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
    


def get_parameter_value(parameters, parameter_name):
    for param in parameters:
        if param['name'] == parameter_name:
            return param['value']
    return None

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
