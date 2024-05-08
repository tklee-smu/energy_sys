import os
import pandas as pd
from Config import read_config
from AutoAdvice import advice_service
from AutoAlloc import allocate_energy_consumption
from ARIMA import arima_model
from AutoPredict import predict_energy
from DegreeHour import load_data, calculate_degree_hours, train_energy_model, predict_next_day_energy

def read_building_ids(filepath, sheet_name='Sheet1'):
    df = pd.read_excel(filepath, sheet_name=sheet_name)
    df['Building_ID'] = df['Building_ID'].astype(str)  # Ensure Building_ID is a string
    return df.set_index('Building_ID')

def load_config():
    ini_path = os.path.join('C:\\', 'Users', 'tklee', 'Desktop', 'IASYSTEM')
    config_filename = 'CONFIG.ini'
    return read_config(ini_path, config_filename)

def main():
    # Load configuration
    config = load_config()

    # Define necessary variables using the configuration
    common_ipath = config['Filepath']['input_path']
    table_path = config['Table Info']['table_path']
    ec_day_table_ec_col_name = 'eg_value'  # Assuming 'eg_value' is correct
    ec_hour_table_fname = config['Table Info']['ec_hourly_table_filename']
    tem_hour_table_fname = config['Table Info']['tem_hourly_table_filename']
    sch = 1
    set_tem_mach = config['User Variables']['setpoint_temperature_machine']
    set_hum_mach = config['User Variables']['setpoint_humidity_machine']
    set_tem_oheat = config['User Variables']['setpoint_temperature_office_heating']
    set_tem_ocool = config['User Variables']['setpoint_temperature_office_cooling']
    target_es = config['User Variables']['target_value_of_energy_saving']

    # Path to the Excel file with Building IDs
    building_id_filepath = os.path.join(common_ipath, 'building_ids.xlsx')

    # Get Building ID from user input
    building_id = input("Please enter the Building ID: ")
    building_id = str(building_id)

    # Read building IDs
    building_data = read_building_ids(building_id_filepath)

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

        print(f"Configuration updated for Building ID: {building_id} with Location: {location}")
    else:
        print("Building ID not found in the database. Exiting program.")
        return

    # User chooses the prediction method
    print("Select the prediction method:")
    print("1: ARIMA Model")
    print("2: Energy Prediction Model")
    print("3: Degree Hour Based Prediction")
    method_choice = input("Enter your choice (1, 2, or 3): ")

    # Proceed with processing for the building
    print(f"Processing for Building ID: {building_id}")

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

    if method_choice == '1' or method_choice == '2':
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

if __name__ == "__main__":
    main()
