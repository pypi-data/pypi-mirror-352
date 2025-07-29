"""The pearson process function."""

from typing import Any, Iterator

import numpy as np
import pandas as pd
from timeseriesfeatures.feature import FEATURE_TYPE_LAG  # type: ignore
from timeseriesfeatures.feature import Feature  # type: ignore
from timeseriesfeatures.transform import Transform  # type: ignore
from timeseriesfeatures.transforms import TRANSFORMS  # type: ignore

_PEARSON_CACHE: dict[str, Feature] = {}


def pearson_correlation_positive_lags(
    predictor: pd.Series,
    predictand: pd.Series,
    max_window: int,
    predictor_transform: Transform,
    column: str,
) -> Feature:
    """Calculate the best pearson correlation for the 2 series within a lag window"""
    predictand = predictand.dropna()
    predictor = TRANSFORMS[predictor_transform](predictor)
    corrs = []
    lags = range(1, max_window + 1)

    for lag in lags:
        predictor_shifted = predictor.shift(lag)
        valid_idx = predictand.index.intersection(predictor_shifted.index)  # type: ignore
        corr = predictand.loc[valid_idx].corr(predictor_shifted.loc[valid_idx])
        corrs.append(corr)

    best_idx = np.argmax(np.abs(corrs))
    best_lag = lags[best_idx]
    best_corr = corrs[best_idx]
    if np.isnan(best_corr):
        best_corr = 0.0

    return Feature(
        feature_type=FEATURE_TYPE_LAG,
        columns=[column],
        value1=int(best_lag),
        transform=str(predictor_transform),
        rank_value=best_corr,
        rank_type="pearson",
    )


def pearson_process(
    df: pd.DataFrame,
    predictand: str,
    max_window: int,
    pool: Any,
) -> Iterator[Feature]:
    """Process the dataframe for tsuniverse features."""
    predictors = df.columns.values.tolist()
    cached_predictors = []
    for predictor in predictors:
        for transform in TRANSFORMS:
            key = "_".join(sorted([predictor, transform, predictand]))
            feature = _PEARSON_CACHE.get(key)
            if feature is not None:
                yield feature
                cached_predictors.append(predictor)
    for transform in TRANSFORMS:
        for feature in pool.starmap(
            pearson_correlation_positive_lags,
            [
                (df[x], df[predictand], max_window, transform, x)
                for x in df.columns.values.tolist()
                if x != predictand and x not in cached_predictors
            ],
        ):
            if feature is None:
                continue
            key = "_".join(
                sorted(
                    [
                        feature["columns"][0],
                        transform,
                        predictand,
                    ]
                )
            )
            _PEARSON_CACHE[key] = feature
            yield feature
