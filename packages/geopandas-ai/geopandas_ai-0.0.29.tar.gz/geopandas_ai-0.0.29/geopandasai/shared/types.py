from dataclasses import dataclass
from typing import Dict, List, Union

from geopandas import GeoDataFrame
from pandas import DataFrame

GeoOrDataFrame = Union[GeoDataFrame, DataFrame]
