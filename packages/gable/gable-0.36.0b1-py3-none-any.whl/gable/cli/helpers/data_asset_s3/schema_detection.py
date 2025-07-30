import io
import math
from dataclasses import dataclass
from typing import Optional, Union

import boto3
import click
import fastavro
import pandas as pd
import pyarrow.fs
import pyarrow.orc
import s3fs
from fastparquet import ParquetFile
from gable.cli.helpers.data_asset_s3.compression_handler import CompressionHandler
from gable.cli.helpers.data_asset_s3.logger import log_debug
from gable.cli.helpers.data_asset_s3.native_s3_converter import NativeS3Converter
from gable.cli.helpers.data_asset_s3.path_pattern_manager import SUPPORTED_FILE_TYPES
from gable.cli.helpers.data_asset_s3.schema_profiler import (
    get_data_asset_field_profiles_for_data_asset,
)
from gable.openapi import DataAssetFieldsToProfilesMapping, S3SamplingParameters
from loguru import logger

CHUNK_SIZE = 100


@dataclass
class S3DetectionResult:
    schema: dict
    data_asset_fields_to_profiles_map: Optional[DataAssetFieldsToProfilesMapping] = None


@dataclass
class S3ReadResult:
    df: pd.DataFrame
    has_schema: bool


def read_s3_files(
    s3_urls: list[str],
    row_sample_count: int,
    s3_opts: Optional[dict] = None,
) -> dict[str, S3ReadResult]:
    """
    Read data from given S3 file urls (only CSV, JSON, and parquet currently supported) and return pandas DataFrames.
    Args:
        s3_urls (list[str]): List of S3 URLs.
        row_sample_count (int): Number of rows to sample per S3 file.
        s3_opts (dict): S3 storage options. - only needed for tests using moto mocking
    Returns:
        dict[str, S3ReadResult]: Dict of file url to pandas DataFrames and a boolean indicating if the DataFrame has a predefined schema.
    """
    result: dict[str, S3ReadResult] = {}

    for url in s3_urls:
        df_result = read_s3_file(url, row_sample_count, s3_opts)

        if df_result is not None and not df_result.df.empty:  # ✅ Safe check
            result[url] = df_result

    return result


def read_s3_file(
    url: str, num_rows_to_sample: int, s3_opts: Optional[dict] = None
) -> Optional[S3ReadResult]:
    """Reads an S3 file, decompresses if needed, and returns a DataFrame."""
    try:
        s3_filesystem = s3fs.S3FileSystem(**(s3_opts or {}))

        with s3_filesystem.open(url, mode="rb") as f:
            file_content = f.read()

            # Ensure file_content is always bytes
            if isinstance(file_content, str):
                file_content = file_content.encode("utf-8")

            # Initialize original_file_key to avoid unbound variable error
            is_compressed = CompressionHandler.is_compressed(
                url
            ) or CompressionHandler.detect_compression_by_magic_bytes(file_content)

            # If compressed, decompress and then detect original format
            if is_compressed:
                file_stream, original_file_key = CompressionHandler.decompress(
                    url, file_content
                )
                file_source = file_stream
                file_s3_opts = None
            else:
                # Not compressed, so we can detect the format directly
                original_file_key = CompressionHandler.get_original_format(
                    url, file_content
                )
                file_source = url
                file_s3_opts = s3_opts
                # Determine file type and process accordingly
        has_schema = False
        if original_file_key.endswith(SUPPORTED_FILE_TYPES.CSV.value):
            df = get_csv_df(file_source, num_rows_to_sample, file_s3_opts)
        elif original_file_key.endswith(SUPPORTED_FILE_TYPES.TSV.value):
            df = get_tsv_df(file_source, num_rows_to_sample, file_s3_opts)
        elif original_file_key.endswith(SUPPORTED_FILE_TYPES.JSON.value):
            df = get_json_df(file_source, num_rows_to_sample, file_s3_opts)
        elif original_file_key.endswith(SUPPORTED_FILE_TYPES.PARQUET.value):
            df = get_parquet_df(file_source, num_rows_to_sample, file_s3_opts)
            has_schema = True
        elif original_file_key.endswith(SUPPORTED_FILE_TYPES.ORC.value):
            df = get_orc_df(file_source, num_rows_to_sample, file_s3_opts)
            has_schema = True
        elif original_file_key.endswith(SUPPORTED_FILE_TYPES.AVRO.value):
            df = get_avro_df(file_source, num_rows_to_sample, file_s3_opts)
            has_schema = True
        else:
            logger.error(f"Unsupported file format: {original_file_key}")
            return None

        return S3ReadResult(df, has_schema) if not df.empty else None

    except Exception as e:
        logger.error(f"Error reading file {url}: {e}")
        return None


def get_avro_df(
    file_source: Union[str, io.BytesIO],
    num_rows_to_sample: int,
    s3_opts: Optional[dict] = None,
) -> pd.DataFrame:
    """
    Read an Avro file from either an S3 URL or a decompressed BytesIO stream and return a pandas DataFrame.

    Args:
        file_source (Union[str, io.BytesIO]): S3 URL or decompressed BytesIO stream of the Avro file.
        num_rows_to_sample (int): Number of rows to sample from the Avro file.
        s3_opts (Optional[dict]): S3 storage options (only used if reading from S3).

    Returns:
        pd.DataFrame: A pandas DataFrame containing Avro file data.
    """
    try:
        # Handle S3 URLs
        if isinstance(file_source, str):
            s3_filesystem = s3fs.S3FileSystem(**(s3_opts or {}))
            with s3_filesystem.open(file_source, mode="rb") as f:
                file_content = f.read()
                file_buffer = io.BytesIO(
                    file_content.encode()
                    if isinstance(file_content, str)
                    else file_content
                )

        # Handle decompressed BytesIO streams
        else:
            file_source.seek(0)  # Ensure reading starts at the beginning
            file_buffer = file_source  # Use in-memory file stream

        # Read Avro file
        avro_reader = fastavro.reader(file_buffer)
        rows = []

        # Read rows up to the sample count
        for i, record in enumerate(avro_reader):
            if i >= num_rows_to_sample:
                break
            rows.append(record)

        # If no rows were read, return an empty DataFrame
        if not rows:
            logger.debug(f"No data found in the Avro file: {file_source}")
            return pd.DataFrame()

        # Convert rows to a pandas DataFrame
        df = pd.DataFrame(rows)
        return df

    except Exception as e:
        logger.error(f"Error reading Avro file {file_source}: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on error


def get_tsv_df(
    file_source: Union[str, io.BytesIO],
    num_rows_to_sample: int,
    s3_opts: Optional[dict] = None,
) -> pd.DataFrame:
    """
    Read a TSV file from either an S3 URL or a decompressed BytesIO stream and return a pandas DataFrame.
    Special handling for TSV files with and without headers.
    """
    try:
        # Handle compressed `BytesIO` streams vs S3 URLs
        if isinstance(file_source, str):
            sample_no_header_df = pd.read_csv(
                file_source,
                sep="\t",
                nrows=10,
                storage_options=s3_opts,
                engine="python",
                header=None,
            )
        else:
            file_source.seek(0)  # Ensure reading starts at the beginning
            sample_no_header_df = pd.read_csv(
                file_source,
                sep="\t",
                nrows=10,
                engine="python",
                header=None,
            )

        # If the sample dataframe is empty, return an empty DataFrame
        if sample_no_header_df.empty:
            log_debug(f"The TSV file {file_source} is empty.")
            return (
                pd.DataFrame()
            )  # Return an empty DataFrame if the TSV file has no rows

        # Determine if the file has a header
        has_header = df_has_header(sample_no_header_df)

        # Read full data based on detected header
        if has_header:
            if isinstance(file_source, str):
                df = pd.concat(
                    pd.read_csv(
                        file_source,
                        sep="\t",
                        chunksize=CHUNK_SIZE,
                        nrows=num_rows_to_sample,
                        storage_options=s3_opts,
                    ),
                    ignore_index=True,
                )
            else:
                file_source.seek(0)
                df = pd.concat(
                    pd.read_csv(
                        file_source,
                        sep="\t",
                        chunksize=CHUNK_SIZE,
                        nrows=num_rows_to_sample,
                    ),
                    ignore_index=True,
                )
        else:
            if isinstance(file_source, str):
                df = pd.concat(
                    pd.read_csv(
                        file_source,
                        sep="\t",
                        header=None,
                        chunksize=CHUNK_SIZE,
                        nrows=num_rows_to_sample,
                        storage_options=s3_opts,
                    ),
                    ignore_index=True,
                )
            else:
                file_source.seek(0)
                df = pd.concat(
                    pd.read_csv(
                        file_source,
                        sep="\t",
                        header=None,
                        chunksize=CHUNK_SIZE,
                        nrows=num_rows_to_sample,
                    ),
                    ignore_index=True,
                )

        return df

    except pd.errors.EmptyDataError:
        log_debug(
            f"No columns to parse from file {file_source}. Returning empty DataFrame."
        )
        return (
            pd.DataFrame()
        )  # Return an empty DataFrame if the TSV file has no columns

    except Exception as e:
        logger.error(f"Unexpected error while reading TSV file {file_source}: {e}")
        raise


def get_orc_df(
    file_source: Union[str, io.BytesIO],
    num_rows_to_sample: int,
    s3_opts: Optional[dict] = None,
) -> pd.DataFrame:
    """
    Read ORC file from either an S3 URL or a decompressed BytesIO stream and return a pandas DataFrame.

    Args:
        file_source (Union[str, io.BytesIO]): S3 URL or decompressed BytesIO stream of the ORC file.
        num_rows_to_sample (int): Number of rows to sample.
        s3_opts (Optional[dict]): S3 storage options (only used if reading from S3).

    Returns:
        pd.DataFrame: A pandas DataFrame containing ORC file data.
    """
    try:
        # Handle S3 URLs
        if isinstance(file_source, str):
            endpoint_override = (
                s3_opts.get("client_kwargs", {}).get("endpoint_url")
                if s3_opts
                else None
            )
            session = boto3.Session()
            credentials = session.get_credentials()
            if not credentials:
                raise click.ClickException("No AWS credentials found")

            filesystem = pyarrow.fs.S3FileSystem(
                endpoint_override=endpoint_override,
                access_key=credentials.access_key,
                secret_key=credentials.secret_key,
                session_token=credentials.token,
                region=boto3.Session().region_name,
            )
            bucket_and_path = strip_s3_bucket_prefix(file_source)
            file_obj = filesystem.open_input_file(bucket_and_path)

        # Handle decompressed BytesIO streams
        else:
            file_source.seek(0)  # Ensure reading starts at the beginning
            file_obj = file_source  # Use in-memory file stream

        # Read ORC file
        orcfile = pyarrow.orc.ORCFile(file_obj)

        # Handle empty ORC file case
        if orcfile.nrows == 0:
            logger.debug(f"The ORC file {file_source} is empty.")
            return (
                pd.DataFrame()
            )  # Return an empty DataFrame if the ORC file has no rows

        # Determine number of stripes to sample
        rows_per_stripe = orcfile.nrows / orcfile.nstripes
        stripes_to_sample = min(
            math.ceil(num_rows_to_sample / rows_per_stripe), orcfile.nstripes
        )

        logger.debug(
            f"Reading {stripes_to_sample} stripes from {file_source} (total rows: {orcfile.nrows}, total stripes: {orcfile.nstripes})"
        )

        # Convert ORC to Pandas DataFrame
        return pyarrow.Table.from_batches(
            [orcfile.read_stripe(i) for i in range(stripes_to_sample)]
        ).to_pandas()

    except Exception as e:
        logger.error(f"Error reading ORC file {file_source}: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on error


def get_parquet_df(
    file_source: Union[str, io.BytesIO],
    num_rows_to_sample: int,
    s3_opts: Optional[dict] = None,
) -> pd.DataFrame:
    """
    Read a Parquet file from either an S3 URL or a decompressed BytesIO stream and return a pandas DataFrame.

    Args:
        file_source (Union[str, io.BytesIO]): S3 URL or decompressed BytesIO stream of the Parquet file.
        num_rows_to_sample (int): Number of rows to sample.
        s3_opts (Optional[dict]): S3 storage options (only used if reading from S3).

    Returns:
        pd.DataFrame: A pandas DataFrame containing Parquet file data.
    """
    try:
        # Handle S3 URLs
        if isinstance(file_source, str):
            s3_filesystem = s3fs.S3FileSystem(**(s3_opts or {}))
            parquet_file = ParquetFile(file_source, fs=s3_filesystem)

        # Handle decompressed BytesIO streams
        else:
            file_source.seek(0)  # Ensure reading starts at the beginning
            parquet_file = ParquetFile(file_source)

        # Check if the file has any rows
        if parquet_file.count == 0:
            logger.debug(f"The Parquet file {file_source} is empty.")
            return (
                pd.DataFrame()
            )  # Return an empty DataFrame if the Parquet file has no rows

        # Try to read the specified number of rows
        return parquet_file.head(num_rows_to_sample)

    except ValueError as ve:
        if "Seek before start of file" in str(ve):
            logger.debug(
                f"Seek error for file {file_source}, this could be due to an empty or corrupted file."
            )
            return pd.DataFrame()  # Return an empty DataFrame in case of seek error
        else:
            logger.error(
                f"ValueError encountered while reading Parquet file {file_source}: {ve}"
            )
            raise

    except Exception as e:
        logger.error(f"Unexpected error while reading Parquet file {file_source}: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on error


def df_has_header(df: pd.DataFrame) -> bool:
    # (Modified from csv.Sniffer.has_header)
    # Creates a dictionary of types of data in each column. If any
    # column is of a single type (say, integers), *except* for the first
    # row, then the first row is presumed to be labels. If the type
    # can't be determined, it is assumed to be a string in which case
    # the length of the string is the determining factor: if all of the
    # rows except for the first are the same length, it's a header.
    # Finally, a 'vote' is taken at the end for each column, adding or
    # subtracting from the likelihood of the first row being a header.

    maybe_header = df.iloc[0]
    columns = len(df.columns)
    columnTypes: dict[int, type[complex] | int | None] = {}
    for i in range(columns):
        columnTypes[i] = None

    checked = 0
    for _, row in df.iloc[1:].iterrows():
        # arbitrary number of rows to check, to keep it sane
        if checked > 20:
            break
        checked += 1

        if len(row) != columns:
            continue  # skip rows that have irregular number of columns

        for col in list(columnTypes.keys()):
            thisType = complex
            try:
                thisType(row[col])
            except (ValueError, OverflowError):
                # fallback to length of string
                thisType = len(row[col])

            if thisType != columnTypes[col]:
                if columnTypes[col] is None:  # add new column type
                    columnTypes[col] = thisType
                else:
                    # type is inconsistent, remove column from
                    # consideration
                    del columnTypes[col]

    # finally, compare results against first row and "vote"
    # on whether it's a header
    hasHeader = 0
    for col, colType in columnTypes.items():
        if type(colType) == type(0):  # it's a length
            if len(maybe_header[col]) != colType:
                hasHeader += 1
            else:
                hasHeader -= 1
        else:  # attempt typecast
            try:
                colType(maybe_header[col])  # type: ignore
            except (ValueError, TypeError):
                hasHeader += 1
            else:
                hasHeader -= 1

    return hasHeader > 0


def get_csv_df(
    file_source: Union[str, io.BytesIO],
    num_rows_to_sample: int,
    s3_opts: Optional[dict] = None,
) -> pd.DataFrame:
    """
    Read CSV file from either an S3 URL or a decompressed BytesIO stream and return a pandas DataFrame.
    """
    try:
        if isinstance(file_source, str):  # If it's an S3 URL
            sample_no_header_df = pd.read_csv(
                file_source,
                nrows=10,
                storage_options=s3_opts,
                engine="python",
                header=None,
            )
        else:  # If it's a decompressed BytesIO stream
            file_source.seek(0)  # Ensure reading starts at the beginning
            sample_no_header_df = pd.read_csv(
                file_source, nrows=10, engine="python", header=None
            )

        if sample_no_header_df.empty:
            log_debug(f"The CSV file {file_source} is empty.")
            return pd.DataFrame()

        has_header = df_has_header(sample_no_header_df)

        if has_header:
            if isinstance(file_source, str):
                df = pd.concat(
                    pd.read_csv(
                        file_source,
                        chunksize=CHUNK_SIZE,
                        nrows=num_rows_to_sample,
                        storage_options=s3_opts,
                    ),
                    ignore_index=True,
                )
            else:
                file_source.seek(0)
                df = pd.concat(
                    pd.read_csv(
                        file_source, chunksize=CHUNK_SIZE, nrows=num_rows_to_sample
                    ),
                    ignore_index=True,
                )
        else:
            if isinstance(file_source, str):
                df = pd.concat(
                    pd.read_csv(
                        file_source,
                        header=None,
                        chunksize=CHUNK_SIZE,
                        nrows=num_rows_to_sample,
                        storage_options=s3_opts,
                    ),
                    ignore_index=True,
                )
            else:
                file_source.seek(0)
                df = pd.concat(
                    pd.read_csv(
                        file_source,
                        header=None,
                        chunksize=CHUNK_SIZE,
                        nrows=num_rows_to_sample,
                    ),
                    ignore_index=True,
                )

        return df

    except pd.errors.EmptyDataError:
        log_debug(
            f"No columns to parse from file {file_source}. Returning empty DataFrame."
        )
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Unexpected error while reading CSV file {file_source}: {e}")
        raise


def get_json_df(
    file_source: Union[str, io.BytesIO],
    num_rows_to_sample: int,
    s3_opts: Optional[dict] = None,
) -> pd.DataFrame:
    """
    Read a JSON file from either an S3 URL or a decompressed BytesIO stream and return a pandas DataFrame.

    Args:
        file_source (Union[str, io.BytesIO]): S3 URL or decompressed BytesIO stream of the JSON file.
        num_rows_to_sample (int): Number of rows to sample.
        s3_opts (Optional[dict]): S3 storage options (only used if reading from S3).

    Returns:
        pd.DataFrame: A pandas DataFrame containing JSON file data.
    """
    try:
        # Handle S3 URLs
        if isinstance(file_source, str):
            s3_filesystem = s3fs.S3FileSystem(**(s3_opts or {}))
            json_reader = pd.read_json(
                file_source,
                lines=True,
                chunksize=CHUNK_SIZE,
                nrows=num_rows_to_sample,
                storage_options=s3_opts,
            )

        # Handle decompressed BytesIO streams
        else:
            file_source.seek(0)  # Ensure reading starts at the beginning
            json_reader = pd.read_json(
                file_source,
                lines=True,
                chunksize=CHUNK_SIZE,
                nrows=num_rows_to_sample,
            )

        # Read chunks into a dataframe
        chunks = list(json_reader)

        if not chunks:  # No data was read, file is empty
            logger.info(f"No data found in the JSON file: {file_source}")
            return pd.DataFrame()

        df = pd.concat(chunks, ignore_index=True)

        return flatten_json(df)

    except pd.errors.EmptyDataError:
        logger.debug(
            f"No columns to parse from file {file_source}. Returning empty DataFrame."
        )
        return (
            pd.DataFrame()
        )  # Return an empty DataFrame if the JSON file has no columns

    except Exception as e:
        logger.error(f"Unexpected error while reading JSON file {file_source}: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on error


def flatten_json(df: pd.DataFrame) -> pd.DataFrame:
    """
    Flattens any nested JSON data to a single column
    {"customerDetails": {"technicalContact": {"email": "...."}}}" => customerDetails.technicalContact.email
    """
    normalized_df = pd.json_normalize(df.to_dict(orient="records"))
    return drop_null_parents(normalized_df)


def drop_null_parents(df: pd.DataFrame) -> pd.DataFrame:
    # Identify null columns
    null_columns = {col for col in df.columns if df[col].isnull().all()}  # type: ignore

    # Identify nested columns
    parent_columns = {col for col in df.columns if "." in col}

    # For null parent columns, drop them if they will be represented by the nested columns
    columns_to_drop = [
        null_column
        for null_column in null_columns
        for parent_column in parent_columns
        if null_column != parent_column and null_column in parent_column
    ]
    return df.drop(columns=columns_to_drop)


def append_s3_url_prefix(bucket_name: str, url: str) -> str:
    return "s3://" + bucket_name + "/" + url if not url.startswith("s3://") else url


def strip_s3_bucket_prefix(bucket_name: str) -> str:
    return bucket_name.removeprefix("s3://")


def get_schema_from_s3_files(
    bucket: str,
    event_name: str,
    s3_urls: set[str],
    row_sample_count: int,
    recent_file_count: int,
    skip_profiling: bool = False,
) -> Optional[S3DetectionResult]:
    """
    Get schema along with data profile from given S3 file urls (only CSV, JSON, and parquet currently supported).
    Args:
        bucket_name (str): S3 bucket name.
        event_name (str): Event name.
        s3_urls (list[str]): List of S3 URLs.
        row_sample_count (int): Number of rows to sample per S3 file.
    Returns:
        S3DetectionResult: Merged schema and data profile if able to be computed.
    """
    urls = [append_s3_url_prefix(bucket, url) for url in s3_urls]
    s3_data = read_s3_files(urls, row_sample_count)
    if len(s3_data) > 0:
        schema = merge_schemas(
            [
                NativeS3Converter().to_recap(
                    df_result.df, df_result.has_schema, event_name
                )
                for _, df_result in s3_data.items()
                if len(df_result.df.columns) > 0
            ]
        )
        if skip_profiling:
            log_debug(f"Skipping data profiling for event name: {event_name}")
            return S3DetectionResult(schema)
        else:
            profiles = get_data_asset_field_profiles_for_data_asset(
                schema,
                {file_url: df_data.df for file_url, df_data in s3_data.items()},
                event_name,
                S3SamplingParameters(
                    rowSampleCount=row_sample_count,
                    recentFileCount=recent_file_count,
                ),
            )
            return S3DetectionResult(schema, profiles)


def merge_schemas(schemas: list[dict]) -> dict:
    """
    Merge multiple schemas into a single schema.
    Args:
        schemas (list[dict]): List of schemas.
    Returns:
        dict: Merged schema.
    """
    # Dictionary of final fields, will be turned into a struct type at the end
    result_dict: dict[str, dict] = {}
    for schema in schemas:
        if "fields" in schema:
            for field in schema["fields"]:
                field_name = field["name"]
                # If the field is not yet in the result, just add it
                if field_name not in result_dict:
                    result_dict[field_name] = field
                elif field != result_dict[field_name]:
                    # If both types are structs, recursively merge them
                    if (
                        field["type"] == "struct"
                        and result_dict[field_name]["type"] == "struct"
                    ):
                        result_dict[field_name] = {
                            "fields": merge_schemas([result_dict[field_name], field])[
                                "fields"
                            ],
                            "name": field_name,
                            "type": "struct",
                        }
                    else:
                        # Merge the two type into a union, taking into account that one or both of them
                        # may already be unions
                        result_types = (
                            result_dict[field_name]["types"]
                            if result_dict[field_name]["type"] == "union"
                            else [result_dict[field_name]]
                        )
                        field_types = (
                            field["types"] if field["type"] == "union" else [field]
                        )
                        result_dict[field_name] = {
                            "type": "union",
                            "types": get_distinct_dictionaries(
                                remove_names(result_types) + remove_names(field_types)
                            ),
                            "name": field_name,
                        }

    return {"fields": list(result_dict.values()), "type": "struct"}


def get_distinct_dictionaries(dictionaries: list[dict]) -> list[dict]:
    """
    Get distinct dictionaries from a list of dictionaries.
    Args:
        dictionaries (list[dict]): List of dictionaries.
    Returns:
        list[dict]: List of distinct dictionaries.
    """
    # Remove duplicates, use a list instead of a set to avoid
    # errors about unhashable types
    distinct = []
    for d in dictionaries:
        if d not in distinct:
            distinct.append(d)
    # Sort for testing so we have deterministic results
    return sorted(
        distinct,
        key=lambda x: x["type"],
    )


def remove_names(list: list[dict]) -> list[dict]:
    """
    Remove names from a list of dictionaries.
    Args:
        list (dict): List of dictionaries.
    Returns:
        dict: List of dictionaries without names.
    """
    for t in list:
        if "name" in t:
            del t["name"]
    return list
