import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from SimilarWD import similar_weather_days
from AutoAccess import access_table

def perform_regression(x, y, sample_weights=None):
    """
    Fits a linear regression model to the data.
    
    Parameters:
        x (np.array): The independent variable.
        y (np.array): The dependent variable.
        sample_weights (np.array, optional): Array of weights that are assigned to individual samples.
    
    Returns:
        tuple: Returns the coefficients and the intercept of the regression model.
    """
    x = x.reshape(-1, 1)
    y = y.reshape(-1, 1)
    model = LinearRegression()
    model.fit(x, y, sample_weight=sample_weights)
    return model.coef_[0][0], model.intercept_[0]

def predict_energy(table_path, hybrid_table_fname, ed_table_fname, ec_col_name, ed_col_name, tem_storage_path, hum_storage_path, common_ipath, pred_tem_input_fname, pred_hum_input_fname, sch, set_tem_mach, set_hum_mach, set_tem_oheat, set_tem_ocool):
    """
    Predicts energy consumption based on regression analysis and other factors.
    
    Parameters:
        table_path (str): Path to the data table.
        hybrid_table_fname (str): File name of the hybrid table.
        ed_table_fname (str): File name of the energy demand table.
        ec_col_name (str): Column name for energy consumption in the hybrid table.
        ed_col_name (str): Column name for energy demand in the hybrid table.
        ... (additional parameters for external functions)
    
    Returns:
        float: Predicted weighted energy consumption.
    """
    tem_index, hum_index = similar_weather_days(tem_storage_path, hum_storage_path, common_ipath, pred_tem_input_fname, pred_hum_input_fname)
    pred_ed = access_table(table_path, ed_table_fname, tem_index, hum_index, sch, set_tem_mach, set_hum_mach, set_tem_oheat, set_tem_ocool)
    df = pd.read_csv(f"{table_path}{hybrid_table_fname}")
    y = df[ec_col_name].values
    x = df[ed_col_name].values

    sample_weight = np.ones(len(x)) * 10
    sample_weight[-7:] *= 1000

    coef, intercept = perform_regression(x, y, sample_weight)
    return coef * pred_ed + intercept

def regression_analysis(table_path, hybrid_table_fname, target, is_forward=True):
    """
    Performs forward or reverse regression analysis.
    
    Parameters:
        table_path (str): Path to the data table.
        hybrid_table_fname (str): File name of the hybrid table.
        target (float): Target value for prediction or reverse calculation.
        is_forward (bool): Determines whether to perform forward or reverse regression.
    
    Returns:
        float: The result of regression analysis.
    """
    df = pd.read_csv(f"{table_path}{hybrid_table_fname}")
    if is_forward:
        x = df[df.columns[0]].values
        y = df[df.columns[-1]].values
    else:
        x = df[df.columns[-1]].values
        y = df[df.columns[0]].values
    
    coef, intercept = perform_regression(x, y)
    if is_forward:
        return coef * target + intercept
    else:
        return (target - intercept) / coef
