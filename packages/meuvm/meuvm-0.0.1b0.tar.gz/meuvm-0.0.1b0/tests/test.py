from meuvm._meuvm_ba import MeuvmBa
from meuvm._meuvm_r import MeuvmR
from meuvm._meuvm_br import MeuvmBr
from matplotlib import pyplot as plt

import math
import re
import numpy as np
import pandas as pd
import xarray as xr
from sklearn.linear_model import LinearRegression
from matplotlib import pyplot as plt


# считаем среднее за 81 день, включая начало и конец, то есть всего 81 день и этот день, для которого считаем среднее



# f107 = pd.read_csv('clear_data/clear_data_avg.csv')
# f107_2002 = f107[f107['time'] >= '2002-02-08'].reset_index(drop=True)
#
# ssi = pd.read_csv('grouped_ssi_190cols.csv')
# ssi = ssi.loc[(ssi['time'] != '2004-12-16') & \
#               (ssi['time'] != '2004-12-17') & \
#               (ssi['time'] != '2004-12-18') & \
#               (ssi['time'] != '2004-12-19') & \
#               (ssi['time'] != '2004-12-20') & \
#               (ssi['time'] != '2008-02-03') & \
#               (ssi['time'] != '2008-12-21') & \
#               (ssi['time'] != '2011-01-01') & \
#               (ssi['time'] != '2012-01-01') & \
#               (ssi['time'] != '2015-01-13') & \
#               (ssi['time'] != '2021-05-09')]
#
# ssi = ssi.reset_index(drop=True)
# ssi = ssi[ssi.columns[2:]]
#
# data_full = pd.concat([f107_2002, ssi], axis=1)

# raw_data = pd.read_csv('clear_data_no_intervals.csv')
# step = 20
# bins = np.arange(60,430,step)
# intervals, cut_bins = pd.cut(raw_data['f107'], bins=bins,  retbins=True)
# intervals = pd.DataFrame(intervals)
# raw_data['intervals'] = intervals
#
# groups = raw_data.groupby(['intervals'])['f107']
# stats = groups.agg(['size','min','max','mean','median','std'])
# q25 = pd.DataFrame(groups.quantile(0.25))
# q25.columns=['q25']
# q50 = pd.DataFrame(groups.quantile(0.50))
# q50.columns=['q50']
# q75 = pd.DataFrame(groups.quantile(0.75))
# q75.columns=['q75']
# q10 = pd.DataFrame(groups.quantile(0.1))
# q10.columns=['q10']
# q90 = pd.DataFrame(groups.quantile(0.9))
# q90.columns=['q90']
# stats = pd.concat([stats, q25, q50, q75, q10, q90],axis=1)
# stats['range'] = stats['max'] - stats['min']
# stats.to_csv('f107_statistics_2002.csv')



# dict = {"(60, 80]" : 0,
#         "(80, 100]" : 1,
#         "(100, 120]" : 2,
#         "(120, 140]" : 3,
#         "(140, 160]" : 4,
#         "(160, 180]" : 5,
#         "(180, 200]" : 6,
#         "(200, 220]" : 7,
#         "(220, 240]" : 8,
#         "(240, 260]" : 9,
#         "(260, 280]" : 10,
#         "(280, 300]" : 11,
#         "(300, 320]" : 12,
#         "(320, 340]" : 13,
#         "(340, 360]" : 14,
#         "(360, 380]" : 15,
#         "(380, 400]" : 16,
#         "(400, 420]" : 17,}

# data = pd.read_csv('clear_data_with_intervals_and_numbers.csv')
# data['interval_no'] = [dict[i] for i in data['intervals']]
# data.to_csv('clear_data_with_intervals_and_numbers.csv',index=False)
# print(data[data['intervals'] == "(180, 200]"])

# data = pd.read_csv('clear_data_with_intervals_and_numbers.csv')
# out = pd.DataFrame(data.iloc[:, 5:-2].apply(lambda x: x != -1.0).all(True))
# out.columns = ['yes']
# print(out)
# yes = data.iloc[out[out['yes'] == True].index]
# yes = yes.reset_index(drop=True)


# 0 - 10 не пустые
# data = pd.read_csv('clear_data/clear_available_data.csv')
# print(data.groupby('interval_no').size())
#
# data = pd.read_csv('clear_data/clear_available_data.csv')
# coefs = []
#
# for i in range(10, 11):
#         print(i)
#         test = data[data['interval_no'] == i]
#         if test.shape[0] == 0:
#                 pass
#
#         x_test = [[j] for j in np.arange(60 + i*20, 81 + i*20, 1)]
#         x = test['f107'].to_numpy().reshape((-1,1))
#
#         for k in range(190):
#                 y = test[f'{0.5 + k}irr']
#                 model = LinearRegression(fit_intercept=True).fit(x, y)
#                 coefs.append([*model.coef_, model.intercept_])
#
#         coefs = pd.DataFrame(coefs)
#         coefs.columns=['B0', 'B1']
#         print(coefs)
#         coefs.to_csv('260_280.csv', index=False)



# data = pd.read_csv('clear_data/clear_available_data.csv')
# data = data[data['interval_no'] == 2]
# i = 1
# my_coefs = pd.read_csv('100_120.csv')
# x_test = [[100], [121]]
# k = my_coefs['B0'][i]
# b = my_coefs['B1'][i]
# y = [k*100 + b, k*121 + b]
#
# plt.scatter(data['f107'], data[f'{i}.5irr'], color='b', label='f107')
# plt.plot(x_test, y, color='r', label='Регрессия')
# plt.legend()
# plt.show()

# data = pd.DataFrame()
# data.insert(0, 'lband', np.arange(190))
# data.insert(1, 'center', [i+0.5 for i in range(190)])
# data.insert(2, 'uband', np.arange(1,191))
# print(data)
#
# for i in range(11):
#     dt = pd.read_csv(f'lin_interval_step20_coeffs/test_lin_interval_{i}.csv')
#     data = pd.concat([data, dt], axis=1)



# data = pd.read_csv('clear_data/clear_available_data.csv')
# print(data)
# data['189.5irr'].apply(lambda x: x / (6.62607015e-34 * 3e9 / 189.5))
# print(data)