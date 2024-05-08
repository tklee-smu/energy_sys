import os
import pandas as pd
from datetime import datetime, timedelta
import threading
from Config import read_config
from AutoAdvice import advice_service
from AutoAlloc import allocate_energy_consumption
from ARIMA import arima_model
from AutoPredict import predict_energy
from DegreeHour import load_data, calculate_degree_hours, train_energy_model, predict_next_day_energy


# Function to determine the current season based on month and day
def determine_season(month, day):
    if (month in (12, 1, 2)) or (month == 3 and day < 21):
        return 'heating'
    elif (month in (6, 7, 8)) or (month == 9 and day < 23):
        return 'cooling'
    else:
        return 'transition'


# Function to determine the season based on external temperature
def determine_season_from_temperature(temperature):
    if temperature < 10:
        return 'heating'
    elif temperature > 20:
        return 'cooling'
    else:
        return 'transition'


# Function to load seasonal configuration based on the season name
def load_seasonal_config(season):
    ini_path = os.path.join('C:\\', 'Users', 'tklee', 'Desktop', 'IASYSTEM')
    config_filename = f'CONFIG_{season.upper()}.ini'
    return read_config(ini_path, config_filename)


# Function to read building IDs from Excel
def read_building_ids(filepath, sheet_name='Sheet1'):
    df = pd.read_excel(filepath, sheet_name=sheet_name)
    df['Building_ID'] = df['Building_ID'].astype(str)  # Ensure Building_ID is a string
    return df.set_index('Building_ID')


# Function to get user input with a timeout
def input_with_timeout(prompt, timeout=10, default='1'):
    """Get user input with a timeout. If no input is received within the timeout, return a default value."""
    user_input = [default]  # Use a list to allow modification in nested functions

    def _timeout_input():
        print(f"\nNo response detected. Proceeding with default option {default}.")
        user_input[0] = default  # Directly set the user input to the default value

    def _get_input():
        try:
            user_input[0] = input(prompt)
        except EOFError:
            user_input[0] = default

    timer = threading.Timer(timeout, _timeout_input)
    timer.start()
    _get_input()
    timer.cancel()
    return user_input[0]


# Function to aggregate all buildings' energy demands using method 2
def aggregate_all_buildings_demand(building_id_filepath, season):
    # Load seasonal configuration
    config = load_seasonal_config(season)

    # Define necessary variables from the configuration
    common_ipath = config['Filepath']['input_path']
    table_path = config['Table Info']['table_path']
    sch = 1
    set_tem_mach = config['User Variables']['setpoint_temperature_machine']
    set_hum_mach = config['User Variables']['setpoint_humidity_machine']
    set_tem_oheat = config['User Variables']['setpoint_temperature_office_heating']
    set_tem_ocool = config['User Variables']['setpoint_temperature_office_cooling']

    # Read all buildings from the Excel file
    building_data = read_building_ids(building_id_filepath)

    # Aggregate energy predictions across all buildings using method 2
    total_demand = pd.DataFrame()

    for building_id in building_data.index:
        config['Table Info']['hybrid_table_filename'] = building_data.loc[building_id, 'Hybrid DB']
        config['Table Info']['ed_table_filename'] = building_data.loc[building_id, 'ED DB']
        config['Table Info']['ec_daily_table_filename'] = building_data.loc[building_id, 'EC Daily']
        config['Table Info']['ec_min_table_filename'] = building_data.loc[building_id, 'EC Minutely']
        
        location = building_data.loc[building_id, 'Location']

        # Update paths for each building
        config['Table Info']['hybrid_table_filename'] = building_data.loc[building_id, 'Hybrid DB']
        config['Table Info']['ed_table_filename'] = building_data.loc[building_id, 'ED DB']
        config['Table Info']['temperature_profile_storage_path'] = os.path.join('C:\\Users\\tklee\\Desktop\\IASYSTEM\\STORAGE\\WD', location, 'TEM')
        config['Table Info']['humidity_profile_storage_path'] = os.path.join('C:\\Users\\tklee\\Desktop\\IASYSTEM\\STORAGE\\WD', location, 'HUM')
        config['Filepath']['temperature_input_filename'] = f"Pred_{location}_Tem_hourly.csv"
        config['Filepath']['humidity_input_filename'] = f"Pred_{location}_Hum_hourly.csv"

        # Perform the energy prediction for each building (option 2)
        pred_result = predict_energy(table_path, config['Table Info']['hybrid_table_filename'], config['Table Info']['ed_table_filename'], 'EC', 'ED', config['Table Info']['temperature_profile_storage_path'], config['Table Info']['humidity_profile_storage_path'],
                                     common_ipath, config['Filepath']['temperature_input_filename'], config['Filepath']['humidity_input_filename'], sch, set_tem_mach, set_hum_mach, set_tem_oheat, set_tem_ocool)
        allocated_result = allocate_energy_consumption(table_path, config['Table Info']['ec_min_table_filename'], pred_result)
        
        # Ensure pred_result is a DataFrame
        if not isinstance(allocated_result, pd.DataFrame):
            allocated_result = pd.DataFrame(allocated_result).transpose()

        # Append each building's prediction result into total_demand
        total_demand = pd.concat([total_demand, allocated_result], axis=1)
    
    total_demand['Total'] = total_demand.sum(axis=1)

    print("Aggregated Total Energy Demand Across All Buildings:")
    print(total_demand['Total'])

# Function to process individual building demand predictions
def process_individual_building(config, season, building_id, building_data, common_ipath, table_path, sch, set_tem_mach, set_hum_mach, set_tem_oheat, set_tem_ocool, target_es, ec_day_table_ec_col_name, ec_hour_table_fname, tem_hour_table_fname):
    if building_id in building_data.index:
        config['Table Info']['hybrid_table_filename'] = building_data.loc[building_id, 'Hybrid DB']
        config['Table Info']['ed_table_filename'] = building_data.loc[building_id, 'ED DB']
        config['Table Info']['ec_daily_table_filename'] = building_data.loc[building_id, 'EC Daily']
        config['Table Info']['ec_min_table_filename'] = building_data.loc[building_id, 'EC Minutely']

        # Update temperature and humidity paths based on the location
        location = building_data.loc[building_id, 'Location']
        config['Table Info']['temperature_profile_storage_path'] = os.path.join('C:\\Users\\tklee\\Desktop\\IASYSTEM\\STORAGE\\WD', location, 'TEM')
        config['Table Info']['humidity_profile_storage_path'] = os.path.join('C:\\Users\\tklee\\Desktop\\IASYSTEM\\STORAGE\\WD', location, 'HUM')
        config['Filepath']['temperature_input_filename'] = f"Pred_{location}_Tem_hourly.csv"
        config['Filepath']['humidity_input_filename'] = f"Pred_{location}_Hum_hourly.csv"

        print(f"Configuration updated for Building ID: {building_id} with Location: {location} and Season: {season.capitalize()}")

        # User chooses the prediction method
        print("Select the prediction method:")
        print("1: ARIMA Model")
        print("2: Energy Prediction Model")
        print("3: Degree Hour Based Prediction")
        method_choice = input("Enter your choice (1, 2, or 3): ")

        # Proceed with processing for the building
        print(f"Processing for Building ID: {building_id} in the {season.capitalize()} Season")

        # Execute predictions and calculate advice based on the selected method
        if method_choice == '1':
            pred_result = arima_model(table_path, config['Table Info']['ec_daily_table_filename'], ec_day_table_ec_col_name, order=(1, 1, 0))
        elif method_choice == '2':
            pred_result = predict_energy(table_path, config['Table Info']['hybrid_table_filename'], config['Table Info']['ed_table_filename'], 'EC', 'ED', config['Table Info']['temperature_profile_storage_path'], config['Table Info']['humidity_profile_storage_path'],
                                         common_ipath, config['Filepath']['temperature_input_filename'], config['Filepath']['humidity_input_filename'], sch, set_tem_mach, set_hum_mach, set_tem_oheat, set_tem_ocool)
        elif method_choice == '3':
            new_tem_input_fname = input("Enter the next day hourly temperature input filename: ")
            new_temperature_path = os.path.join(common_ipath, new_tem_input_fname)
            new_temperature_file = new_temperature_path

            # Load and prepare data
            temperature_file = os.path.join(table_path, tem_hour_table_fname)
            energy_file = os.path.join(table_path, ec_hour_table_fname)
            temp_df, energy_df = load_data(temperature_file, energy_file)
            temp_df = calculate_degree_hours(temp_df)

            # Train the model
            model = train_energy_model(temp_df, energy_df)

            # Assuming 'next_day_temperature.csv' for predictions
            next_day_temp_df = pd.read_csv(new_temperature_file)
            predicted_energy_df = predict_next_day_energy(model, next_day_temp_df)

            print("Predicted Hourly Energy Consumption for the Next Day:")
            print(predicted_energy_df)
        else:
            print("Invalid prediction method selected.")
            return

        if method_choice in ('1', '2'):
            # Allocate predicted energy consumption using the selected prediction method
            allocated_result = allocate_energy_consumption(table_path, config['Table Info']['ec_min_table_filename'], pred_result)
            # Output the results and advice
            print(f"Prediction result for Building {building_id} using method {method_choice}: {pred_result}")
            print(f"Allocated Energy Consumption for Building {building_id}: {allocated_result}")

        # Generate advice based on predictions
        if method_choice == '2':
            advice = advice_service(table_path, config['Table Info']['ed_table_filename'], config['Table Info']['hybrid_table_filename'], config['Table Info']['temperature_profile_storage_path'], config['Table Info']['humidity_profile_storage_path'], common_ipath, config['Filepath']['temperature_input_filename'], config['Filepath']['humidity_input_filename'],
                                    'EC', 'ED', pred_result, set_tem_mach, set_hum_mach, set_tem_oheat, set_tem_ocool, target_es)
            print(f"Advice DataFrame for Building {building_id}:", advice)


# Main function with option selection
def main():
    # Path to the Excel file with Building IDs
    building_id_filepath = os.path.join('C:\\', 'Users', 'tklee', 'Desktop', 'IASYSTEM', 'INPUT', 'building_ids.xlsx')

    # Ask the user to choose an option
    print("Choose an option:")
    print("1: Aggregate all buildings' energy demand using Method 2")
    print("2: Process an individual building")
    option_choice = input_with_timeout("Enter your choice (1 or 2): ", timeout=10, default='1')

    # Ask the user to choose a season detection option
    print("Select the season detection method:")
    print("1: Use the next day's date")
    print("2: Use external temperature data")
    print("3: Allow the user to select")
    season_option = input_with_timeout("Enter your choice (1, 2, or 3): ", timeout=10, default='1')

    # Determine the season based on the chosen option
    if season_option == '1':
        next_day = datetime.today() + timedelta(days=1)
        season = determine_season(next_day.month, next_day.day)
    elif season_option == '2':
        temperature_filename = input("Enter the next day hourly temperature input filename: ")
        temperature_filepath = os.path.join('C:\\Users\\tklee\\Desktop\\IASYSTEM', temperature_filename)
        next_day_temperature = pd.read_csv(temperature_filepath).iloc[0, 1]  # Assuming temperature is in the second column
        season = determine_season_from_temperature(next_day_temperature)
    elif season_option == '3':
        print("Choose the season:")
        print("1: Heating")
        print("2: Cooling")
        print("3: Transition")
        season_choice = input("Enter your choice (1, 2, or 3): ")

        season_map = {'1': 'heating', '2': 'cooling', '3': 'transition'}
        season = season_map.get(season_choice, 'transition')
    else:
        print("Invalid choice. Defaulting to option 1.")
        next_day = datetime.today() + timedelta(days=1)
        season = determine_season(next_day.month, next_day.day)

    if option_choice == '1':
        # Option 1: Aggregate all buildings' energy demand
        aggregate_all_buildings_demand(building_id_filepath, season)
        
    elif option_choice == '2':
        # Option 2: Process an individual building
        config = load_seasonal_config(season)

        # Define necessary variables using the seasonal configuration
        common_ipath = config['Filepath']['input_path']
        table_path = config['Table Info']['table_path']
        sch = 1
        set_tem_mach = config['User Variables']['setpoint_temperature_machine']
        set_hum_mach = config['User Variables']['setpoint_humidity_machine']
        set_tem_oheat = config['User Variables']['setpoint_temperature_office_heating']
        set_tem_ocool = config['User Variables']['setpoint_temperature_office_cooling']
        target_es = config['User Variables']['target_value_of_energy_saving']
        ec_day_table_ec_col_name = 'eg_value'
        ec_hour_table_fname = config['Table Info']['ec_hourly_table_filename']
        tem_hour_table_fname = config['Table Info']['tem_hourly_table_filename']

        # Read building IDs
        building_data = read_building_ids(building_id_filepath)

        # Get Building ID from user input
        building_id = input("Please enter the Building ID: ")
        building_id = str(building_id)

        # Process the individual building
        process_individual_building(config, season, building_id, building_data, common_ipath, table_path, sch, set_tem_mach, set_hum_mach, set_tem_oheat, set_tem_ocool, target_es, ec_day_table_ec_col_name, ec_hour_table_fname, tem_hour_table_fname)

    else:
        print("Invalid option selected. Exiting program.")


if __name__ == "__main__":
    main()
