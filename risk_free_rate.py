#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  2 11:53:40 2019

@author: alifahsanul
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import pickle
import datetime as dt
import os

def indonesia_5y_default():
    filepath = './data/default_probability.pkl'
    if os.path.exists(filepath):
        today = dt.datetime.now().date()
        filetime = dt.datetime.fromtimestamp(os.path.getctime(filepath))
        if filetime.date() == today:
            with open(filepath, 'rb') as f:
                default_prob = pickle.load(f)
            return default_prob
    url = 'http://www.worldgovernmentbonds.com/country/indonesia/'
    print('parsing Indonesia 5y CDS from web ...')  
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.findAll('table')[2]
    rows = table.findAll(lambda tag: tag.name=='tr')
    l = []
    for tr in rows:
        td = tr.find_all('td')
        row = [tr.text.strip() for tr in td]
        non_blank = [x for x in row if x != '']
        if len(non_blank) > 0:
            l.append(non_blank)
    rate_table = pd.DataFrame(l, columns=['Credit Default Swap', 'CDS Value', 'Var % 1W', 'Var % 1M', 'Implied PD (%)'])
    rate_table['CDS Value'] = rate_table['CDS Value'].map(lambda x: float(x))
    rate_table['Var % 1W'] = rate_table['Var % 1W'].map(lambda x: float(x.replace('%', '').strip()))
    rate_table['Var % 1M'] = rate_table['Var % 1M'].map(lambda x: float(x.replace('%', '').strip()))
    rate_table['Implied PD (%)'] = rate_table['Implied PD (%)'].map(lambda x: float(x.replace('%', '').strip()))
    default_prob = rate_table.iloc[0]['Implied PD (%)']
    return default_prob

def indonesia_bond_rates():
    filepath = './data/indonesia_bond_table.csv'
    if os.path.exists(filepath):
        today = dt.datetime.now().date()
        filetime = dt.datetime.fromtimestamp(os.path.getctime(filepath))
        if filetime.date() == today:
            rate_table = pd.read_csv(filepath)
            return rate_table
    url = 'http://www.worldgovernmentbonds.com/country/indonesia/'
    print('parsing Indonesia bond rates from web ...')
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.findAll('table')[3]
    rows = table.findAll(lambda tag: tag.name=='tr')
    l = []
    for tr in rows:
        td = tr.find_all('td')
        row = [tr.text.strip() for tr in td]
        non_blank = [x for x in row if x != '']
        if len(non_blank) > 0:
            l.append(non_blank)
    rate_table = pd.DataFrame(l, columns=['Maturity', 'Y Last (%)', 'Y Chg 1M (bp)', 'Y Chg 6M (bp)', 'ZC Last', 'ZC Chg 1M (%)', 'ZC Chg 6M (%)'])
    rate_table['Y Last (%)'] = rate_table['Y Last (%)'].map(lambda x: float(x.replace('%', '').strip()))
    rate_table['Y Chg 1M (bp)'] = rate_table['Y Chg 1M (bp)'].map(lambda x: float(x.replace('bp', '').strip()))
    rate_table['Y Chg 6M (bp)'] = rate_table['Y Chg 6M (bp)'].map(lambda x: float(x.replace('bp', '').strip()))
    rate_table['ZC Last'] = rate_table['ZC Last'].map(lambda x: np.nan if x==None else float(x))
    rate_table['ZC Chg 1M (%)'] = rate_table['ZC Chg 1M (%)'].map(lambda x: np.nan if x==None else float(x.replace('%', '').strip()))
    rate_table['ZC Chg 6M (%)'] = rate_table['ZC Chg 6M (%)'].map(lambda x: np.nan if x==None else float(x.replace('%', '').strip()))
    return rate_table

def get_indonesia_bond_rate(table, period='5 years'):
    rate = table[table['Maturity'] == period]['Y Last (%)'].values[0]
    return rate


indonesia_bond_table = indonesia_bond_rates()
indo_5y_bond_rates = get_indonesia_bond_rate(indonesia_bond_table, '5 years')
default_probability = indonesia_5y_default()
y5_riskfree_rate = indo_5y_bond_rates - default_probability

with open('./data/default_probability.pkl', 'wb') as f:
    pickle.dump(default_probability, f)
indonesia_bond_table.to_csv('./data/indonesia_bond_table.csv')




#def create_indonesia_bond_rates(): #use bond rate from cds table
#    url = 'http://www.ibpa.co.id/DataPasarSuratUtang/HargadanYieldHarian/tabid/84/Default.aspx'
#    response = requests.get(url)
#    soup = BeautifulSoup(response.text, 'html.parser')
#    table = soup.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=='dnn_ctr504_ListGovernmentBond_gvTenor1') 
#    rows = table.findAll(lambda tag: tag.name=='tr')
#    
#    l = []
#    for tr in rows:
#        td = tr.find_all('td')
#        row = [tr.text for tr in td if tr.text != '']
#        row_num = [float(x) for x in row]
#        if len(row) > 0:
#            l.append(row_num)
#    rate_table = pd.DataFrame(l, columns = ['Year', 'Today', 'Yesterday'])
#    return rate_table

#def create_govts_rate():
#    url = 'http://www.worldgovernmentbonds.com/spread-historical-data/'
#    response = requests.get(url)
#    soup = BeautifulSoup(response.text, 'html.parser')
#    table = soup.find(lambda tag: tag.name=='table')
#    rows = table.findAll(lambda tag: tag.name=='tr')
#    l = []
#    for tr in rows:
#        td = tr.find_all('td')
#        row = [tr.text.strip() for tr in td]
#        non_blank = [x for x in row if x != '']
#        if len(non_blank) > 0:
#            l.append(non_blank)
#    rate_table = pd.DataFrame(l)
#    rows_bad_ind = rate_table[0].str.contains('Spread').values
#    rows_to_delete = rate_table[rows_bad_ind]
#    for i in range(len(rows_to_delete)-1):
#        row_now = rows_to_delete.iloc[i].values
#        row_next = rows_to_delete.iloc[i+1].values
#        assert row_now.shape == row_next.shape
#        for j in range(row_now.shape[0]):
#            el_now = row_now[j]
#            el_next = row_next[j]
#            assert el_now == el_next
#    vs_country_list = ['vs {} (%)'.format(x) for x in rows_to_delete.iloc[0].values[1:-1]]
#    rate_table_filtered = rate_table[~rows_bad_ind].copy()
#    rate_table_filtered.columns = ['Country', '10Y Yield (%)'] + vs_country_list
#    rate_table_filtered['10Y Yield (%)'] = rate_table_filtered['10Y Yield (%)'].map(lambda x: float(x.replace('%', '').strip()))
#    for colname in vs_country_list:
#        rate_table_filtered[colname] = rate_table_filtered[colname].map(lambda x: float(x.replace('bp', '').strip())/100)
#    return rate_table_filtered





