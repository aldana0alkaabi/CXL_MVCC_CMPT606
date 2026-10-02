class MVCCValidator:

    def validate(self, transaction, other_transactions):
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