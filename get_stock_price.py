import pandas as pd
import re
import requests


API_KEY =

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
    trs = soup.select("tbody > tr")
    
    data_dict = dict()
    for tr in trs:
        exdate, amount, decldate, recdate, paydate = (d.text for d in tr.select('span'))
        row_data = {
            'amount': float(amount),
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
    return df
