"""The main process function."""

from multiprocessing import Pool
from typing import Iterator

import pandas as pd
from sklearn.preprocessing import MinMaxScaler  # type: ignore
from timeseriesfeatures.feature import Feature  # type: ignore

from .distance_correlation_process import distance_correlation_process
from .hsic_process import hsic_process
from .kendall_process import kendall_process
from .mutual_information_process import mutual_information_process
from .pearson_process import pearson_process
from .spearman_process import spearman_process


def process(
    df: pd.DataFrame,
    predictands: list[str],
    max_window: int,
    max_process_features: int = 10,
) -> Iterator[list[Feature]]:
    """Process the dataframe for tsuniverse features."""
    new_df = df.copy()
    for column in df.columns:
        scaler = MinMaxScaler()
        new_df[column] = scaler.fit_transform(new_df[[column]])
    with Pool() as p:
        for predictand in predictands:
            for sub_process in [
                pearson_process,
                mutual_information_process,
                spearman_process,
                kendall_process,
                distance_correlation_process,
                hsic_process,
            ]:
                features = list(sub_process(new_df, predictand, max_window, p))
                features = sorted(
                    features,
                    key=lambda x: abs(x["rank_value"] if "rank_value" in x else 0.0),
                    reverse=True,
                )[:max_process_features]
                yield features
