import pandas as pd
import pandas_datareader.data as web
import datetime
import os
import numpy as np

start = datetime.datetime(1990, 1, 1)
end = datetime.datetime(2022, 11, 25)


def get_daily_value(code, name):
    try:
        daily = web.DataReader(code+".KS", "yahoo", start, end)
    except:
        daily = web.DataReader(code+".KQ", "yahoo", start, end)

    daily['code'] = code
    daily['name'] = name
    return daily.reset_index()


def read_data():
    codelist_pd = pd.read_csv('data/code_list.csv')
    # print(len(codelist_pd))
    # print(codelist_pd[:5])

    fn = 'data/daily_values.csv'
    err_list = []
    if os.path.exists(fn):
        daily_value = pd.read_csv(fn, dtype={'code': np.str})
    else:
        daily_value = pd.DataFrame(columns=['Date', 'code', 'name', 'High', 'Low', 'Close', 'Adj Close'])
        for row in codelist_pd.iterrows():
            try:
                daily_value = pd.concat([daily_value, get_daily_value(row[1][0], row[1][1])], axis=0)
            except Exception as e:
                # print('error: ', e, ', stock_code: ', row[1][0], ', company_name: ', row[1][1])
                err_list.append(row[1])
            finally:
                if row[0] % 500 + 1 == 0:
                    print('Done: ', row[0], 'Downloaded: ', len(daily_value), ', Error: ', len(err_list))

        err_df = pd.DataFrame(err_list)
        daily_value.to_csv(fn, index=False)
        err_df.to_csv('data/err_list')
    return daily_value


data_df = read_data()
# print(data_df[:3])
# data_df[(data_df['code'] == '033270') & (data_df['Date'] >= '2021-01-01')][:3]
print(data_df[data_df['code'] == '033270'])
# 이동평균을 구해보자
# 엔벨로프 돌파 전략
# https://stylebalance.tistory.com/77
