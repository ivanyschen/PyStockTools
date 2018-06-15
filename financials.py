import collections
import pprint
import pandas as pd
import requests
from bs4 import BeautifulSoup


def get_financial_statement(symbol, statement_type, preriod_type='quarterly'):
    """
    obtain a company's 4 most recent income statements.
    Data source: Nasdaq

    Args:
        symbol (str): ticker of a company
        statement_type (str): 'income-statement' or 'balance-sheet' or 'cash-flow'
        preriod_type (str): 'quarterly' or 'annual'

    Returns:
        data (pd.DataFrame): data
    """
    if preriod_type not in ['quarterly', 'annual']:
        raise ValueError('preriod_type should be either "quaterly" or "annual"')
    url = f'https://www.nasdaq.com/symbol/{symbol.lower()}/financials?query={statement_type}&data={preriod_type}'
    r = requests.get(url)
    if r.status_code != 200:
        r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html5lib')

    data_dict = collections.OrderedDict()
    thead_trs = soup.find(class_='genTable').select('table > thead > tr')
    for tr in thead_trs:
        ths = tr.select('th')
        if 'ending' in ths[0].text.lower():
            for th in ths[2:]:
                data_dict[th.text] = collections.OrderedDict()

    tbody_trs = soup.find(class_='genTable').select('table > tbody > tr')
    for tr in tbody_trs:
        if not tr.select('td') or not tr.select('th'):
            continue
        col_name = tr.select('th')[0].text
        tds = (td.text for td in tr.select('td')[1:] if '$' in td.text)
        for date, val in zip(data_dict.keys(), tds):
            data_dict[date][col_name] = val

    data = pd.DataFrame.from_dict(data_dict, orient='index')
    data = data[data.columns].apply(lambda x: x.str.replace(r'\$|,', ''))
    for col in data.columns.tolist():
        negative_ind = data[col].str.contains(r'\([0-9]+\)')
        cur_col = data[col].str.replace(r'\(|\)', '')
        cur_col = cur_col.apply(lambda x: float(x))
        cur_col[negative_ind] = (-1) * cur_col[negative_ind]
        data[col] = cur_col
    return data
