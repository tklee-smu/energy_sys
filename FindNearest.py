import numpy as np

def find_nearest(data, target_value, column='Ed'):
    """
    Finds the index of the rows in the DataFrame where the specified column's value is closest to the target value.

    Parameters:
        data (pd.DataFrame): The DataFrame to search.
        target_value (float): The value to find the closest to in the DataFrame.
        column (str): The column in the DataFrame to compare the target value against.

    Returns:
        pd.Index: The index of the rows where the column value is closest to the target value.
    """
    # Compute absolute differences and find the minimum distance
    abs_diff = np.abs(data[column] - target_value)
    min_distance = abs_diff.min()

    # Find all indices where the distance is equal to the minimum distance
    nearest_indices = data[abs_diff == min_distance].index

    return nearest_indices

# Example Usage:
# df = pd.DataFrame({'Ed': [100, 200, 300, 400, 500]})
# target_value = 305
# nearest_index = find_nearest(df, target_value)
# print(f"Nearest index: {nearest_index}")
