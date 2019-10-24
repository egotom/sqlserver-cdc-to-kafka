import datetime

import pyodbc

from cdc_kafka import constants


class MetricsAccumulator(object):
    def __init__(self, db_conn: pyodbc.Connection):
        self._cursor = db_conn.cursor()

        self.tombstone_publish = 0
        self.record_publish = 0
        self.cdc_lag_behind_now_ms = None
        self.app_lag_behind_cdc_ms = None

    def determine_lags(self, last_published_msg_db_time: datetime.datetime):
        self._cursor.execute(constants.LAG_QUERY)
        latest_cdc, db_lag = self._cursor.fetchone()
        self.cdc_lag_behind_now_ms = db_lag
        if not last_published_msg_db_time:
            self.app_lag_behind_cdc_ms = None
        else:
            app_lag = (latest_cdc - last_published_msg_db_time).total_seconds() * 1000
            self.app_lag_behind_cdc_ms = max(app_lag, 0.0)