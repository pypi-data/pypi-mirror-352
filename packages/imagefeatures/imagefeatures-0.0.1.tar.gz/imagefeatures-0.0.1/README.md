# image-features

<a href="https://pypi.org/project/image-features/">
    <img alt="PyPi" src="https://img.shields.io/pypi/v/image-features">
</a>

A library for processing image features in a dataframe. 

## Dependencies :globe_with_meridians:

Python 3.11.6:

- [pandas](https://pandas.pydata.org/)
- [pyarrow](https://arrow.apache.org/docs/python/index.html)
- [imgembeddings](https://github.com/minimaxir/imgbeddings)
- [pillow](https://python-pillow.github.io/)
- [requests](https://requests.readthedocs.io/en/latest/)
- [numpy](https://numpy.org/)
- [torch](https://pytorch.org/)

## Raison D'être :thought_balloon:

`image-features` transforms URLs in a dataframe into image features.

## Architecture :triangular_ruler:

`image-features` is a functional library, meaning that each phase of feature extraction gets put through a different function until the final output. The features its computes are as follows:

1. Embeddings - An embedding for each image in the row.
2. Luminosity - A measure of the luminosity of the image.
3. Mean Channels - The mean of each R/G/B channel.

## Installation :inbox_tray:

This is a python package hosted on pypi, so to install simply run the following command:

`pip install image-features`

or install using this local repository:

`python setup.py install --old-and-unmanageable`

## Usage example :eyes:

The use of `image-features` is entirely through code due to it being a library. It attempts to hide most of its complexity from the user, so it only has a few functions of relevance in its outward API.

### Generating Features

To generate features:

```python
import datetime

import pandas as pd

from imagefeatures.process import process

df = ... # Your timeseries dataframe
df = process(df, {"image_url"})
```

This will produce a dataframe that contains the new image related features.

## License :memo:

The project is available under the [MIT License](LICENSE).
