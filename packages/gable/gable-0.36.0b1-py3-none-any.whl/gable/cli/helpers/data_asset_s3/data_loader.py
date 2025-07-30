"""
Data loading functionality for storage inventory files.
"""

import os
import re
from pathlib import Path
from typing import List, Optional

import duckdb
import pyarrow as pa

from .cache_manager import InventoryCacheManager
from .constants import StorageInventoryConstants


class InventoryDataLoader:
    """Handles loading data from storage inventory files"""

    def __init__(self, logger, inventory_dir=None):
        """
        Initialize the data loader.

        Args:
            logger: Logger instance
            inventory_dir: Directory where inventory reports are stored.
                           If None, uses the default location.
        """
        self.logger = logger
        self.inventory_dir = inventory_dir or self._get_default_inventory_dir()
        self.cache_manager = InventoryCacheManager()

    def _get_default_inventory_dir(self) -> str:
        """
        Determine the default inventory directory based on environment variables or Linux standards.

        Following Linux FHS (Filesystem Hierarchy Standard) conventions:
        - /var/lib/{app_name} for system-wide data
        - ~/.local/share/{app_name} for user data
        - Current working directory for backward compatibility with original implementation

        Returns:
            str: Path to the default inventory directory
        """
        # First check if an environment variable is set
        if "INVENTORY_REPORTS_DIR" in os.environ:
            return os.environ["INVENTORY_REPORTS_DIR"]

        # For system-wide installation
        system_dir = Path("/var/lib/inventory-reports")
        if system_dir.exists() and system_dir.is_dir():
            return str(system_dir)

        # For user installation
        user_dir = Path.home() / ".local" / "share" / "inventory-reports"
        if user_dir.exists() and user_dir.is_dir():
            return str(user_dir)

        # For backward compatibility with original implementation,
        # return the current working directory where the script is run
        cwd = os.getcwd()
        self.logger.info(f"Using current working directory for inventory files: {cwd}")
        return cwd

    def find_inventory_files(self) -> List[str]:
        """Find all inventory CSV.GZ files in the inventory directory"""
        # Check cache first
        cached_files = self.cache_manager.get_inventory_files(self.inventory_dir)
        if cached_files is not None:
            self.logger.info(
                "Using %d cached .csv.gz inventory files", len(cached_files)
            )
            return cached_files

        # If not in cache, find files and cache them
        inventory_path = Path(self.inventory_dir)
        csv_gz_files = [str(f) for f in inventory_path.glob("**/*.csv.gz")]

        if not csv_gz_files:
            self.logger.error(
                "No .csv.gz inventory files found in %s", self.inventory_dir
            )
        else:
            self.logger.info(
                "Discovered %d .csv.gz files for metadata summary.", len(csv_gz_files)
            )

        # Cache the results
        self.cache_manager.cache_inventory_files(self.inventory_dir, csv_gz_files)

        return csv_gz_files

    def build_duckdb_query(
        self, csv_gz_files: List[str], prefixes: Optional[List[str]] = None
    ) -> str:
        """Build a DuckDB query to extract data from inventory files"""
        # Currently using S3 inventory column structure - can be extended for other cloud providers
        columns_struct = (
            "{"
            + ", ".join(
                [
                    f"'{col}': 'VARCHAR'"
                    for col in StorageInventoryConstants.S3_INVENTORY_COLUMNS
                ]
            )
            + "}"
        )

        exclude_clause = " AND ".join(
            [f"NOT Key LIKE '%{x}%'" for x in StorageInventoryConstants.EXCLUDE_KEYS]
        )

        if prefixes is None or len(prefixes) == 0:
            prefix_clause = ""
        elif len(prefixes) == 1:
            prefix = prefixes[0]
            prefix_clause = f"Key LIKE '{prefix}/%' AND "
        else:
            pattern = "^(" + "|".join(re.escape(p) for p in prefixes) + ")/"
            prefix_clause = f"REGEXP_MATCHES(Key, '{pattern}') AND "

        query = f"""
            SELECT Key FROM read_csv_auto({csv_gz_files}, header=False, columns={columns_struct})
            WHERE {prefix_clause}{exclude_clause}
        """
        return query

    def load_keys(self, prefixes: Optional[List[str]] = None) -> List[str]:
        """Load keys from inventory files with optional prefix filtering"""
        csv_gz_files = self.find_inventory_files()
        if not csv_gz_files:
            return []

        query = self.build_duckdb_query(csv_gz_files, prefixes)
        keys = duckdb.query(query).fetchall()
        keys = [k[0] for k in keys]

        self.logger.info("Loaded %d keys for processing", len(keys))
        return keys

    def load_file_metadata(self, prefixes: Optional[List[str]] = None) -> pa.Table:
        """Load file metadata from inventory files as an Arrow table"""
        # Check cache first
        cached_records = self.cache_manager.get_file_records(self.inventory_dir)
        if cached_records is not None:
            self.logger.info(
                "Using cached file records with %d rows", cached_records.num_rows
            )
            return cached_records

        # If not in cache, load data and cache it
        csv_gz_files = self.find_inventory_files()
        if not csv_gz_files:
            return pa.table([])

        # Use glob pattern for DuckDB
        inventory_path = Path(self.inventory_dir)
        pattern = str(inventory_path / "**" / "*.csv.gz")
        exclude_sql = " AND ".join(
            [f"NOT Key LIKE '%{x}%'" for x in StorageInventoryConstants.EXCLUDE_KEYS]
        )

        query = f"""
            SELECT column01 AS Key,
                   CAST(column02 AS BIGINT) AS Size,
                   column03 AS LastModifiedDate
            FROM read_csv_auto('{pattern}', header=False, all_varchar=True)
            WHERE {exclude_sql}
        """

        if prefixes and len(prefixes) > 0:
            prefix_patterns = [f"Key LIKE '{p}/%'" for p in prefixes]
            query += f" AND ({' OR '.join(prefix_patterns)})"

        arrow_table = duckdb.query(query).arrow()
        self.logger.info("Loaded %d file records.", arrow_table.num_rows)

        # Cache the results
        self.cache_manager.cache_file_records(self.inventory_dir, arrow_table)

        return arrow_table

    def get_latest_objects(self, prefix: str, limit: int = 5) -> pa.Table:
        """
        Retrieve the latest N objects for a specific prefix based on LastModifiedDate.

        Args:
            prefix: The prefix to filter objects by
            limit: Maximum number of objects to return (default: 5)

        Returns:
            Arrow table containing the latest objects with their metadata
        """
        # Generate a cache key for this query
        cache_key = f"latest_objects_{prefix}_{limit}"
        cached_result = self.cache_manager.get_query_result(cache_key)
        if cached_result is not None:
            self.logger.info(f"Using cached latest objects for prefix '{prefix}'")
            return cached_result

        # If not in cache, query the data
        arrow_table = self.load_file_metadata([prefix])
        if arrow_table.num_rows == 0:
            self.logger.warning(f"No objects found for prefix: {prefix}")
            return pa.table([])

        # Use DuckDB to query the Arrow table directly for the latest objects
        query = f"""
            SELECT *
            FROM arrow_table
            WHERE Key LIKE '{prefix}/%'
            ORDER BY LastModifiedDate DESC
            LIMIT {limit}
        """

        try:
            conn = duckdb.connect(":memory:")
            conn.register("arrow_table", arrow_table)
            result = conn.execute(query).arrow()

            count = result.num_rows
            self.logger.info(f"Retrieved {count} latest objects for prefix '{prefix}'")

            # Cache the result
            self.cache_manager.cache_query_result(cache_key, result)

            return result
        except Exception as e:
            self.logger.error(
                f"Error retrieving latest objects for prefix '{prefix}': {str(e)}"
            )
            return pa.table([])
