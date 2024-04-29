import pandas as pd
import numpy as np
from datetime import datetime
from tslearn.clustering import TimeSeriesKMeans

def min_max_scaler(data):
    """
    Normalize data using the min-max scaling method.
    """
    if np.max(data) == np.min(data):
        return data  # Avoid division by zero if all values are the same
    return (data - np.min(data)) / (np.max(data) - np.min(data))

def cluster_time_series(data, n_clusters=1, random_seed=0):
    """
    Cluster time series data using TimeSeries KMeans.
    """
    if data.size == 0:
        return None, None  # Handle empty data scenarios
    km = TimeSeriesKMeans(n_clusters=n_clusters, max_iter=1000, metric='euclidean', random_state=random_seed)
    labels = km.fit_predict(data)
    return km, labels

def organize_data_by_weekday(df, column='eg_value'):
    """
    Organize data into lists for each weekday.
    """
    weekdays_data = [[] for _ in range(7)]  # List of lists for each day of the week
    for _, row in df.iterrows():
        weekday = datetime.strptime(row['date'], '%Y-%m-%d %H:%M').weekday()
        weekdays_data[weekday].append(row[column])
    return [np.array(day).reshape(-1, 96) for day in weekdays_data if day]  # Ensure each day has data

def auto_profile(table_path, min_ec_table_fname):
    """
    Generate profiles for each weekday using historical energy consumption data.
    """
    # Load data
    df = pd.read_csv(f"{table_path}{min_ec_table_fname}")
    
    # Organize data by weekdays
    weekday_data = organize_data_by_weekday(df)
    
    # Normalize and cluster data for each weekday
    profiles = []
    for data in weekday_data:
        normalized_data = min_max_scaler(data)
        km, _ = cluster_time_series(normalized_data, n_clusters=1, random_seed=0)
        if km:
            profiles.append(km.cluster_centers_)
    
    return profiles

# Example Usage
# table_path = '/path/to/data/'
# min_ec_table_fname = 'min_energy_consumption.csv'
# try:
#     profiles = auto_profile(table_path, min_ec_table_fname)
#     print("Generated Profiles:", profiles)
# except Exception as e:
#     print("Failed to generate profiles due to:", str(e))