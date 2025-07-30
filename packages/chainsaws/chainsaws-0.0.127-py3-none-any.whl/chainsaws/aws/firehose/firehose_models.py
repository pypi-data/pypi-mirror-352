from dataclasses import dataclass

from chainsaws.aws.shared.config import APIConfig


@dataclass
class FirehoseAPIConfig(APIConfig):
    """Kinesis Firehose configuration."""

    max_retries: int = 3  # Maximum number of API call retries
    timeout: int = 30  # Timeout for API calls in seconds


@dataclass
class S3DestinationConfig:
    """S3 destination configuration."""

    role_arn: str  # IAM role ARN for Firehose
    bucket_name: str  # S3 bucket name
    prefix: str  # Object key prefix
    error_prefix: str = "error"  # Error output prefix

    @property
    def bucket_arn(self) -> str:
        return f"arn:aws:s3:::{self.bucket_name}"


@dataclass
class DeliveryStreamRequest:
    """Delivery stream creation request."""

    name: str  # Stream name
    s3_config: S3DestinationConfig  # S3 destination configuration
    tags: dict[str, str] | None = None  # Resource tags
