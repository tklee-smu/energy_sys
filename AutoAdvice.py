import pandas as pd
from AutoPredict import regression_analysis
from FindNearest import find_nearest
from SimilarWD import similar_weather_days

def get_setpoints_indices(set_tem_mach, set_hum_mach, set_tem_oheat, set_tem_ocool):
    Set_M_T = list(range(15, 26))  # Machinery room temperatures
    Set_M_H = list(range(20, 70, 10))  # Machinery room humidity levels
    Set_O_HT = list(range(18, 23))  # Office heating temperatures
    Set_O_CT = list(range(24, 29))  # Office cooling temperatures

    return {
        'a': Set_M_T.index(int(set_tem_mach)) + 1,
        'b': Set_M_H.index(int(set_hum_mach)) + 1,
        'c': Set_O_HT.index(int(set_tem_oheat)) + 1,
        'd': Set_O_CT.index(int(set_tem_ocool)) + 1
    }

def filter_ed_table(df, indices, tem_index, hum_index):
    return df[(df['Tem'] == tem_index) & (df['RH'] == hum_index) & (df['mSPT'] > indices['a']) & 
              (df['mSPH'] > indices['b']) & (df['oSPhT'] > indices['c']) & (df['oSPcT'] < indices['d'])]

def get_nearest_indices(ed_rev, req_ed):
    idx = find_nearest(ed_rev, req_ed)
    all_indices = idx.to_list() + (idx - 3).to_list() + (idx + 3).to_list()
    return sorted(set(all_indices))

def get_advice_list(df, indices, req_ed):
    list_df = df.loc[indices]
    filtered_list = list_df[list_df['Ed'] <= req_ed].to_numpy()
    return pd.DataFrame(filtered_list, columns=df.columns)

def update_target_ec(advice, table_path, hybrid_table_fname, target):
    for i in range(len(advice)):
        predicted_value = regression_analysis(table_path, hybrid_table_fname, target, is_forward=True)
        advice.at[i, 'Ed'] = predicted_value
    return advice

def advice_service(table_path, ed_table_fname, hybrid_table_fname, tem_storage_path, hum_storage_path, common_ipath, pred_tem_input_fname, pred_hum_input_fname,
                   ec_col_name, ed_col_name, pred_ec, set_tem_mach, set_hum_mach, set_tem_oheat, set_tem_ocool, target_es):

    indices = get_setpoints_indices(set_tem_mach, set_hum_mach, set_tem_oheat, set_tem_ocool)
    tem_index, hum_index = similar_weather_days(tem_storage_path, hum_storage_path, common_ipath, pred_tem_input_fname, pred_hum_input_fname)
    target = pred_ec - int(target_es)
    req_ed = regression_analysis(table_path, hybrid_table_fname, target, is_forward=False)

    df = pd.read_csv(f"{table_path}{ed_table_fname}")
    ed_rev = filter_ed_table(df, indices, tem_index, hum_index)
    nearest_indices = get_nearest_indices(ed_rev, req_ed)
    advice = get_advice_list(df, nearest_indices, req_ed)
    advice = update_target_ec(advice, table_path, hybrid_table_fname, target)

    # Calculate savings potential and sort
    advice['Saving Potential[%]'] = 100 - (advice['Ed'] / pred_ec * 100)
    advice.sort_values(by='Ed', inplace=True)
    advice.drop_duplicates(subset='Ed', inplace=True)
    advice.index = range(1, len(advice) + 1)

    if advice.empty:
        print("There is no suggested condition because (1) No matched condition in TRNSYS ED Table (2) Ideal setpoint control operating")

    return advice