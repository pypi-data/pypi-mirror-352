from string_date_controller import get_all_data_historical_dates, get_all_data_monthly_date_pairs
from .timeseries_matrix import TimeseriesMatrix

class PricesMatrix(TimeseriesMatrix):
    def __init__(self, prices, date_ref=None):
        super().__init__(df=prices, index_ref=date_ref)
        self.date_ref = self.index_ref
        self._historical_dates = None
        self._monthly_date_pairs = None

    @property
    def historical_dates(self):
        if self._historical_dates is None:
            self._historical_dates = get_all_data_historical_dates(dates=self.dates, date_ref=self.date_ref)
        return self._historical_dates

    @property
    def monthly_date_pairs(self):
        if self._monthly_date_pairs is None:
            self._monthly_date_pairs = get_all_data_monthly_date_pairs(dates=self.dates)
        return self._monthly_date_pairs
    
    

    