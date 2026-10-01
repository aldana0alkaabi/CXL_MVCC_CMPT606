from transaction import Transaction
from mvcc import MVCC
from validator import MVCCValidator

#Create transaction
t1 = Transaction("T1")
t2 = Transaction("T2")

#Define operations
t1.write("A")
t2.read("A")

#Create MVCC and validator
mvcc = MVCC()
validator = MVCCValidator()

#Store a version
mvcc.write_version("A", 100, t1.transaction_id)

#Validate T2
result = validator.validate(t2, [t1])

#Print result
print("T2 validation result:", result)
