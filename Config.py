import configparser
import os

def create_config_file(filename):
    """Creates and writes default settings to a configuration file."""
    config = configparser.ConfigParser()

    # Input Path
    config['Filepath'] = {
        'Input_Path': 'C:\\Users\\tklee\\Desktop\\IASYSTEM\\INPUT\\',
        'Temperature_Input_Filename': 'PRED_TEM_HOUR.csv',
        'Humidity_Input_Filename': 'PRED_HUM_HOUR.csv',
        'Radiation_Input_Filename': 'PRED_RAD_HOUR.csv',
        'EC_Min_Input_Filename': 'NEW_EC_MIN.csv',
        'PV_Min_Input_Filename': 'NEW_PV_MIN.csv',
        'RAD_Hour_Input_Filename': 'NEW_RAD_HOUR.csv',
        'TEM_Hour_Input_Filename': 'NEW_TEM_HOUR.csv',
        'HUM_Hour_Input_Filename': 'NEW_HUM_HOUR.csv'
    }

    # Model and Table Paths
    config['Modelpath'] = {'AI_Model_Path': 'C:\\Users\\tklee\\Desktop\\IASYSTEM\\STORAGE\\MODEL\\'}
    config['Table Info'] = {
        'Table_path': 'C:\\Users\\tklee\\Desktop\\IASYSTEM\\STORAGE\\',
        'ED_Table_Filename': 'ED_TABLE.csv',
        'Hybrid_Table_Filename': 'HYBRID_TABLE.csv',
        'PV_Hourly_Table_Filename': 'PV_HOUR_TABLE.csv',
        'EC_Min_Table_Filename': 'EC_MIN_TABLE.csv',
        'EC_Daily_Table_Filename': 'EC_DAY_TABLE.csv',
        'WD_Hourly_Table_Filename': 'WD_HOUR_TABLE.csv',
        'RAD_Hourly_Table_Filename': 'RAD_HOUR_TABLE.csv',
        'Temperature_Profile_Storage_Path': 'C:\\Users\\tklee\\Desktop\\IASYSTEM\\STORAGE\\WD\\TEM\\',
        'Humidity_Profile_Storage_Path': 'C:\\Users\\tklee\\Desktop\\IASYSTEM\\STORAGE\\WD\\HUM\\'
    }

    # User Variables
    config['User Variables'] = {
        'Setpoint_temperature_machine': '16',
        'Setpoint_humidity_machine': '30',
        'Setpoint_temperature_office_heating': '20',
        'Setpoint_temperature_office_cooling': '26',
        'Target_Value_of_Energy_Saving': '500'
    }

    # Save to file
    with open(filename, 'w', encoding='utf-8') as configfile:
        config.write(configfile)

def read_config(path, filename):
    """Reads configuration from file and returns a dictionary of settings."""
    config = configparser.ConfigParser()
    config.read(os.path.join(path, filename), encoding='utf-8')

    settings = {section: {key: config[section][key] for key in config[section]} for section in config.sections()}
    return settings

def main():
    config_filename = 'CONFIG.ini'
    config_path = os.path.join('C:\\', 'Users', 'tklee', 'Desktop', 'IASYSTEM')
    full_config_path = os.path.join(config_path, config_filename)

    # Create configuration file if it doesn't exist
    if not os.path.exists(full_config_path):
        create_config_file(full_config_path)

    # Read configuration
    config = read_config(config_path, config_filename)
    print(config)

if __name__ == "__main__":
    main()
