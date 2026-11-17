import sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from metadata_store import MetadataStore
from cxl_shared_memory import CXLSharedMemory
from transaction import Transaction
from logical_clock import LogicalClock


def test_invalid_delay_rejected():
    with pytest.raises(ValueError):
        MetadataStore(cxl_access_delay_us=-1)


def test_delay_does_not_change_metadata_values():
    store = MetadataStore(cxl_access_delay_us=50)
    store.put("k", {"v": 1}, location="cxl")
    assert store.get("k", location="cxl") == {"v": 1}


def test_cxl_commit_with_delay():
    memory = CXLSharedMemory(cxl_access_delay_us=50)
    tx = Transaction(1, LogicalClock())
    tx.write("k")
    assert memory.commit_transaction(tx, {"k": 1})
    assert memory.read_latest("k")["value"] == 1
