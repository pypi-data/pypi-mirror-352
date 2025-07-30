import gzip
import io
import zipfile

import snappy
from gable.cli.helpers.data_asset_s3.logger import log_debug


class CompressionHandler:
    """Handles compressed S3 files by detecting and decompressing their content."""

    SUPPORTED_FILE_TYPES = {"json", "csv", "tsv", "parquet", "orc", "avro"}
    COMPRESSION_EXTENSIONS = {"gz", "snappy", "zip"}

    @staticmethod
    def is_compressed(file_key: str) -> bool:
        """Check if the file contains a known compression extension, in any order."""
        extensions = set(file_key.lower().split("."))
        is_compressed = any(
            ext in CompressionHandler.COMPRESSION_EXTENSIONS for ext in extensions
        )
        log_debug(f"Compression detected for '{file_key}': {is_compressed}")
        return is_compressed

    @staticmethod
    def has_external_compression(file_key: str) -> bool:
        """Detect if compression is applied externally via filename."""
        parts = file_key.lower().split(".")
        return any(ext in CompressionHandler.COMPRESSION_EXTENSIONS for ext in parts)

    @staticmethod
    def detect_compression_by_magic_bytes(data: bytes) -> str:
        if data.startswith(b"\x1f\x8b"):
            return "gz"
        elif data.startswith(b"PK\x03\x04"):
            return "zip"
        elif data.startswith(b"\xff\x06\x00\x00sNaPpY"):
            return "snappy"
        try:
            snappy.decompress(data)
            return "snappy"
        except Exception:
            pass

        return ""

    @staticmethod
    def detect_format_by_magic_bytes(data: bytes) -> str:
        if b"ORC" in data[-16:]:
            return ".orc"
        elif data.startswith(b"PAR1"):
            return ".parquet"
        elif data.startswith(b"Obj"):
            return ".avro"
        elif data.strip().startswith(b"{") or data.strip().startswith(b"["):
            return ".json"
        elif b"," in data[:1024]:
            return ".csv"
        elif b"\t" in data[:1024]:
            return ".tsv"
        return ""

    @staticmethod
    def get_original_format(file_key: str, file_content: bytes = b"") -> str:
        """
        Extracts the original format from filename, or falls back to content-based detection
        if the extension is missing or unsupported.
        """
        parts = file_key.lower().split(".")
        file_format = next(
            (p for p in parts if p in CompressionHandler.SUPPORTED_FILE_TYPES), None
        )
        if file_format:
            return f".{file_format}"

        if file_content:
            detected_format = CompressionHandler.detect_format_by_magic_bytes(
                file_content
            )
            if detected_format:
                return detected_format

        log_debug(f"Could not determine original file format from: {file_key}")
        return ""

    @staticmethod
    def decompress(file_key: str, file_content: bytes) -> tuple[io.BytesIO, str]:
        """
        Decompresses a file and returns a BytesIO object with decompressed data.
        Also returns the **original file format**.
        """
        try:
            log_debug(f"Starting decompression for: {file_key}")

            # First try to determine compression by extension
            if ".gz" in file_key:
                compression_type = "gz"
            elif ".snappy" in file_key:
                compression_type = "snappy"
            elif ".zip" in file_key:
                compression_type = "zip"
            else:
                # Fallback to magic byte detection
                compression_type = CompressionHandler.detect_compression_by_magic_bytes(
                    file_content
                )

            if compression_type == "gz":
                log_debug(f"Decompressing GZ file: {file_key}")
                decompressed_data = gzip.decompress(file_content)
                original_file_key = CompressionHandler.get_original_format(
                    file_key, decompressed_data
                )
                return io.BytesIO(decompressed_data), original_file_key

            elif compression_type == "snappy":
                log_debug(f"Decompressing Snappy file: {file_key}")
                decompressed_content = snappy.decompress(file_content)
                if isinstance(decompressed_content, str):
                    decompressed_content = decompressed_content.encode("utf-8")
                original_file_key = CompressionHandler.get_original_format(
                    file_key, decompressed_content
                )
                return io.BytesIO(decompressed_content), original_file_key

            elif compression_type == "zip":
                log_debug(f"Decompressing ZIP file: {file_key}")
                with zipfile.ZipFile(io.BytesIO(file_content), "r") as z:
                    file_names = z.namelist()
                    if not file_names:
                        raise ValueError("ZIP archive is empty.")
                    file_name = file_names[0]
                    log_debug(f"Extracting file '{file_name}' from ZIP archive.")
                    with z.open(file_name) as zip_file:
                        decompressed_data = zip_file.read()
                        original_file_key = CompressionHandler.get_original_format(
                            file_name, decompressed_data
                        )
                        return io.BytesIO(decompressed_data), original_file_key

            else:
                raise ValueError(f"Unsupported compression format for file: {file_key}")

        except zipfile.BadZipFile:
            log_debug(f"Failed to decompress ZIP file: {file_key} (Invalid ZIP format)")
            raise
        except snappy.UncompressError:
            log_debug(
                f"Failed to decompress Snappy file: {file_key} (Invalid Snappy format)"
            )
            raise
        except Exception as e:
            log_debug(f"Decompression failed for '{file_key}': {e}")
            raise
