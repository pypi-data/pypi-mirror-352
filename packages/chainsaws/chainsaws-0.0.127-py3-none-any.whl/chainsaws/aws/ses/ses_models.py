from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from chainsaws.aws.shared.config import APIConfig


class EmailFormat(str, Enum):
    """Email content format."""

    TEXT = "Text"
    HTML = "Html"
    BOTH = "Both"


class EmailPriority(str, Enum):
    """Email priority level."""

    HIGH = "1"
    NORMAL = "3"
    LOW = "5"


@dataclass
class EmailContent:
    """Email content configuration."""

    subject: str  # Email subject
    body_text: Optional[str] = None  # Plain text body
    body_html: Optional[str] = None  # HTML body
    charset: str = "UTF-8"  # Content character set


@dataclass
class EmailAddress:
    """Email address with optional name."""

    email: str  # Email address
    name: Optional[str] = None  # Display name

    def __str__(self) -> str:
        if self.name:
            return f"{self.name} <{self.email}>"
        return str(self.email)


@dataclass
class SESAPIConfig(APIConfig):
    """Configuration for SES API."""

    default_region: str = field(default="ap-northeast-2")  # Default AWS region
    default_sender: Optional[EmailAddress] = None  # Default sender address
    default_format: EmailFormat = field(
        default=EmailFormat.BOTH)  # Default email format


@dataclass
class SendEmailConfig:
    """Configuration for sending email."""

    sender: EmailAddress  # Sender address
    recipients: list[EmailAddress]  # Recipient addresses
    content: EmailContent  # Email content
    cc: Optional[list[EmailAddress]] = None  # CC addresses
    bcc: Optional[list[EmailAddress]] = None  # BCC addresses
    reply_to: Optional[list[EmailAddress]] = None  # Reply-To addresses
    priority: EmailPriority = field(
        default=EmailPriority.NORMAL)  # Email priority
    tags: dict[str, str] = field(default_factory=dict)  # Email tags


@dataclass
class TemplateContent:
    """Email template content."""

    subject: str  # Template subject
    text: Optional[str] = None  # Text version template
    html: Optional[str] = None  # HTML version template


@dataclass
class SendTemplateConfig:
    """Configuration for sending templated email."""

    template_name: str  # Template name
    sender: EmailAddress  # Sender address
    recipients: list[EmailAddress]  # Recipient addresses
    template_data: dict[str, Any]  # Template variables
    cc: Optional[list[EmailAddress]] = None  # CC addresses
    bcc: Optional[list[EmailAddress]] = None  # BCC addresses
    tags: dict[str, str] = field(default_factory=dict)  # Email tags


@dataclass
class EmailQuota:
    """SES sending quota information."""

    max_24_hour_send: int  # Max sends per 24 hours
    max_send_rate: float  # Max send rate per second
    sent_last_24_hours: int  # Sent in last 24 hours


@dataclass
class BulkEmailRecipient:
    """Recipient for bulk email sending."""

    email: EmailAddress  # Recipient email address
    template_data: dict[str, Any] = field(
        default_factory=dict)  # Template data for this recipient
    tags: dict[str, str] = field(
        default_factory=dict)  # Tags for this recipient


@dataclass
class BulkEmailConfig:
    """Configuration for bulk email sending."""

    sender: EmailAddress  # Sender address
    recipients: list[BulkEmailRecipient]  # Recipients list
    template_name: Optional[str] = None  # Template name if using template
    content: Optional[EmailContent] = None  # Content if not using template
    batch_size: int = 50  # Number of emails per batch
    max_workers: Optional[int] = None  # Maximum number of worker threads
    format: Optional[EmailFormat] = None  # Email format if not using template
