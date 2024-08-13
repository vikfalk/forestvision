import datetime as dt
from typing import Tuple

def timeframe_constructor(
        datetime_string: str,
        temporal_padding: int
    ) -> Tuple[str, str]:
    """Takes the '2021-01-01' string from the UI and returns a
    tuple of date strings in the format YY-MM-DD."""
    date_tuple = (
        int(datetime_string[0:4]),
        int(datetime_string[5:7]),
        int(datetime_string[8:10])
    )
    dt_object = dt.datetime(
        year=date_tuple[0], month=date_tuple[1], day=date_tuple[2]
    )
    timeframe_start = dt_object - dt.timedelta(days=temporal_padding)
    timeframe_end = dt_object + dt.timedelta(days=temporal_padding)
    time_interval = (
        timeframe_start.strftime("%Y-%m-%d"),
        timeframe_end.strftime("%Y-%m-%d")
    )
    return time_interval
