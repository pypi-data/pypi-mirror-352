"""
Writer interface for saving DataFrames to external storage systems.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Literal, Union

if TYPE_CHECKING:
    from langframe.api.dataframe import DataFrame

from langframe._logical_plan.plans import FileSink, TableSink
from langframe.api.metrics import QueryMetrics
from pydantic import ConfigDict, validate_call

logger = logging.getLogger(__name__)


class DataFrameWriter:
    """
    Interface used to write a DataFrame to external storage systems.
    Similar to PySpark's DataFrameWriter.
    """

    def __init__(self, dataframe: DataFrame):
        self._dataframe = dataframe

    def save_as_table(
        self,
        table_name: str,
        mode: Literal["error", "append", "overwrite", "ignore"] = "error",
    ) -> QueryMetrics:
        """
        Saves the content of the DataFrame as the specified table.

        Args:
            table_name: Name of the table to save to
            mode: Write mode. Default is "error".
                 - error: Raises an error if table exists
                 - append: Appends data to table if it exists
                 - overwrite: Overwrites existing table
                 - ignore: Silently ignores operation if table exists

        Returns:
            QueryMetrics: The query metrics
        """
        sink_plan = TableSink(
            child=self._dataframe._logical_plan, table_name=table_name, mode=mode
        )

        metrics = self._dataframe._execution.save_as_table(
            sink_plan, table_name=table_name, mode=mode
        )
        logger.info(metrics.get_summary())
        return metrics

    def csv(
        self,
        file_path: Union[str, Path],
        mode: Literal["error", "overwrite", "ignore"] = "overwrite",
    ) -> QueryMetrics:
        """
        Saves the content of the DataFrame as a single CSV file with comma as the delimiter and headers in the first row.

        Args:
            file_path: Path to save the CSV file to
            mode: Write mode. Default is "overwrite".
                 - error: Raises an error if file exists
                 - overwrite: Overwrites the file if it exists
                 - ignore: Silently ignores operation if file exists

        Returns:
            QueryMetrics: The query metrics
        """
        file_path = str(file_path)
        if not file_path.endswith(".csv"):
            raise ValueError(
                f"For CSV output, file path must end with '.csv', got '{file_path}'. "
                "Example: df.write.csv('/path/to/output.csv')"
            )

        sink_plan = FileSink(
            child=self._dataframe._logical_plan,
            sink_type="csv",
            path=file_path,
            mode=mode,
        )

        metrics = self._dataframe._execution.save_to_file(
            sink_plan, file_path=file_path, mode=mode
        )
        logger.info(metrics.get_summary())
        return metrics

    def parquet(
        self,
        file_path: Union[str, Path],
        mode: Literal["error", "overwrite", "ignore"] = "overwrite",
    ) -> QueryMetrics:
        """
        Saves the content of the DataFrame as a single Parquet file.

        Args:
            file_path: Path to save the Parquet file to
            mode: Write mode. Default is "overwrite".
                 - error: Raises an error if file exists
                 - overwrite: Overwrites the file if it exists
                 - ignore: Silently ignores operation if file exists

        Returns:
            QueryMetrics: The query metrics
        """
        file_path = str(file_path)
        if not file_path.endswith(".parquet"):
            raise ValueError(
                f"For Parquet output, file path must end with '.parquet', got '{file_path}'. "
                "Example: df.write.parquet('/path/to/output.parquet')"
            )

        sink_plan = FileSink(
            child=self._dataframe._logical_plan,
            sink_type="parquet",
            path=file_path,
            mode=mode,
        )

        metrics = self._dataframe._execution.save_to_file(
            sink_plan, file_path=file_path, mode=mode
        )
        logger.info(metrics.get_summary())
        return metrics


DataFrameWriter.save_as_table = validate_call(config=ConfigDict(strict=True))(
    DataFrameWriter.save_as_table
)
DataFrameWriter.saveAsTable = DataFrameWriter.save_as_table
DataFrameWriter.csv = validate_call(
    config=ConfigDict(strict=True, arbitrary_types_allowed=True)
)(DataFrameWriter.csv)
DataFrameWriter.parquet = validate_call(
    config=ConfigDict(strict=True, arbitrary_types_allowed=True)
)(DataFrameWriter.parquet)
