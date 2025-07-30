import logging

import numpy as np
import polars as pl
from lance.util import KMeans

logger = logging.getLogger(__name__)


class Cluster:
    def __init__(
        self,
        input: pl.DataFrame,
        embedding_column_name: str,
        num_centroids: int,
        app_name: str,
        num_iter: int = 20,
    ):
        self.input = input
        self.embedding_column_name = embedding_column_name
        input_height = input.height
        if num_centroids > input_height:
            logger.warning(
                f"`num_centroids` was set to {num_centroids}, but the input DataFrame only contains {input_height} rows. "
                f"Reducing `num_centroids` to {input_height} to match the available number of rows."
            )
        self.num_centroids = min(num_centroids, input_height)
        self.num_iter = num_iter
        self.app_name = app_name

    def execute(self) -> pl.DataFrame:
        """
        Perform semantic clustering on the DataFrame.

        Args:
            col_name (str): The column name to cluster on.
            ncentroids (int): The number of centroids.
            niter (int): The number of iterations.
            verbose (bool): Whether to print verbose output.

        Returns:
            pl.DataFrame: The DataFrame with the cluster assignments - a new column called "_cluster_id"
        """
        return self.input.with_columns(
            pl.Series(self._cluster_by_column()).alias("_cluster_id")
        )

    def _cluster_by_column(
        self,
    ) -> list[int | None]:
        """
        Returns a list of that clusters a DataFrame by a column using kmeans.

        Args:
            col_name (str): The column name to cluster by.
                Expects the column to be a list of embeddings (type List[float])
            ncentroids (int): The number of centroids to use.

        Returns:
            The dataframe with an added column of cluster_ids
        """
        df = self.input
        is_not_null = df[self.embedding_column_name].is_not_null()
        no_nan = (
            df[self.embedding_column_name]
            .list.eval(pl.element().is_nan() | pl.element().is_null())
            .list.any()
            .not_()
        )

        valid_mask = is_not_null & no_nan
        valid_df = df.filter(valid_mask)

        if valid_df.is_empty():
            return [None] * df.height

        # Perform clustering on valid embeddings
        embeddings = np.stack(valid_df[self.embedding_column_name])
        kmeans = KMeans(k=self.num_centroids, max_iters=self.num_iter)
        kmeans.fit(embeddings)
        predicted = kmeans.predict(embeddings).tolist()

        # Build full result with None for invalid rows
        cluster_ids = [None] * df.height
        valid_indices = valid_mask.to_numpy().nonzero()[0]

        for idx, cluster_id in zip(valid_indices, predicted, strict=True):
            cluster_ids[idx] = cluster_id

        return cluster_ids
