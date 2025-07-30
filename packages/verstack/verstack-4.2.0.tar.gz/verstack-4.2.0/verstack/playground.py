
import pandas as pd
df = pd.read_csv('/Users/danil/Downloads/NYC_Taxi_train неверный формат даты.csv', sep=';')



dff = df.copy()
dff.loc[:110, 'pickup_datetime'] = 'z'

dp = DateParser()
dp.fit_transform(dff)

dp.col_contains_dates(dff['pickup_datetime'])