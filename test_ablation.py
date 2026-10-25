from src.cxl_shared_memory import CXLSharedMemory

def test_ablation_configuration():
    full = CXLSharedMemory()
    ablation = CXLSharedMemory(
        enable_metadata_validation=False
    )

    assert full.enable_metadata_validation is True
    assert ablation.enable_metadata_validation is False

from src.transaction import Transaction

def test_ablation_commit_abort_consistency():
    results = []

    for enabled in (True, False):
        memory = CXLSharedMemory(
            enable_metadata_validation=enabled
        )

        tx1 = Transaction(transaction_id=1)
        tx1.write("key_1")

        tx2 = Transaction(transaction_id=2)
        tx2.write("key_1")

        first = memory.commit_transaction(
            tx1, {"key_1": 100}
        )

        second = memory.commit_transaction(
            tx2, {"key_1": 200}
        )

        results.append((first, second))

    assert results [0] == results [1]
    assert results [0] == (True, False)


def test_checkpoint_snapshot():
    memory = CXLSharedMemory()

    tx = Transaction(transaction_id=100)
    tx.write("key_1")

    assert memory.commit_transaction(tx, {"key_1": 500})

    snapshot = memory.create_checkpoint_snapshot()

    assert snapshot["memory"]["key_1"][0]["value"] == 500
    assert snapshot["next_version_id"] == 2
    assert len(snapshot["committed_transactions"]) == 1
    assert snapshot["committed_transactions"][0]["status"] == "committed"
    assert len(snapshot["metadata"]["key_1"]) == 1

    memory.write(
        host_id=0,
        key="key_1",
        value=999,
        transaction_id=200
    )

    assert len(snapshot["memory"]["key_1"]) == 1
    assert snapshot["memory"]["key_1"][0]["value"] == 500


def test_save_checkpoint(tmp_path):
    import json

    memory = CXLSharedMemory()

    tx = Transaction(transaction_id=101)
    tx.write("key_1")

    assert memory.commit_transaction(tx, {"key_1": 500})

    checkpoint_path = tmp_path / "checkpoint.json"
    memory.save_checkpoint(checkpoint_path)

    assert checkpoint_path.exists()

    with open(checkpoint_path, "r", encoding="utf-8") as file:
        saved = json.load(file)

    assert saved["memory"]["key_1"][0]["value"] == 500
    assert saved["next_version_id"] == 2
    assert len(saved["committed_transactions"]) == 1
    assert saved["committed_transactions"][0]["status"] == "committed"
    assert len(saved["metadata"]["key_1"]) == 1


def test_checkpoint_restore_and_mvcc(tmp_path):
    from src.logical_clock import LogicalClock

    clock = LogicalClock()
    memory = CXLSharedMemory()

    tx1 = Transaction(transaction_id=201, clock=clock)
    tx1.write("key_1")

    assert memory.commit_transaction(tx1, {"key_1": 500})

    checkpoint_path = tmp_path / "recovery.json"
    memory.save_checkpoint(checkpoint_path)

    restored = CXLSharedMemory()
    restored_clock = restored.restore_checkpoint(checkpoint_path)

    assert restored.read_latest("key_1")["value"] == 500
    assert restored.get_stats()["total_versions"] == 1
    assert restored._next_version_id == 2
    assert len(restored._committed_transactions) == 1
    assert len(
        restored.metadata_store.get("key_1", location="cxl")
    ) == 1

    assert restored_clock.current() >= tx1.commit_timestamp

    tx2 = Transaction(transaction_id=202, clock=restored_clock)
    tx2.write("key_1")

    assert restored.commit_transaction(
        tx2, {"key_1": 999}
    ) is True

    assert restored.read_latest("key_1")["value"] == 999
    assert restored.get_stats()["total_versions"] == 2


def test_checkpoint_restore_conflict_detection(tmp_path):
    from src.logical_clock import LogicalClock

    clock = LogicalClock()
    memory = CXLSharedMemory()

    tx1 = Transaction(transaction_id=301, clock=clock)
    tx1.write("key_1")

    checkpoint_path = tmp_path / "conflict_recovery.json"

    assert memory.commit_transaction(tx1, {"key_1": 100})
    memory.save_checkpoint(checkpoint_path)

    restored = CXLSharedMemory()
    restored_clock = restored.restore_checkpoint(checkpoint_path)

    tx2 = Transaction(transaction_id=302, clock=restored_clock)
    tx3 = Transaction(transaction_id=303, clock=restored_clock)

    tx2.write("key_1")
    tx3.write("key_1")

    assert restored.commit_transaction(tx2, {"key_1": 200}) is True
    assert restored.commit_transaction(tx3, {"key_1": 300}) is False

    assert tx3.status == "aborted"
    assert restored.read_latest("key_1")["value"] == 200
    assert restored.get_stats()["total_versions"] == 2

def test_corrupted_checkpoint_preserves_state(tmp_path):
    import pytest

    memory = CXLSharedMemory()

    tx = Transaction(transaction_id=401)
    tx.write("key_1")

    assert memory.commit_transaction(tx, {"key_1": 500})

    before = memory.create_checkpoint_snapshot()

    corrupted_path = tmp_path / "corrupted.json"
    corrupted_path.write_text(
        '{"memory":',
        encoding="utf-8"
    )

    with pytest.raises(ValueError):
        memory.restore_checkpoint(corrupted_path)

    after = memory.create_checkpoint_snapshot()

    assert after == before


def test_multi_host_commit():
    memory = CXLSharedMemory()

    tx1 = Transaction(transaction_id=501)
    tx1.write("key_1")

    tx2 = Transaction(transaction_id=502)
    tx2.write("key_2")

    assert memory.commit_transaction(
        tx1, {"key_1": 100}, host_id=1
    ) is True

    assert memory.commit_transaction(
        tx2, {"key_2": 200}, host_id=2
    ) is True

    assert memory.read_latest("key_1")["host_id"] == 1
    assert memory.read_latest("key_2")["host_id"] == 2
    assert memory.get_stats()["total_versions"] == 2

def test_ablation_skips_metadata_reads():
    from unittest.mock import patch

    memory = CXLSharedMemory(
        enable_metadata_validation=False
    )

    tx = Transaction(transaction_id=601)
    tx.write("key_1")

    with patch.object(
        memory.metadata_store,
        "get",
        side_effect=AssertionError(
            "Metadata should not be read"
        )
    ):
        assert memory.commit_transaction(
            tx, {"key_1": 100}
        ) is True








