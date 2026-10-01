class MVCCValidator:

    def validate(self, transaction, other_transactions):
        for other in other_transactions:

            if other.transaction_id == transaction.transaction_id:
                continue

            #Read-Write Conflict
            if transaction.read_set & other.write_set:
                return False

            #Write-Write Conflict
            if transaction.write_set & other.write_set:
                return False

            #Write-Read Conflict
            if transaction.write_set & other.read_set:
                return False

        return True