import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

def load_data(temperature_file, energy_file):
    """
    Load temperature and energy data from CSV files.
    
    Args:
    temperature_file (str): Path to the CSV file containing hourly temperatures.
    energy_file (str): Path to the CSV file containing hourly energy consumption.
    
    Returns:
    DataFrame, DataFrame: DataFrames containing the temperature and energy data.
    """
    try:
        temp_df = pd.read_csv(temperature_file)
        energy_df = pd.read_csv(energy_file)

        # Ensure no missing values
        temp_df = temp_df.dropna()
        energy_df = energy_df.dropna()
        
        if temp_df.empty or energy_df.empty:
            raise ValueError("One of the data files is empty after removing NaNs.")
        
        return temp_df, energy_df
    except FileNotFoundError:
        print(f"Error: One of the files {temperature_file} or {energy_file} was not found.")
        raise
    except pd.errors.EmptyDataError:
        print("Error: One of the files is empty.")
        raise
    except Exception as e:
        print(f"An error occurred: {e}")
        raise

def calculate_degree_hours(temp_df, threshold=18):
    """
    Calculate both heating and cooling degree hours from temperature data based on a threshold.
    Cooling degree hours are calculated for temperatures above the threshold and are stored in
    'Cooling_Degree_Hours'. Heating degree hours are calculated for temperatures below the threshold
    and are stored in 'Heating_Degree_Hours'.

    Args:
    temp_df (DataFrame): DataFrame containing the temperature data with columns ['Hour', 'Temperature'].
    threshold (float): The temperature threshold for calculating degree hours.

    Returns:
    DataFrame: Updated DataFrame with additional 'Cooling_Degree_Hours' and 'Heating_Degree_Hours' columns.
    """
    try:
        # Cooling Degree Hours: Positive when temperature is above the threshold
        temp_df['Degree_Hours'] = np.where(temp_df['Temperature'] > threshold,
                                                   temp_df['Temperature'] - threshold, 0)
        # Heating Degree Hours: Positive when temperature is below the threshold
        temp_df['Degree_Hours'] = np.where(temp_df['Temperature'] < threshold,
                                                   threshold - temp_df['Temperature'], 0)
        temp_df = pd.DataFrame(temp_df)
        return temp_df
    except KeyError:
        print("Error: 'Temperature' column not found in the DataFrame.")
        raise
    except TypeError:
        print("Error: Non-numeric data found in 'Temperature' column.")
        raise


def train_energy_model(temp_df, energy_df):
    """
    Train a linear regression model using degree hours as the feature for predicting energy consumption.
    
    Args:
    temp_df (DataFrame): DataFrame containing the temperature and degree hour data.
    energy_df (DataFrame): DataFrame containing the energy consumption data.
    
    Returns:
    LinearRegression: A trained linear regression model.
    """
    try:
        model = LinearRegression()
        model.fit(temp_df[['Degree_Hours']], energy_df['eg_value'])
        return model
    except KeyError:
        print("Error: Check if 'Degree_Hours' is in temp_df or 'eg_value' is in energy_df.")
        raise
    except ValueError as e:
        print(f"Error during model training: {e}")
        raise

def predict_next_day_energy(model, next_day_temp_df, threshold=18):
    """
    Predict the next day's hourly energy consumption based on degree hours calculated from hourly temperature data.
    
    Args:
    model (LinearRegression): The trained linear regression model.
    next_day_temp_df (DataFrame): DataFrame containing the next day's hourly temperatures with columns ['Hour', 'Temperature'].
    threshold (float): The temperature threshold for calculating degree hours.
    
    Returns:
    DataFrame: A DataFrame containing the predicted hourly energy consumption.
    """
    try:
        next_day_temp_df = calculate_degree_hours(next_day_temp_df, threshold)
        predicted_energy = model.predict(next_day_temp_df[['Degree_Hours']])
        return pd.DataFrame({
            'Predicted_Energy': predicted_energy
        })
    except Exception as e:
        print(f"Error in prediction: {e}")
        raise

