from threading import RLock

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