#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  2 18:39:38 2019

@author: alifahsanul
"""

"""
Approaches:
1. Country default spread
    Total ERP = US market premium + Indonesia bond CDS
2. Equity volatility based
    Total ERP = US market premium * (σ Indonesia equity / σ US equity)
3. Combine approach
    Total ERP = US market premium + country risk premium (CRP)
    CRP = Indonesia bond CDS * (σ Indonesia equity / σ Indonesia bond)
"""

import pandas as pd
import numpy as np

from risk_free_rate import default_probability

def nearest(items, pivot):
    return min(items, key=lambda x: abs(x - pivot))

def sync_start_df(df_list):
    start_date = pd.Timestamp(1900, 1, 1)
    for i in range(len(df_list)-1):
        start_date = max(start_date, min(df_list[i].index), min(df_list[i+1].index))
    res = [0] * len(df_list)
    for i in range(len(res)):
        df_i = df_list[i]
        res[i] = df_i[start_date:]
    return res

def get_indo_5y_bond():
    indo_5y_bond = pd.read_csv('./data/Indonesia 5-Year Bond Yield Historical Data.csv', parse_dates=['Date'], usecols=['Date', 'Price'], index_col=['Date'])
    indo_5y_bond.index = indo_5y_bond.index.normalize()
    indo_5y_bond = indo_5y_bond.sort_index()
    indo_5y_bond = indo_5y_bond.dropna()
    return indo_5y_bond

def get_indo_10y_bond():
    indo_10y_bond = pd.read_csv('./data/Indonesia 10-Year Bond Yield Historical Data.csv', parse_dates=['Date'], usecols=['Date', 'Price'], index_col=['Date'])
    indo_10y_bond.index = indo_10y_bond.index.normalize()
    indo_10y_bond = indo_10y_bond.sort_index()
    indo_10y_bond = indo_10y_bond.dropna()
    return indo_10y_bond

def get_ihsg():
    ihsg = pd.read_excel('./data/ihsg_history.xlsx', parse_dates=[0])
    ihsg.set_index('Date', inplace=True)
    ihsg.index = ihsg.index.normalize()
    ihsg = ihsg.sort_index()
    ihsg['Return'] = ihsg['Close'].pct_change() * 100
    ihsg['1Y Return'] = np.nan
    for i in range(len(ihsg)-1, 0, -1):
        curr_date = ihsg.index[i]
        curr_price = ihsg.loc[curr_date, 'Close']
        prev_date = curr_date + pd.DateOffset(years=-1)
        if prev_date in ihsg.index:
            prev_price = ihsg.loc[prev_date, 'Close']
            delta = curr_price - prev_price
            perc_return = 100 * delta / prev_price
            ihsg.loc[curr_date, '1Y Return'] = perc_return
    ihsg = ihsg.dropna()
    return ihsg

def get_usa_5y_bond():
    usa_5y_bond = pd.read_csv('./data/United States 5-Year Bond Yield Historical Data.csv', parse_dates=['Date'], usecols=['Date', 'Price'], index_col=['Date'])
    usa_5y_bond.index = usa_5y_bond.index.normalize()
    usa_5y_bond = usa_5y_bond.sort_index()
    usa_5y_bond = usa_5y_bond.dropna()
    return usa_5y_bond

def get_usa_10y_bond():
    usa_10y_bond = pd.read_csv('./data/United States 10-Year Bond Yield Historical Data.csv', parse_dates=['Date'], usecols=['Date', 'Price'], index_col=['Date'])
    usa_10y_bond.index = usa_10y_bond.index.normalize()
    usa_10y_bond = usa_10y_bond.sort_index()
    usa_10y_bond = usa_10y_bond.dropna()
    return usa_10y_bond

def get_snp500():
    snp500 = pd.read_excel('./data/s&p500_history.xlsx', parse_dates=[0])
    snp500.set_index('Date', inplace=True)
    snp500.index = snp500.index.normalize()
    snp500 = snp500.sort_index()
    snp500['Return'] = snp500['Close'].pct_change() * 100
    snp500['1Y Return'] = np.nan
    for i in range(len(snp500)-1, 0, -1):
        curr_date = snp500.index[i]
        curr_price = snp500.loc[curr_date, 'Close']
        prev_date = curr_date + pd.DateOffset(years=-1)
        if prev_date in snp500.index:
            prev_price = snp500.loc[prev_date, 'Close']
            delta = curr_price - prev_price
            perc_return = 100 * delta / prev_price
            snp500.loc[curr_date, '1Y Return'] = perc_return
    snp500 = snp500.dropna()
    return snp500

def usa_market_premium(stock_df, bond_df, verbose=False):
    stock_df, bond_df = sync_start_df([stock_df, bond_df])
    df_index = [x for x in stock_df.index]
    df_index = df_index + [x for x in bond_df.index if x not in df_index]
    consolidated_df = pd.DataFrame(index=df_index)
    consolidated_df = consolidated_df.sort_index()
    consolidated_df['stock'] = stock_df['1Y Return']
    consolidated_df['bond'] = bond_df['Price']
    consolidated_df['equity premium'] = consolidated_df['stock'] - consolidated_df['bond']
    consolidated_df = consolidated_df.dropna()
    standard_error = consolidated_df['equity premium'].sem()
    stock_arithmetic_avg_ret = consolidated_df['stock'].mean()
    bond_arithmetic_avg_ret = consolidated_df['bond'].mean()
    usa_equity_risk_premium = stock_arithmetic_avg_ret - bond_arithmetic_avg_ret
    if verbose == True:
        print('Start day of calculation: {}'.format(stock_df.index[0]))
        print('Arithmetic avg USA stock return is {:.2f}%'.format(stock_arithmetic_avg_ret))
        print('Arithmetic avg USA bond return is {:.2f}%'.format(bond_arithmetic_avg_ret))
        print('Arithmetic average USA equity risk premium is {:.1f}%'.format(usa_equity_risk_premium))
        print('Standard error is {:.2f}%'.format(standard_error))
    return usa_equity_risk_premium

approach = 1

approach_title = {1: 'Country default spread', 2:'Equity volatility based', 3:'Combine approach'}
print('Selected approach: {}. {}'.format(approach, approach_title[approach]))



if approach == 1:
    """
    Total ERP = US market premium + Indonesia bond CDS
    """
    snp500 = get_snp500()
    usa_5y_bond = get_usa_5y_bond()
    snp500, usa_5y_bond = sync_start_df([snp500, usa_5y_bond])
    us_market_premium = usa_market_premium(snp500, usa_5y_bond, verbose=True)
    indo_cds_spread = default_probability
    total_erp = us_market_premium + indo_cds_spread
    print('US Market Premium is {:.1f}%'.format(us_market_premium))
    print('Indonesia bond CDS spread is {:.1f}%'.format(indo_cds_spread))
    print('Total ERP is {:.1f}%'.format(total_erp))
elif approach == 2:
    """
    Total ERP = US market premium * (σ Indonesia equity / σ US equity)
    """
    snp500 = get_snp500()
    usa_5y_bond = get_usa_5y_bond()
    ihsg = get_ihsg()
    us_market_premium = usa_market_premium(snp500, usa_5y_bond, verbose=True)
    snp500, usa_5y_bond, ihsg = sync_start_df([snp500, usa_5y_bond, ihsg])
    sigma_ihsg = ihsg['1Y Return'].std()
    sigma_snp500 = snp500['1Y Return'].std()
    total_erp = us_market_premium * sigma_ihsg / sigma_snp500
    print('US Market Premium is {:.1f}%'.format(us_market_premium))
    print('IHSG stdev is {:.1f}%'.format(sigma_ihsg))
    print('S&P 500 stdev is {:.1f}%'.format(sigma_snp500))
    print('Total ERP is {:.1f}%'.format(total_erp))
elif approach == 3:
    """
    Total ERP = US market premium + country risk premium (CRP)
    CRP = Indonesia bond CDS * (σ Indonesia equity / σ Indonesia bond)
    """
    snp500 = get_snp500()
    usa_5y_bond = get_usa_5y_bond()
    ihsg = get_ihsg()
    indo_5y_bond = get_indo_5y_bond()
    snp500, usa_5y_bond, ihsg, indo_5y_bond = sync_start_df([snp500, usa_5y_bond, ihsg, indo_5y_bond])
    us_market_premium = usa_market_premium(snp500, usa_5y_bond, verbose=True)
    sigma_ihsg = ihsg['1Y Return'].std()
    sigma_indo_bond = indo_5y_bond['Price'].std()
    indo_bond_cds_spread = default_probability
    crp = indo_bond_cds_spread * sigma_ihsg / sigma_indo_bond
    total_erp = us_market_premium + crp
    print('Indonesia country risk premium is {:.1f}%'.format(crp))
    print('Total ERP is {:.1f}%'.format(total_erp))
else:
    raise ValueError('wrong approach')











