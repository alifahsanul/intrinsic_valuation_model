#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  2 18:39:38 2019

@author: alifahsanul
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def nearest(items, pivot):
    return min(items, key=lambda x: abs(x - pivot))

indo_5y_bond = pd.read_csv('./data/Indonesia 5-Year Bond Yield Historical Data.csv', parse_dates=['Date'], usecols=['Date', 'Price'], index_col=['Date'])
indo_5y_bond = indo_5y_bond.sort_index()
indo_10y_bond = pd.read_csv('./data/Indonesia 10-Year Bond Yield Historical Data.csv', parse_dates=['Date'], usecols=['Date', 'Price'], index_col=['Date'])
indo_10y_bond = indo_10y_bond.sort_index()
ihsg = pd.read_excel('./data/ihsg_history.xlsx', header=None, parse_dates=[0])
ihsg.columns = ['Date', 'Price']
ihsg.set_index('Date', inplace=True)
ihsg = ihsg.sort_index()
ihsg['Return'] = ihsg['Price'].pct_change() * 100
ihsg['1Y Return'] = np.nan
for i in range(len(ihsg)-1, 0, -1):
    curr_date = ihsg.index[i]
    curr_price = ihsg.loc[curr_date, 'Price']
    prev_date = curr_date + pd.DateOffset(years=-1)
    if prev_date in ihsg.index:
        prev_price = ihsg.loc[prev_date, 'Price']
        delta = curr_price - prev_price
        perc_return = 100 * delta / prev_price
        ihsg.loc[curr_date, '1Y Return'] = perc_return

#fig, ax1 = plt.subplots()
#ax2 = ax1.twinx()
#ax1.plot(indo_5y_bond, label='5y bond')
#ax1.plot(indo_10y_bond, label='10y bond')
#ax2.plot(ihsg['1Y Return'], label='ihsg')
#plt.show()



stock_df = ihsg
bond_df = indo_5y_bond
start_date = max(min(stock_df.index), min(bond_df.index))
#start_date = pd.Timestamp(2009, 1, 1)
stock_df = stock_df[start_date:]
bond_df = bond_df[start_date:]


stock_arithmetic_avg_ret = stock_df['1Y Return'].mean()
bond_arithmetic_avg_ret = bond_df['Price'].mean()
equity_risk_premium = stock_arithmetic_avg_ret - bond_arithmetic_avg_ret
print('Stock arithmetic average return is {:.2f}%'.format(stock_arithmetic_avg_ret))
print('5Y bond arithmetic average return is {:.2f}%'.format(bond_arithmetic_avg_ret))
print('Equity risk premium is {:.1f}%'.format(equity_risk_premium))




















