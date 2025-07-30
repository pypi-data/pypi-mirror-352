"""Distributed locking mechanism using DynamoDB."""

import time
import uuid
import logging
import threading
import asyncio
from datetime import datetime
from typing import Optional
from contextlib import contextmanager
from threading import Lock

from chainsaws.aws.dynamodb import DynamoDBAPI, DynamoDBAPIConfig
from .lock_types import LockConfig, LockItem, LockStatus
from .lock_exceptions import LockAcquisitionError, LockReleaseError, LockRenewalError

logger = logging.getLogger(__name__)

class DistributedLockAPI:
    """Distributed locking mechanism using DynamoDB."""

    PARTITION_NAME = "distributed_locks"
    
    def __init__(self, config: LockConfig):
        """Initialize distributed lock.
        
        Args:
            config: Lock configuration
            
        Raises:
            ValueError: If configuration is invalid
        """
        if not config.get('table_name'):
            raise ValueError("table_name is required")
            
        self.config = config
        self.ttl_seconds = config.get('ttl_seconds', 60)
        self.owner_id = config.get('owner_id', str(uuid.uuid4()))
        self.retry_times = config.get('retry_times', 3)
        self.retry_delay = config.get('retry_delay', 1.0)
        self.heartbeat_interval = config.get('heartbeat_interval', self.ttl_seconds // 2)
        
        # Validate timing configuration
        if self.ttl_seconds <= self.heartbeat_interval:
            raise ValueError("ttl_seconds must be greater than heartbeat_interval")
        
        # DynamoDB 설정 추가
        dynamodb_config = DynamoDBAPIConfig(
            credentials=config.get('credentials', None),
            region=config.get('region', None),           
            endpoint_url=config.get('endpoint_url', None)
        )
        
        self.dynamodb = DynamoDBAPI(
            table_name=config['table_name'],
            config=dynamodb_config
        )
        
        # Thread safety
        self._locks_mutex = Lock()
        self._active_locks = {}
        self._renewal_threads = {}
        self._shutdown = threading.Event()
        
        self._ensure_lock_partition()

    def _ensure_lock_partition(self) -> None:
        """Ensure the DynamoDB partition for locks exists."""
        try:
            self.dynamodb.create_partition(
                partition=self.PARTITION_NAME,
                pk_field="lock_id",
                sk_field="owner_id",
                create_default_index=True
            )
        except Exception as e:
            if "already exists" not in str(e):
                raise

    def _verify_lock_ownership(self, lock_id: str) -> bool:
        """Verify that we still own the lock.
        
        Args:
            lock_id: Lock identifier to verify
            
        Returns:
            bool: True if we still own the lock
        """
        item = self.dynamodb.get_item(
            item_id=f"{self.PARTITION_NAME}#{lock_id}#{self.owner_id}"
        )
        if not item:
            return False
        return (
            item.get('owner_id') == self.owner_id and
            item.get('expires_at', 0) > time.time()
        )

    def get_lock_status(self, lock_id: str) -> LockStatus:
        """Get current status of a lock.
        
        Args:
            lock_id: Lock identifier to check
            
        Returns:
            LockStatus object containing current lock state
        """
        item = self.dynamodb.get_item(
            item_id=f"{self.PARTITION_NAME}#{lock_id}"
        )
        if not item:
            return LockStatus(
                is_locked=False,
                owner_id=None,
                expires_at=None,
                last_renewed_at=None,
                metadata=None
            )
        
        current_time = time.time()
        expires_at = item.get('expires_at', 0)
        
        return LockStatus(
            is_locked=expires_at > current_time,
            owner_id=item.get('owner_id'),
            expires_at=expires_at,
            last_renewed_at=item.get('last_renewed_at'),
            metadata=item.get('metadata')
        )

    def acquire(
        self,
        lock_id: str,
        timeout: Optional[float] = None,
        metadata: Optional[dict] = None
    ) -> bool:
        """Acquire a distributed lock.
        
        Args:
            lock_id: Unique lock identifier
            timeout: Maximum time to wait for lock acquisition
            metadata: Optional metadata to store with the lock
            
        Returns:
            bool: True if lock was acquired
            
        Raises:
            ValueError: If lock_id is empty or timeout is negative
            LockAcquisitionError: If lock acquisition fails
        """
        if not lock_id:
            raise ValueError("lock_id cannot be empty")
        if timeout is not None and timeout < 0:
            raise ValueError("timeout cannot be negative")
            
        # Check if we already own the lock
        with self._locks_mutex:
            if lock_id in self._active_locks:
                if self._verify_lock_ownership(lock_id):
                    return True
                # Clean up expired lock
                self._cleanup_expired_lock(lock_id)
            
        start_time = time.time()
        attempts = 0
        
        while True:
            try:
                expires_at = int(time.time() + self.ttl_seconds)
                
                item: LockItem = {
                    'lock_id': lock_id,
                    'owner_id': self.owner_id,
                    'expires_at': expires_at,
                    'created_at': datetime.now(),
                    'last_renewed_at': None,
                    'metadata': metadata
                }

                # Try to acquire the lock using conditional put
                condition = {
                    'field': 'expires_at',
                    'condition': 'lt',
                    'value': int(time.time())
                }
                
                self.dynamodb.put_item(
                    partition=self.PARTITION_NAME,
                    item=item,
                    can_overwrite=False,
                    condition=condition
                )

                # Start renewal thread
                with self._locks_mutex:
                    self._active_locks[lock_id] = item
                    self._start_renewal_thread(lock_id)
                
                logger.debug(f"Acquired lock '{lock_id}'")
                return True

            except Exception:
                attempts += 1
                if timeout and time.time() - start_time >= timeout:
                    raise LockAcquisitionError(lock_id, "Timeout waiting for lock")
                if attempts >= self.retry_times:
                    raise LockAcquisitionError(lock_id, f"Failed after {attempts} attempts")
                time.sleep(self.retry_delay)
                continue

    def _cleanup_expired_lock(self, lock_id: str) -> None:
        """Clean up an expired lock.
        
        Args:
            lock_id: Lock identifier to clean up
        """
        with self._locks_mutex:
            if lock_id in self._active_locks:
                self._stop_renewal_thread(lock_id)
                del self._active_locks[lock_id]

    def release(self, lock_id: str) -> None:
        """Release a distributed lock.
        
        Args:
            lock_id: Lock identifier to release
            
        Raises:
            LockReleaseError: If lock release fails
        """
        try:
            # Verify ownership before release
            if not self._verify_lock_ownership(lock_id):
                logger.warning(f"Cannot release lock '{lock_id}': not owner or expired")
                return

            # Stop renewal thread
            self._stop_renewal_thread(lock_id)

            # Delete the lock
            self.dynamodb.delete_item(
                item_id=f"{self.PARTITION_NAME}#{lock_id}#{self.owner_id}"
            )
            
            with self._locks_mutex:
                del self._active_locks[lock_id]
            
            logger.debug(f"Released lock '{lock_id}'")

        except Exception as e:
            raise LockReleaseError(lock_id, str(e))

    def _renew_lock(self, lock_id: str) -> None:
        """Renew a lock's expiration time.
        
        Args:
            lock_id: Lock identifier to renew
            
        Raises:
            LockRenewalError: If renewal fails after retries
        """
        retry_count = 0
        while retry_count < self.retry_times:
            try:
                # Verify ownership before renewal
                if not self._verify_lock_ownership(lock_id):
                    raise LockRenewalError(lock_id, "Lost lock ownership")
                    
                expires_at = int(time.time() + self.ttl_seconds)
                
                self.dynamodb.update_item(
                    partition=self.PARTITION_NAME,
                    item_id=f"{self.PARTITION_NAME}#{lock_id}#{self.owner_id}",
                    item={
                        'expires_at': expires_at,
                        'last_renewed_at': datetime.now()
                    }
                )

                logger.debug(f"Renewed lock '{lock_id}'")
                return

            except Exception as e:
                retry_count += 1
                if retry_count >= self.retry_times:
                    logger.warning(f"Failed to renew lock '{lock_id}': {e}")
                    self._stop_renewal_thread(lock_id)
                    raise LockRenewalError(lock_id, str(e))
                time.sleep(self.retry_delay)

    def _renewal_worker(self, lock_id: str) -> None:
        """Background worker for lock renewal.
        
        Args:
            lock_id: Lock identifier to renew
        """
        while not self._shutdown.is_set():
            try:
                self._renew_lock(lock_id)
                self._shutdown.wait(self.heartbeat_interval)
            except Exception as e:
                logger.error(f"Error in renewal worker for lock '{lock_id}': {e}")
                break

    def _start_renewal_thread(self, lock_id: str) -> None:
        """Start a background thread for lock renewal.
        
        Args:
            lock_id: Lock identifier to renew
        """
        if lock_id not in self._renewal_threads:
            thread = threading.Thread(
                target=self._renewal_worker,
                args=(lock_id,),
                daemon=True
            )
            self._renewal_threads[lock_id] = thread
            thread.start()

    def _stop_renewal_thread(self, lock_id: str) -> None:
        """Stop the renewal thread for a lock.
        
        Args:
            lock_id: Lock identifier
        """
        with self._locks_mutex:
            if lock_id in self._renewal_threads:
                self._renewal_threads[lock_id].join(timeout=1.0)
                del self._renewal_threads[lock_id]

    @contextmanager
    def lock(
        self,
        lock_id: str,
        timeout: Optional[float] = None,
        metadata: Optional[dict] = None
    ):
        """Context manager for acquiring and releasing a lock.
        
        Args:
            lock_id: Lock identifier
            timeout: Maximum time to wait for lock acquisition
            metadata: Optional metadata to store with the lock
            
        Yields:
            None
            
        Example:
            ```python
            lock_config = LockConfig(
                table_name="my-table",
                ttl_seconds=60,
                retry_times=3
            )
            lock_manager = DistributedLock(lock_config)
            
            try:
                with lock_manager.lock("my-resource"):
                    # Critical section
                    process_resource()
            except LockAcquisitionError:
                # Handle lock acquisition failure
                pass
            ```
        """
        try:
            self.acquire(lock_id, timeout, metadata)
            yield
        finally:
            self.release(lock_id)

    def shutdown(self) -> None:
        """Shutdown the lock manager and release all locks."""
        self._shutdown.set()
        
        with self._locks_mutex:
            active_locks = list(self._active_locks.keys())
            
        for lock_id in active_locks:
            try:
                self.release(lock_id)
            except Exception as e:
                logger.error(f"Error releasing lock '{lock_id}' during shutdown: {e}")

        with self._locks_mutex:
            for thread in self._renewal_threads.values():
                thread.join(timeout=1.0)

            self._active_locks.clear()
            self._renewal_threads.clear()

    def __del__(self):
        """Ensure cleanup on object destruction."""
        try:
            self.shutdown()
        except Exception:
            pass

    async def async_acquire(
        self,
        lock_id: str,
        timeout: Optional[float] = None,
        metadata: Optional[dict] = None
    ) -> bool:
        """Async version of acquire.
        
        Args:
            lock_id: Unique lock identifier
            timeout: Maximum time to wait for lock acquisition
            metadata: Optional metadata to store with the lock
            
        Returns:
            bool: True if lock was acquired
            
        Raises:
            ValueError: If lock_id is empty or timeout is negative
            LockAcquisitionError: If lock acquisition fails
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            lambda: self.acquire(lock_id, timeout, metadata)
        )

    async def async_release(self, lock_id: str) -> None:
        """Async version of release.
        
        Args:
            lock_id: Lock identifier to release
            
        Raises:
            LockReleaseError: If lock release fails
        """
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: self.release(lock_id)
        )

    @contextmanager
    async def async_lock(
        self,
        lock_id: str,
        timeout: Optional[float] = None,
        metadata: Optional[dict] = None
    ):
        """Async context manager for acquiring and releasing a lock.
        
        Args:
            lock_id: Lock identifier
            timeout: Maximum time to wait for lock acquisition
            metadata: Optional metadata to store with the lock
            
        Yields:
            None
            
        Example:
            ```python
            async with lock_manager.async_lock("my-resource"):
                # Critical section
                await process_resource()
            ```
        """
        try:
            await self.async_acquire(lock_id, timeout, metadata)
            yield
        finally:
            await self.async_release(lock_id) 