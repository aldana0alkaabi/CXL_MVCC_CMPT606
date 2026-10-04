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

if __name__ == "__main__":
    unittest.main()
