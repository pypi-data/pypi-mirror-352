"""The main process function."""

import pandas as pd
import requests
from PIL import Image

from .embedding_process import embedding_process
from .luminosity_process import luminosity_process
from .rgb_process import rgb_process


def _extract_image_features(url: str, session: requests.Session) -> dict[str, float]:
    image_file = Image.open(session.get(url, stream=True).raw)  # type: ignore
    image = image_file.convert("RGB")
    features = embedding_process(image)
    features.update(luminosity_process(image))
    features.update(rgb_process(image))
    return features


def process(
    df: pd.DataFrame,
    columns: set[str],
    session: requests.Session,
) -> pd.DataFrame:
    """Process the dataframe for image features."""
    df_dict: dict[str, list[float | None]] = {}

    written_columns = set()
    for column in columns:
        images = df[column].tolist()
        for count, image in enumerate(images):
            if image is None:
                continue
            features = _extract_image_features(image, session)
            for k, v in features.items():
                added_col = column + "_" + k
                if k not in df_dict:
                    df_dict[added_col] = [None for _ in range(len(df))]
                df_dict[added_col][count] = v
                written_columns.add(added_col)

    for column in written_columns:
        df.loc[:, column] = df_dict[column]

    return df[sorted(df.columns.values.tolist())]
