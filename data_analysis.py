import numpy as np
import pandas as pd

df = pd.read_csv('./외기온도_시간자료.csv')
df.columns = ['date', 'tem']
df = df.set_index('date')
df.index = pd.to_datetime(df.index)

df['cooling degree hour'] = np.where(df['tem'] > 18, df['tem'] - 18, 0)
df['heating degree hour'] = np.where(df['tem'] <= 18, 18 - df['tem'], 0)
df['degree hour'] = df['cooling degree hour'] + df['heating degree hour']

df.to_csv('./degree hour_hourly.csv')

df_daily = df.resample('D').sum()

df_daily.to_csv('./degree hour.csv')