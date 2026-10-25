class MVCCValidator:

    def __init__(self, metadata_store=None, metadata_location="local", enable_metadata_validation=True):
        if metadata_location not in ("local", "cxl"):
            raise ValueError("Unsupported metadata location")

        if metadata_location not in ("local", "cxl"):
            raise ValueError("Unsupported metadata location")
        self.metadata_store = metadata_store
        self.metadata_location = metadata_location
        self.enable_metadata_validation = enable_metadata_validation

    
    def read_metadata(self, key):
        if not self.enable_metadata_validation:
            return None

        if self.metadata_store is None:
            return None

        return self.metadata_store.get(
            key,
            location=self.metadata_location
        )


    def read_committed_metadata(self, key):
        records = self.read_metadata(key)

        if records is None:
            return []

        if isinstance(records, dict):
            records = [records]

        return [
            record for record in records
            if record.get("status") == "committed"
        ]

    def validate(self, transaction, other_transactions):

        if self.metadata_store is not None:
            keys = transaction.read_set | transaction.write_set

            for key in keys:
                records = self.read_committed_metadata(key)

                for record in records:
                    if record["transaction_id"] == transaction.transaction_id:
                        continue

                    if (
                        transaction.start_timestamp is not None
                        and record.get("commit_timestamp") is not None
                        and any(
                            other.transaction_id == record["transaction_id"]
                            and other.clock is transaction.clock
                            for other in other_transactions
                        )
                        and record["commit_timestamp"] < transaction.start_timestamp
                    ):
                        continue

                    other_reads = set(record["read_set"])
                    other_writes = set(record["write_set"])

                    if (
                        transaction.read_set & other_writes
                        or transaction.write_set & other_writes
                        or transaction.write_set & other_reads
                    ):
                        return False
        
        for other in other_transactions:

            # Ignore the same transaction
            if other.transaction_id == transaction.transaction_id:
                continue

            # Ignore aborted transactions
            if other.status == "aborted":
                continue

            # Ignore active transactions for this basic test
            if other.status != "committed":
                continue  
            if (
                transaction.start_timestamp is not None
                and other.commit_timestamp is not None
                and transaction.clock is not None
                and transaction.clock is other.clock
                and other.commit_timestamp < transaction.start_timestamp
            ):
                continue  

            # Read-Write Conflict
            if transaction.read_set & other.write_set:
                return False

            # Write-Write Conflict
            if transaction.write_set & other.write_set:
                return False

            # Write-Read Conflict
            if transaction.write_set & other.read_set:
                return False

        return True