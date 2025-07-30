# this file is copied from external/gable to control-plane/packages/core/python/types/control_plane_types
# as part of generating oas types. Edits should only be made to the original in external/gable/

from .openapi import SourceType

ALL_SOURCE_TYPES = list(SourceType)

DATABASE_SOURCE_TYPES = [
    SourceType.mysql,
    SourceType.mssql,
    SourceType.postgres,
]

FILE_SOURCE_TYPES = [SourceType.protobuf, SourceType.avro]

STATIC_CODE_ANALYSIS_SOURCE_TYPES = [
    SourceType.python,
    SourceType.typescript,
    SourceType.pyspark,
    SourceType.s3,
]

SCHEMA_SOURCE_TYPES = DATABASE_SOURCE_TYPES + FILE_SOURCE_TYPES
