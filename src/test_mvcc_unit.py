import unittest
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from transaction import Transaction
from mvcc import MVCC
from validator import MVCCValidator


class TestMVCC(unittest.TestCase):

    def test_transaction_commit(self):
        tx = Transaction("T1")
        tx.commit()
        self.assertEqual(tx.status, "committed")

    def test_transaction_abort(self):
        tx = Transaction("T1")
        tx.abort()
        self.assertEqual(tx.status, "aborted")

    def test_write_and_read_latest_version(self):
        mvcc = MVCC()
        mvcc.write_version("A", 100, "T1")
        mvcc.write_version("A", 200, "T2")
        self.assertEqual(mvcc.read_latest_version("A")["value"], 200)

    def test_read_missing_key(self):
        mvcc = MVCC()
        self.assertIsNone(mvcc.read_latest_version("missing"))

    def test_validator_accepts_non_conflicting_transactions(self):
        validator = MVCCValidator()
       
        tx1 = Transaction("T1")
        tx1.write("A")
        tx1.commit()

        tx2 = Transaction("T2")
        tx2.write("B")

        self.assertTrue(validator.validate(tx2, [tx1]))

    def test_validator_rejects_conflicting_transactions(self):
        validator = MVCCValidator()
       
        tx1 = Transaction("T1")
        tx1.write("A")
        tx1.commit()

        tx2 = Transaction("T2")
        tx2.write("A")

        self.assertFalse(validator.validate(tx2, [tx1]))

    def test_shared_memory_between_hosts(self):
        from cxl_shared_memory import CXLSharedMemory

        shared_memory = CXLSharedMemory()
        mvcc_host1 = MVCC(shared_memory=shared_memory, host_id=1)
        mvcc_host2 = MVCC(shared_memory=shared_memory, host_id=2)

        mvcc_host1.write_version("A", 100, "T1")

        result = mvcc_host2.read_latest_version("A")

        self.assertEqual(result["value"], 100)
        self.assertEqual(result["host_id"], 1)

    def test_benchmark_cxl_shared_memory(self):
        from src.cxl_shared_memory import CXLSharedMemory
        from src.mvcc import MVCC

        shared = CXLSharedMemory()
        mvcc = MVCC(shared_memory=shared, host_id=1)

        mvcc.write_version("benchmark_key", 10, 1)

        result = mvcc.read_latest_version("benchmark_key")

        assert result["value"] == 10
        assert result ["host_id"] == 1
        assert shared.get_stats()["total_versions"] == 1



if __name__ == "__main__":
    unittest.main()
