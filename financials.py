import collections
import pprint
import pandas as pd
import requests
from bs4 import BeautifulSoup


def get_income_statement(symbol, type_='quarterly'):
    """
    obtain a company's 4 most recent income statements.
    Data source: Nasdaq

    Args:
        symbol (str): ticker of a company
        type_ (str): 'quarterly' or 'annual'

    Returns:
        data (pd.DataFrame): data
    """
    if type_ not in ['quarterly', 'annual']:
        raise ValueError('type_ should be either "quaterly" or "annual"')

    url = f'https://www.nasdaq.com/symbol/{symbol.lower()}/financials?query=income-statement&data={type_}'
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
    pprint.pprint(data_dict)

    # # table =s
    # data_dict = dict()
    # print(table_div)


def get_balance_sheet(symbol, type_='quarterly'):
    """
    obtain a company's 4 most recent balance sheets.
    Data source: Nasdaq

    :param symbol:
    :param type_:
    :return:
    """


def get_cashflow_statement(symbol, type_='quarterly'):
    """
    obtain a company's 4 most recent cashflow statements.
    Data source: Nasdaq

    :param symbol:
    :param type_:
    :return:
    """
    pass
