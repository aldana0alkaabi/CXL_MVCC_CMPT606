class Transaction:
    def __init__(self, transaction_id):
        self.transaction_id = transaction_id
        self.read_set = set()
        self.write_set = set()
        self.status = "active"

    def read(self, key):
        self.read_set.add(key)

    def write(self, key):
        self.write_set.add(key)

    def commit(self):
        self.status = "committed"

    def abort(self):
        self.status = "aborted"