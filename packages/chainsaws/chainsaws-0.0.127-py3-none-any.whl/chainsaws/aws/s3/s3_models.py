from enum import Enum
from typing import Any, Literal, TypedDict, List, NotRequired, Callable, Optional, Dict
from datetime import datetime
from dataclasses import dataclass, field


from chainsaws.aws.shared.config import APIConfig

BucketACL = Literal["private", "public-read",
                    "public-read-write", "authenticated-read"]


class ContentType(str, Enum):
    """Common MIME content types."""

    # Application types
    JSON = "application/json"
    PDF = "application/pdf"
    ZIP = "application/zip"
    GZIP = "application/gzip"
    EXCEL = "application/vnd.ms-excel"
    EXCEL_XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    WORD = "application/msword"
    WORD_DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    BINARY = "application/octet-stream"

    # Text types
    TEXT = "text/plain"
    HTML = "text/html"
    CSS = "text/css"
    CSV = "text/csv"
    XML = "text/xml"

    # Image types
    JPEG = "image/jpeg"
    PNG = "image/png"
    GIF = "image/gif"
    SVG = "image/svg+xml"
    WEBP = "image/webp"
    ICO = "image/x-icon"

    # Audio types
    MP3 = "audio/mpeg"
    WAV = "audio/wav"
    OGG = "audio/ogg"

    # Video types
    MP4 = "video/mp4"
    MPEG = "video/mpeg"
    WEBM = "video/webm"

    @classmethod
    def from_extension(cls, extension: str) -> "ContentType":
        """Get content type from file extension."""
        extension = extension.lower().lstrip(".")
        mapping = {
            # Application
            "json": cls.JSON,
            "pdf": cls.PDF,
            "zip": cls.ZIP,
            "gz": cls.GZIP,
            "xls": cls.EXCEL,
            "xlsx": cls.EXCEL_XLSX,
            "doc": cls.WORD,
            "docx": cls.WORD_DOCX,

            # Text
            "txt": cls.TEXT,
            "html": cls.HTML,
            "htm": cls.HTML,
            "css": cls.CSS,
            "csv": cls.CSV,
            "xml": cls.XML,

            # Image
            "jpg": cls.JPEG,
            "jpeg": cls.JPEG,
            "png": cls.PNG,
            "gif": cls.GIF,
            "svg": cls.SVG,
            "webp": cls.WEBP,
            "ico": cls.ICO,

            # Audio
            "mp3": cls.MP3,
            "wav": cls.WAV,
            "ogg": cls.OGG,

            # Video
            "mp4": cls.MP4,
            "mpeg": cls.MPEG,
            "webm": cls.WEBM,
        }

        return mapping.get(extension, cls.BINARY)


@dataclass
class S3APIConfig(APIConfig):
    """Configuration for S3API."""

    acl: BucketACL = "private"  # Bucket ACL
    use_accelerate: bool = True  # Config for bucket-level data acceleration


@dataclass
class BucketConfig:
    """Bucket creation/management configuration."""

    bucket_name: str  # Name of the S3 bucket
    acl: BucketACL = "private"  # Bucket ACL
    use_accelerate: bool = True  # Config for bucket-level data acceleration


@dataclass
class FileUploadConfig:
    """File upload configuration."""

    bucket_name: str  # Target bucket name
    file_name: str  # Target file name (key)
    content_type: Optional[ContentType] = None  # Content type of the file


@dataclass
class ObjectListConfig:
    """Configuration for listing objects."""

    prefix: str = ""  # Prefix for filtering objects
    # Continuation token for pagination
    continuation_token: Optional[str] = None
    start_after: Optional[str] = None  # Start listing after this key
    limit: int = 1000  # Maximum number of objects to return

    def __post_init__(self) -> None:
        if self.limit > 1000:
            raise ValueError("limit must be less than or equal to 1000")


class FileUploadResult(TypedDict):
    """Result of file upload operation."""
    url: str  # Changed from HttpUrl to str
    object_key: str


@dataclass
class PresignedUrlConfig:
    """Configuration for presigned URL generation."""

    bucket_name: str  # Bucket name
    object_name: str  # Object key
    client_method: Literal["get_object", "put_object"]  # S3 client method
    content_type: Optional[str] = None  # Content type of the object
    acl: BucketACL = "private"  # Object ACL
    expiration: int = 3600  # URL expiration in seconds

    def __post_init__(self) -> None:
        if not 1 <= self.expiration <= 604800:
            raise ValueError("expiration must be between 1 and 604800 seconds")


@dataclass
class SelectObjectConfig:
    """Configuration for S3 Select operations."""

    bucket_name: str  # Bucket name
    object_key: str  # Object key
    query: str  # SQL query to execute
    input_serialization: dict[str, Any] = field(
        # Input serialization configuration
        default_factory=lambda: {"JSON": {"Type": "DOCUMENT"}})
    output_serialization: dict[str, Any] = field(
        default_factory=lambda: {"JSON": {}})  # Output format configuration


@dataclass
class CopyObjectResult:
    """Result of copy object operation."""

    success: bool  # Whether the copy operation was successful
    object_key: str  # Key of the copied object
    url: Optional[str] = None  # URL of the copied object if successful
    error_message: Optional[str] = None  # Error message if copy failed


@dataclass
class BulkUploadItem:
    """Configuration for a single file in bulk upload."""

    object_key: str  # The key (path) where the object will be stored in S3
    data: bytes | str  # File data: can be bytes, file object, or path to file
    content_type: Optional[ContentType] = None  # MIME type of the file
    acl: str = "private"  # S3 access control list setting

    def __post_init__(self) -> None:
        if self.acl not in ["private", "public-read", "public-read-write", "authenticated-read"]:
            raise ValueError("Invalid ACL value")


@dataclass
class BulkUploadResult:
    """Result of a bulk upload operation."""

    # Dictionary of successful uploads mapping object_key to S3 URL
    successful: dict[str, str] = field(default_factory=dict)

    # Dictionary of failed uploads mapping object_key to error message
    failed: dict[str, str] = field(default_factory=dict)


class S3SelectFormat(str, Enum):
    """S3 Select input/output format."""

    JSON = "JSON"
    CSV = "CSV"
    PARQUET = "PARQUET"


class S3SelectJSONType(str, Enum):
    """S3 Select JSON type."""

    DOCUMENT = "DOCUMENT"
    LINES = "LINES"


@dataclass
class S3SelectCSVConfig:
    """Configuration for CSV format in S3 Select."""

    # FileHeaderInfo (NONE, USE, IGNORE)
    file_header_info: Optional[str] = None
    delimiter: str = ","  # Field delimiter
    quote_character: str = '"'  # Quote character
    quote_escape_character: str = '"'  # Quote escape character
    comments: Optional[str] = None  # Comment character
    record_delimiter: str = "\n"  # Record delimiter

    def to_dict(self, exclude_none: bool = True) -> dict[str, Any]:
        """Convert to dictionary format expected by AWS API.

        Args:
            exclude_none: Whether to exclude None values from the output

        Returns:
            dict[str, Any]: The model as a dictionary
        """
        result = {
            "Delimiter": self.delimiter,
            "QuoteCharacter": self.quote_character,
            "QuoteEscapeCharacter": self.quote_escape_character,
            "RecordDelimiter": self.record_delimiter,
        }
        if not exclude_none or self.file_header_info is not None:
            result["FileHeaderInfo"] = self.file_header_info
        if not exclude_none or self.comments is not None:
            result["Comments"] = self.comments
        return result


@dataclass
class S3SelectConfig:
    """Configuration for S3 Select operations."""

    query: str  # SQL query to execute
    input_format: S3SelectFormat  # Input format
    output_format: S3SelectFormat = S3SelectFormat.JSON  # Output format
    # Input compression (NONE, GZIP, BZIP2)
    compression_type: Optional[str] = None
    json_type: Optional[S3SelectJSONType] = None  # JSON input type
    # CSV input configuration
    csv_input_config: Optional[S3SelectCSVConfig] = None
    # CSV output configuration
    csv_output_config: Optional[S3SelectCSVConfig] = None
    max_rows: Optional[int] = None  # Maximum number of rows to return


class S3Owner(TypedDict):
    """S3 object owner information"""
    DisplayName: str
    ID: str


class S3RestoreStatus(TypedDict):
    """S3 object restore status"""
    IsRestoreInProgress: bool
    RestoreExpiryDate: datetime


class S3CommonPrefix(TypedDict):
    """S3 common prefix"""
    Prefix: str


class S3Object(TypedDict, total=False):
    """S3 object information"""
    Key: str
    LastModified: datetime
    ETag: str
    ChecksumAlgorithm: List[Literal["CRC32", "CRC32C", "SHA1", "SHA256"]]
    Size: int
    StorageClass: Literal[
        "STANDARD",
        "REDUCED_REDUNDANCY",
        "GLACIER",
        "STANDARD_IA",
        "ONEZONE_IA",
        "INTELLIGENT_TIERING",
        "DEEP_ARCHIVE",
        "OUTPOSTS",
        "GLACIER_IR",
        "SNOW",
        "EXPRESS_ONEZONE"
    ]
    Owner: NotRequired[S3Owner]
    RestoreStatus: NotRequired[S3RestoreStatus]


class ListObjectsResponse(TypedDict, total=False):
    """S3 ListObjectsV2 response"""
    IsTruncated: bool
    Contents: List[S3Object]
    Name: str
    Prefix: str
    Delimiter: str
    MaxKeys: int
    CommonPrefixes: List[S3CommonPrefix]
    EncodingType: Literal["url"]
    KeyCount: int
    ContinuationToken: str
    NextContinuationToken: str
    StartAfter: str
    RequestCharged: Literal["requester"]


@dataclass
class UploadConfig:
    """Configuration for file upload operations."""
    content_type: Optional[ContentType] = None
    part_size: int = 5 * 1024 * 1024  # 5MB
    progress_callback: Optional[Callable[[int, int], None]] = None
    acl: str = "private"


@dataclass
class DownloadConfig:
    """Configuration for file download operations."""
    max_retries: int = 3
    retry_delay: float = 1.0
    progress_callback: Optional[Callable[[int, int], None]] = None
    chunk_size: int = 8 * 1024 * 1024  # 8MB


@dataclass
class BatchOperationConfig:
    """Configuration for batch operations."""
    max_workers: Optional[int] = None
    chunk_size: int = 8 * 1024 * 1024  # 8MB
    progress_callback: Optional[Callable[[str, int, int], None]] = None


class DownloadResult(TypedDict):
    """Download result"""
    object_key: str
    local_path: str
    success: bool
    error: Optional[str]


class ObjectTags(TypedDict):
    """S3 object tags"""
    TagSet: List[Dict[Literal["Key", "Value"], str]]


class BulkDownloadResult(TypedDict):
    """Bulk download operation results"""
    successful: List[DownloadResult]
    failed: List[DownloadResult]


class DirectoryUploadResult(TypedDict):
    """Directory upload operation results"""
    successful: List[FileUploadResult]
    failed: List[Dict[str, str]]  # {file_path: error_message}


class DirectorySyncResult(TypedDict):
    """Directory synchronization results"""
    uploaded: List[str]  # List of uploaded files
    updated: List[str]   # List of updated files
    deleted: List[str]   # List of deleted files
    failed: List[Dict[str, str]]  # List of failed operations


class WebsiteRedirectConfig(TypedDict, total=False):
    """S3 website redirect configuration"""
    HostName: str
    Protocol: Literal["http", "https"]


class WebsiteIndexConfig(TypedDict):
    """S3 website index document configuration"""
    Suffix: str


class WebsiteErrorConfig(TypedDict):
    """S3 website error document configuration"""
    Key: str


class WebsiteRoutingRuleCondition(TypedDict, total=False):
    """S3 website routing rule condition"""
    HttpErrorCodeReturnedEquals: str
    KeyPrefixEquals: str


class WebsiteRoutingRuleRedirect(TypedDict, total=False):
    """S3 website routing rule redirect configuration"""
    HostName: str
    HttpRedirectCode: str
    Protocol: Literal["http", "https"]
    ReplaceKeyPrefixWith: str
    ReplaceKeyWith: str


class WebsiteRoutingRule(TypedDict):
    """S3 website routing rule"""
    Condition: Optional[WebsiteRoutingRuleCondition]
    Redirect: WebsiteRoutingRuleRedirect


class WebsiteConfig(TypedDict, total=False):
    """S3 website configuration"""
    RedirectAllRequestsTo: WebsiteRedirectConfig
    IndexDocument: WebsiteIndexConfig
    ErrorDocument: WebsiteErrorConfig
    RoutingRules: list[WebsiteRoutingRule]
