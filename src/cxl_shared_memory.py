import json
import os
import tempfile

from threading import RLock
from copy import deepcopy

try:
    from.metadata_store import MetadataStore
except ImportError:
    from metadata_store import MetadataStore

try:
    from .validator import MVCCValidator
except ImportError:
    from validator import MVCCValidator

try:
    from .transaction import Transaction
    from .logical_clock import LogicalClock
except ImportError:
    from transaction import Transaction
    from logical_clock import LogicalClock

class CXLSharedMemory:
    """
    Simulate a CXL shared-memory region accsseible by multiple hosts.
    This is a software simulation, not a real CXL hardware.
    """

    def __init__(self, enable_metadata_validation=True):
        self._memory = {}
        self._lock = RLock()
        self._next_version_id = 1
        self.metadata_store = MetadataStore()
        self.enable_metadata_validation = enable_metadata_validation
        self._committed_transactions = []

    def write(self, host_id, key, value, transaction_id):
        """Write a version to the shared-memory region."""
        with self._lock:
            version = {
                "key": key,
                "value": value,
                "host_id": host_id,
                "transaction_id": transaction_id,
                "version_id": self._next_version_id
            }

            self._memory.setdefault(key, []).append(version)
            self._next_version_id += 1
            return version.copy()

    def read_latest(self, key):
        """Read the latest version visible in shared-memory region."""
        with self._lock:
            version = self._memory.get(key, [])
            return version[-1].copy() if version else None

    def read_all_versions(self, key):
        """Return all stored versions for a key."""
        with self._lock:
            return [
                version.copy()
                for version in self._memory.get(key, [])
            ]

    def get_stats(self):
        """Return basic shared-memory activity counters."""
        with self._lock:
            return {
                "keys": len(self._memory),
                "total_versions": sum(
                    len(versions) for versions in self._memory.values()
                ),
            }

    
    def create_checkpoint_snapshot(self):
        """Capture a consistent in-memory recovery snapshot."""
        with self._lock:
            committed = getattr(self, "_committed_transactions", [])

            transactions = [
                {
                    "transaction_id": tx.transaction_id,
                    "start_timestamp": tx.start_timestamp,
                    "commit_timestamp": tx.commit_timestamp,
                    "read_set": sorted(tx.read_set),
                    "write_set": sorted(tx.write_set),
                    "status": tx.status,
                    "has_logical_clock": tx.clock is not None,
                }
                for tx in committed
            ]

            with self.metadata_store._lock:
                metadata = deepcopy(self.metadata_store._cxl)

            return {
                "memory": deepcopy(self._memory),
                "metadata": metadata,
                "committed_transactions": transactions,
                "next_version_id": self._next_version_id,
                "enable_metadata_validation": self.enable_metadata_validation,
            }

    
    def save_checkpoint(self, path):
        """Save a checkpoint using a temporary file and atomic replacement."""
        snapshot = self.create_checkpoint_snapshot()
        destination = os.path.abspath(path)
        directory = os.path.dirname(destination)

        os.makedirs(directory, exist_ok=True)

        temporary_path = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=directory,
                prefix=".checkpoint_",
                suffix=".tmp",
                delete=False
            ) as file:
                temporary_path = file.name
                json.dump(snapshot, file, indent=2)
                file.flush()
                os.fsync(file.fileno())

            os.replace(temporary_path, destination)

        finally:
            if temporary_path and os.path.exists(temporary_path):
                os.remove(temporary_path)

        return destination

    
    def restore_checkpoint(self, path):
        """Restore a checkpoint from disk."""
        with open(path, "r", encoding="utf-8") as file:
            snapshot = json.load(file)

        required = {
            "memory",
            "metadata",
            "committed_transactions",
            "next_version_id",
            "enable_metadata_validation",
        }

        if not required.issubset(snapshot):
            raise ValueError("Incomplete checkpoint")

        records = snapshot["committed_transactions"]

        timestamps = [
            timestamp
            for record in records
            for timestamp in (
                record["start_timestamp"],
                record["commit_timestamp"],
            )
            if timestamp is not None
        ]

        clock = LogicalClock(
            initial_value=max(timestamps, default=0)
        )

        restored_transactions = []

        for record in records:
            tx = Transaction.__new__(Transaction)
            tx.transaction_id = record["transaction_id"]
            tx.clock = (
                clock if record.get("has_logical_clock", False)
                else None
            )
            tx.start_timestamp = record["start_timestamp"]
            tx.commit_timestamp = record["commit_timestamp"]
            tx.read_set = set(record["read_set"])
            tx.write_set = set(record["write_set"])
            tx.status = record["status"]

            if tx.status != "committed":
                raise ValueError("Invalid committed transaction")

            restored_transactions.append(tx)

        with self._lock:
            self._memory = deepcopy(snapshot["memory"])
            self._next_version_id = snapshot["next_version_id"]
            self.enable_metadata_validation = snapshot[
                "enable_metadata_validation"
            ]
            self._committed_transactions = restored_transactions

            with self.metadata_store._lock:
                self.metadata_store._cxl = deepcopy(
                    snapshot["metadata"]
                )

        return clock

    def commit_transaction(self, transaction, writes, host_id=0):
        with self._lock:
            if transaction.status != "active":
                return False

            if set(writes) != transaction.write_set:
                raise ValueError("Write do not match transaction write_set")

            validator = MVCCValidator(
                metadata_store=self.metadata_store,
                metadata_location="cxl",
                enable_metadata_validation=self.enable_metadata_validation
            )

            if not validator.validate(
                transaction, self._committed_transactions
            ):
                transaction.abort()
                return False

            transaction.commit()

            for key, value in writes.items():
                self.write(
                    host_id=host_id,
                    key=key,
                    value=value,
                    transaction_id=transaction.transaction_id
                )

            self._committed_transactions.append(transaction)

            for key in transaction.read_set | transaction.write_set:
                self.metadata_store.append(
                    key,
                    {
                        "transaction_id": transaction.transaction_id,
                        "status": transaction.status,
                        "start_timestamp": transaction.start_timestamp,
                        "commit_timestamp": transaction.commit_timestamp,
                        "write_set": list(transaction.write_set),
                        "read_set": list(transaction.read_set),
                    },
                    location="cxl"
                )
            return True