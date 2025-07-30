"""
Concrete metadata collector implementations for the inventory metadata builder.
"""

import datetime
import urllib.parse
from typing import Any, Dict, List, Optional

import pyarrow as pa

from .cache_manager import InventoryCacheManager
from .data_loader import InventoryDataLoader
from .metadata_builder import MetadataCollector
from .summarizers import InventoryMetadataSummarizer, PartitionSummarizer


class FileMetadataCollector(MetadataCollector):
    """Collector for file-level metadata like counts, sizes, and types"""

    def __init__(self, logger, inventory_dir=None):
        """
        Initialize the FileMetadataCollector

        Args:
            logger: Logger instance
            inventory_dir: Directory where inventory reports are stored
        """
        super().__init__(logger, inventory_dir)
        self.summarizer = InventoryMetadataSummarizer(logger, inventory_dir)
        self.cache_manager = InventoryCacheManager()

    def collect(
        self, metadata: Dict[str, Dict[str, Any]], prefixes: Optional[List[str]] = None
    ) -> None:
        """
        Collect file-level metadata and add it to the metadata dictionary

        Args:
            metadata: Dictionary to add metadata to
            prefixes: Optional list of prefixes to limit collection to
        """
        self.logger.info("Collecting file metadata")

        # Generate a cache key based on prefixes
        prefixes_str = "_".join(sorted(prefixes)) if prefixes else "all"
        cache_key = f"file_metadata_{prefixes_str}"

        # Check if we have cached results
        cached_result = self.cache_manager.get_query_result(cache_key)
        if cached_result is not None:
            self.logger.info("Using cached file metadata")
            file_metadata = cached_result
        else:
            # Get file metadata (no parallelization)
            file_metadata = self.summarizer.analyze_inventory(prefixes)

            # Cache the results
            self.cache_manager.cache_query_result(cache_key, file_metadata)

        # If metadata is empty, initialize with discovered prefixes
        if not metadata and file_metadata:
            for prefix in file_metadata:
                metadata[prefix] = {}

        # Add file metadata to existing prefixes
        for prefix, prefix_metadata in file_metadata.items():
            if prefix not in metadata:
                metadata[prefix] = {}
            metadata[prefix].update(prefix_metadata)

        self.logger.info(
            "File metadata collection complete for %d prefixes", len(file_metadata)
        )


class PartitionMetadataCollector(MetadataCollector):
    """Collector for partition-level metadata like partition keys and schemes"""

    def __init__(self, logger, inventory_dir=None):
        super().__init__(logger, inventory_dir)
        self.summarizer = PartitionSummarizer(logger, inventory_dir)
        self.cache_manager = InventoryCacheManager()

    def collect(
        self, metadata: Dict[str, Dict[str, Any]], prefixes: Optional[List[str]] = None
    ) -> None:
        """
        Collect partition metadata and add it to the metadata dictionary

        Args:
            metadata: Dictionary to add metadata to
            prefixes: Optional list of prefixes to limit collection to
        """
        self.logger.info("Collecting partition metadata")

        # Generate a cache key based on prefixes
        prefixes_str = "_".join(sorted(prefixes)) if prefixes else "all"
        cache_key = f"partition_metadata_{prefixes_str}"

        # Check if we have cached results
        cached_result = self.cache_manager.get_query_result(cache_key)
        if cached_result is not None:
            self.logger.info("Using cached partition metadata")
            partition_metadata = cached_result
        else:
            # Instead of discovering prefixes again, use the ones already in metadata
            # This ensures we analyze all prefixes found during file metadata collection
            existing_prefixes = list(metadata.keys()) if metadata else None

            # If both file-discovered prefixes and user-specified prefixes exist, use their intersection
            if existing_prefixes and prefixes:
                prefixes_to_analyze = [p for p in existing_prefixes if p in prefixes]
                self.logger.info(
                    f"Analyzing {len(prefixes_to_analyze)} prefixes that exist in both file metadata and user-specified list"
                )
            elif existing_prefixes:
                prefixes_to_analyze = existing_prefixes
                self.logger.info(
                    f"Analyzing all {len(prefixes_to_analyze)} prefixes found in file metadata"
                )
            else:
                prefixes_to_analyze = prefixes
                self.logger.info(
                    f"No existing metadata prefixes found, using user-specified prefixes"
                )

            # Get partition metadata using the existing prefixes
            partition_metadata = self.summarizer.analyze_inventory(prefixes_to_analyze)

            # Cache the results
            self.cache_manager.cache_query_result(cache_key, partition_metadata)

        # If metadata is empty, initialize with discovered prefixes
        if not metadata and partition_metadata:
            for prefix in partition_metadata:
                metadata[prefix] = {}

        # Add partition metadata to existing prefixes
        for prefix, prefix_metadata in partition_metadata.items():
            if prefix not in metadata:
                metadata[prefix] = {}
            metadata[prefix].update(prefix_metadata)

        self.logger.info(
            "Partition metadata collection complete for %d prefixes",
            len(partition_metadata),
        )


class LatestObjectsCollector(MetadataCollector):
    """Collector for the latest N objects for each prefix"""

    def __init__(self, logger, inventory_dir=None, limit: int = 5):
        super().__init__(logger, inventory_dir)
        self.data_loader = InventoryDataLoader(logger, inventory_dir)
        self.limit = limit
        self.cache_manager = InventoryCacheManager()

    def collect(
        self, metadata: Dict[str, Dict[str, Any]], prefixes: Optional[List[str]] = None
    ) -> None:
        """
        Collect the latest objects for each prefix and add to the metadata dictionary

        Args:
            metadata: Dictionary to add metadata to
            prefixes: Optional list of prefixes to limit collection to
        """
        self.logger.info(f"Collecting latest {self.limit} objects per prefix")

        # If prefixes not specified, use keys from metadata
        collect_prefixes = prefixes if prefixes else list(metadata.keys())

        for prefix in collect_prefixes:
            if prefix not in metadata:
                self.logger.warning(
                    f"Skip collecting latest objects: prefix {prefix} not in metadata"
                )
                continue

            self.logger.info(f"Collecting latest objects for prefix: {prefix}")

            # Generate a cache key
            cache_key = f"latest_objects_formatted_{prefix}_{self.limit}"
            cached_objects = self.cache_manager.get_query_result(cache_key)

            if cached_objects is not None:
                self.logger.info(
                    f"Using cached formatted latest objects for prefix: {prefix}"
                )
                latest_objects = cached_objects
            else:
                arrow_table = self.data_loader.get_latest_objects(prefix, self.limit)

                if arrow_table.num_rows == 0:
                    self.logger.warning(f"No objects found for prefix: {prefix}")
                    continue

                # Convert Arrow table to list of dictionaries
                latest_objects = []
                for i in range(arrow_table.num_rows):
                    # URL-decode the key to convert %3D to = and other encoded characters
                    raw_key = arrow_table["Key"][i].as_py()
                    decoded_key = urllib.parse.unquote(raw_key)

                    # Get the last_modified timestamp
                    last_modified_iso = arrow_table["LastModifiedDate"][i].as_py()

                    # Convert ISO format to standard UTC format used in the report
                    # Parse the ISO timestamp and format as "YYYY-MM-DD HH:MM:SS UTC"
                    if isinstance(last_modified_iso, str):
                        try:
                            # Convert from ISO 8601 format to the desired format
                            last_modified_datetime = datetime.datetime.fromisoformat(
                                last_modified_iso.replace("Z", "+00:00")
                            )
                            last_modified_formatted = last_modified_datetime.strftime(
                                "%Y-%m-%d %H:%M:%S UTC"
                            )
                        except (ValueError, TypeError):
                            # If parsing fails, use the original value
                            last_modified_formatted = last_modified_iso
                    else:
                        # If it's already a datetime object, just format it
                        last_modified_formatted = (
                            last_modified_iso.strftime("%Y-%m-%d %H:%M:%S UTC")
                            if hasattr(last_modified_iso, "strftime")
                            else str(last_modified_iso)
                        )

                    row = {
                        "key": decoded_key,
                        "raw_key": raw_key,  # Keep the original key for S3 operations
                        "size_bytes": arrow_table["Size"][i].as_py(),
                        "last_modified": last_modified_formatted,
                    }
                    latest_objects.append(row)

                # Cache the formatted results
                self.cache_manager.cache_query_result(cache_key, latest_objects)

            # Add to metadata
            metadata[prefix]["latest_objects"] = latest_objects
            self.logger.info(
                f"Added {len(latest_objects)} latest objects to prefix {prefix}"
            )

        self.logger.info("Latest objects collection complete")
