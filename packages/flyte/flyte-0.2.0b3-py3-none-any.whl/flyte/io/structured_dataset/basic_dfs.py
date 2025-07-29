import os
import typing
from pathlib import Path
from typing import TypeVar

from flyteidl.core import literals_pb2, types_pb2
from fsspec.core import split_protocol, strip_protocol

import flyte.storage as storage
from flyte._logging import logger
from flyte._utils import lazy_module
from flyte.io.structured_dataset.structured_dataset import (
    CSV,
    PARQUET,
    StructuredDataset,
    StructuredDatasetDecoder,
    StructuredDatasetEncoder,
)

if typing.TYPE_CHECKING:
    import pandas as pd
    import pyarrow as pa
else:
    pd = lazy_module("pandas")
    pa = lazy_module("pyarrow")

T = TypeVar("T")


# pr: add back after storage
def get_pandas_storage_options(uri: str, data_config=None, anonymous: bool = False) -> typing.Optional[typing.Dict]:
    from pandas.io.common import is_fsspec_url  # type: ignore

    if is_fsspec_url(uri):
        if uri.startswith("s3"):
            # pr: after storage, replace with real call to get_fsspec_storage_options
            return {
                "cache_regions": True,
                "client_kwargs": {"endpoint_url": "http://localhost:30002"},
                "key": "minio",
                "secret": "miniostorage",
            }
        return {}

    # Pandas does not allow storage_options for non-fsspec paths e.g. local.
    return None


class PandasToCSVEncodingHandler(StructuredDatasetEncoder):
    def __init__(self):
        super().__init__(pd.DataFrame, None, CSV)

    async def encode(
        self,
        structured_dataset: StructuredDataset,
        structured_dataset_type: types_pb2.StructuredDatasetType,
    ) -> literals_pb2.StructuredDataset:
        if not structured_dataset.uri:
            from flyte._context import internal_ctx

            ctx = internal_ctx()
            uri = ctx.raw_data.get_random_remote_path()
        else:
            uri = typing.cast(str, structured_dataset.uri)

        if not storage.is_remote(uri):
            Path(uri).mkdir(parents=True, exist_ok=True)
        path = os.path.join(uri, ".csv")
        df = typing.cast(pd.DataFrame, structured_dataset.dataframe)
        df.to_csv(
            path,
            index=False,
            storage_options=get_pandas_storage_options(uri=path, data_config=None),
        )
        structured_dataset_type.format = CSV
        return literals_pb2.StructuredDataset(
            uri=uri, metadata=literals_pb2.StructuredDatasetMetadata(structured_dataset_type)
        )


class CSVToPandasDecodingHandler(StructuredDatasetDecoder):
    def __init__(self):
        super().__init__(pd.DataFrame, None, CSV)

    async def decode(
        self,
        proto_value: literals_pb2.StructuredDataset,
        current_task_metadata: literals_pb2.StructuredDatasetMetadata,
    ) -> "pd.DataFrame":
        from botocore.exceptions import NoCredentialsError

        uri = proto_value.uri
        columns = None
        kwargs = get_pandas_storage_options(uri=uri, data_config=None)
        path = os.path.join(uri, ".csv")
        if current_task_metadata.structured_dataset_type and current_task_metadata.structured_dataset_type.columns:
            columns = [c.name for c in current_task_metadata.structured_dataset_type.columns]
        try:
            return pd.read_csv(path, usecols=columns, storage_options=kwargs)
        except NoCredentialsError:
            logger.debug("S3 source detected, attempting anonymous S3 access")
            kwargs = get_pandas_storage_options(uri=uri, data_config=None, anonymous=True)
            return pd.read_csv(path, usecols=columns, storage_options=kwargs)


class PandasToParquetEncodingHandler(StructuredDatasetEncoder):
    def __init__(self):
        super().__init__(pd.DataFrame, None, PARQUET)

    async def encode(
        self,
        structured_dataset: StructuredDataset,
        structured_dataset_type: types_pb2.StructuredDatasetType,
    ) -> literals_pb2.StructuredDataset:
        if not structured_dataset.uri:
            from flyte._context import internal_ctx

            ctx = internal_ctx()
            uri = str(ctx.raw_data.get_random_remote_path())
        else:
            uri = typing.cast(str, structured_dataset.uri)

        if not storage.is_remote(uri):
            Path(uri).mkdir(parents=True, exist_ok=True)
        path = os.path.join(uri, f"{0:05}")
        df = typing.cast(pd.DataFrame, structured_dataset.dataframe)
        df.to_parquet(
            path,
            coerce_timestamps="us",
            allow_truncated_timestamps=False,
            storage_options=get_pandas_storage_options(uri=path, data_config=None),
        )
        structured_dataset_type.format = PARQUET
        return literals_pb2.StructuredDataset(
            uri=uri, metadata=literals_pb2.StructuredDatasetMetadata(structured_dataset_type=structured_dataset_type)
        )


class ParquetToPandasDecodingHandler(StructuredDatasetDecoder):
    def __init__(self):
        super().__init__(pd.DataFrame, None, PARQUET)

    async def decode(
        self,
        flyte_value: literals_pb2.StructuredDataset,
        current_task_metadata: literals_pb2.StructuredDatasetMetadata,
    ) -> "pd.DataFrame":
        from botocore.exceptions import NoCredentialsError

        uri = flyte_value.uri
        columns = None
        kwargs = get_pandas_storage_options(uri=uri, data_config=None)
        if current_task_metadata.structured_dataset_type and current_task_metadata.structured_dataset_type.columns:
            columns = [c.name for c in current_task_metadata.structured_dataset_type.columns]
        try:
            return pd.read_parquet(uri, columns=columns, storage_options=kwargs)
        except NoCredentialsError:
            logger.debug("S3 source detected, attempting anonymous S3 access")
            kwargs = get_pandas_storage_options(uri=uri, data_config=None, anonymous=True)
            return pd.read_parquet(uri, columns=columns, storage_options=kwargs)


class ArrowToParquetEncodingHandler(StructuredDatasetEncoder):
    def __init__(self):
        super().__init__(pa.Table, None, PARQUET)

    async def encode(
        self,
        structured_dataset: StructuredDataset,
        structured_dataset_type: types_pb2.StructuredDatasetType,
    ) -> literals_pb2.StructuredDataset:
        import pyarrow.parquet as pq

        if not structured_dataset.uri:
            from flyte._context import internal_ctx

            ctx = internal_ctx()
            uri = ctx.raw_data.get_random_remote_path()
        else:
            uri = typing.cast(str, structured_dataset.uri)

        if not storage.is_remote(uri):
            Path(uri).mkdir(parents=True, exist_ok=True)
        path = os.path.join(uri, f"{0:05}")
        filesystem = storage.get_underlying_filesystem(path=path)
        pq.write_table(structured_dataset.dataframe, strip_protocol(path), filesystem=filesystem)
        return literals_pb2.StructuredDataset(
            uri=uri, metadata=literals_pb2.StructuredDatasetMetadata(structured_dataset_type)
        )


class ParquetToArrowDecodingHandler(StructuredDatasetDecoder):
    def __init__(self):
        super().__init__(pa.Table, None, PARQUET)

    async def decode(
        self,
        proto_value: literals_pb2.StructuredDataset,
        current_task_metadata: literals_pb2.StructuredDatasetMetadata,
    ) -> "pa.Table":
        import pyarrow.parquet as pq
        from botocore.exceptions import NoCredentialsError

        uri = proto_value.uri
        if not storage.is_remote(uri):
            Path(uri).parent.mkdir(parents=True, exist_ok=True)
        _, path = split_protocol(uri)

        columns = None
        if current_task_metadata.structured_dataset_type and current_task_metadata.structured_dataset_type.columns:
            columns = [c.name for c in current_task_metadata.structured_dataset_type.columns]
        try:
            return pq.read_table(path, columns=columns)
        except NoCredentialsError as e:
            logger.debug("S3 source detected, attempting anonymous S3 access")
            fs = storage.get_underlying_filesystem(path=uri, anonymous=True)
            if fs is not None:
                return pq.read_table(path, filesystem=fs, columns=columns)
            raise e
