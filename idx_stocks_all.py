#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  5 21:15:52 2019

@author: alifahsanul
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt
import os

FILEPATH = './data/idx_all_stocks.csv'

def correct_decimal_format(df_col):
    df_col = df_col.map(lambda x: x.replace('.', ''))
    df_col = df_col.map(lambda x: x.replace(',', '.'))
    df_col = df_col.map(lambda x: float(x))
    return df_col

def parse_table(page_n):
    if page_n == 0:
        url = 'https://www.idnfinancials.com/en/company'
    else:
        url = 'https://www.idnfinancials.com/en/company/page/{}'.format(page_n)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.findAll('table')[0]
    rows = table.findAll(lambda tag: tag.name=='tr')
    l = []
    for tr in rows:
        td = tr.find_all('td')
        row = [tr.text.strip() for tr in td]
        non_blank = [x for x in row if x != '']
        if len(non_blank) > 0:
            l.append(non_blank)
    stocks_df = pd.DataFrame(l)
    return stocks_df

def get_all_companies():
    filepath = FILEPATH
    if os.path.exists(filepath):
        today = dt.datetime.now().date()
        filetime = dt.datetime.fromtimestamp(os.path.getctime(filepath))
        if filetime.date() == today:
            companies = pd.read_csv(FILEPATH)
            return companies
    print('parsing companies data from web ...')
    table_list = []
    start_page = 0
    end_page = 640
    interval_page = 20
    for page_num in range(start_page, end_page+interval_page, interval_page):
        table = parse_table(page_num)
        table_list.append(table)
    companies = pd.DataFrame()
    for table in table_list:
        companies = companies.append(table)
    columns = ['Ticker', 'Company', 'Price', 'Change', 'EPS', 'PE Ratio (ttm)', 'Market Cap. (Million IDR)']
    companies.columns = columns
    companies['Price'] = correct_decimal_format(companies['Price'])
    companies['Market Cap. (Million IDR)'] = correct_decimal_format(companies['Market Cap. (Million IDR)'])
    companies['EPS'] = correct_decimal_format(companies['EPS'])
    companies['PE Ratio (ttm)'] = correct_decimal_format(companies['PE Ratio (ttm)'])
    companies = companies.sort_values('Market Cap. (Million IDR)')
    companies = companies.reset_index(drop=True)
    return companies

all_companies = get_all_companies()
filtered_companies = all_companies[all_companies['Price'] > 0]
all_companies.to_csv(FILEPATH, index=False)




















