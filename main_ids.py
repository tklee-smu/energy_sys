import os
import pandas as pd
from Config import read_config
from AutoAdvice import advice_service
from AutoAlloc import allocate_energy_consumption
from ARIMA import arima_model
from AutoPredict import predict_energy

def read_building_ids(filepath, sheet_name='Sheet1'):
    df = pd.read_excel(filepath, sheet_name=sheet_name)
    df['Building_ID'] = df['Building_ID'].astype(str)  # Make sure Building_ID is a string
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
    pred_tem_input_fname = config['Filepath']['temperature_input_filename']
    pred_hum_input_fname = config['Filepath']['humidity_input_filename']
    table_path = config['Table Info']['table_path']
    ec_day_table_ec_col_name = 'eg_value'  # Assuming 'eg_value' is correct
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
        config['Table Info']['temperature_profile_storage_path'] = f"C:\\Users\\tklee\\Desktop\\IASYSTEM\\STORAGE\\WD\\{location}\\TEM"
        config['Table Info']['humidity_profile_storage_path'] = f"C:\\Users\\tklee\\Desktop\\IASYSTEM\\STORAGE\\WD\\{location}\\HUM"
        pred_tem_input_fname = f"Pred_{location}_Tem_hourly.csv"
        pred_hum_input_fname = f"Pred_{location}_Hum_hourly.csv"

        print(f"Configuration updated for Building ID: {building_id} with Location: {location}")
    else:
        print("Building ID not found in the database. Exiting program.")
        return

    # Proceed with processing for the building
    print(f"Processing for Building ID: {building_id}")
    
    # Perform ARIMA model predictions
    pred_ec1 = arima_model(table_path, config['Table Info']['ec_daily_table_filename'], ec_day_table_ec_col_name, order=(1, 1, 0))

    # Perform regression to predict energy consumption
    pred_ec2 = predict_energy(table_path, config['Table Info']['hybrid_table_filename'], config['Table Info']['ed_table_filename'], 'EC', 'ED', config['Table Info']['temperature_profile_storage_path'], config['Table Info']['humidity_profile_storage_path'],
                              common_ipath, pred_tem_input_fname, pred_hum_input_fname, sch, set_tem_mach, set_hum_mach, set_tem_oheat, set_tem_ocool)

    # Generate advice based on predictions
    advice = advice_service(table_path, config['Table Info']['ed_table_filename'], config['Table Info']['hybrid_table_filename'], config['Table Info']['temperature_profile_storage_path'], config['Table Info']['humidity_profile_storage_path'], common_ipath, pred_tem_input_fname, pred_hum_input_fname,
                            'EC', 'ED', pred_ec2, set_tem_mach, set_hum_mach, set_tem_oheat, set_tem_ocool, target_es)

    # Allocate predicted energy consumption using ARIMA and Hybrid model predictions
    arima_pred = allocate_energy_consumption(table_path, config['Table Info']['ec_min_table_filename'], pred_ec1)
    hybrid_pred = allocate_energy_consumption(table_path, config['Table Info']['ec_min_table_filename'], pred_ec2)

    # Print results or perform further processing
    print(f"ARIMA Predictions for Building {building_id}:", arima_pred)
    print(f"Hybrid Model Predictions for Building {building_id}:", hybrid_pred)
    print(f"Advice DataFrame for Building {building_id}:", advice)

if __name__ == "__main__":
    main()
