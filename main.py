import os
from Config import read_config
from AutoAdvice import advice_service
from AutoAlloc import allocate_energy_consumption
from ARIMA import arima_model
from AutoPredict import predict_energy

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
    hybrid_table_ec_col_name = 'EC'
    hybrid_table_ed_col_name = 'ED'
    sch = 1
    set_tem_mach = config['User Variables']['setpoint_temperature_machine']
    set_hum_mach = config['User Variables']['setpoint_humidity_machine']
    set_tem_oheat = config['User Variables']['setpoint_temperature_office_heating']
    set_tem_ocool = config['User Variables']['setpoint_temperature_office_cooling']
    target_es = config['User Variables']['target_value_of_energy_saving']

    # Perform ARIMA model predictions
    pred_ec1 = arima_model(config['Table Info']['table_path'], config['Table Info']['ec_daily_table_filename'], ec_day_table_ec_col_name, order=(1, 1, 0))

    # Perform regression to predict energy consumption
    pred_ec2 = predict_energy(table_path, config['Table Info']['hybrid_table_filename'], config['Table Info']['ed_table_filename'], hybrid_table_ec_col_name, hybrid_table_ed_col_name, config['Table Info']['temperature_profile_storage_path'], config['Table Info']['humidity_profile_storage_path'],
        common_ipath, pred_tem_input_fname, pred_hum_input_fname, sch, set_tem_mach, set_hum_mach, set_tem_oheat, set_tem_ocool)

    # Generate advice based on predictions
    advice = advice_service(table_path, config['Table Info']['ed_table_filename'], config['Table Info']['hybrid_table_filename'], config['Table Info']['temperature_profile_storage_path'], config['Table Info']['humidity_profile_storage_path'], common_ipath, pred_tem_input_fname, pred_hum_input_fname,
                    hybrid_table_ec_col_name, hybrid_table_ed_col_name, pred_ec2, set_tem_mach, set_hum_mach, set_tem_oheat, set_tem_ocool, target_es)

    # Allocate predicted energy consumption using ARIMA and Hybrid model predictions
    arima_pred = allocate_energy_consumption(table_path, config['Table Info']['ec_min_table_filename'], pred_ec1)
    hybrid_pred = allocate_energy_consumption(table_path, config['Table Info']['ec_min_table_filename'], pred_ec2)

    # Optionally print results or perform further processing
    print("ARIMA Predictions:", arima_pred)
    print("Hybrid Model Predictions:", hybrid_pred)
    print("Advice DataFrame:", advice)

if __name__ == "__main__":
    main()
