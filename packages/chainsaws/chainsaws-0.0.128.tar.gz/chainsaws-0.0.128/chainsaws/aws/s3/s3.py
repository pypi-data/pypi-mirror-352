import io
import json
import logging
import fnmatch
import hashlib
from pathlib import Path
from typing import Any, BinaryIO, Optional, Callable, Union, List, Generator, TypeVar, Literal
from urllib.parse import urljoin
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor, as_completed

from chainsaws.aws.s3._s3_internal import S3
from chainsaws.aws.s3.s3_models import (
    BucketConfig,
    BulkUploadItem,
    BulkUploadResult,
    ContentType,
    CopyObjectResult,
    FileUploadConfig,
    FileUploadResult,
    ObjectListConfig,
    PresignedUrlConfig,
    S3APIConfig,
    S3Object,
    S3SelectCSVConfig,
    S3SelectFormat,
    S3SelectJSONType,
    SelectObjectConfig,
    UploadConfig,
    DownloadConfig,
    BatchOperationConfig,
    BulkDownloadResult,
    ObjectTags,
    DirectoryUploadResult,
    DirectorySyncResult,
    WebsiteConfig,
)
from chainsaws.aws.s3.s3_exception import (
    InvalidObjectKeyError,
    S3BucketPolicyUpdateError,
    S3BucketPolicyGetError,
    S3LambdaPermissionAddError,
    S3LambdaNotificationAddError,
    S3LambdaNotificationRemoveError,
    S3MultipartUploadError,
    S3StreamingError,
    S3WebsiteConfigurationError,
    S3WebsiteConfigurationGetError,
    S3WebsiteConfigurationDeleteError,
)
from chainsaws.aws.shared import session
from .stream_manager import StreamManager

logger = logging.getLogger(__name__)

T = TypeVar('T')


class S3API:
    """High-level S3 API for AWS S3 operations."""

    def __init__(self, bucket_name: str, config: Optional[S3APIConfig] = None) -> None:
        """Initialize S3 client.

        Args:
            bucket_name: Target bucket name
            config: Optional S3 configuration
        """
        self.bucket_name = bucket_name
        self.config = config or S3APIConfig()
        self.boto3_session = session.get_boto_session(
            self.config.credentials if self.config.credentials else None,
        )
        self.s3 = S3(
            boto3_session=self.boto3_session,
            bucket_name=bucket_name,
            config=config,
        )
        self.stream = StreamManager(self)  # Initialize StreamManager

    def init_s3_bucket(self) -> None:
        """Initialize S3 bucket."""
        bucket_config = BucketConfig(
            bucket_name=self.bucket_name, acl=self.config.acl, use_accelerate=self.config.use_accelerate)
        return self.s3.init_bucket(config=bucket_config)

    # Upload Operations
    def upload_file(
        self,
        object_key: str,
        file_bytes: Union[bytes, BinaryIO],
        config: Optional[UploadConfig] = None,
    ) -> FileUploadResult:
        """Upload a file to S3.

        Args:
            object_key: Target object key
            file_bytes: File content or file-like object
            config: Upload configuration

        Returns:
            FileUploadResult: Upload result with URL
        """
        config = config or UploadConfig()
        upload_config = FileUploadConfig(
            bucket_name=self.bucket_name,
            file_name=object_key,
            content_type=config.content_type,
        )

        self.s3.upload_file(upload_config, file_bytes)

        base_url = self._get_base_url(
            use_accelerate=self.config.use_accelerate)
        return {
            "url": urljoin(base_url, object_key),
            "object_key": object_key,
        }

    def upload_binary(self, file_name: str, binary: bytes) -> None:
        """Upload binary data to S3.

        Args:
            file_name: Target file name
            binary: Binary data
        """
        self.s3.upload_binary(file_name, binary)

    def _get_base_url(self, bucket_name: Optional[str] = None, use_accelerate: bool = False) -> str:
        """Generate base URL for S3 bucket.

        Args:
            bucket_name: Optional bucket name (defaults to self.bucket_name)
            use_accelerate: Whether to use S3 Transfer Acceleration

        Returns:
            str: Base URL for the S3 bucket

        """
        target_bucket = bucket_name or self.bucket_name

        if use_accelerate:
            return f"https://{target_bucket}.s3-accelerate.amazonaws.com/"

        return f"https://{target_bucket}.s3.{self.s3.region}.amazonaws.com/"

    def upload_items_for_select(self, file_name: str, item_list: list[dict[str, Any]]) -> None:
        """Upload JSON items for S3 Select queries."""
        if not all(isinstance(item, dict) for item in enumerate(item_list)):
            msg = "All items must be dictionaries"
            raise InvalidObjectKeyError(msg)

        json_string = "\n".join(json.dumps(item) for item in item_list)
        return self.upload_binary(file_name, json_string.encode("utf-8"))

    # TODO: Make as typed
    def get_object(self, object_key: str) -> dict[str, Any]:
        """Get an object from S3.

        Args:
            object_key: The key of the object to get

        Returns:
            dict: The response from S3 containing the object data and metadata
        """
        return self.s3.get_object(object_key)

    def upload_large_file(
        self,
        object_key: str,
        file_bytes: bytes | BinaryIO,
        content_type: Optional[ContentType] = None,
        part_size: int = 5 * 1024 * 1024,  # 5MB
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> FileUploadResult:
        """Upload a large file using multipart upload.

        Args:
            object_key: The key to store the object under
            file_bytes: File data as bytes or file-like object
            content_type: Optional content type
            part_size: Size of each part in bytes (minimum 5MB)
            progress_callback: Optional callback function to monitor progress.
                            Takes (bytes_uploaded, total_bytes) as arguments.

        Returns:
            FileUploadResult: An object containing the public URL and the object key of the uploaded file

        Raises:
            S3MultipartUploadError: If the multipart upload fails
            InvalidObjectKeyError: If the object key is invalid
            InvalidFileUploadError: If the file upload configuration is invalid
        """
        if content_type is None:
            extension = object_key.split(".")[-1] if "." in object_key else ""
            content_type = ContentType.from_extension(extension)

        if isinstance(file_bytes, bytes):
            file_bytes = io.BytesIO(file_bytes)

        # Get total file size
        file_bytes.seek(0, io.SEEK_END)
        total_size = file_bytes.tell()
        file_bytes.seek(0)

        # If file is smaller than part_size, use regular upload
        if total_size <= part_size:
            return self.upload_file_and_return_url(
                file_bytes=file_bytes.read(),
                extension=object_key.split(
                    ".")[-1] if "." in object_key else None,
                object_key=object_key,
                content_type=content_type,
            )

        try:
            upload_id = self.s3.create_multipart_upload(
                object_key=object_key,
                content_type=content_type,
            )

            parts = []
            part_number = 1
            bytes_uploaded = 0

            while True:
                data = file_bytes.read(part_size)
                if not data:
                    break

                part = self.s3.upload_part(
                    object_key=object_key,
                    upload_id=upload_id,
                    part_number=part_number,
                    body=data,
                )
                parts.append({
                    "PartNumber": part_number,
                    "ETag": part["ETag"],
                })

                bytes_uploaded += len(data)
                if progress_callback:
                    progress_callback(bytes_uploaded, total_size)

                part_number += 1

            self.s3.complete_multipart_upload(
                object_key=object_key,
                upload_id=upload_id,
                parts=parts,
            )

            base_url = self._get_base_url(
                use_accelerate=self.config.use_accelerate)

            return FileUploadResult(
                url=urljoin(base_url, object_key),
                object_key=object_key,
            )

        except Exception as ex:
            logger.exception(f"Failed to upload large file: {ex!s}")
            if "upload_id" in locals():
                try:
                    self.s3.abort_multipart_upload(
                        object_key=object_key,
                        upload_id=upload_id,
                    )
                except Exception as abort_ex:
                    logger.error(
                        f"Failed to abort multipart upload: {abort_ex!s}")

            raise S3MultipartUploadError(
                object_key=object_key,
                upload_id=upload_id if "upload_id" in locals() else "N/A",
                reason=str(ex)
            ) from ex

    # Download Operations
    def download_file(
        self,
        object_key: str,
        file_path: Union[str, Path],
        config: Optional[DownloadConfig] = None,
    ) -> None:
        """Download a file from S3.

        Args:
            object_key: Source object key
            file_path: Target file path
            config: Download configuration
        """
        config = config or DownloadConfig()
        self.s3.download_file(
            object_key=object_key,
            file_path=file_path,
            max_retries=config.max_retries,
            retry_delay=config.retry_delay,
            progress_callback=config.progress_callback,
        )

    def stream_object(
        self,
        object_key: str,
        chunk_size: int = 8192,
    ) -> Generator[bytes, None, None]:
        """Stream an object from S3 in chunks.

        Args:
            object_key: The key of the object to stream
            chunk_size: Size of each chunk in bytes

        Yields:
            bytes: Chunks of the object data

        Raises:
            S3StreamingError: If streaming fails
        """
        try:
            response = self.s3.get_object(object_key)
            stream = response["Body"]

            while True:
                chunk = stream.read(chunk_size)
                if not chunk:
                    break
                yield chunk

        except Exception as ex:
            raise S3StreamingError(object_key=object_key,
                                   reason=str(ex)) from ex

    # Batch Operations
    @contextmanager
    def batch_operation(self, config: Optional[BatchOperationConfig] = None) -> Generator["S3API", None, None]:
        """Context manager for batch operations.

        Args:
            config: Batch operation configuration

        Yields:
            S3API: Self for batch operations
        """
        config = config or BatchOperationConfig()
        try:
            yield self
        finally:
            # Cleanup after batch operations
            pass

    def bulk_upload(
        self,
        items: List[BulkUploadItem],
        config: Optional[BatchOperationConfig] = None,
    ) -> BulkUploadResult:
        """Upload multiple files in parallel.

        Args:
            items: List of items to upload
            config: Batch operation configuration

        Returns:
            BulkUploadResult: Upload results
        """

        config = config or BatchOperationConfig()
        max_workers = config.max_workers or min(32, len(items))
        results = {"successful": [], "failed": []}

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_item = {
                executor.submit(
                    self.upload_file,
                    item.object_key,
                    item.data,
                    UploadConfig(
                        content_type=item.content_type,
                        part_size=config.chunk_size,
                        progress_callback=lambda current, total: config.progress_callback(
                            item.object_key, current, total) if config.progress_callback else None
                    )
                ): item
                for item in items
            }

            for future in as_completed(future_to_item):
                item = future_to_item[future]
                try:
                    result = future.result()
                    results["successful"].append({
                        "object_key": item.object_key,
                        "url": result["url"]
                    })
                except Exception as e:
                    results["failed"].append({
                        "object_key": item.object_key,
                        "error": str(e)
                    })

        return results

    def download_multiple_files(
        self,
        object_keys: List[str],
        output_dir: Union[str, Path],
        config: Optional[BatchOperationConfig] = None,
    ) -> BulkDownloadResult:
        """Download multiple files in parallel.

        Args:
            object_keys: List of object keys to download
            output_dir: Target directory
            config: Batch operation configuration

        Returns:
            BulkDownloadResult: Download results with successful and failed downloads
        """
        config = config or BatchOperationConfig()
        max_workers = config.max_workers or min(32, len(object_keys))
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        results: BulkDownloadResult = {"successful": [], "failed": []}

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_key = {
                executor.submit(
                    self.download_file,
                    object_key,
                    output_dir / Path(object_key).name,
                    DownloadConfig(
                        chunk_size=config.chunk_size,
                        progress_callback=lambda current, total: config.progress_callback(
                            object_key, current, total) if config.progress_callback else None
                    )
                ): object_key
                for object_key in object_keys
            }

            for future in as_completed(future_to_key):
                object_key = future_to_key[future]
                local_path = str(output_dir / Path(object_key).name)
                try:
                    future.result()
                    results["successful"].append({
                        "object_key": object_key,
                        "local_path": local_path,
                        "success": True,
                        "error": None
                    })
                except Exception as e:
                    logger.error(f"Failed to download {object_key}: {e}")
                    results["failed"].append({
                        "object_key": object_key,
                        "local_path": local_path,
                        "success": False,
                        "error": str(e)
                    })

        return results

    def copy_object(
        self,
        source_key: str,
        dest_key: str,
        dest_bucket: Optional[str] = None,
        acl: str = "private",
    ) -> CopyObjectResult:
        """Copy an object within S3.

        Args:
            source_key: Source object key
            dest_key: Destination object key
            dest_bucket: Optional destination bucket
            acl: Object ACL

        Returns:
            CopyObjectResult: Copy operation result
        """
        return self.s3.copy_object(
            source_key=source_key,
            dest_key=dest_key,
            dest_bucket=dest_bucket,
            acl=acl,
        )

    def enable_transfer_acceleration(self) -> bool:
        """Enable transfer acceleration for the bucket.

        Returns:
            bool: True if successful
        """
        try:
            self.s3.put_bucket_accelerate_configuration('Enabled')
            return True
        except Exception as e:
            logger.error(f"Failed to enable transfer acceleration: {e}")
            return False

    # Management Operations
    def delete_object(self, object_key: str) -> bool:
        """Delete an object from S3.

        Args:
            object_key: Object key to delete

        Returns:
            bool: True if successful
        """
        return self.s3.delete_object(object_key)

    def delete_objects(self, object_keys: List[str]) -> bool:
        """Delete multiple objects from S3.

        Args:
            object_keys: List of object keys to delete

        Returns:
            bool: True if successful
        """
        return self.s3.delete_objects(object_keys)

    # Utility Operations
    def check_key_exists(self, object_key: str) -> bool:
        """Check if an object exists.

        Args:
            object_key: Object key to check

        Returns:
            bool: True if exists
        """
        return self.s3.check_key_exists(object_key)

    def get_url_by_object_key(self, object_key: str, use_accelerate: bool = False) -> Optional[str]:
        """Get URL for an object.

        Args:
            object_key: Object key
            use_accelerate: Whether to use transfer acceleration

        Returns:
            Optional[str]: Object URL if exists
        """
        return self._get_base_url(use_accelerate=use_accelerate) + object_key if object_key else None

    # Performance Operations
    def optimize_transfer_settings(self) -> None:
        """Optimize transfer settings for better performance."""
        if self._check_transfer_acceleration_eligibility():
            self.enable_transfer_acceleration()
    # Context Managers

    @contextmanager
    def upload_session(self, config: Optional[UploadConfig] = None) -> Generator["S3API", None, None]:
        """Context manager for upload operations.

        Args:
            config: Upload configuration

        Yields:
            S3API: Self for upload operations
        """
        config = config or UploadConfig()
        try:
            yield self
        finally:
            # Cleanup if needed
            pass

    @contextmanager
    def download_session(self, config: Optional[DownloadConfig] = None) -> Generator["S3API", None, None]:
        """Context manager for download operations.

        Args:
            config: Download configuration

        Yields:
            S3API: Self for download operations
        """
        config = config or DownloadConfig()
        try:
            yield self
        finally:
            # Cleanup if needed
            pass

    def generate_object_keys(
        self,
        prefix: str = '',
        start_after: Optional[str] = None,
        limit: int = 1000,
    ) -> Generator[S3Object, None, None]:
        """Generate object keys with pagination."""
        continuation_token = None

        while True:
            list_config = ObjectListConfig(
                prefix=prefix,
                continuation_token=continuation_token,
                start_after=start_after,
                limit=limit,
            )

            response = self.s3.list_objects_v2(list_config)

            yield from response.get("Contents", [])

            continuation_token = response.get("NextContinuationToken")
            if not continuation_token:
                break

    def select(self, object_key: str, query: str) -> dict[str, Any]:
        """Execute S3 Select query."""
        select_config = SelectObjectConfig(
            bucket_name=self.bucket_name,
            object_key=object_key,
            query=query,
            input_serialization={"JSON": {"Type": "DOCUMENT"}},
            output_serialization={"JSON": {}},
        )

        return self.s3.select_object_content(select_config)

    def create_presigned_url_put_object(
        self,
        object_key: str,
        content_type: Optional[str] = None,
        acl: Optional[str] = None,
        expiration: Optional[int] = None,
    ) -> str:
        """Generate presigned URL for PUT operation."""

        if not content_type:
            extension = object_key.split(".")[-1] if "." in object_key else ""
            content_type = ContentType.from_extension(extension)

        config = PresignedUrlConfig(
            bucket_name=self.bucket_name,
            object_name=object_key,
            client_method="put_object",
            content_type=content_type,
            acl=acl or "private",
            expiration=expiration or 3600,
        )
        return self.s3.create_presigned_url(config)

    def create_presigned_url_get_object(
        self,
        object_key: str,
        expiration: int = 3600,
    ) -> str:
        """Generate presigned URL for GET operation."""
        config = PresignedUrlConfig(
            bucket_name=self.bucket_name,
            object_name=object_key,
            client_method="get_object",
            expiration=expiration,
        )
        return self.s3.create_presigned_url(config)

    def get_object_tags(self, object_key: str) -> ObjectTags:
        """Get tags for an object."""
        return self.s3.get_object_tags(object_key=object_key)

    def put_object_tags(self, object_key: str, tags: dict[str, str]) -> dict:
        """Set tags for an object."""
        return self.s3.put_object_tags(object_key=object_key, tags=tags)

    def get_object_metadata(
        self,
        object_key: str,
        version_id: Optional[str] = None,
    ) -> dict:
        """Get detailed metadata for an object."""
        return self.s3.get_object_metadata(
            object_key=object_key,
            version_id=version_id,
        )

    def put_bucket_policy(self, policy: dict[str, Any]) -> None:
        """Put/Update bucket policy.

        Args:
            policy: Dictionary containing the bucket policy

        Example:
            ```python
            s3.put_bucket_policy({
                "Version": "2012-10-17",
                "Statement": [{
                    "Sid": "AllowCloudFrontServicePrincipal",
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "cloudfront.amazonaws.com"
                    },
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{bucket_name}/*",
                    "Condition": {
                        "StringEquals": {
                            "AWS:SourceArn": "arn:aws:cloudfront::ACCOUNT_ID:distribution/*"
                        }
                    }
                }]
            })
            ```

        Raises:
            Exception: If policy update fails

        """
        try:
            return self.s3.put_bucket_policy(policy=json.dumps(policy))
        except Exception as e:
            msg = f"Failed to put bucket policy: {e!s}"
            logger.exception(msg)
            raise S3BucketPolicyUpdateError(
                bucket_name=self.bucket_name,
                reason=msg
            ) from e

    def get_bucket_policy(self) -> dict[str, Any]:
        """Get current bucket policy.

        Returns:
            Dict containing the bucket policy. Empty dict if no policy exists.

        Raises:
            Exception: If policy retrieval fails

        """
        try:
            policy = self.s3.get_bucket_policy(self.bucket_name)
            return json.loads(policy.get("Policy", "{}"))
        except Exception as e:
            logger.exception(f"Failed to get bucket policy: {e!s}")
            raise S3BucketPolicyGetError from e

    def add_lambda_notification(
        self,
        lambda_function_arn: str,
        events: Optional[list[str]] = None,
        prefix: Optional[str] = None,
        suffix: Optional[str] = None,
        id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Add Lambda function notification configuration to S3 bucket.

        Args:
            lambda_function_arn: Lambda function ARN
            events: List of S3 events to trigger Lambda. Defaults to ['s3:ObjectCreated:*']
            prefix: Optional key prefix filter
            suffix: Optional key suffix filter
            id: Optional configuration ID

        Example:
            ```python
            # Trigger Lambda when PNG files are uploaded to 'images/' prefix
            s3.add_lambda_notification(
                lambda_function_arn="arn:aws:lambda:region:account:function:image-processor",
                events=['s3:ObjectCreated:Put'],
                prefix='images/',
                suffix='.png'
            )
            ```

        """
        from chainsaws.aws.lambda_client.lambda_client import LambdaAPI

        if not events:
            events = ["s3:ObjectCreated:*"]

        if not id:
            import uuid
            id = f"LambdaTrigger-{str(uuid.uuid4())[:8]}"

        try:
            lambda_api = LambdaAPI(self.config)
            try:
                lambda_api.add_permission(
                    function_name=lambda_function_arn,
                    statement_id=f"S3Trigger-{id}",
                    action="lambda:InvokeFunction",
                    principal="s3.amazonaws.com",
                    source_arn=f"arn:aws:s3:::{self.bucket_name}",
                )
            except Exception as e:
                if "ResourceConflictException" not in str(e):
                    raise S3LambdaPermissionAddError from e

            config = {
                "LambdaFunctionArn": lambda_function_arn,
                "Events": events,
            }

            if prefix or suffix:
                filter_rules = []
                if prefix:
                    filter_rules.append({"Name": "prefix", "Value": prefix})
                if suffix:
                    filter_rules.append({"Name": "suffix", "Value": suffix})
                config["Filter"] = {"Key": {"FilterRules": filter_rules}}

            return self.s3.put_bucket_notification_configuration(
                config={id: config},
            )

        except Exception as e:
            logger.exception(f"Failed to add Lambda notification: {e!s}")
            raise S3LambdaNotificationAddError from e

    def remove_lambda_notification(
        self,
        id: str,
        lambda_function_arn: Optional[str] = None,
        remove_permission: bool = True,
    ) -> None:
        """Remove Lambda function notification configuration.

        Args:
            id: Configuration ID to remove
            lambda_function_arn: Optional Lambda ARN (needed for permission removal)
            remove_permission: Whether to remove Lambda permission

        Example:
            ```python
            s3.remove_lambda_notification(
                id="LambdaTrigger-12345678",
                lambda_function_arn="arn:aws:lambda:region:account:function:image-processor"
            )
            ```

        """
        try:
            # Get current configuration
            current_config = self.s3.get_bucket_notification_configuration()

            # Remove specified configuration
            if id in current_config:
                del current_config[id]
                self.s3.put_bucket_notification_configuration(
                    config=current_config,
                )

            # Remove Lambda permission if requested
            if remove_permission and lambda_function_arn:
                from chainsaws.aws.lambda_client.lambda_client import LambdaAPI
                lambda_api = LambdaAPI(self.config)
                try:
                    lambda_api.remove_permission(
                        function_name=lambda_function_arn,
                        statement_id=f"S3Trigger-{id}",
                    )
                except Exception as e:
                    if "ResourceNotFoundException" not in str(e):
                        logger.warning(
                            f"Failed to remove Lambda permission: {e!s}")

        except Exception as e:
            logger.exception(f"Failed to remove Lambda notification: {e!s}")
            raise S3LambdaNotificationRemoveError from e

    def select_query(
        self,
        object_key: str,
        query: str,
        input_format: S3SelectFormat = S3SelectFormat.JSON,
        output_format: S3SelectFormat = S3SelectFormat.JSON,
        json_type: S3SelectJSONType = S3SelectJSONType.LINES,
        compression_type: Optional[str] = None,
        csv_input_config: Optional[S3SelectCSVConfig] = None,
        csv_output_config: Optional[S3SelectCSVConfig] = None,
        max_rows: Optional[int] = None,
    ) -> Generator[dict[str, Any], None, None]:
        """Execute S3 Select query with advanced options.

        Args:
            object_key: S3 object key
            query: SQL query to execute
            input_format: Input format (JSON, CSV, PARQUET)
            output_format: Output format (JSON, CSV)
            json_type: JSON type for input (DOCUMENT or LINES)
            compression_type: Input compression type
            csv_input_config: CSV input configuration
            csv_output_config: CSV output configuration
            max_rows: Maximum number of rows to return

        Yields:
            Query results as dictionaries

        Example:
            ```python
            # Query JSON Lines
            results = s3.select_query(
                object_key="data/logs.jsonl",
                query="SELECT * FROM s3object s WHERE s.level = 'ERROR'",
                input_format=S3SelectFormat.JSON,
                json_type=S3SelectJSONType.LINES
            )

            # Query CSV with custom configuration
            results = s3.select_query(
                object_key="data/users.csv",
                query="SELECT name, email FROM s3object WHERE age > 25",
                input_format=S3SelectFormat.CSV,
                csv_input_config=S3SelectCSVConfig(
                    file_header_info="USE",
                    delimiter=","
                )
            )
            ```

        """
        input_serialization = {}
        output_serialization = {}

        # Configure input serialization
        if input_format == S3SelectFormat.JSON:
            input_serialization["JSON"] = {"Type": json_type}
        elif input_format == S3SelectFormat.CSV:
            csv_config = csv_input_config or S3SelectCSVConfig()
            input_serialization["CSV"] = csv_config.to_dict(
                exclude_none=True)
        elif input_format == S3SelectFormat.PARQUET:
            input_serialization["Parquet"] = {}

        # Configure output serialization
        if output_format == S3SelectFormat.JSON:
            output_serialization["JSON"] = {}
        elif output_format == S3SelectFormat.CSV:
            csv_config = csv_output_config or S3SelectCSVConfig()
            output_serialization["CSV"] = csv_config.to_dict(
                exclude_none=True)

        if compression_type:
            input_serialization["CompressionType"] = compression_type

        select_config = SelectObjectConfig(
            bucket_name=self.bucket_name,
            object_key=object_key,
            query=query,
            input_serialization=input_serialization,
            output_serialization=output_serialization,
        )

        row_count = 0
        for record in self.s3.select_object_content(select_config):
            if max_rows and row_count >= max_rows:
                break
            yield record
            row_count += 1

    def upload_jsonlines(
        self,
        object_key: str,
        items: list[dict[str, Any]],
        compression: Optional[Literal["gzip", "bzip2"]] = None,
    ) -> str:
        """Upload items as JSON Lines format for efficient S3 Select queries.

        Args:
            object_key: Target object key
            items: List of dictionaries to upload
            compression: Optional compression (gzip, bzip2)

        Returns:
            URL of uploaded object

        Example:
            ```python
            url = s3.upload_jsonlines(
                "data/logs.jsonl",
                [
                    {"timestamp": "2023-01-01", "level": "INFO", "message": "Started"},
                    {"timestamp": "2023-01-01", "level": "ERROR", "message": "Failed"}
                ],
                compression="gzip"
            )
            ```

        """
        if not all(isinstance(item, dict) for item in items):
            msg = "All items must be dictionaries"
            raise ValueError(msg)

        # Convert to JSON Lines format
        json_lines = "\n".join(json.dumps(item) for item in items)
        data = json_lines.encode("utf-8")

        # Apply compression if requested
        if compression:
            if compression.lower() == "gzip":
                import gzip
                data = gzip.compress(data)
            elif compression.lower() == "bzip2":
                import bz2
                data = bz2.compress(data)
            else:
                msg = "Unsupported compression format"
                raise ValueError(msg)

        # Upload with appropriate content type
        content_type = "application/x-jsonlines"
        if compression:
            content_type += f"+{compression}"

        return self.upload_binary(object_key, data, content_type=content_type)

    def make_bucket_public(self) -> None:
        """Make the S3 bucket publicly accessible.
        This method:
        1. Disables bucket's public access block settings
        2. Updates the bucket policy to allow public access.

        Example:
            ```python
            s3 = S3API(bucket_name="my-bucket")
            s3.make_bucket_public()
            ```

        Raises:
            Exception: If any step of making the bucket public fails

        """
        try:
            logger.info(f"Disabling public access block for bucket '{
                        self.bucket_name}'")
            self.s3.put_public_access_block(
                public_access_block_configuration={
                    "BlockPublicAcls": False,
                    "IgnorePublicAcls": False,
                    "BlockPublicPolicy": False,
                    "RestrictPublicBuckets": False,
                },
            )

            # Wait for public access block configuration to be applied
            self.s3.wait_for_public_access_block_configuration()

            # Update bucket policy to allow public read access
            logger.info("Updating bucket policy to allow public access")
            public_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "PublicReadGetObject",
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": "s3:GetObject",
                        "Resource": f"arn:aws:s3:::{self.bucket_name}/*",
                    },
                ],
            }
            self.s3.update_bucket_policy(public_policy)

            logger.info(f"Successfully made bucket '{
                        self.bucket_name}' public")
        except Exception as e:
            logger.exception(f"Failed to make bucket public: {e!s}")
            raise

    def make_bucket_private(self) -> None:
        """Make the S3 bucket private.
        This method:
        1. Removes any bucket policy
        2. Enables bucket's public access block settings.

        Example:
            ```python
            s3 = S3API(bucket_name="my-bucket")
            s3.make_bucket_private()
            ```

        Raises:
            Exception: If any step of making the bucket private fails

        """
        try:
            logger.info(f"Removing bucket policy from '{self.bucket_name}'")
            self.s3.delete_bucket_policy(self.bucket_name)

            logger.info(f"Enabling public access block for bucket '{
                        self.bucket_name}'")
            self.s3.put_public_access_block(
                self.bucket_name,
                {
                    "BlockPublicAcls": True,
                    "IgnorePublicAcls": True,
                    "BlockPublicPolicy": True,
                    "RestrictPublicBuckets": True,
                },
            )

            logger.info(f"Successfully made bucket '{
                        self.bucket_name}' private")
        except Exception as e:
            logger.exception(f"Failed to make bucket private: {e!s}")
            raise

    def _check_transfer_acceleration_eligibility(self) -> bool:
        """Check if the bucket is eligible for S3 Transfer Acceleration.

        Returns:
            bool: True if the bucket is eligible for acceleration
        """
        try:
            response = self.s3.get_bucket_accelerate_configuration()
            current_status = response.get('Status', 'Suspended')
            return current_status != 'Suspended'
        except Exception as ex:
            logger.warning(
                f"Failed to check transfer acceleration status: {ex!s}")
            return False

    def upload_directory(
        self,
        local_dir: Union[str, Path],
        prefix: str = "",
        exclude_patterns: Optional[List[str]] = None,
    ) -> DirectoryUploadResult:
        """Upload an entire local directory to S3.

        Args:
            local_dir: Local directory path
            prefix: S3 prefix to prepend to uploaded files
            exclude_patterns: List of glob patterns to exclude

        Returns:
            DirectoryUploadResult: Upload results with successful and failed uploads
        """
        local_dir = Path(local_dir)
        if not local_dir.is_dir():
            raise ValueError(f"'{local_dir}' is not a directory")

        exclude_patterns = exclude_patterns or []
        results: DirectoryUploadResult = {"successful": [], "failed": []}

        for file_path in local_dir.rglob("*"):
            if not file_path.is_file():
                continue

            relative_path = str(file_path.relative_to(local_dir))
            if any(fnmatch.fnmatch(relative_path, pattern) for pattern in exclude_patterns):
                continue

            object_key = f"{prefix.rstrip(
                '/')}/{relative_path}" if prefix else relative_path

            try:
                with open(file_path, "rb") as f:
                    result = self.upload_file(
                        object_key=object_key,
                        file_bytes=f,
                    )
                    results["successful"].append(result)
            except Exception as e:
                results["failed"].append({
                    relative_path: str(e)
                })

        return results

    def download_directory(
        self,
        prefix: str,
        local_dir: Union[str, Path],
        include_patterns: Optional[List[str]] = None,
    ) -> None:
        """Download all files under an S3 prefix to a local directory.

        Args:
            prefix: S3 prefix to download from
            local_dir: Local directory to download to
            include_patterns: List of glob patterns to include
        """
        local_dir = Path(local_dir)
        local_dir.mkdir(parents=True, exist_ok=True)

        include_patterns = include_patterns or ["*"]

        # List all objects
        for obj in self.generate_object_keys(prefix=prefix):
            # Check pattern matching
            relative_key = obj["Key"][len(prefix):].lstrip("/")
            if not any(fnmatch.fnmatch(relative_key, pattern) for pattern in include_patterns):
                continue

            # Create download path
            download_path = local_dir / relative_key
            download_path.parent.mkdir(parents=True, exist_ok=True)

            # Download file
            self.download_file(
                object_key=obj["Key"],
                file_path=download_path,
            )

    def sync_directory(
        self,
        local_dir: Union[str, Path],
        prefix: str = "",
        delete: bool = False,
    ) -> DirectorySyncResult:
        """Sync a local directory with S3 (similar to aws s3 sync).

        Args:
            local_dir: Local directory to sync
            prefix: S3 prefix to sync with
            delete: Whether to delete files that exist in the destination but not in the source

        Returns:
            DirectorySyncResult: Sync results with uploaded, updated, deleted, and failed files
        """
        local_dir = Path(local_dir)
        if not local_dir.is_dir():
            raise ValueError(f"'{local_dir}' is not a directory")

        results: DirectorySyncResult = {
            "uploaded": [],
            "updated": [],
            "deleted": [],
            "failed": []
        }

        local_files = {
            str(f.relative_to(local_dir)): f
            for f in local_dir.rglob("*")
            if f.is_file()
        }

        s3_objects = {
            obj["Key"][len(prefix):].lstrip("/"): obj
            for obj in self.generate_object_keys(prefix=prefix)
        }

        for relative_path, local_file in local_files.items():
            object_key = f"{prefix.rstrip(
                '/')}/{relative_path}" if prefix else relative_path

            try:
                if relative_path not in s3_objects:
                    with open(local_file, "rb") as f:
                        self.upload_file(object_key=object_key, file_bytes=f)
                    results["uploaded"].append(relative_path)
                else:
                    with open(local_file, "rb") as f:
                        local_md5 = hashlib.md5(f.read()).hexdigest()
                    s3_etag = s3_objects[relative_path]["ETag"].strip('"')

                    if local_md5 != s3_etag:
                        with open(local_file, "rb") as f:
                            self.upload_file(
                                object_key=object_key, file_bytes=f)
                        results["updated"].append(relative_path)
            except Exception as e:
                results["failed"].append({relative_path: str(e)})

        if delete:
            for relative_path in s3_objects:
                if relative_path not in local_files:
                    object_key = f"{prefix.rstrip(
                        '/')}/{relative_path}" if prefix else relative_path
                    try:
                        self.delete_object(object_key)
                        results["deleted"].append(relative_path)
                    except Exception as e:
                        results["failed"].append({relative_path: str(e)})

        return results

    def find_objects(
        self,
        pattern: str = "*",
        recursive: bool = True,
        max_items: Optional[int] = None,
    ) -> Generator[S3Object, None, None]:
        """Find objects in S3 using glob patterns.

        Args:
            pattern: Glob pattern to match against object keys
            recursive: Whether to search recursively
            max_items: Maximum number of items to return

        Yields:
            S3Object: Matching S3 objects
        """
        import fnmatch
        from pathlib import PurePath

        # 패턴을 prefix와 실제 패턴으로 분리
        pattern_path = PurePath(pattern)
        if pattern_path.is_absolute():
            pattern = str(pattern_path.relative_to(pattern_path.root))

        prefix = str(pattern_path.parent) if str(
            pattern_path.parent) != "." else ""
        name_pattern = pattern_path.name

        # 재귀 검색이 아닌 경우 패턴 조정
        if not recursive and "**" not in pattern:
            name_pattern = f"*/{name_pattern}" if prefix else name_pattern

        count = 0
        for obj in self.generate_object_keys(prefix=prefix):
            if max_items and count >= max_items:
                break

            # 패턴 매칭
            relative_key = obj["Key"][len(prefix):].lstrip(
                "/") if prefix else obj["Key"]
            if fnmatch.fnmatch(relative_key, name_pattern):
                count += 1
                yield obj

    def get_website_configuration(self) -> WebsiteConfig:
        """Get website configuration for the bucket.

        Returns:
            WebsiteConfig: Website configuration information

        Raises:
            S3WebsiteConfigurationGetError: If getting website configuration fails

        Example:
            ```python
            config = s3.get_website_configuration()
            if "IndexDocument" in config:
                print(f"Index document: {config['IndexDocument']['Suffix']}")
            ```
        """
        try:
            return self.s3.get_bucket_website()
        except Exception as ex:
            raise S3WebsiteConfigurationGetError(
                self.bucket_name, str(ex)) from ex

    def configure_website(self, config: WebsiteConfig) -> None:
        """Configure website settings for the bucket.

        Args:
            config: Website configuration information

        Raises:
            S3WebsiteConfigurationError: If website configuration fails

        Example:
            ```python
            # Static website configuration
            s3.configure_website({
                "IndexDocument": {"Suffix": "index.html"},
                "ErrorDocument": {"Key": "error.html"}
            })

            # Redirect all requests configuration
            s3.configure_website({
                "RedirectAllRequestsTo": {
                    "HostName": "www.example.com",
                    "Protocol": "https"
                }
            })

            # Routing rules configuration
            s3.configure_website({
                "IndexDocument": {"Suffix": "index.html"},
                "RoutingRules": [{
                    "Condition": {
                        "KeyPrefixEquals": "docs/"
                    },
                    "Redirect": {
                        "ReplaceKeyPrefixWith": "documents/"
                    }
                }]
            })
            ```
        """
        try:
            self.s3.put_bucket_website(config)
        except Exception as ex:
            raise S3WebsiteConfigurationError(
                self.bucket_name, str(ex)) from ex

    def delete_website_configuration(self) -> None:
        """Delete website configuration for the bucket.

        Raises:
            S3WebsiteConfigurationDeleteError: If deleting website configuration fails

        Example:
            ```python
            s3.delete_website_configuration()
            ```
        """
        try:
            self.s3.delete_bucket_website()
        except Exception as ex:
            raise S3WebsiteConfigurationDeleteError(
                self.bucket_name, str(ex)) from ex

    def get_website_endpoint(self) -> str:
        """Get the website endpoint URL for the bucket.

        Returns:
            str: Website endpoint URL

        Example:
            ```python
            endpoint = s3.get_website_endpoint()
            print(f"Website URL: http://{endpoint}")
            ```
        """
        return f"{self.bucket_name}.s3-website-{self.s3.region}.amazonaws.com"
