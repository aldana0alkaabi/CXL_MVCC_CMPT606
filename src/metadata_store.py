from threading import RLock
from copy import deepcopy

class MetadataStore:
    """Simulate local DRAM and shared CXL metadata storage."""

    def __init__(self):
        self._lock = RLock()
        self._local = {}
        self._cxl = {}

    def put(self, key, metadata, location="local"):
        if location not in ("local", "cxl"):
            raise ValueError("Unsupported metadata location")

        with self._lock:
            store = self._local if location == "local" else self._cxl
            store[key] = metadata.copy()

    def get(self, key, location="local"):
        if location not in ("local", "cxl"):
            raise ValueError("Unsupported metadata location")

        with self._lock:
            store = self._local if location == "local" else self._cxl
            metadata = store.get(key)
            return deepcopy(metadata) if metadata is not None else None

    def append(self, key, metadata, location="local"):
        if location not in ("local", "cxl"):
            raise ValueError("Unsupported metadata location")
        
        with self._lock:
            store = self._local if location == "local" else self._cxl
            store.setdefault(key, []).append(metadata.copy())