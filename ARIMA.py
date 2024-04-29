import warnings
import os
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tools.sm_exceptions import ConvergenceWarning

# Suppress warnings from ARIMA model for a cleaner output
warnings.simplefilter('ignore', ConvergenceWarning)
warnings.simplefilter('ignore', UserWarning)

def arima_model(table_path, filename, column_name, order=(1, 1, 0)):
    """
    Forecast the next value in a time series using the ARIMA model.
    
    Parameters:
        table_path (str): The path to the directory containing the CSV file.
        filename (str): The name of the CSV file.
        column_name (str): The name of the column containing the time series data.
        order (tuple): The order of the ARIMA model (p, d, q).
        
    Returns:
        float: The forecasted next value of the time series.
    """
    # Construct full file path
    full_path = os.path.join(table_path, filename)
    
    # Read the specified column from the CSV file
    try:
        data_frame = pd.read_csv(full_path)
        time_series = data_frame[column_name].values
    except FileNotFoundError:
        print("The file was not found.")
        return None
    except pd.errors.EmptyDataError:
        print("The file is empty.")
        return None
    except KeyError:
        print(f"The column '{column_name}' does not exist in the data.")
        return None

    # Fit the ARIMA model
    try:
        model = ARIMA(time_series, order=order)
        model_fit = model.fit()
    except ValueError as e:
        print(f"Model fitting failed: {e}")
        return None
    
    # Forecast the next value
    forecasted_value = model_fit.forecast()[0]
    
    return forecasted_value

# Example usage:
# result = arima_model('path_to_data', 'energy_data.csv', 'energy_consumption')
# print(f"Forecasted Energy Consumption: {result}")
