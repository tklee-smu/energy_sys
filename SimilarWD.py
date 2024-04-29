import os
import numpy as np
import pandas as pd

def read_and_reshape(path, filename, encoding='cp949'):
    """
    Helper function to read a CSV file and reshape it for further processing.
    """
    data = pd.read_csv(os.path.join(path, filename), encoding=encoding)
    return data.iloc[:, 1].values.reshape(-1, 1)  # Assumes data is in the second column

def calculate_distances(input_data, storage_path, file_extension='.csv'):
    """
    Calculate Euclidean distances between input data and each data file in the storage path.
    """
    storage_files = [f for f in os.listdir(storage_path) if f.endswith(file_extension)]
    distances = []

    for filename in storage_files:
        reference_data = read_and_reshape(storage_path, filename)
        distance = np.linalg.norm(input_data - reference_data)
        distances.append(distance)

    return distances

def similar_weather_days(tem_storage_path, hum_storage_path, common_ipath, pred_tem_input_fname, pred_hum_input_fname):
    """
    Determine the most similar weather days for temperature and humidity based on historical data.
    """
    # Read and reshape input temperature and humidity data
    tem_input = read_and_reshape(common_ipath, pred_tem_input_fname)
    hum_input = read_and_reshape(common_ipath, pred_hum_input_fname)

    # Calculate distances to stored temperature and humidity profiles
    dist_tem = calculate_distances(tem_input, tem_storage_path)
    dist_hum = calculate_distances(hum_input, hum_storage_path)

    # Find the index of the minimum distance
    tem_index = dist_tem.index(min(dist_tem)) + 1
    hum_index = dist_hum.index(min(dist_hum)) + 1

    return tem_index, hum_index

# # Example usage
# try:
#     tem_storage_path = '/path/to/temperature/storage'
#     hum_storage_path = '/path/to/humidity/storage'
#     common_ipath = '/path/to/common/input'
#     pred_tem_input_fname = 'predicted_temperature.csv'
#     pred_hum_input_fname = 'predicted_humidity.csv'
    
#     tem_index, hum_index = similar_weather_days(tem_storage_path, hum_storage_path, common_ipath, pred_tem_input_fname, pred_hum_input_fname)
#     print(f"Temperature Index: {tem_index}, Humidity Index: {hum_index}")
# except Exception as e:
#     print(f"An error occurred: {str(e)}")