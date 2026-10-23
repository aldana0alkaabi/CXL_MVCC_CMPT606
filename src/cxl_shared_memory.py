from threading import RLock

try:
    from .validator import MVCCValidator
except ImportError:
    from validator import MVCCValidator

class CXLSharedMemory:
    """
    Simulate a CXL shared-memory region accsseible by multiple hosts.
    This is a software simulation, not a real CXL hardware.
    """

    def __init__(self):
        self._memory = {}
        self._lock = RLock()
        self._next_version_id = 1

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

    def commit_transaction(self, transaction, writes):
        with self._lock:
            if transaction.status != "active":
                return False

            if set(writes) != transaction.write_set:
                raise ValueError("Write do not match transaction write_set")

            if not hasattr(self, "_committed_transactions"):
                self._committed_transactions = []

            validator = MVCCValidator()

            if not validator.validate(
                transaction, self._committed_transactions
            ):
                transaction.abort()
                return False

            transaction.commit()

            for key, value in writes.items():
                self.write(
                    host_id=0,
                    key=key,
                    value=value,
                    transaction_id=transaction.transaction_id
                )

            self._committed_transactions.append(transaction)
            return True