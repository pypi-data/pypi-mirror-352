from string_date_controller import get_all_dates_between_dates
from .timeseries_matrix import TimeseriesMatrix

class PricesMatrix(TimeseriesMatrix):
    def __init__(self, prices, date_ref=None):
        super().__init__(df=prices, index_ref=date_ref)
        self._historical_dates = None

    @property
    def historical_dates(self):
        if self._historical_dates is None:
            # Get all dates from the first to the last date in the dataset
            min_date = min(self.dates)
            max_date = max(self.dates)
            self._historical_dates = get_all_dates_between_dates(min_date, max_date)
        return self._historical_dates

    