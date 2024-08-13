import datetime as dt
import numpy as np
import pandas as pd
from typing import List


HECTAR_PER_IMAGE = 2621.44


def day_difference_calculator(row):
    try:
        date_obj_1 = dt.datetime.strptime(row.date, '%Y-%m-%d').date()
        date_obj_2 = dt.datetime.strptime(row.prev_date, '%Y-%m-%d').date()
        difference = date_obj_1 - date_obj_2
        return difference.days
    except TypeError:
        return pd.NA


def date_reformatter(row):
    try:
        return dt.datetime.strptime(row.date, '%Y-%m-%d').date().strftime("%Y/%m")
    except TypeError:
        return pd.NA


def convert_to_ha(percentage: float) -> float:
    ha = percentage / 100 * HECTAR_PER_IMAGE
    return ha


def calculate_metrics(
        dates: List[str],
        segmented_images: List[np.ndarray]
    ) -> pd.DataFrame:
    coverage_list = [np.count_nonzero(arr == 0) / arr.size * 100 for arr in segmented_images]
    coverage_list_inverted = [100 - cov for cov in coverage_list]
    pd.set_option('future.no_silent_downcasting', True)
    dataframe = (
        pd.DataFrame({
            "date": dates,
            "coverage": coverage_list_inverted
        })
        .assign(prev_coverage=lambda df_: df_.coverage.shift(1))
        .assign(prev_date=lambda df_: df_.date.shift(1))
        .assign(cover_diff_rel=lambda df_: (
            df_.coverage - df_.prev_coverage) / df_.prev_coverage * 100
        )
        .assign(cover_diff_pp=lambda df_: df_.coverage - df_.prev_coverage)
        .assign(cover_diff_pp_cum=lambda df_: df_.cover_diff_pp.cumsum())
        .assign(cover_diff_ha=lambda df_: (
            df_.coverage - df_.prev_coverage) / 100 * HECTAR_PER_IMAGE
        )
        .assign(cover_diff_ha_cum=lambda df_: df_.cover_diff_ha.cumsum())
        .assign(days_since_prev=lambda df_: df_.apply(day_difference_calculator, axis=1))
        .assign(months_since_prev=lambda df_: df_.days_since_prev / 30.437)
        .assign(loss_per_months_ha=lambda df_: df_.cover_diff_ha / df_.months_since_prev)
        .drop(columns=["prev_coverage", "prev_date"])
        .assign(date=lambda df_: df_.apply(date_reformatter, axis=1))
        .fillna(0)
        .infer_objects()
        .set_index("date")
    )
    return dataframe


def label(df: pd.DataFrame) -> pd.DataFrame:
    labelled_df = (df
    .drop(columns=["months_since_prev"])
    .rename(columns={
        'date': 'Dates',
        'coverage': 'Coverage (%)',
        'days_since_prev': 'Time Passed Since Previous Cloud-Free Image (Days)',
        'cover_diff_rel': 'Relative Change in Coverage (Previous Period, %)',
        'cover_diff_pp': 'Difference in Coverage (Previous Period, pp)',
        'cover_diff_pp_cum': 'Difference in Coverage (Cumulative, pp)',
        'cover_diff_ha': 'Forest Area Change (Previous Period, ha)',
        'cover_diff_ha_cum': 'Forest Area Change (Cumulative, ha)',
        'loss_per_months_ha': 'Forest Area Change Rate (Previous Period, Monthly)'
        })
    .astype('float32')
    .round(2)
    )
    return labelled_df
