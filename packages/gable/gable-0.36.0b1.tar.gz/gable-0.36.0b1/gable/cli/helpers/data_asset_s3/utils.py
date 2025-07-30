"""
Utility functions for the inventory report manager.
"""

import urllib.parse
from datetime import datetime
from typing import Optional


class Utils:
    """Utility functions used across the application"""

    @staticmethod
    def fully_decode(encoded_str: str) -> str:
        """
        Robustly decode a URL-encoded string, handling multiple encoding layers.
        """
        prev = encoded_str
        for _ in range(5):  # up to 5 passes if needed
            decoded = urllib.parse.unquote(prev)
            if decoded == prev:
                break
            prev = decoded
        return prev

    @staticmethod
    def format_timestamp(ts: Optional[str]) -> Optional[str]:
        """Format a timestamp string to a standard format"""
        if not ts:
            return None

        try:
            # Try with milliseconds
            dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            try:
                # Try without milliseconds
                dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")
            except Exception:
                return ts

        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
