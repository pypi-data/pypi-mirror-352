"""The mutual information process function."""

# pylint: disable=duplicate-code,too-many-locals
from typing import Any, Iterator

import numpy as np
import pandas as pd
from sklearn.feature_selection import mutual_info_regression  # type: ignore
from timeseriesfeatures.feature import FEATURE_TYPE_LAG  # type: ignore
from timeseriesfeatures.feature import Feature  # type: ignore
from timeseriesfeatures.transform import Transform  # type: ignore
from timeseriesfeatures.transforms import TRANSFORMS  # type: ignore

_MUTUAL_INFORMATION_CACHE: dict[str, Feature] = {}


def mutual_information_positive_lags(
    target: pd.Series,
    predictor: pd.Series,
    max_window: int,
    y_transform: Transform,
    column: str,
) -> Feature:
    """Calculate the best pearson correlation for the 2 series within a lag window"""
    target = target.dropna()
    predictor = TRANSFORMS[y_transform](predictor).dropna()

    mi_vals = []
    lags = range(1, max_window + 1)

    for lag in lags:
        shifted = predictor.shift(lag)
        aligned = pd.concat([target, shifted], axis=1, join="inner").dropna()

        if aligned.shape[0] < 5 or aligned.iloc[:, 1].nunique() < 2:
            # Too few samples or no variation in predictor → MI is zero
            mi_vals.append(0.0)
            continue

        x = aligned.iloc[:, 1].values.reshape(-1, 1)  # type: ignore
        y = aligned.iloc[:, 0].values  # target

        try:
            mi = mutual_info_regression(x, y, n_neighbors=3, random_state=42)[0]
        except ValueError:
            mi = 0.0

        mi_vals.append(mi)

    best_idx = np.argmax(mi_vals)
    best_lag = lags[best_idx]
    best_mi = mi_vals[best_idx]

    return Feature(
        feature_type=FEATURE_TYPE_LAG,
        columns=[column],
        value1=int(best_lag),
        transform=str(y_transform),
        rank_value=best_mi,
        rank_type="mutual_information",
    )


def mutual_information_process(
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
            feature = _MUTUAL_INFORMATION_CACHE.get(key)
            if feature is not None:
                yield feature
                cached_predictors.append(predictor)
    for transform in TRANSFORMS:
        for feature in pool.starmap(
            mutual_information_positive_lags,
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
            _MUTUAL_INFORMATION_CACHE[key] = feature
            yield feature
