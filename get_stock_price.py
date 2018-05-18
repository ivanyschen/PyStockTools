import re
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import config


API_KEY = config.ALPHAVANTAGE_API_KEY
WEBDRIVER_PATH = config.WEBDRIVER_PATH
options = Options()
options.set_headless()
WEBDRIVER = webdriver.Chrome(WEBDRIVER_PATH, options=options)

def get_daily_price(symbol, outputsize='compact'):
    url = (
        f'https://www.alphavantage.co/query?'
        f'function=TIME_SERIES_DAILY&'
        f'symbol={symbol}&'
        f'outputsize={outputsize}&'
        f'apikey={API_KEY}')
    r = requests.get(url)
    if r.status_code == 200:
        data = dict(r.json()["Time Series (Daily)"])
    else:
        raise(f'Request not valid. Status code: {r.status_code}.')    
    
    data = pd.DataFrame.from_dict(data, orient='index')
    mapper = lambda col_name: re.sub(r'[1-5]. ', '', col_name)
    data.rename(mapper, axis='columns', inplace=True)
    data = data.astype('float64')
    data = data.astype({'volume': 'int64'})
    data.index = pd.to_datetime(data.index)
    return data

def get_ohlc_avg(data):
    data['ohlc_avg'] = (data['open'] + data['high'] + data['low'] + data['close']) / 4
    return data

def get_hlc_avg(data):
    data['hlc_avg'] = (data['high'] + data['low'] + data['close']) / 3
    return data

def get_dividend_info(symbol):
    url = f'https://www.nasdaq.com/symbol/{symbol.lower()}/dividend-history'
    r = requests.get(url)
    if r.status_code != 200:
        raise(f'Request not valid. Status code: {r.status_code}')
    soup = BeautifulSoup(r.text, 'html5lib')
    soup = soup.find(id="quotes_content_left_dividendhistoryGrid")
    try:
        trs = soup.select("tbody > tr")
    except AttributeError:
        raise AttributeError("Dividend Info of the symbol not exist.")
    
    data_dict = dict()
    for tr in trs:
        exdate, div_amount, decldate, recdate, paydate = (d.text for d in tr.select('span'))
        row_data = {
            'div_amount': float(div_amount),
            'decldate': decldate,
            'recdate': recdate,
            'paydate': paydate
        }
        data_dict[exdate] = row_data

    df = pd.DataFrame.from_dict(data_dict, orient='index')
    df.index = pd.to_datetime(df.index)
    df['decldate'] = pd.to_datetime(df['decldate'], errors='coerce', format='%m/%d/%Y')
    df['recdate'] = pd.to_datetime(df['recdate'], errors='coerce', format='%m/%d/%Y')
    df['paydate'] = pd.to_datetime(df['paydate'], errors='coerce', format='%m/%d/%Y')
    df.sort_index(inplace=True)
    return df

def parse_for_data(html, data_dict):
    soup = BeautifulSoup(html, 'html5lib')
    trs = soup.find(id='earnings_announcements_earnings_table').select('tbody > tr')
    for tr in trs:
        date, period, estimate, reported, surprise, surprise_per, time = [td.text for td in tr.select('td')]
        data_dict[date] = {
            'period': period,
            'estimate': estimate,
            'reported': reported,
            'surprise': surprise,
            'surprise_per': surprise_per,
            'time': time,
        }

def get_earning_history(symbol):
    data_dict = dict()
    url = f'https://www.zacks.com/stock/research/{symbol.lower()}/earnings-announcements'
    WEBDRIVER.get(url)
    WEBDRIVER.implicitly_wait(10)
    html = WEBDRIVER.page_source
    parse_for_data(html, data_dict)
    while True:
        next_button = WEBDRIVER.find_element_by_id('earnings_announcements_earnings_table_next')
        button_class = next_button.get_attribute("class")
        if 'disable' in button_class:
            break
        next_button.click()
        WEBDRIVER.implicitly_wait(10)
        html = WEBDRIVER.page_source
        parse_for_data(html, data_dict)
    df = pd.DataFrame.from_dict(data_dict, orient='index')
    df.index = pd.to_datetime(df.index, errors='coerce', format='%m/%d/%Y')
    df['period'] = pd.to_datetime(df['period'], errors='coerce', format='%m/%Y')
    df[['estimate', 'reported']] = df[['estimate', 'reported']].apply(lambda x: x.str.replace('$', ''))
    df['surprise_per'] = df['surprise_per'].apply(lambda x: x.replace('%', ''))
    num_col = ['estimate', 'reported', 'surprise', 'surprise_per']
    df[num_col] = df[num_col].apply(pd.to_numeric)
    df['quarter'] = df['period'].apply(lambda d: d.month)
    df.loc[data['quarter'] == 3, 'quarter'] = 1
    df.loc[data['quarter'] == 6, 'quarter'] = 2
    df.loc[data['quarter'] == 9, 'quarter'] = 3
    df.loc[data['quarter'] == 12, 'quarter'] = 4
    return df
