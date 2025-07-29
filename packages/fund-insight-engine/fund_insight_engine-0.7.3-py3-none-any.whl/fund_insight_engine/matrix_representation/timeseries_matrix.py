"""
TimeseriesMatrix class for fund insight engine.
Provides powerful functionality for return and cumulative return analysis.
"""

import numpy as np
from functools import partial
from fund_insight_engine.fund_data_retriever.timeseries.timeseries_utils import (
    map_timeseries_to_returns,
    map_timeseries_to_cumreturns,
)


class TimeseriesMatrix:
    """
    A class for handling time series data in matrix form with enhanced return and cumulative return functionality.
    
    This class provides convenient methods for accessing and manipulating time series data,
    particularly for financial return calculations.
    """
    
    def __init__(self, df, index_ref=None):
        """
        Initialize the TimeseriesMatrix with a DataFrame and optional reference index.
        
        Args:
            df: pandas DataFrame with time series data (dates as index)
            index_ref: reference index for relative cumulative return calculations
        """
        self.df = df
        self.index_ref = index_ref
        self.srs_ref = self.set_srs_ref()
        self.dates = list(df.index)
        self._basis = None
        self._datetime = None
        self._unixtime = None
        self._string = None
        self._returns = None
        self._cumreturns = None
        self._cumreturns_ref = None

    @property
    def basis(self):
        """Get the basis dates as a numpy array."""
        if self._basis is None:
            self._basis = np.array(self.dates)
        return self._basis

    @property
    def date_i(self):
        """Get the first date in the time series."""
        return self.dates[0]
    
    @property
    def date_f(self):
        """Get the last date in the time series."""
        return self.dates[-1]

    def row(self, i):
        """Get a specific row by index."""
        return self.df.iloc[[i], :]

    def column(self, j):
        """Get a specific column by index."""
        return self.df.iloc[:, [j]]
        
    def row_by_name(self, name):
        """Get a specific row by name."""
        return self.df.loc[[name], :]

    def column_by_name(self, name):
        """Get a specific column by name."""
        return self.df.loc[:, [name]]

    def component(self, i, j):
        """Get a specific component by indices."""
        return self.df.iloc[i, j]

    def component_by_name(self, name_i, name_j):
        """Get a specific component by names."""
        return self.df.loc[name_i, name_j]

    def rows(self, i_list):
        """Get multiple rows by indices."""
        return self.df.iloc[i_list, :]
        
    def columns(self, j_list):
        """Get multiple columns by indices."""
        return self.df.iloc[:, j_list]

    def rows_by_names(self, names):
        """Get multiple rows by names."""
        return self.df.loc[names, :]
        
    def columns_by_names(self, names):
        """Get multiple columns by names."""
        return self.df.loc[:, names]

    @property
    def returns(self):
        """
        Calculate and return the returns time series.
        
        Returns:
            DataFrame with return values
        """
        if self._returns is None:
            self._returns = map_timeseries_to_returns(self.df)
        return self._returns

    @property
    def cumreturns(self):
        """
        Calculate and return the cumulative returns time series.
        
        Returns:
            DataFrame with cumulative return values
        """
        if self._cumreturns is None:
            self._cumreturns = map_timeseries_to_cumreturns(self.df)
        return self._cumreturns

    def set_srs_ref(self):
        """Set the reference series for relative calculations."""
        if self.index_ref is not None:
            return self.df[self.index_ref]
        else:
            return None

    def get_return_at_date(self, date):
        """
        Get returns at a specific date.
        
        Args:
            date: The date to get returns for
            
        Returns:
            Series with returns at the specified date
        """
        if date in self.returns.index:
            return self.returns.loc[date]
        return None
    
    def get_cumreturn_at_date(self, date):
        """
        Get cumulative returns at a specific date.
        
        Args:
            date: The date to get cumulative returns for
            
        Returns:
            Series with cumulative returns at the specified date
        """
        if date in self.cumreturns.index:
            return self.cumreturns.loc[date]
        return None
    
    def get_return_between_dates(self, start_date, end_date):
        """
        Calculate returns between two dates.
        
        Args:
            start_date: Start date for calculation
            end_date: End date for calculation
            
        Returns:
            Series with returns between the specified dates
        """
        if start_date in self.df.index and end_date in self.df.index:
            start_values = self.df.loc[start_date]
            end_values = self.df.loc[end_date]
            return (end_values / start_values) - 1
        return None
    
    def slice_by_date_range(self, start_date, end_date):
        """
        Slice the time series data between two dates.
        
        Args:
            start_date: Start date for slicing
            end_date: End date for slicing
            
        Returns:
            DataFrame with data between the specified dates
        """
        return self.df.loc[start_date:end_date]
