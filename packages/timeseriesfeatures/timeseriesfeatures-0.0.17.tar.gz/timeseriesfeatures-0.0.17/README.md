# timeseries-features

<a href="https://pypi.org/project/timeseriesfeatures/">
    <img alt="PyPi" src="https://img.shields.io/pypi/v/timeseriesfeatures">
</a>

A library for processing timeseries features over a dataframe of timeseries.

## Dependencies :globe_with_meridians:

Python 3.11.6:

- [pandas](https://pandas.pydata.org/)
- [pyarrow](https://arrow.apache.org/docs/python/index.html)
- [statsmodels](https://www.statsmodels.org/stable/index.html)

## Raison D'être :thought_balloon:

`timeseries-features` aims to process features relevant to predicting future values.

## Architecture :triangular_ruler:

`timeseries-features` is a functional library, meaning that each phase of feature extraction gets put through a different function until the final output. It contains some caching when the processing is heavy (such as skill processing). The features its computes are as follows:

1. Lags
2. Rolling Count
3. Rolling Sum
4. Rolling Mean
5. Rolling Median
6. Rolling Variance
7. Rolling Standard Deviation
8. Rolling Minimum
9. Rolling Maximum
10. Rolling Skew
11. Rolling Kurtosis
12. Rolling Standard Error of the Mean
13. Rolling Rank

## Installation :inbox_tray:

This is a python package hosted on pypi, so to install simply run the following command:

`pip install timeseriesfeatures`

or install using this local repository:

`python setup.py install --old-and-unmanageable`

## Usage example :eyes:

The use of `timeseriesfeatures` is entirely through code due to it being a library. It attempts to hide most of its complexity from the user, so it only has a few functions of relevance in its outward API.

### Generating Features

To generate features:

```python
import datetime

import pandas as pd

from timeseriesfeatures.process import compute
from timeseriesfeatures.process import process
from timeseriesfeatures.feature import Feature, FEATURE_TYPE_LAG, FEATURE_TYPE_ROLLING, VALUE_TYPE_NONE, VALUE_TYPE_DAYS

df = ... # Your timeseries dataframe
features = compute(df, max_lag=30)
features.extend([
    Feature(feature_type=FEATURE_TYPE_LAG, value1=1),
    Feature(feature_type=FEATURE_TYPE_LAG, value1=2),
    Feature(feature_type=FEATURE_TYPE_LAG, value1=4),
    Feature(feature_type=FEATURE_TYPE_LAG, value1=8),
    Feature(feature_type=FEATURE_TYPE_ROLLING, value1=VALUE_TYPE_NONE, value2=None),
    Feature(feature_type=FEATURE_TYPE_ROLLING, value1=VALUE_TYPE_DAYS, value2=30),
])
df = process(df, features=features)
```

This will produce a dataframe that contains the new timeseries related features.

## License :memo:

The project is available under the [MIT License](LICENSE).
