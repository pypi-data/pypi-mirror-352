"""Models for AWS SQS operations."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from chainsaws.aws.shared.config import APIConfig


@dataclass
class SQSAPIConfig(APIConfig):
    """Configuration for SQS client."""


@dataclass
class SQSMessageAttributes:
    """SQS message attributes."""
    data_type: str
    string_value: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format expected by AWS API."""
        return {
            "DataType": self.data_type,
            "StringValue": self.string_value,
        }


@dataclass
class SQSMessage:
    """SQS message structure."""
    queue_url: str
    message_body: str
    delay_seconds: Optional[int] = None
    message_attributes: Optional[dict[str, SQSMessageAttributes]] = None
    message_deduplication_id: Optional[str] = None
    message_group_id: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format expected by AWS API."""
        result = {
            "QueueUrl": self.queue_url,
            "MessageBody": self.message_body,
        }
        if self.delay_seconds is not None:
            result["DelaySeconds"] = self.delay_seconds
        if self.message_attributes:
            result["MessageAttributes"] = {
                k: v.to_dict() for k, v in self.message_attributes.items()}
        if self.message_deduplication_id:
            result["MessageDeduplicationId"] = self.message_deduplication_id
        if self.message_group_id:
            result["MessageGroupId"] = self.message_group_id
        return result


@dataclass
class SQSResponse:
    """Single message response."""
    message_id: str
    sequence_number: Optional[str] = None
    md5_of_message_body: str = field(default="")
    md5_of_message_attributes: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format expected by AWS API."""
        result = {
            "MessageId": self.message_id,
            "MD5OfMessageBody": self.md5_of_message_body,
        }
        if self.sequence_number:
            result["SequenceNumber"] = self.sequence_number
        if self.md5_of_message_attributes:
            result["MD5OfMessageAttributes"] = self.md5_of_message_attributes
        return result


@dataclass
class SQSBatchResultEntry:
    """Batch operation result entry."""
    id: str
    message_id: str
    md5_of_message_body: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format expected by AWS API."""
        return {
            "Id": self.id,
            "MessageId": self.message_id,
            "MD5OfMessageBody": self.md5_of_message_body,
        }


@dataclass
class SQSMessageBatchResponse:
    """Batch operation response."""
    successful: list[SQSBatchResultEntry] = field(default_factory=list)
    failed: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format expected by AWS API."""
        return {
            "Successful": [entry.to_dict() for entry in self.successful],
            "Failed": self.failed,
        }


@dataclass
class SQSReceivedMessage:
    """Received message structure."""
    message_id: str
    receipt_handle: str
    body: str
    md5_of_body: str
    attributes: Optional[dict[str, str]] = None
    message_attributes: Optional[dict[str, SQSMessageAttributes]] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format expected by AWS API."""
        result = {
            "MessageId": self.message_id,
            "ReceiptHandle": self.receipt_handle,
            "Body": self.body,
            "MD5OfBody": self.md5_of_body,
        }
        if self.attributes:
            result["Attributes"] = self.attributes
        if self.message_attributes:
            result["MessageAttributes"] = {
                k: v.to_dict() for k, v in self.message_attributes.items()}
        return result


@dataclass
class SQSReceiveMessageResponse:
    """Receive message operation response."""
    messages: list[SQSReceivedMessage] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format expected by AWS API."""
        return {
            "Messages": [msg.to_dict() for msg in self.messages],
        }


@dataclass
class SQSQueueAttributes:
    """Queue attributes."""
    delay_seconds: int = 0
    maximum_message_size: int = field(default=0)
    message_retention_period: int = field(default=0)
    visibility_timeout: int = field(default=0)
    created_timestamp: datetime = field(default_factory=datetime.now)
    last_modified_timestamp: datetime = field(default_factory=datetime.now)
    queue_arn: str = field(default="")
    approximate_number_of_messages: int = field(default=0)
    approximate_number_of_messages_not_visible: int = field(default=0)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format expected by AWS API."""
        return {
            "DelaySeconds": self.delay_seconds,
            "MaximumMessageSize": self.maximum_message_size,
            "MessageRetentionPeriod": self.message_retention_period,
            "VisibilityTimeout": self.visibility_timeout,
            "CreatedTimestamp": int(self.created_timestamp.timestamp()),
            "LastModifiedTimestamp": int(self.last_modified_timestamp.timestamp()),
            "QueueArn": self.queue_arn,
            "ApproximateNumberOfMessages": self.approximate_number_of_messages,
            "ApproximateNumberOfMessagesNotVisible": self.approximate_number_of_messages_not_visible,
        }
