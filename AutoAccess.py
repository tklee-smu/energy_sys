import pandas as pd

def access_table(table_path, ed_table_fname, tem_index, hum_index, sch, set_tem_mach, set_hum_mach, set_tem_oheat, set_tem_ocool):
    """
    Access a data table and extract predicted energy demand based on set conditions.

    Parameters:
        table_path (str): Directory path where the data file is located.
        ed_table_fname (str): Filename of the energy demand table.
        tem_index (int): Temperature index for lookup.
        hum_index (int): Humidity index for lookup.
        sch (int): Schedule index.
        set_tem_mach (int): Set temperature for machinery.
        set_hum_mach (int): Set humidity for machinery.
        set_tem_oheat (int): Set heating temperature for office.
        set_tem_ocool (int): Set cooling temperature for office.

    Returns:
        float: Predicted energy demand for the given settings.
    """
    # Mapping setpoints to their index positions
    set_m_t = list(range(15, 26))  # Machinery room temperatures
    set_m_h = list(range(20, 70, 10))  # Machinery room humidity levels
    set_o_ht = list(range(18, 23))  # Office heating temperatures
    set_o_ct = list(range(24, 29))  # Office cooling temperatures

    # Convert set points to indices used in the table
    settings_indices = [
        set_m_t.index(int(set_tem_mach)) + 1,
        set_m_h.index(int(set_hum_mach)) + 1,
        set_o_ht.index(int(set_tem_oheat)) + 1,
        set_o_ct.index(int(set_tem_ocool)) + 1
    ]

    # Create a list of input settings to match against the table
    input_settings = [tem_index, hum_index, sch] + settings_indices

    # Load the table from the CSV file
    df = pd.read_csv(f"{table_path}{ed_table_fname}")
    df_array = df.to_numpy()

    # Find matching row based on the input settings
    for row in df_array:
        if input_settings == row[:7].tolist():
            return row[7]  # Return the predicted energy demand

    # If no matching row is found, raise an error or return a default value
    raise ValueError("No matching settings found in the table.")

# Example usage:
# pred_ed = access_table('path/to/table/', 'energy_demand.csv', 1, 2, 1, 20, 40, 21, 24)
# print(f"Predicted Energy Demand: {pred_ed}")
