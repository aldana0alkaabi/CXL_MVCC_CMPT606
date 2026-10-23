import unittest
from concurrent.futures import ThreadPoolExecutor

try:
    from .transaction import Transaction
    from .mvcc import MVCC
    from .cxl_shared_memory import CXLSharedMemory
    from .validator import MVCCValidator
    from .logical_clock import LogicalClock
except ImportError:
    from transaction import Transaction
    from mvcc import MVCC
    from cxl_shared_memory import CXLSharedMemory
    from validator import MVCCValidator
    from logical_clock import LogicalClock


class TestConcurrentMVCC(unittest.TestCase):

    def test_concurrent_writes_same_key(self):
        shared_memory = CXLSharedMemory()

        def writer(transaction_id):
            tx = Transaction(transaction_id)
            tx.write("A")

            mvcc = MVCC(
                shared_memory=shared_memory,
                host_id=transaction_id
            )

            mvcc.write_version("A", transaction_id, transaction_id)
            tx.commit()
            return tx.status

        with ThreadPoolExecutor(max_workers=2) as executor:
            statuses = list(executor.map(writer, [1,2]))

        versions = shared_memory.read_all_versions("A")

        self.assertEqual(len(versions), 2)
        self.assertEqual(statuses, ["committed", "committed"])

    def test_validator_detects_write_conflict(self):
        validator = MVCCValidator()

        tx1 = Transaction(1)
        tx1.write("A")
        tx1.commit()

        tx2 = Transaction(2)
        tx2.write("A")

        result = validator.validate(tx2, [tx1])

        self.assertFalse(result)

    def test_sequential_writes_should_be_allowed(self):
            clock = LogicalClock()
            validator = MVCCValidator()
    
            tx1 = Transaction(1, clock)
            tx1.write("A")
            tx1.commit()
    
            tx2 = Transaction(2, clock)
            tx2.write("A")

            self.assertLess(
                tx1.commit_timestamp,
                tx2.start_timestamp
            )
    
            result = validator.validate(tx2, [tx1])
    
            self.assertTrue(result)

    def test_overlapping_writes_conflict(self):
            clock = LogicalClock()
            validator = MVCCValidator()
        
            tx1 = Transaction(1, clock)
            tx2 = Transaction(2, clock)
            
            tx1.write("A")
            tx2.write("A")
            
            tx1.commit()
    
            self.assertLess(
                tx2.start_timestamp,
                tx1.commit_timestamp
            )
        
            result = validator.validate(tx2, [tx1])
        
            self.assertFalse(result)

    def test_atomic_commit_rejects_conflicting_writes(self):
        clock = LogicalClock()
        shared_memory = CXLSharedMemory()
        validator = MVCCValidator()
        
        tx1 = Transaction(1, clock)
        tx2 = Transaction(2, clock)
            
        tx1.write("A")
        tx2.write("A")
            
        result1 = shared_memory.commit_transaction(
             tx1, {"A": 100}
        )

        result2 = shared_memory.commit_transaction(
             tx2, {"A": 200}
        )
    
        self.assertTrue(result1)
        self.assertFalse(result2)
        self.assertEqual(tx1.status, "committed")
        self.assertEqual(tx2.status, "aborted")
        self.assertEqual(
            shared_memory.read_latest("A")["value"], 100
        )

    def test_concurrent_atomic_commit(self):
         clock = LogicalClock()
         shared_memory = CXLSharedMemory()

         tx1 = Transaction(1, clock)
         tx2 = Transaction(2, clock)

         tx1.write("A")
         tx2.write("A")

         def commit_worker(item):
              tx, value = item 
              return shared_memory.commit_transaction(
                   tx, {"A": value}
              )

         with ThreadPoolExecutor(max_workers=2) as executor:
              results = list(executor.map(
                   commit_worker,
                   [(tx1, 100), (tx2, 200)]
              ))

         self.assertEqual(results.count(True), 1)
         self.assertEqual(results.count(False), 1)
    
         versions = shared_memory.read_all_versions("A")
         self.assertEqual(len(versions), 1)

    def test_atomic_commit_stress(self):
         clock = LogicalClock()
         shared_memory = CXLSharedMemory()

         transactions = [
              Transaction(i, clock) for i in range(100)
         ]

         for tx in transactions:
              tx.write("A")
         def commit_worker(tx):
             return shared_memory.commit_transaction(
                 tx, {"A": tx.transaction_id}
             )

         with ThreadPoolExecutor(max_workers=10) as executor:
              results = list(executor.map(
                   commit_worker, transactions
              ))

         self.assertEqual(results.count(True), 1)
         self.assertEqual(results.count(False), 99)

         versions = shared_memory.read_all_versions("A")
         self.assertEqual(len(versions), 1)

    if __name__ == "__main__":
        unittest.main()
 
