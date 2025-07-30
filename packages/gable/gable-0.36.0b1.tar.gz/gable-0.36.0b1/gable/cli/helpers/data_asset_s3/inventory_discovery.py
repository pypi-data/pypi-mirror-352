"""
Dynamic S3 Inventory-Based Discovery Module
Author: Raed Alrfooh
Purpose: Uses modular inventory analysis components to replace pattern discovery and yield structured prefix-to-file mappings.
"""

import os
import re
import shutil
import tempfile
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import boto3

from .catalog_generator import InventoryCatalogGenerator
from .logging_manager import LoggingManager


def run_inventory_discovery(
    bucket: str,
    inventory_dir: str,
    recent_file_count: int = 5,
    include_prefix_list: Optional[List[str]] = None,
    exclude_prefix_list: Optional[List[str]] = None,
) -> Dict[str, List[Tuple[datetime, str]]]:
    """
    Run modular inventory report analysis and return prefix -> recent S3 object mappings.

    Args:
        bucket: Target S3 data bucket.
        inventory_dir: Can be a local directory or an S3 URI (e.g., s3://my-bucket/path).
        recent_file_count: Number of recent files to return per prefix.
        include_prefix_list: Optional filter for prefixes.
        exclude_prefix_list: Optional prefixes to exclude.

    Returns:
        Mapping of "prefix/{...}" -> list of (datetime, s3_url) for recent files.
    """
    logger = LoggingManager.setup()

    if inventory_dir.startswith("s3://"):
        s3 = boto3.client("s3")
        match = re.match(r"s3://([^/]+)/(.+)", inventory_dir)
        if not match:
            raise ValueError(f"Invalid S3 inventory path: {inventory_dir}")
        bucket_name, prefix = match.group(1), match.group(2)

        tmp_dir = tempfile.mkdtemp(prefix="inventory_download_")
        paginator = s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
            for obj in page.get("Contents", []):
                key = obj["Key"]  # type: ignore
                if not key.endswith(".csv.gz"):
                    continue
                dest_path = os.path.join(tmp_dir, os.path.basename(key))
                s3.download_file(bucket_name, key, dest_path)
        local_inventory_dir = tmp_dir
    else:
        local_inventory_dir = inventory_dir

    generator = InventoryCatalogGenerator(inventory_dir=local_inventory_dir)
    metadata = generator.generate_inventory_profile(
        prefixes=include_prefix_list,
        output_path="/tmp/full_report.json",
        partitions_only=False,
        filemeta_only=False,
        include_latest_objects=True,
        latest_objects_limit=recent_file_count,
    )

    pattern_to_urls: Dict[str, List[Tuple[datetime, str]]] = {}

    for prefix, values in metadata.items():
        if exclude_prefix_list and any(
            prefix.startswith(p) for p in exclude_prefix_list
        ):
            continue

        latest_objs = values.get("latest_objects", [])
        pattern = (
            f"{prefix}/{{...}}" if not prefix.endswith("/") else f"{prefix}{{...}}"
        )
        urls = []
        for obj in latest_objs:
            ts_str = obj["last_modified"].replace(" UTC", "")
            try:
                dt = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
            except Exception:
                logger.warning(f"Invalid timestamp format in: {obj['key']}")
                continue

            urls.append((dt, f"s3://{bucket}/{obj['key']}"))

        if urls:
            pattern_to_urls[pattern] = urls

    # Clean up temp directory if we downloaded from S3
    if inventory_dir.startswith("s3://"):
        shutil.rmtree(local_inventory_dir)

    return pattern_to_urls
