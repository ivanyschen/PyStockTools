import collections
import pandas as pd
import requests
from bs4 import BeautifulSoup


class FinancialStatement(object):
    def __init__(self, symbol, period_type='quarterly'):
        self.symbol = symbol
        self._period_type = period_type

    @property
    def period_type(self):
        return self._period_type

    @period_type.setter
    def period_type(self, period):
        if period not in ['quarterly', 'annual']:
            raise ValueError('preriod_type should be either "quarterly" or "annual"')
        self._period_type = period

    @property
    def income_statement(self):
        return self._get_data(self.symbol, self._period_type, 'income-statement')

    @property
    def balance_sheet(self):
        return self._get_data(self.symbol, self._period_type, 'balance-sheet')

    @property
    def cashflow_statement(self):
        return self._get_data(self.symbol, self._period_type, 'cash-flow')

    def _get_data(self, symbol, period_type, statement_type):
        """
        obtain a company's 4 most recent income statements.
        Data source: Nasdaq

        Args:
            symbol (str): ticker of a company
            statement_type (str): 'income-statement' or 'balance-sheet' or 'cash-flow'
            period_type (str): 'quarterly' or 'annual'

        Returns:
            data (pd.DataFrame): data
        """
        if period_type not in ['quarterly', 'annual']:
            raise ValueError('preriod_type should be either "quarterly" or "annual"')
        url = f'https://www.nasdaq.com/symbol/{symbol.lower()}/financials?query={statement_type}&data={period_type}'
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
        data.index = pd.to_datetime(data.index)
        data.sort_index(inplace=True)

        return data
