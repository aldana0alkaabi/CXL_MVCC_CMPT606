import time
from threading import RLock
from copy import deepcopy

class MetadataStore:
    """Simulate local DRAM and shared CXL metadata storage."""

    def __init__(self, cxl_access_delay_us=0.0):
        if cxl_access_delay_us < 0:
            raise ValueError("cxl_access_delay_us must be non-negative")
        self.cxl_access_delay_us = float(cxl_access_delay_us)
        self._lock = RLock()
        self._local = {}
        self._cxl = {}

    def _charge_access(self, location):
        if location == "cxl" and self.cxl_access_delay_us:
            time.sleep(self.cxl_access_delay_us / 1_000_000)

    def put(self, key, metadata, location="local"):
        if location not in ("local", "cxl"):
            raise ValueError("Unsupported metadata location")

        self._charge_access(location)
        with self._lock:
            store = self._local if location == "local" else self._cxl
            store[key] = metadata.copy()

    def get(self, key, location="local"):
        if location not in ("local", "cxl"):
            raise ValueError("Unsupported metadata location")

        self._charge_access(location)
        with self._lock:
            store = self._local if location == "local" else self._cxl
            metadata = store.get(key)
            return deepcopy(metadata) if metadata is not None else None

    def append(self, key, metadata, location="local"):
        if location not in ("local", "cxl"):
            raise ValueError("Unsupported metadata location")
        
        self._charge_access(location)
        with self._lock:
            store = self._local if location == "local" else self._cxl
            store.setdefault(key, []).append(metadata.copy())