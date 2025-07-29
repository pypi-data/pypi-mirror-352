from string_date_controller import get_all_data_historical_dates
from .timeseries_matrix import TimeseriesMatrix

class PricesMatrix(TimeseriesMatrix):
    def __init__(self, prices, date_ref=None):
        super().__init__(df=prices, index_ref=date_ref)
        self._historical_dates = None

    @property
    def historical_dates(self):
        if self._historical_dates is None:
            self._historical_dates = get_all_data_historical_dates(self.df)
        return self._historical_dates

    