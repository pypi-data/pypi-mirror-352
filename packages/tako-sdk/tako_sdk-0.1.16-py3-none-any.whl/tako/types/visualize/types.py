from enum import Enum
from typing import Union, Optional

from pydantic import BaseModel, Field


class TakoDataFormatValueType(str, Enum):
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    FLOAT = "float"
    NULL = "null"
    ANY = "any"


class TakoDataFormatCellValue(BaseModel):
    variable_name: str = Field(
        description="The name of the variable",
        examples=["Company", "Revenue"],
    )
    value: Optional[Union[str, int, float, bool]] = Field(
        description="The value of the variable",
        examples=["Apple", 1000000],
    )


class TakoDataFormatRowValues(BaseModel):
    cell_values: list[TakoDataFormatCellValue] = Field(
        description="Each cell contains a single aspect (variable + value)",
        examples=[
            [
                {"variable_name": "Company", "value": "Apple"},
                {"variable_name": "Revenue", "value": 1000000},
            ]
        ],
    )


class TakoDataFormatTimeseriesVariableType(str, Enum):
    SERIES = "series"
    X_AXIS = "x_axis"
    Y_AXIS = "y_axis"


class TakoDataFormatCategoryVariableType(str, Enum):
    CATEGORY = "category"
    VALUE = "value"


class TakoDataFormatVariable(BaseModel):
    # Variable contains rich metadata about the variables for each observation
    name: str = Field(
        description="The human friendly name of the column variable",
        examples=["Company", "Revenue"],
    )
    type: TakoDataFormatValueType = Field(
        description="The type of the column variable",
        examples=[TakoDataFormatValueType.STRING, TakoDataFormatValueType.NUMBER],
    )
    units: Optional[str] = Field(
        description="The units of the variable in the data",
        examples=["USD", "EUR"],
    )
    is_sortable: Optional[bool] = Field(
        description="Whether the data is sortable by this variable",
    )
    is_higher_better: Optional[bool] = Field(
        description="Whether a higher value of this variable is better",
    )


class TakoDataFormatTimeseriesVariable(TakoDataFormatVariable):
    timeseries_variable_type: Optional[TakoDataFormatTimeseriesVariableType] = Field(
        description="The type of the variable in the timeseries visualization. "
        "SERIES: The variable should be a series in the timeseries visualization. "
        "X_AXIS: The variable should be the x-axis of the timeseries visualization. This "
        "must be in ISO 8601 format (YYYY-MM-DD). "
        "Y_AXIS: The variable should be the y-axis of the timeseries visualization. "
        "This is typically a numeric column.",
        examples=[
            TakoDataFormatTimeseriesVariableType.SERIES,
            TakoDataFormatTimeseriesVariableType.X_AXIS,
            TakoDataFormatTimeseriesVariableType.Y_AXIS,
        ],
    )


class TakoDataFormatCategoryVariable(TakoDataFormatVariable):
    category_variable_type: Optional[TakoDataFormatCategoryVariableType] = Field(
        description="The type of the category variable",
        examples=[
            TakoDataFormatCategoryVariableType.CATEGORY,
            TakoDataFormatCategoryVariableType.VALUE,
        ],
    )

ValidTakoDataFormatVariable = Union[
    TakoDataFormatTimeseriesVariable,
    TakoDataFormatCategoryVariable,
    TakoDataFormatVariable,
]


class TakoDataFormatDataset(BaseModel):
    # A single dataset contains all column variables and all the rows of data
    title: str = Field(
        description="The title of the dataset",
        examples=["Walmart vs Verizon Total Revenue"],
    )
    description: Optional[str] = Field(
        description="The description of the dataset",
        examples=["Comparison of Walmart and Verizon's Total Revenue (fiscal years)"],
    )
    variables: list[ValidTakoDataFormatVariable] = Field(
        description="Details about all variables in the dataset",
        examples=[
            [
                {
                    "name": "Company",
                    "type": TakoDataFormatValueType.STRING,
                    "units": None,
                    "is_sortable": True,
                    "is_higher_better": True,
                },
            ]
        ],
    )
    rows: list[TakoDataFormatRowValues] = Field(
        description="Each row contains a single coherent set of values with each "
        "cell having different aspects (variable + value)",
        examples=[
            [
                {
                    "values": [
                        {"variable_name": "Company", "value": "Apple"},
                        {"variable_name": "Revenue", "value": 1000000},
                    ]
                },
            ]
        ],
    )


class SimpleDataPoint(BaseModel):
    variable_name: str = Field(
        description="The name of the variable",
        examples=["Company", "Revenue"],
    )
    value: Optional[Union[str, int, float, bool]] = Field(
        description="The value of the variable",
        examples=["Apple", 1000000],
    )



tdf_description = """
A Tako Data Format (TDF) dataset is a dataset that is formatted in a way that is easy to visualize.
This is based on the tidy data format. See:
* https://cran.r-project.org/web/packages/tidyr/vignettes/tidy-data.html
* https://dimewiki.worldbank.org/Tidying_Data
* https://aeturrell.github.io/python4DS/data-tidy.html#introduction
There are three interrelated features that make a dataset tidy:
1. Each variable is a column; each column is a variable.
2. Each observation is row; each row is an observation.
3. Each value is a cell; each cell is a single value.
There are two common problems you find in data that are ingested that make them not tidy:
1. A variable might be spread across multiple columns - if this is the case, you should
   "melt" the wide data, with multiple columns, into long data.
2. An observation might be scattered across multiple rows - if this is the case, you should
   "unstack" or "pivot" the multiple rows into columns (ie go from long to wide.)
"""

class VisualizeRequest(BaseModel):
    tako_formatted_dataset: Optional[TakoDataFormatDataset] = Field(
        description=tdf_description, default=None
    )
