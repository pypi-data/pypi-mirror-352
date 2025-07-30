import warnings
from typing import Any

import numpy as np
import pandas as pd
from pandas.api.types import infer_dtype

# TODO - Replace return types with Gable Types
# from gable.openapi import (
#     FieldModel,
#     GableSchemaBool,
#     GableSchemaFloat,
#     GableSchemaInt,
#     GableSchemaList,
#     GableSchemaNull,
#     GableSchemaString,
#     GableSchemaStruct,
#     GableSchemaType,
#     GableSchemaUnion,
# )


class NativeS3Converter:
    def __init__(self):
        pass

    def to_recap(self, df: pd.DataFrame, has_schema: bool, event_name: str) -> dict:
        """
        Convert a pandas DataFrame to a Recap StructType.
        Args:
            df (pd.DataFrame): The pandas DataFrame to convert.
            event_name (str): The name of the field.
            has_schema (bool): Whether the DataFrame has a predefined schema. If False, the schema will be inferred based on its contents
        Returns:
            StructType: The Recap StructType representing the DataFrame.
        """
        df.columns = df.columns.map(str)

        nullable_columns = df.isnull().any(axis=0)

        if isinstance(nullable_columns, bool):
            nullable_columns = pd.Series([nullable_columns], index=[df.columns[0]])

        nullable_columns = nullable_columns.rename(index=str)

        nullable_columns.index = nullable_columns.index.map(str)

        df = (
            df.infer_objects()
        )  # Optional: Convert object dtypes to best possible types

        schema = self._get_schema(df, has_schema)
        fields = []
        for field_name, field_dtypes in schema.items():
            field_name = str(field_name)
            try:
                # Handle column representing nested JSON field
                if "." in field_name:
                    self._handle_nested_fields(
                        field_name,
                        field_dtypes,
                        nullable_columns[field_name],  # type: ignore
                        fields,
                        df[field_name],  # type: ignore
                        has_schema,
                    )
                else:
                    gable_type = self._parse_type(
                        field_dtypes,
                        field_name,
                        nullable_columns[field_name],  # type: ignore
                        df[field_name],  # type: ignore
                        has_schema,
                    )
                    fields.append(gable_type)
            except ValueError as e:
                print(f"Error parsing field {field_name} of type {field_dtypes}: {e}")

        return {"fields": fields, "name": event_name, "type": "struct"}

    def _parse_type(
        self,
        dtypes: list[str],
        field_name: str,
        nullable: bool,
        column: pd.Series,
        has_schema: bool,
    ) -> dict:
        gable_types = []

        if column.isnull().all():
            return {"type": "null", "name": field_name}

        for dtype in dtypes:
            if dtype == "string":
                gable_types.append({"type": "string", "name": field_name})
            elif dtype == "Int64":
                gable_types.append({"type": "int", "name": field_name, "bits": 64})
            elif dtype == "Int32":
                gable_types.append({"type": "int", "name": field_name, "bits": 32})
            elif dtype == "Float64":
                gable_types.append({"type": "float", "name": field_name, "bits": 64})
            elif dtype == "boolean":
                gable_types.append({"type": "bool", "name": field_name})
            elif dtype == "object":
                non_null_column = column.dropna()

                # ✅ Fix: Ensure we check length first to avoid Series boolean evaluation issues
                if not non_null_column.empty and all(
                    isinstance(x, list) for x in non_null_column
                ):

                    gable_types.append(
                        self._parse_list_type(non_null_column, field_name)
                    )
                else:
                    gable_types.append(
                        self._parse_object_type(
                            non_null_column, field_name, has_schema, nullable
                        )
                    )
            elif dtype.startswith("datetime64[ns") and dtype.endswith("]"):
                gable_types.append(self._parse_datetime_type(column, field_name))
            else:
                raise ValueError(f"Unsupported dtype: {dtype}")

        if nullable and {"type": "null"} not in gable_types:
            gable_types.append({"type": "null"})

        if len(gable_types) > 1:
            return {"type": "union", "types": gable_types, "name": field_name}

        elif len(gable_types) == 1:
            field_type = gable_types[0]
            if field_type["type"] == "Unknown" and "name" not in field_type:
                field_type["name"] = field_name  # ✅ Ensure field name is added
            return field_type

        return {"type": "null", "name": field_name}

    def _parse_datetime_type(self, column: pd.Series, field_name: str) -> dict:
        """
        Parse a datetime type and return the corresponding Gable Type.
        Args:
            df (pd.DataFrame): The pandas DataFrame to convert.
            field_name (str): The name of the field.
        Returns:
            The Gable Type corresponding to the field type.
        """
        # If the datetime column has a timezone, assume it's a timestamp
        if column.dt.tz is not None:
            return {
                "type": "int",
                "logical": "Timestamp",
                "name": field_name,
                "bits": 64,
            }

        # If all values are midnight, assume it's a date
        is_date = (
            all(column.dt.hour == 0)
            and all(column.dt.minute == 0)
            and all(column.dt.second == 0)
            and all(column.dt.microsecond == 0)
            and all(column.dt.nanosecond == 0)
        )
        if is_date:
            return {
                "type": "int",
                "logical": "Date",
                "name": field_name,
                "bits": 64,
            }

        # If we could not determine, assume it's a timestamp
        return {
            "type": "int",
            "logical": "Timestamp",  # TODO - improve. Consider a Duration, Time, etc.
            "name": field_name,
            "bits": 64,
        }

    def _parse_list_type(self, column: pd.Series, field_name: str) -> dict:
        list_types: set[frozenset] = set()
        has_null_values = False

        for list_item in column:
            if list_item is None or (
                isinstance(list_item, float) and pd.isna(list_item)
            ):
                has_null_values = True
                continue

            if isinstance(list_item, list):
                for item in list_item:
                    if isinstance(item, int):
                        list_types.add(frozenset({"type": "int", "bits": 64}.items()))
                    elif isinstance(item, float):
                        list_types.add(frozenset({"type": "float", "bits": 64}.items()))
                    elif isinstance(item, str):
                        list_types.add(frozenset({"type": "string"}.items()))
                    elif isinstance(item, bool):
                        list_types.add(frozenset({"type": "bool"}.items()))
                    else:
                        list_types.add(frozenset({"type": "Unknown"}.items()))

        gable_types = [dict(t) for t in list_types]

        # ✅ If multiple types exist, wrap them in a union
        if len(gable_types) > 1:
            values = {"type": "union", "types": gable_types}
        elif len(gable_types) == 1:
            values = gable_types[0]
        else:
            values = {
                "type": "Unknown",
                "name": field_name,
            }  # Handle empty lists properly

        # ✅ Ensure nullability is correctly handled
        if has_null_values:
            return {
                "type": "union",
                "types": [
                    {"type": "list", "values": values},
                    {"type": "null"},
                ],
                "name": field_name,
            }

        return {"type": "list", "name": field_name, "values": values}

    def _handle_nested_fields(
        self,
        field_name: str,
        field_types: list[str],
        nullable: bool,
        current_level_fields: list[dict],
        column: pd.Series,
        has_schema: bool,
    ):
        """
        Handle nested fields in a DataFrame.
        Args:
            field_name (str): The name of the field.
            field_types List[str]: List of field types to parse.
            nullable (bool): Whether the field is nullable.
            current_level_fields (list): The current "level" of fields.
            column (pd.Series): The column to parse.
            has_schema (bool): Whether the DataFrame has a predefined schema. If False, the schema will be inferred based on its contents
        """

        field_name_parts = field_name.split(".")
        # Iterate through each "level" of the nested fields
        for index, subfield_name in enumerate(field_name_parts):
            # Look to see if the subfield has already been added to the current level
            found_recap_type = next(
                (
                    field
                    for field in current_level_fields
                    if field["name"] == subfield_name
                ),
                None,
            )
            if found_recap_type is not None:
                subfield_recap_type = found_recap_type
            else:
                if index == len(field_name_parts) - 1:
                    # Last item in the list is not a StructType
                    subfield_recap_type = self._parse_type(
                        field_types,
                        subfield_name,
                        nullable,
                        column,
                        has_schema,
                    )
                else:
                    subfield_recap_type = {
                        "fields": [],
                        "name": subfield_name,
                        "type": "struct",
                    }
                current_level_fields.append(subfield_recap_type)

            if subfield_recap_type["type"] == "struct":
                # Update current_level_fields to the next "level"
                current_level_fields = subfield_recap_type["fields"]

    def _get_schema(self, df: pd.DataFrame, has_schema: bool) -> dict[str, list[str]]:
        """
        Infer the schema of the DataFrame by examining the data type of each entry in each column.
        Handles mixed types and assigns the most appropriate type.
        """
        # if it has a schema already, assume it is correct and don't try coercing types down
        if has_schema:
            dtypes_dict = df.convert_dtypes().dtypes.to_dict()
            return {col: [str(dtype)] for col, dtype in dtypes_dict.items()}

        df.columns = df.columns.astype(str)
        type_schema = {col: set() for col in df.columns}
        for col in df.columns:
            for entry in df[col].replace("", np.nan).dropna():
                if isinstance(entry, list):
                    type_schema[col].add("object")
                else:
                    type_detected = self.detect_type(entry, df, col)
                    type_schema[col].add(type_detected)
        value = {
            col: sorted((str(type) for type in types), key=lambda x: x)
            for col, types in type_schema.items()
        }
        return value

    def detect_type(self, entry: Any, df: pd.DataFrame, col: str):
        """
        Detect the type of an entry, handling numeric, datetime, and other types.
        """

        with warnings.catch_warnings():
            # Stop pandas from warning about converting types and spamming the console logs
            warnings.simplefilter(action="ignore", category=UserWarning)

            inferred_dtype = infer_dtype([entry])
            if inferred_dtype == "boolean":
                return pd.BooleanDtype()
            try:
                converted_col_dtype = df[col].convert_dtypes().dtypes
                numeric_entry = pd.to_numeric(entry, errors="raise")
                numeric_dtype = infer_dtype([numeric_entry])
                if (
                    converted_col_dtype in [pd.Int64Dtype(), pd.Float64Dtype()]
                    and str(converted_col_dtype) != numeric_dtype
                ):
                    return converted_col_dtype
                return (
                    pd.Int64Dtype() if numeric_dtype == "integer" else pd.Float64Dtype()
                )
            except (ValueError, TypeError):
                try:
                    pd.to_datetime(entry, errors="raise")
                    df[col] = pd.to_datetime(df[col], errors="raise")
                    return pd.Series([entry]).astype("datetime64[ns]").dtype
                except ValueError:
                    return (
                        pd.StringDtype()
                        if inferred_dtype == "string"
                        else pd.Series([entry]).dtype
                    )

    def _parse_object_type(
        self, column: pd.Series, field_name: str, has_schema: bool, nullable: bool
    ) -> dict:
        non_null_vals = column.dropna()  # ✅ **Ignore `None` for type inference**
        unique_scalar_types = set()
        contains_list = False

        for x in non_null_vals:
            if isinstance(x, list):
                contains_list = True
            elif isinstance(x, bool) or isinstance(x, (np.bool_,)):
                unique_scalar_types.add(frozenset({"type": "bool"}.items()))
            elif isinstance(x, (int, np.integer)) and not isinstance(x, bool):
                unique_scalar_types.add(frozenset({"type": "int", "bits": 64}.items()))
            elif isinstance(x, (float, np.floating)):
                unique_scalar_types.add(
                    frozenset({"type": "float", "bits": 64}.items())
                )
            elif isinstance(x, (str, np.str_)):
                unique_scalar_types.add(frozenset({"type": "string"}.items()))
            else:
                unique_scalar_types.add(frozenset({"type": "Unknown"}.items()))

        if contains_list and len(unique_scalar_types) == 0:
            return self._parse_list_type(non_null_vals, field_name)
        elif contains_list and len(unique_scalar_types) > 0:
            return {
                "type": "union",
                "types": [self._parse_list_type(non_null_vals, field_name)]
                + [
                    dict(t)
                    for t in sorted(
                        unique_scalar_types, key=lambda x: next(iter(dict(x).values()))
                    )
                ],
                "name": field_name,
            }
        if len(unique_scalar_types) > 1:
            return {
                "type": "union",
                "types": [
                    dict(t)
                    for t in sorted(
                        unique_scalar_types, key=lambda x: next(iter(dict(x).values()))
                    )
                ],
                "name": field_name,
            }
        elif len(unique_scalar_types) == 1:
            return dict(unique_scalar_types.pop())  # Return the single detected type

        return {"type": "Unknown", "name": field_name}
