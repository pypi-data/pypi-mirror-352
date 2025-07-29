from fund_insight_engine.fund_data_retriever.timeseries.timeseries_utils import get_df_timeseries_by_fund
from fund_insight_engine.fund_data_retriever.portfolio.portfolio import Portfolio
from fund_insight_engine.market_retriever.universal_index import get_bms
from universal_timeseries_transformer import map_timeseries_to_returns, map_timeseries_to_cumreturns
from .fund_consts import COL_FOR_FUND_PRICE, DEFAULT_COLS_FOR_BM_PRICE

class Fund:
    def __init__(self, fund_code, start_date=None, end_date=None, date_ref=None):
        self.fund_code = fund_code
        self.start_date = start_date
        self.end_date = end_date
        self.date_ref = self._set_date_ref(date_ref, end_date)        
        self.timeseries = None
        self.benchmarks = None  
        self.portfolio = None
        self.prices = None
        self._returns = None
        self._cumreturns = None
        self._columns_ref = None
        self._load_basic_data()        

    def _set_date_ref(self, date_ref, end_date):
        return date_ref or end_date

    def _load_basic_data(self):
        self.timeseries = get_df_timeseries_by_fund(
            fund_code=self.fund_code, 
            start_date=self.start_date, 
            end_date=self.end_date
        )
        
        self.benchmarks = get_bms(
            start_date=self.start_date, 
            end_date=self.end_date
        )[DEFAULT_COLS_FOR_BM_PRICE]
        
        self.portfolio = Portfolio(fund_code=self.fund_code, date_ref=self.date_ref).df
        
        self.prices = (
            self.timeseries[[COL_FOR_FUND_PRICE]]
            .join(self.benchmarks)
            .rename_axis('date')
            .rename(columns={COL_FOR_FUND_PRICE: self.fund_code})
        )
        
    @property
    def returns(self):
        if self._returns is None:
            self._returns = map_timeseries_to_returns(self.prices)
        return self._returns

    @property  
    def cumreturns(self):
        if self._cumreturns is None:
            self._cumreturns = map_timeseries_to_cumreturns(self.prices)
        return self._cumreturns

    @property
    def columns_ref(self):
        if self._columns_ref is None:
            self._columns_ref = self.prices.columns
        return self._columns_ref