import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from AutoProfile import auto_profile

def allocate_energy_consumption(table_path, min_ec_table_fname, predicted_ec):
    """
    Allocates predicted energy consumption over the next day's time periods based on energy profiles.

    Parameters:
        table_path (str): Path to the data table.
        min_ec_table_fname (str): Filename of the minimum energy consumption table.
        predicted_ec (float): Total predicted energy consumption for the next day.

    Returns:
        pd.DataFrame: DataFrame with energy consumption allocated over different time periods.
    """
    # Obtain the time profiles for energy consumption
    time_profiles = auto_profile(table_path, min_ec_table_fname)

    # Determine the next day's weekday index
    next_day_index = (datetime.today() + timedelta(days=1)).weekday()

    # Retrieve the specific time profile for the next day
    next_day_profile = time_profiles[next_day_index].reshape(-1, 96)

    # Ensure the profile sums to 1 to proportionally distribute the predicted energy consumption
    if np.sum(next_day_profile) == 0:
        raise ValueError("Profile sum for the next day is zero, cannot allocate energy.")

    # Allocate predicted energy based on the profile
    allocated_energy = predicted_ec * next_day_profile / np.sum(next_day_profile)

    # # Reshape and create a DataFrame for output
    # allocated_energy_df = pd.DataFrame(allocated_energy, columns=['Energy consumption [kWh]'])

    return allocated_energy

# Example usage:
# table_path = "path/to/your/data"
# min_ec_table_fname = "min_energy_consumption.csv"
# predicted_ec = 1000.0  # Predicted total energy consumption for the next day
# try:
#     allocation_result = allocate_energy_consumption(table_path, min_ec_table_fname, predicted_ec)
#     print(allocation_result)
# except Exception as e:
#     print(f"Error
