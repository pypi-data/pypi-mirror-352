"""Process a dataframe for its datetime information."""

from warnings import simplefilter

import pandas as pd
from feature_engine.datetime import DatetimeFeatures


def datetime_process(
    df: pd.DataFrame, dt_column: str, datetime_columns: set[str] | None
) -> pd.DataFrame:
    """Process datetime features."""
    simplefilter(action="ignore", category=pd.errors.PerformanceWarning)
    cols = [dt_column]
    if datetime_columns is not None:
        cols.extend(datetime_columns)
    dtf = DatetimeFeatures(
        variables=cols,  # type: ignore
        features_to_extract="all",
        missing_values="ignore",
        drop_original=False,
        utc=True,
    )
    return dtf.fit_transform(df).copy()
