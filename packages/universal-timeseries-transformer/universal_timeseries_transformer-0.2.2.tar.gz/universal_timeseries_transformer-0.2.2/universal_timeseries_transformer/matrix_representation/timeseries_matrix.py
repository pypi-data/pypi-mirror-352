import numpy as np
from functools import partial
from universal_timeseries_transformer.timeseries_transformer import transform_timeseries
from universal_timeseries_transformer.timeseries_application import (
    transform_timeseries_to_cumreturns_ref_by_series,
    transform_timeseries_to_cumreturns,
    transform_timeseries_to_returns,
)
from universal_timeseries_transformer.timeseries_slicer import slice_timeseries_around_index

class TimeseriesMatrix:
    def __init__(self, df, index_ref=None):
        self.df = df
        self.index_ref = index_ref
        self.srs_ref = self.set_srs_ref()
        self._basis = None
        self._dates = None
        self._datetime = None
        self._unixtime = None
        self._string = None
        self._returns = None
        self._cumreturns = None
        self._cumreturns_ref = None

    @property
    def basis(self):
        if self._basis is None:
            self._basis = self.df.index.values
        return self._basis

    @property
    def dates(self):
        if self._dates is None:
            self._dates = list(self.basis)
        return self._dates

    @property
    def date_i(self):
        return self.dates[0]
    
    @property
    def date_f(self):
        return self.dates[-1]

    def row(self, i):
        return self.df.iloc[[i], :]

    def column(self, j):
        return self.df.iloc[:, [j]]
        
    def row_by_name(self, name):
        return self.df.loc[[name], :]

    def column_by_name(self, name):
        return self.df.loc[:, [name]]

    def component(self, i, j):
        return self.df.iloc[i, j]

    def component_by_name(self, name_i, name_j):
        return self.df.loc[name_i, name_j]

    def rows(self, i_list):
        return self.df.iloc[i_list, :]
        
    def columns(self, j_list):
        return self.df.iloc[:, j_list]

    def rows_by_names(self, names):
        return self.df.loc[names, :]
        
    def columns_by_names(self, names):
        return self.df.loc[:, names]

    def set_datetime(self):
        if self._datetime is None:
            self._datetime = transform_timeseries(self.df, 'datetime')
        return self._datetime

    def set_unixtime(self):
        if self._unixtime is None:
            self._unixtime = transform_timeseries(self.df, 'unix_timestamp')
        return self._unixtime

    def set_string(self):
        if self._string is None:
            self._string = transform_timeseries(self.df, 'str')
        return self._string

    @property
    def returns(self):
        if self._returns is None:
            self._returns = transform_timeseries_to_returns(self.df)
        return self._returns

    @property
    def cumreturns(self):
        if self._cumreturns is None:
            self._cumreturns = transform_timeseries_to_cumreturns(self.df)
        return self._cumreturns

    @property
    def cumreturns_ref(self):
        if self.index_ref is None:
            raise ValueError("Cannot calculate cumreturns_ref: no reference index set")
        if self._cumreturns_ref is None:
            df = transform_timeseries_to_cumreturns_ref_by_series(self.df, self.srs_ref)
            df.slice = partial(self.slice_cumreturns_ref)
            df.slice_by_name = partial(self.slice_cumreturns_ref_by_name)
            self._cumreturns_ref = df

        return self._cumreturns_ref

    def set_srs_ref(self):
        if self.index_ref is not None:
            return self.row_by_name(self.index_ref).iloc[0]
        else:
            return None

    def slice_cumreturns_ref(self, index_start, index_end):
        if self._cumreturns_ref is None:
            return None
        return slice_timeseries_around_index(timeseries=self._cumreturns_ref, index_ref=self.index_ref, index_start=index_start, index_end=index_end)

    def slice_cumreturns_ref_by_name(self, name_start, name_end):
        if self._cumreturns_ref is None:
            return None
        return self._cumreturns_ref.loc[name_start:name_end]
