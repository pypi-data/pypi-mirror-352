from typing import TYPE_CHECKING, Any, Union

from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    import geopandas as gpd
    import pandas as pd
    import pyarrow as pa

    DataType = Union[pa.Table, pd.DataFrame, gpd.GeoDataFrame, None]
else:
    DataType = Any


class Output(BaseModel):
    data: DataType = None

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")
