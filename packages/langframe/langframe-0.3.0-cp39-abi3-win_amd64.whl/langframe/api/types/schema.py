from typing import List

from langframe.api.types import DataType
from pydantic.dataclasses import ConfigDict, dataclass


@dataclass(frozen=True, config=ConfigDict(arbitrary_types_allowed=True))
class ColumnField:
    """Represents a typed column in a DataFrame schema.

    A ColumnField defines the structure of a single column by specifying its name
    and data type. This is used as a building block for DataFrame schemas.

    Attributes:
        name: The name of the column.
        data_type: The data type of the column, as a DataType instance.
    """

    name: str
    data_type: DataType

    def __str__(self) -> str:
        return f"ColumnField(name='{self.name}', data_type={self.data_type})"


@dataclass(frozen=True, config=ConfigDict(arbitrary_types_allowed=True))
class Schema:
    """Represents the schema of a DataFrame.

    A Schema defines the structure of a DataFrame by specifying an ordered collection
    of column fields. Each column field defines the name and data type of a column
    in the DataFrame.

    Attributes:
        column_fields: An ordered list of ColumnField objects that define the
            structure of the DataFrame.
    """

    column_fields: List[ColumnField]

    def __str__(self) -> str:
        return f"schema=[{', '.join([str(field) for field in self.column_fields])}]"

    def column_names(self) -> List[str]:
        return [field.name for field in self.column_fields]
