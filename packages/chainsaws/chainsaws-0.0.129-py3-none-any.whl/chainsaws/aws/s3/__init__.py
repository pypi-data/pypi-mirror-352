"""AWS S3 Client Wrapper

This module provides a high-level interface for AWS S3 operations with enhanced features:
- Simplified file upload and download operations
- Directory operations (upload, download, sync)
- Batch operations with parallel processing
- Progress tracking and retry mechanisms
- Type-safe interfaces with comprehensive type hints
"""

from chainsaws.aws.s3.s3 import S3API
from chainsaws.aws.s3.s3_models import (
    BucketACL,
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
    DownloadResult,
    BulkDownloadResult,
    ObjectTags,
    DirectoryUploadResult,
    DirectorySyncResult,
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
)

__all__ = [
    "S3API",
    # Models
    "BucketACL",
    "BucketConfig",
    "BulkUploadItem",
    "BulkUploadResult",
    "ContentType",
    "CopyObjectResult",
    "FileUploadConfig",
    "FileUploadResult",
    "ObjectListConfig",
    "PresignedUrlConfig",
    "S3APIConfig",
    "S3Object",
    "S3SelectCSVConfig",
    "S3SelectFormat",
    "S3SelectJSONType",
    "SelectObjectConfig",
    "UploadConfig",
    "DownloadConfig",
    "BatchOperationConfig",
    "DownloadResult",
    "BulkDownloadResult",
    "ObjectTags",
    "DirectoryUploadResult",
    "DirectorySyncResult",
    # Exceptions
    "InvalidObjectKeyError",
    "S3BucketPolicyUpdateError",
    "S3BucketPolicyGetError",
    "S3LambdaPermissionAddError",
    "S3LambdaNotificationAddError",
    "S3LambdaNotificationRemoveError",
    "S3MultipartUploadError",
    "S3StreamingError",
]
