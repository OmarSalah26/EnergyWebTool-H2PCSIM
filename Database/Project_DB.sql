Create Database energy_project;
use energy_project;

CREATE TABLE User (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),
    role VARCHAR(255),
    password VARCHAR(255)
);
-- Create the KPI table
CREATE TABLE KPI (
    id INT PRIMARY KEY PRIMARY KEY,
    name VARCHAR(255),
    description TEXT,
    value VARCHAR(255)
);


-- Table for GeoLocation
CREATE TABLE GeoLocation (
    id INT PRIMARY KEY AUTO_INCREMENT,
    longitude DECIMAL(9, 6),
    latitude DECIMAL(9, 6),
    altitude DECIMAL(7, 2),
    name VARCHAR(255),
    description TEXT,
    country VARCHAR(255),
    city VARCHAR(255),
    address VARCHAR(255)
);


CREATE TABLE Site (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),
    site_type VARCHAR(255),
    demand DECIMAL(10, 2),
    daily_consumption DECIMAL(10, 2),
    surplus DECIMAL(10, 2),
    number_of_occupants INT,
    size DECIMAL(10, 2),
    location VARCHAR(255),
    User_id INT,
    location_id INT,
    FOREIGN KEY (User_id) REFERENCES User(id),
    FOREIGN KEY (location_id) REFERENCES GeoLocation(id)
);

CREATE TABLE Site_KPI (
   Site_id INT,
    kpi_id INT,
    PRIMARY KEY (Site_id, kpi_id),
    FOREIGN KEY (Site_id) REFERENCES Site(id),
    FOREIGN KEY (kpi_id) REFERENCES KPI(id)
);

-- ---------------------------------------------------
CREATE TABLE Load_ (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),
    load_type VARCHAR(255),  # Type of the load (e.g., "energy", "water", "gas").
    demand DECIMAL(10, 2),   # Demand value for the load.           
    site_id INT,
    FOREIGN KEY (site_id) REFERENCES Site(id)
    
);


-- Table for Utility
CREATE TABLE Utility (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),
    utility_type VARCHAR(255),
    demand DECIMAL(10, 2),
    price_per_unit DECIMAL(10, 2),
    location VARCHAR(255),
    emission_rate DECIMAL(10, 2),
    billing_information TEXT,
    connection_type VARCHAR(255),
    capacity DECIMAL(10, 2),
    tier VARCHAR(255),
    site_id INT,
    location_id INT,
    FOREIGN KEY (site_id) REFERENCES Site(id),
	FOREIGN KEY (location_id) REFERENCES GeoLocation(id)
);
-- Junction table for the many-to-many relationship between Site and Organization
CREATE TABLE Site_Utility (
    site_id INT,
    Utility_id INT,
    PRIMARY KEY (site_id, Utility_id),
    FOREIGN KEY (site_id) REFERENCES Site(id),
    FOREIGN KEY (Utility_id) REFERENCES Utility(id)
);

CREATE TABLE Utility_KPI (
   Utility_id INT,
    kpi_id INT,
    PRIMARY KEY (Utility_id, kpi_id),
    FOREIGN KEY (Utility_id) REFERENCES Utility   (id),
    FOREIGN KEY (kpi_id) REFERENCES KPI(id)
);

-- ---------------------------------------------------
-- Table for Organization
CREATE TABLE Organization (
    id INT PRIMARY KEY AUTO_INCREMENT,
    o_type VARCHAR(255),
    rules TEXT,
    rewards TEXT
);

-- Junction table for the many-to-many relationship between Site and Organization
CREATE TABLE Site_Organization (
    site_id INT,
    organization_id INT,
    PRIMARY KEY (site_id, organization_id),
    FOREIGN KEY (site_id) REFERENCES Site(id),
    FOREIGN KEY (organization_id) REFERENCES Organization(id)
);

CREATE TABLE Organization_KPI (
   Organization_id INT,
    kpi_id INT,
    PRIMARY KEY (Organization_id, kpi_id),
    FOREIGN KEY (Organization_id) REFERENCES Organization   (id),
    FOREIGN KEY (kpi_id) REFERENCES KPI(id)
);

-- ---------------------------------------------------
-- Create the HydrogenFuelCell table
CREATE TABLE HydrogenFuelCell (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),
    capacity DECIMAL(10, 2),
    lifespan INT,
    DC_AC_Out VARCHAR(255),
    location VARCHAR(255),
    description TEXT,
    size VARCHAR(255),
    model_type VARCHAR(255),
    efficiency DECIMAL(5, 2),
    operational_cost DECIMAL(10, 2),
    installation_cost DECIMAL(10, 2),
    maintenance_cost DECIMAL(10, 2),
    capacity_factor DECIMAL(5, 2),
    unit VARCHAR(50),
    generation_type VARCHAR(255),
    environmental_impact TEXT,
    renewable_sources VARCHAR(255),
    hydrogen_consumption_rate DECIMAL(10, 2),
    operating_temperature DECIMAL(5, 2),
    operating_pressure DECIMAL(5, 2),
    power_output_curve JSON, -- Using JSON to store complex data like DataFrame or Dict
    cathode_oxidant_type INT,
    modules_in_series_per_stack INT,
    stacks_in_parallel INT,
    electrode_area DECIMAL(10, 2),
    faraday_efficiency DECIMAL(5, 2),
    operating_voltage DECIMAL(5, 2),
    tafel_slope DECIMAL(5, 2),
    ohmic_resistance DECIMAL(5, 2),
    min_cell_voltage DECIMAL(5, 2)
);

-- Junction table for the many-to-many relationship between Site and HydrogenFuelCell
CREATE TABLE Site_HydrogenFuelCell (
    site_id INT,
    hydrogen_fuel_cell_id INT,
    PRIMARY KEY (site_id, hydrogen_fuel_cell_id),
    FOREIGN KEY (site_id) REFERENCES Site(id),
    FOREIGN KEY (hydrogen_fuel_cell_id) REFERENCES HydrogenFuelCell(id)
);
-- Table for HydrogenFuelCellPlant
CREATE TABLE HydrogenFuelCellPlant (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),
    location VARCHAR(255)
);

-- Junction table for the many-to-many relationship between HydrogenFuelCellPlant and HydrogenFuelCell
CREATE TABLE HydrogenFuelCellPlant_HydrogenFuelCell (
    hydrogen_fuel_cell_plant_id INT,
    hydrogen_fuel_cell_id INT,
    PRIMARY KEY (hydrogen_fuel_cell_plant_id, hydrogen_fuel_cell_id),
    FOREIGN KEY (hydrogen_fuel_cell_plant_id) REFERENCES HydrogenFuelCellPlant(id),
    FOREIGN KEY (hydrogen_fuel_cell_id) REFERENCES HydrogenFuelCell(id)
);
CREATE TABLE HydrogenFuelCell_KPI (
   HydrogenFuelCell_id INT,
    kpi_id INT,
    PRIMARY KEY (HydrogenFuelCell_id, kpi_id),
    FOREIGN KEY (HydrogenFuelCell_id) REFERENCES HydrogenFuelCell   (id),
    FOREIGN KEY (kpi_id) REFERENCES KPI(id)
);


CREATE TABLE HydrogenFuelCellPlant_KPI (
   HydrogenFuelCellPlant_id INT,
    kpi_id INT,
    PRIMARY KEY (HydrogenFuelCellPlant_id, kpi_id),
    FOREIGN KEY (HydrogenFuelCellPlant_id) REFERENCES HydrogenFuelCellPlant   (id),
    FOREIGN KEY (kpi_id) REFERENCES KPI(id)
);
-- ------------------------------------------------------------------------------------


-- Table for Electrolyzer
CREATE TABLE Electrolyzer (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),
    location VARCHAR(255),
    capacity DECIMAL(10, 2),
    efficiency DECIMAL(5, 2),
    hydrogen_production_rate DECIMAL(10, 2),
    operating_temperature DECIMAL(5, 2),
    operating_pressure DECIMAL(5, 2),
    power_to_hydrogen_curve JSON, -- Using JSON to store complex data like DataFrame or Dict
    temperature_mode VARCHAR(255),
    electrode_area DECIMAL(10, 2),
    cells_in_series INT,
    stacks_in_parallel INT,
    max_current_density DECIMAL(10, 2),
    max_operating_temperature DECIMAL(5, 2),
    min_cell_voltage DECIMAL(5, 2),
    thermal_resistance DECIMAL(10, 2),
    thermal_time_constant DECIMAL(10, 2),
    electrolyzer_type INT,
    logical_unit INT,
    size VARCHAR(255),
    model_type VARCHAR(255),
    lifespan INT,
    DC_AC_Out VARCHAR(255),
    operational_cost DECIMAL(10, 2),
    installation_cost DECIMAL(10, 2),
    maintenance_cost DECIMAL(10, 2),
    capacity_factor DECIMAL(5, 2),
    unit VARCHAR(50),
    generation_type VARCHAR(255),
    environmental_impact TEXT,
    renewable_sources VARCHAR(255),
    description TEXT
);

-- Junction table for the many-to-many relationship between Site and Electrolyzer
CREATE TABLE Site_Electrolyzer (
    site_id INT,
    electrolyzer_id INT,
    PRIMARY KEY (site_id, electrolyzer_id),
    FOREIGN KEY (site_id) REFERENCES Site(id),
    FOREIGN KEY (electrolyzer_id) REFERENCES Electrolyzer(id)
);
-- Table for HydrogenFuelCellPlant
CREATE TABLE HydrogenElectrolyzerPlant (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),
    location VARCHAR(255)
);

CREATE TABLE HydrogenElectrolyzerPlant_Electrolyzer (
    Electrolyzer_plant_id INT,
    Electrolyzer_id INT,
    PRIMARY KEY (Electrolyzer_plant_id, Electrolyzer_id),
    FOREIGN KEY (Electrolyzer_plant_id) REFERENCES HydrogenElectrolyzerPlant(id),
    FOREIGN KEY (Electrolyzer_id) REFERENCES Electrolyzer(id)
);

CREATE TABLE Electrolyzer_KPI (
   Electrolyzer_id INT,
    kpi_id INT,
    PRIMARY KEY (Electrolyzer_id, kpi_id),
    FOREIGN KEY (Electrolyzer_id) REFERENCES Electrolyzer   (id),
    FOREIGN KEY (kpi_id) REFERENCES KPI(id)
);

CREATE TABLE HydrogenElectrolyzerPlant_KPI (
   HydrogenElectrolyzerPlant_id INT,
    kpi_id INT,
    PRIMARY KEY (HydrogenElectrolyzerPlant_id, kpi_id),
    FOREIGN KEY (HydrogenElectrolyzerPlant_id) REFERENCES HydrogenElectrolyzerPlant   (id),
    FOREIGN KEY (kpi_id) REFERENCES KPI(id)
);
-- ------------------------------------------------------------------------------------

-- Table for Biomass
CREATE TABLE Biomass (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),
    size VARCHAR(255),
    model_type VARCHAR(255),
    capacity DECIMAL(10, 2),
    efficiency DECIMAL(5, 2),
    unit VARCHAR(50),
    operational_cost DECIMAL(10, 2),
    installation_cost DECIMAL(10, 2),
    maintenance_cost DECIMAL(10, 2),
    lifespan INT,
    capacity_factor DECIMAL(5, 2),
    DC_AC_Out VARCHAR(255),
    location VARCHAR(255),
    description TEXT,
    generation_type VARCHAR(255),
    environmental_impact TEXT,
    fuel_type VARCHAR(255),
    feedstock_characteristics JSON, -- Using JSON to store complex data like Dict
    emission_rate DECIMAL(10, 2),
    renewable_sources VARCHAR(255)
);

-- Junction table for the many-to-many relationship between Site and Biomass
CREATE TABLE Site_Biomass (
    site_id INT,
    biomass_id INT,
    PRIMARY KEY (site_id, biomass_id),
    FOREIGN KEY (site_id) REFERENCES Site(id),
    FOREIGN KEY (biomass_id) REFERENCES Biomass(id)
);

CREATE TABLE Biomass_KPI (
   Biomass_id INT,
    kpi_id INT,
    PRIMARY KEY (Biomass_id, kpi_id),
    FOREIGN KEY (Biomass_id) REFERENCES Biomass   (id),
    FOREIGN KEY (kpi_id) REFERENCES KPI(id)
);

-- ------------------------------------------------------------------------------------




-- Table for Converter
CREATE TABLE Converter_Inverter (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),
    type VARCHAR(255),
    capacity DECIMAL(10, 2),
    efficiency DECIMAL(5, 2),
    unit VARCHAR(50),
    installation_cost DECIMAL(10, 2),
    maintenance_cost DECIMAL(10, 2),
    lifespan INT,
    DC_AC_Out VARCHAR(255),
    location VARCHAR(255),
    description TEXT
);

-- Junction table for the many-to-many relationship between Site and Converter
CREATE TABLE Site_Converter_Inverter (
    site_id INT,
    Converter_Inverter_id INT,
    PRIMARY KEY (site_id, Converter_Inverter_id),
    FOREIGN KEY (site_id) REFERENCES Site(id),
    FOREIGN KEY (Converter_Inverter_id) REFERENCES Converter_Inverter(id)
);

CREATE TABLE Converter_Inverter_KPI (
   Converter_Inverter_id INT,
    kpi_id INT,
    PRIMARY KEY (Converter_Inverter_id, kpi_id),
    FOREIGN KEY (Converter_Inverter_id) REFERENCES Converter_Inverter   (id),
    FOREIGN KEY (kpi_id) REFERENCES KPI(id)
);

-- ------------------------------------------------------------------------------------


-- Table for GeoThermal
CREATE TABLE GeoThermal (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),
    size VARCHAR(255),
    model_type VARCHAR(255),
    capacity DECIMAL(10, 2),
    efficiency DECIMAL(5, 2),
    unit VARCHAR(50),
    operational_cost DECIMAL(10, 2),
    installation_cost DECIMAL(10, 2),
    maintenance_cost DECIMAL(10, 2),
    lifespan INT,
    capacity_factor DECIMAL(5, 2),
    DC_AC_Out VARCHAR(255),
    location VARCHAR(255),
    description TEXT,
    renewable_sources VARCHAR(255),
    generation_type VARCHAR(255),
    environmental_impact TEXT,
    geothermal_gradient DECIMAL(5, 2),
    depth DECIMAL(10, 2),
    flow_rate DECIMAL(10, 2)
);

-- Junction table for the many-to-many relationship between Site and GeoThermal
CREATE TABLE Site_GeoThermal (
    site_id INT,
    geothermal_id INT,
    PRIMARY KEY (site_id, geothermal_id),
    FOREIGN KEY (site_id) REFERENCES Site(id),
    FOREIGN KEY (geothermal_id) REFERENCES GeoThermal(id)
);

CREATE TABLE GeoThermal_KPI (
   GeoThermal_id INT,
    kpi_id INT,
    PRIMARY KEY (GeoThermal_id, kpi_id),
    FOREIGN KEY (GeoThermal_id) REFERENCES GeoThermal   (id),
    FOREIGN KEY (kpi_id) REFERENCES KPI(id)
);

-- ------------------------------------------------------------------------------------

-- Table for Hydropower
CREATE TABLE Hydropower (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),
    size VARCHAR(255),
    model_type VARCHAR(255),
    capacity DECIMAL(10, 2),
    efficiency DECIMAL(5, 2),
    unit VARCHAR(50),
    operational_cost DECIMAL(10, 2),
    installation_cost DECIMAL(10, 2),
    maintenance_cost DECIMAL(10, 2),
    lifespan INT,
    capacity_factor DECIMAL(5, 2),
    DC_AC_Out VARCHAR(255),
    location VARCHAR(255),
    description TEXT,
    renewable_sources VARCHAR(255),
    generation_type VARCHAR(255),
    environmental_impact TEXT,
    water_flow_rate DECIMAL(10, 2),
    head_height DECIMAL(10, 2),
    turbine_efficiency DECIMAL(5, 2)
);

-- Junction table for the many-to-many relationship between Site and Hydropower
CREATE TABLE Site_Hydropower (
    site_id INT,
    hydropower_id INT,
    PRIMARY KEY (site_id, hydropower_id),
    FOREIGN KEY (site_id) REFERENCES Site(id),
    FOREIGN KEY (hydropower_id) REFERENCES Hydropower(id)
);


CREATE TABLE Hydropower_KPI (
   Hydropower_id INT,
    kpi_id INT,
    PRIMARY KEY (Hydropower_id, kpi_id),
    FOREIGN KEY (Hydropower_id) REFERENCES Hydropower   (id),
    FOREIGN KEY (kpi_id) REFERENCES KPI(id)
);

-- ------------------------------------------------------------------------------------

-- Table for PVArray
CREATE TABLE PVArray (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),
    location VARCHAR(255),
    rated_power DECIMAL(10, 2),
    efficiency DECIMAL(5, 2),
    area DECIMAL(10, 2),
    module VARCHAR(255),
    module_type VARCHAR(255),
    module_parameters JSON, -- Using JSON to store complex data like Dict or pd.Series
    temperature_model_parameters JSON, -- Using JSON to store complex data like Dict or pd.Series
    capacity DECIMAL(10, 2),
    lifespan INT,
    DC_AC_Out VARCHAR(255),
    description TEXT,
    size VARCHAR(255),
    model_type VARCHAR(255),
    operational_cost DECIMAL(10, 2),
    installation_cost DECIMAL(10, 2),
    maintenance_cost DECIMAL(10, 2),
    capacity_factor DECIMAL(5, 2),
    unit VARCHAR(50),
    generation_type VARCHAR(255),
    environmental_impact TEXT,
    renewable_sources VARCHAR(255)
);

-- Junction table for the many-to-many relationship between Site and PVArray
CREATE TABLE Site_PVArray (
    site_id INT,
    pv_array_id INT,
    PRIMARY KEY (site_id, pv_array_id),
    FOREIGN KEY (site_id) REFERENCES Site(id),
    FOREIGN KEY (pv_array_id) REFERENCES PVArray(id)
);

-- Table for PV_farm
CREATE TABLE PV_farm (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),
    location VARCHAR(255),
    surface_tilt DECIMAL(5, 2),
    surface_azimuth DECIMAL(5, 2),
    albedo DECIMAL(5, 2),
    surface_type VARCHAR(255)
);

-- Junction table for the many-to-many relationship between PV_farm and PVArray
CREATE TABLE PV_farm_PVArray (
    pv_farm_id INT,
    pv_array_id INT,
    PRIMARY KEY (pv_farm_id, pv_array_id),
    FOREIGN KEY (pv_farm_id) REFERENCES PV_farm(id),
    FOREIGN KEY (pv_array_id) REFERENCES PVArray(id)
);
CREATE TABLE PVArray_KPI (
   PVArray_id INT,
    kpi_id INT,
    PRIMARY KEY (PVArray_id, kpi_id),
    FOREIGN KEY (PVArray_id) REFERENCES PVArray   (id),
    FOREIGN KEY (kpi_id) REFERENCES KPI(id)
);

CREATE TABLE PV_farm_KPI (
   PV_farm_id INT,
    kpi_id INT,
    PRIMARY KEY (PV_farm_id, kpi_id),
    FOREIGN KEY (PV_farm_id) REFERENCES PV_farm   (id),
    FOREIGN KEY (kpi_id) REFERENCES KPI(id)
);
-- ------------------------------------------------------------------------------------


-- Table for WindTurbine
CREATE TABLE WindTurbine (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),
    location VARCHAR(255),
    capacity DECIMAL(10, 2),
    hub_height DECIMAL(10, 2),
    rotor_diameter DECIMAL(10, 2),
    turbine_model VARCHAR(255),
    efficiency DECIMAL(5, 2),
    power_curve JSON, -- Using JSON to store complex data like DataFrame or Dict
    power_coefficient_curve JSON, -- Using JSON to store complex data like DataFrame or Dict
    Len_Unit VARCHAR(50),
    Spd_Unit VARCHAR(50),
    Pwr_Unit VARCHAR(50),
    Ctl_mode VARCHAR(50),
    Rotor_Ht DECIMAL(10, 2),
    Sensr_Ht DECIMAL(10, 2),
    Sher_Exp DECIMAL(5, 2),
    Turb_Int DECIMAL(5, 2),
    Air_Dens DECIMAL(5, 2),
    Pwr_Ratd DECIMAL(10, 2),
    Spd_Ratd DECIMAL(10, 2),
    Num_Pair INT,
    lifespan INT,
    DC_AC_Out VARCHAR(255),
    description TEXT,
    size VARCHAR(255),
    model_type VARCHAR(255),
    operational_cost DECIMAL(10, 2),
    installation_cost DECIMAL(10, 2),
    maintenance_cost DECIMAL(10, 2),
    capacity_factor DECIMAL(5, 2),
    unit VARCHAR(50),
    generation_type VARCHAR(255),
    environmental_impact TEXT,
    renewable_sources VARCHAR(255)
);

-- Junction table for the many-to-many relationship between Site and WindTurbine
CREATE TABLE Site_WindTurbine (
    site_id INT,
    wind_turbine_id INT,
    PRIMARY KEY (site_id, wind_turbine_id),
    FOREIGN KEY (site_id) REFERENCES Site(id),
    FOREIGN KEY (wind_turbine_id) REFERENCES WindTurbine(id)
);

-- Table for WindFarm
CREATE TABLE WindFarm (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),
    location VARCHAR(255),
    farm_efficiency JSON -- Using JSON to store complex data like DataFrame
);

-- Junction table for the many-to-many relationship between WindFarm and WindTurbine
CREATE TABLE WindFarm_WindTurbine (
    wind_farm_id INT,
    wind_turbine_id INT,
    PRIMARY KEY (wind_farm_id, wind_turbine_id),
    FOREIGN KEY (wind_farm_id) REFERENCES WindFarm(id),
    FOREIGN KEY (wind_turbine_id) REFERENCES WindTurbine(id)
);

CREATE TABLE WindTurbine_KPI (
    WindTurbine_id INT,
    kpi_id INT,
    PRIMARY KEY (WindTurbine_id, kpi_id),
    FOREIGN KEY (WindTurbine_id) REFERENCES WindTurbine   (id),
    FOREIGN KEY (kpi_id) REFERENCES KPI(id)
);



CREATE TABLE WindFarm_KPI (
    WindFarm_id INT,
    kpi_id INT,
    PRIMARY KEY (WindFarm_id, kpi_id),
    FOREIGN KEY (WindFarm_id) REFERENCES WindFarm   (id),
    FOREIGN KEY (kpi_id) REFERENCES KPI(id)
);
-- ------------------------------------------------------------------------------------

-- Table for ElectricBattery
CREATE TABLE ElectricBattery (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),
    capacity DECIMAL(10, 2),
    DC_AC_Out VARCHAR(255),
    storage_efficiency DECIMAL(5, 2),
    charge_efficiency DECIMAL(5, 2),
    discharge_efficiency DECIMAL(5, 2),
    state_of_charge DECIMAL(5, 2),
    type VARCHAR(255),
    max_current_charge DECIMAL(10, 2),
    max_current_discharge DECIMAL(10, 2),
    max_charge_voltage DECIMAL(10, 2),
    cells_in_parallel INT,
    cells_in_series INT,
    location VARCHAR(255),
    lifespan INT,
    description TEXT
);

-- Junction table for the many-to-many relationship between Site and ElectricBattery
CREATE TABLE Site_ElectricBattery (
    site_id INT,
    electric_battery_id INT,
    PRIMARY KEY (site_id, electric_battery_id),
    FOREIGN KEY (site_id) REFERENCES Site(id),
    FOREIGN KEY (electric_battery_id) REFERENCES ElectricBattery(id)
);

CREATE TABLE ElectricBattery_KPI (
    ElectricBattery_id INT,
    kpi_id INT,
    PRIMARY KEY (ElectricBattery_id, kpi_id),
    FOREIGN KEY (ElectricBattery_id) REFERENCES ElectricBattery   (id),
    FOREIGN KEY (kpi_id) REFERENCES KPI(id)
);
-- ------------------------------------------------------------------------------------



-- Table for Flywheel_Energy_Storage
CREATE TABLE Flywheel_Energy_Storage (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),
    capacity DECIMAL(10, 2),
    DC_AC_Out VARCHAR(255),
    storage_efficiency DECIMAL(5, 2),
    charge_efficiency DECIMAL(5, 2),
    discharge_efficiency DECIMAL(5, 2),
    state_of_charge DECIMAL(5, 2),
    rotational_speed DECIMAL(10, 2),
    moment_of_inertia DECIMAL(10, 2),
    mechanical_losses DECIMAL(10, 2),
    location VARCHAR(255),
    lifespan INT,
    description TEXT
);

-- Junction table for the many-to-many relationship between Site and Flywheel_Energy_Storage
CREATE TABLE Site_Flywheel_Energy_Storage (
    site_id INT,
    flywheel_energy_storage_id INT,
    PRIMARY KEY (site_id, flywheel_energy_storage_id),
    FOREIGN KEY (site_id) REFERENCES Site(id),
    FOREIGN KEY (flywheel_energy_storage_id) REFERENCES Flywheel_Energy_Storage(id)
);


CREATE TABLE Flywheel_Energy_Storage_KPI (
    Flywheel_Energy_Storage_id INT,
    kpi_id INT,
    PRIMARY KEY (Flywheel_Energy_Storage_id, kpi_id),
    FOREIGN KEY (Flywheel_Energy_Storage_id) REFERENCES Flywheel_Energy_Storage   (id),
    FOREIGN KEY (kpi_id) REFERENCES KPI(id)
);
-- ------------------------------------------------------------------------------------

-- Table for HydrogenEnergyStorage
CREATE TABLE HydrogenEnergyStorage (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),
    capacity DECIMAL(10, 2),
    DC_AC_Out VARCHAR(255),
    storage_efficiency DECIMAL(5, 2),
    charge_efficiency DECIMAL(5, 2),
    discharge_efficiency DECIMAL(5, 2),
    state_of_charge DECIMAL(5, 2),
    lifetime_cycles INT,
    max_charge_rate DECIMAL(10, 2),
    max_discharge_rate DECIMAL(10, 2),
    storage_pressure DECIMAL(10, 2),
    location VARCHAR(255),
    lifespan INT,
    description TEXT
);

-- Junction table for the many-to-many relationship between Site and HydrogenEnergyStorage
CREATE TABLE Site_HydrogenEnergyStorage (
    site_id INT,
    hydrogen_energy_storage_id INT,
    PRIMARY KEY (site_id, hydrogen_energy_storage_id),
    FOREIGN KEY (site_id) REFERENCES Site(id),
    FOREIGN KEY (hydrogen_energy_storage_id) REFERENCES HydrogenEnergyStorage(id)
);


CREATE TABLE HydrogenEnergyStorage_KPI (
    HydrogenEnergyStorage_id INT,
    kpi_id INT,
    PRIMARY KEY (HydrogenEnergyStorage_id, kpi_id),
    FOREIGN KEY (HydrogenEnergyStorage_id) REFERENCES HydrogenEnergyStorage   (id),
    FOREIGN KEY (kpi_id) REFERENCES KPI(id)
);
-- ------------------------------------------------------------------------------------

-- Table for ThermalBattery
CREATE TABLE ThermalBattery (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),
    capacity DECIMAL(10, 2),
    DC_AC_Out VARCHAR(255),
    storage_efficiency DECIMAL(5, 2),
    charge_efficiency DECIMAL(5, 2),
    discharge_efficiency DECIMAL(5, 2),
    state_of_charge DECIMAL(5, 2),
    thermal_conductivity DECIMAL(10, 2),
    temperature_range JSON,
    heat_loss_coefficient DECIMAL(10, 2),
    lifespan INT,
    location VARCHAR(255),
    description TEXT
);

-- Junction table for the many-to-many relationship between Site and ThermalBattery
CREATE TABLE Site_ThermalBattery (
    site_id INT,
    thermal_battery_id INT,
    PRIMARY KEY (site_id, thermal_battery_id),
    FOREIGN KEY (site_id) REFERENCES Site(id),
    FOREIGN KEY (thermal_battery_id) REFERENCES ThermalBattery(id)
);

CREATE TABLE ThermalBattery_KPI (
    ThermalBattery_id INT,
    kpi_id INT,
    PRIMARY KEY (ThermalBattery_id, kpi_id),
    FOREIGN KEY (ThermalBattery_id) REFERENCES ThermalBattery  (id),
    FOREIGN KEY (kpi_id) REFERENCES KPI(id)
);
-- ------------------------------------------------------------------------------------


-- Table for CombinedHeatPower
CREATE TABLE CombinedHeatPower (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),
    capacity DECIMAL(10, 2),
    lifespan INT,
    DC_AC_Out VARCHAR(255),
    location VARCHAR(255),
    description TEXT,
    size VARCHAR(255),
    model_type VARCHAR(255),
    efficiency DECIMAL(5, 2),
    operational_cost DECIMAL(10, 2),
    installation_cost DECIMAL(10, 2),
    maintenance_cost DECIMAL(10, 2),
    capacity_factor DECIMAL(5, 2),
    unit VARCHAR(50),
    fuel_type VARCHAR(255),
    generation_type VARCHAR(255),
    emissions_rate DECIMAL(10, 2),
    thermal_efficiency DECIMAL(5, 2),
    electrical_efficiency DECIMAL(5, 2),
    heat_output DECIMAL(10, 2),
    power_output DECIMAL(10, 2)
);

-- Junction table for the many-to-many relationship between Site and CombinedHeatPower
CREATE TABLE Site_CombinedHeatPower (
    site_id INT,
    combined_heat_power_id INT,
    PRIMARY KEY (site_id, combined_heat_power_id),
    FOREIGN KEY (site_id) REFERENCES Site(id),
    FOREIGN KEY (combined_heat_power_id) REFERENCES CombinedHeatPower(id)
);

CREATE TABLE CombinedHeatPower_KPI (
    CombinedHeatPower_id INT,
    kpi_id INT,
    PRIMARY KEY (CombinedHeatPower_id, kpi_id),
    FOREIGN KEY (CombinedHeatPower_id) REFERENCES CombinedHeatPower  (id),
    FOREIGN KEY (kpi_id) REFERENCES KPI(id)
);
-- ------------------------------------------------------------------------------------

-- Table for Generator
CREATE TABLE Generator (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),
    capacity DECIMAL(10, 2),
    lifespan INT,
    DC_AC_Out VARCHAR(255),
    location VARCHAR(255),
    description TEXT,
    size VARCHAR(255),
    model_type VARCHAR(255),
    efficiency DECIMAL(5, 2),
    operational_cost DECIMAL(10, 2),
    installation_cost DECIMAL(10, 2),
    maintenance_cost DECIMAL(10, 2),
    capacity_factor DECIMAL(5, 2),
    unit VARCHAR(50),
    fuel_type VARCHAR(255),
    generation_type VARCHAR(255),
    emissions_rate DECIMAL(10, 2),
    generator_efficiency DECIMAL(5, 2),
    power_output DECIMAL(10, 2),
    operating_hours DECIMAL(10, 2)
);

-- Junction table for the many-to-many relationship between Site and Generator
CREATE TABLE Site_Generator (
    site_id INT,
    generator_id INT,
    PRIMARY KEY (site_id, generator_id),
    FOREIGN KEY (site_id) REFERENCES Site(id),
    FOREIGN KEY (generator_id) REFERENCES Generator(id)
);

CREATE TABLE Generator_KPI (
    Generator_id INT,
    kpi_id INT,
    PRIMARY KEY (Generator_id, kpi_id),
    FOREIGN KEY (Generator_id) REFERENCES Generator  (id),
    FOREIGN KEY (kpi_id) REFERENCES KPI(id)
);
-- ------------------------------------------------------------------------------------

-- Create the SteamMethaneReformer table
CREATE TABLE SteamMethaneReformer (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),
    capacity DECIMAL(10, 2),
    lifespan INT,
    DC_AC_Out VARCHAR(255),
    location VARCHAR(255),
    description TEXT,
    size VARCHAR(255),
    model_type VARCHAR(255),
    efficiency DECIMAL(5, 2),
    operational_cost DECIMAL(10, 2),
    installation_cost DECIMAL(10, 2),
    maintenance_cost DECIMAL(10, 2),
    capacity_factor DECIMAL(5, 2),
    unit VARCHAR(50),
    fuel_type VARCHAR(255) DEFAULT 'Natural Gas',
    generation_type VARCHAR(255),
    emissions_rate DECIMAL(10, 2),
    reformer_efficiency DECIMAL(5, 2),
    hydrogen_production_rate DECIMAL(10, 2),
    operating_hours DECIMAL(10, 2)
);

-- Create the Site_SteamMethaneReformer junction table
CREATE TABLE Site_SteamMethaneReformer (
    site_id INT,
    steam_methane_reformer_id INT,
    PRIMARY KEY (site_id, steam_methane_reformer_id),
    FOREIGN KEY (site_id) REFERENCES Site(id),
    FOREIGN KEY (steam_methane_reformer_id) REFERENCES SteamMethaneReformer(id)
);
CREATE TABLE SteamMethaneReformer_KPI (
    SteamMethaneReformer_id INT,
    kpi_id INT,
    PRIMARY KEY (SteamMethaneReformer_id, kpi_id),
    FOREIGN KEY (SteamMethaneReformer_id) REFERENCES SteamMethaneReformer  (id),
    FOREIGN KEY (kpi_id) REFERENCES KPI(id)
);
-- ------------------------------------------------------------------------------------
-- Table for HydrogenBasedCPHS
CREATE TABLE HydrogenBasedCPHS (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),
    capacity DECIMAL(10, 2),
    lifespan INT,
    DC_AC_Out VARCHAR(255),
    location VARCHAR(255),
    description TEXT,
    size VARCHAR(255),
    model_type VARCHAR(255),
    efficiency DECIMAL(5, 2),
    operational_cost DECIMAL(10, 2),
    installation_cost DECIMAL(10, 2),
    maintenance_cost DECIMAL(10, 2),
    capacity_factor DECIMAL(5, 2),
    unit VARCHAR(50),
    generation_type VARCHAR(255),
    environmental_impact TEXT,
    renewable_sources VARCHAR(255),
    hydrogen_consumption_rate DECIMAL(10, 2),
    water_consumption_rate DECIMAL(10, 2)
);

-- Junction table for the many-to-many relationship between Site and HydrogenBasedCPHS
CREATE TABLE Site_HydrogenBasedCPHS (
    site_id INT,
    hydrogen_based_cphs_id INT,
    PRIMARY KEY (site_id, hydrogen_based_cphs_id),
    FOREIGN KEY (site_id) REFERENCES Site(id),
    FOREIGN KEY (hydrogen_based_cphs_id) REFERENCES HydrogenBasedCPHS(id)
);
CREATE TABLE HydrogenBasedCPHS_KPI (
    HydrogenBasedCPHS_id INT,
    kpi_id INT,
    PRIMARY KEY (HydrogenBasedCPHS_id, kpi_id),
    FOREIGN KEY (HydrogenBasedCPHS_id) REFERENCES HydrogenBasedCPHS (id),
    FOREIGN KEY (kpi_id) REFERENCES KPI(id)
);
-- ------------------------------------------------------------------------------------
-- Table for WaterTreatmentPlant
CREATE TABLE WaterTreatmentPlant (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),
    capacity DECIMAL(10, 2),
    lifespan INT,
    DC_AC_Out VARCHAR(255),
    location VARCHAR(255),
    description TEXT,
    size VARCHAR(255),
    model_type VARCHAR(255),
    efficiency DECIMAL(5, 2),
    operational_cost DECIMAL(10, 2),
    installation_cost DECIMAL(10, 2),
    maintenance_cost DECIMAL(10, 2),
    capacity_factor DECIMAL(5, 2),
    unit VARCHAR(50),
    generation_type VARCHAR(255),
    environmental_impact TEXT,
    renewable_sources VARCHAR(255),
    power_consumption_per_m3 DECIMAL(10, 2)
);

-- Junction table for the many-to-many relationship between Site and WaterTreatmentPlant
CREATE TABLE Site_WaterTreatmentPlant (
    site_id INT,
    water_treatment_plant_id INT,
    PRIMARY KEY (site_id, water_treatment_plant_id),
    FOREIGN KEY (site_id) REFERENCES Site(id),
    FOREIGN KEY (water_treatment_plant_id) REFERENCES WaterTreatmentPlant(id)
);

CREATE TABLE WaterTreatmentPlant_KPI (
    WaterTreatmentPlant_id INT,
    kpi_id INT,
    PRIMARY KEY (WaterTreatmentPlant_id, kpi_id),
    FOREIGN KEY (WaterTreatmentPlant_id) REFERENCES WaterTreatmentPlant (id),
    FOREIGN KEY (kpi_id) REFERENCES KPI(id)
);
-- ------------------------------------------------------------------------------------
-- Table for PowerPlant
CREATE TABLE PowerPlant (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),
    fuel_type VARCHAR(255),
    capacity DECIMAL(10, 2),
    lifespan INT,
    DC_AC_Out VARCHAR(255),
    location VARCHAR(255),
    description TEXT,
    size VARCHAR(255),
    model_type VARCHAR(255),
    efficiency DECIMAL(5, 2),
    operational_cost DECIMAL(10, 2),
    installation_cost DECIMAL(10, 2),
    maintenance_cost DECIMAL(10, 2),
    capacity_factor DECIMAL(5, 2),
    unit VARCHAR(50),
    emissions_rate DECIMAL(10, 2),
    generation_type VARCHAR(255),
    fuel_consumption_rate DECIMAL(10, 2)
);

-- Junction table for the many-to-many relationship between Site and PowerPlant
CREATE TABLE Site_PowerPlant (
    site_id INT,
    power_plant_id INT,
    PRIMARY KEY (site_id, power_plant_id),
    FOREIGN KEY (site_id) REFERENCES Site(id),
    FOREIGN KEY (power_plant_id) REFERENCES PowerPlant(id)
);
-- Create the Energy_Asset_KPI junction table
CREATE TABLE PowerPlant_KPI (
    PowerPlant_id INT,
    kpi_id INT,
    PRIMARY KEY (PowerPlant_id, kpi_id),
    FOREIGN KEY (PowerPlant_id) REFERENCES PowerPlant (id),
    FOREIGN KEY (kpi_id) REFERENCES KPI(id)
);