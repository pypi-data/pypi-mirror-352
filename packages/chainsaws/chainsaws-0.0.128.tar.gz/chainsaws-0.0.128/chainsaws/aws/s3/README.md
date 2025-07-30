# AWS S3 Client Wrapper

A high-level Python wrapper for AWS S3 operations with enhanced features and type safety.

## Features

- 🚀 High-level API for common S3 operations
- 📁 Directory operations (upload, download, sync)
- 🔄 Batch operations with parallel processing
- 📊 Progress tracking and retry mechanisms
- ⚡ Transfer acceleration support
- 🔍 Pattern-based object search
- 🔒 Type-safe interfaces with comprehensive type hints

## Installation

```bash
pip install chainsaws
```

## Quick Start

```python
from chainsaws.aws.s3 import S3API, UploadConfig, ContentType

# Initialize S3 client
s3 = S3API(bucket_name="my-bucket")

# Upload a file
result = s3.upload_file(
    object_key="path/to/file.txt",
    file_bytes=b"Hello, World!",
    config=UploadConfig(content_type=ContentType.TEXT)
)
print(f"File uploaded: {result['url']}")

# Download a file
s3.download_file(
    object_key="path/to/file.txt",
    file_path="local/file.txt"
)
```

## Directory Operations

### Upload Directory

```python
# Upload entire directory
result = s3.upload_directory(
    local_dir="./data",
    prefix="backup/2024",
    exclude_patterns=["*.tmp", "**/__pycache__/*"]
)

# Check results
for success in result["successful"]:
    print(f"Uploaded: {success['url']}")
for failed in result["failed"]:
    print(f"Failed: {list(failed.keys())[0]}")
```

### Download Directory

```python
# Download directory with pattern matching
s3.download_directory(
    prefix="backup/2024",
    local_dir="./restore",
    include_patterns=["*.json", "*.csv"]
)
```

### Directory Sync

```python
# Sync local directory with S3
result = s3.sync_directory(
    local_dir="./website",
    prefix="static",
    delete=True  # Delete files that don't exist locally
)

print(f"Uploaded: {len(result['uploaded'])} files")
print(f"Updated: {len(result['updated'])} files")
print(f"Deleted: {len(result['deleted'])} files")
```

## Batch Operations

### Bulk Upload

```python
from chainsaws.aws.s3 import BulkUploadItem, BatchOperationConfig

items = [
    BulkUploadItem(object_key="file1.txt", data=b"content1"),
    BulkUploadItem(object_key="file2.txt", data=b"content2")
]

config = BatchOperationConfig(
    max_workers=4,
    progress_callback=lambda key, current, total: print(f"{key}: {current/total*100:.1f}%")
)

result = s3.bulk_upload(items, config=config)
```

### Multiple File Download

```python
result = s3.download_multiple_files(
    object_keys=["file1.txt", "file2.txt"],
    output_dir="./downloads",
    config=BatchOperationConfig(max_workers=4)
)

for success in result["successful"]:
    print(f"Downloaded {success['object_key']} to {success['local_path']}")
```

## Object Search

```python
# Find objects using glob patterns
for obj in s3.find_objects(
    pattern="logs/**/error*.log",
    recursive=True,
    max_items=100
):
    print(f"Found: {obj['Key']} (Size: {obj['Size']} bytes)")
```

## Advanced Features

### Transfer Acceleration

```python
# Enable transfer acceleration
if s3.enable_transfer_acceleration():
    print("Transfer acceleration enabled")

# Automatically optimize transfer settings
s3.optimize_transfer_settings()
```

### Presigned URLs

```python
# Generate presigned URL for upload
upload_url = s3.create_presigned_url_put_object(
    object_key="upload/file.txt",
    expiration=3600  # 1 hour
)

# Generate presigned URL for download
download_url = s3.create_presigned_url_get_object(
    object_key="download/file.txt",
    expiration=3600
)
```

### Object Tags and Metadata

```python
# Get object tags
tags = s3.get_object_tags("path/to/file.txt")

# Set object tags
s3.put_object_tags("path/to/file.txt", {
    "environment": "production",
    "version": "1.0"
})

# Get object metadata
metadata = s3.get_object_metadata("path/to/file.txt")
```

### Streaming Support

```python
# Stream large objects
for chunk in s3.stream_object("large-file.dat"):
    process_chunk(chunk)
```

## Error Handling

The library provides detailed error information through custom exceptions:

```python
from chainsaws.aws.s3 import S3StreamingError, S3MultipartUploadError

try:
    s3.upload_large_file("large.zip", file_bytes)
except S3MultipartUploadError as e:
    print(f"Upload failed: {e.reason}")
    print(f"Object key: {e.object_key}")
    print(f"Upload ID: {e.upload_id}")
```

## Type Safety

All operations are fully typed and provide IDE support:

```python
from chainsaws.aws.s3 import (
    S3API,
    UploadConfig,
    DownloadConfig,
    BatchOperationConfig,
    DirectoryUploadResult,
    DirectorySyncResult
)

def process_upload_result(result: DirectoryUploadResult) -> None:
    for success in result["successful"]:
        print(f"URL: {success['url']}")
```

## Configuration

```python
from chainsaws.aws.s3 import S3APIConfig

config = S3APIConfig(
    use_accelerate=True,
    acl="private",
    credentials={
        "aws_access_key_id": "your-key",
        "aws_secret_access_key": "your-secret"
    }
)

s3 = S3API("my-bucket", config=config)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
