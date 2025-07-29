"""The HSIC process function."""

# pylint: disable=duplicate-code,too-many-locals,invalid-name
from typing import Any, Iterator

import pandas as pd
from pyHSICLasso import HSICLasso  # type: ignore
from timeseriesfeatures.feature import FEATURE_TYPE_LAG  # type: ignore
from timeseriesfeatures.feature import Feature  # type: ignore
from timeseriesfeatures.transform import Transform  # type: ignore
from timeseriesfeatures.transforms import TRANSFORMS  # type: ignore

_HSIC_CACHE: dict[str, Feature] = {}


def _construct_lagged_features(universe_df: pd.DataFrame, max_lag: int):
    """
    Returns a new DataFrame where each column is a lagged version of each input column.
    """
    lagged_features = {}
    for col in universe_df.columns:
        for lag in range(1, max_lag + 1):
            lagged_features[f"{col}_lag{lag}"] = universe_df[col].shift(lag)
    return pd.DataFrame(lagged_features, index=universe_df.index).fillna(0.0)


def _hsic_lag_selector(
    universe_df: pd.DataFrame, target_series: pd.Series, max_lag: int, top_k=10
):
    # Step 1: Create lagged feature DataFrame
    lagged_df = _construct_lagged_features(universe_df, max_lag).dropna()

    # Step 2: Align target and features
    aligned_target = target_series.loc[lagged_df.index]

    # Step 3: Convert to NumPy arrays
    X = lagged_df.values
    y = aligned_target.fillna(0.0).values.reshape(-1, 1).flatten()  # type: ignore

    # Step 4: Run HSIC Lasso
    hsic_lasso = HSICLasso()
    hsic_lasso.input(X, y, lagged_df.columns.tolist())
    hsic_lasso.regression(num_feat=top_k)

    # Step 5: Return selected features and scores
    selected_features = hsic_lasso.get_features()
    selected_scores = hsic_lasso.get_index_score()

    return (
        pd.DataFrame(
            {
                "feature": selected_features,
                "hsic_score": selected_scores,
            }
        )
        .sort_values(by="hsic_score", ascending=False)
        .reset_index(drop=True)
    )


def hsic_positive_lags(
    predictor: pd.Series,
    predictand: pd.Series,
    max_window: int,
    predictor_transform: Transform,
    column: str,
) -> Feature:
    """Calculate the best distance correlation for the 2 series within a lag window"""
    df = _hsic_lag_selector(predictor.to_frame(), predictand, max_window)
    top_feature = df["feature"].tolist()[0]
    top_hsic_score = df["hsic_score"].tolist()[0]
    lag = int(top_feature.split("_")[-1].replace("lag", ""))

    return Feature(
        feature_type=FEATURE_TYPE_LAG,
        columns=[column],
        value1=int(lag),
        transform=str(predictor_transform),
        rank_value=top_hsic_score,
        rank_type="hsic",
    )


def hsic_process(
    df: pd.DataFrame,
    predictand: str,
    max_window: int,
    pool: Any,
) -> Iterator[Feature]:
    """Process the dataframe for distance correlation features."""
    predictors = df.columns.values.tolist()
    cached_predictors = []
    for predictor in predictors:
        for transform in TRANSFORMS:
            key = "_".join(sorted([predictor, transform, predictand]))
            feature = _HSIC_CACHE.get(key)
            if feature is not None:
                yield feature
                cached_predictors.append(predictor)
    for transform in TRANSFORMS:
        for feature in pool.starmap(
            hsic_positive_lags,
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
            _HSIC_CACHE[key] = feature
            yield feature
