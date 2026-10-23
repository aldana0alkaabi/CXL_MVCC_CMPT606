class Transaction:
    def __init__(self, transaction_id, clock=None):
        self.transaction_id = transaction_id
        self.clock = clock
        self.start_timestamp = clock.tick() if clock is not None else None
        self.commit_timestamp = None
        self.read_set = set()
        self.write_set = set()
        self.status = "active"

    def read(self, key):
        self.read_set.add(key)

    def write(self, key):
        self.write_set.add(key)

    def commit(self):
        if self.clock is not None:
            self.commit_timestamp = self.clock.tick()
        self.status = "committed"

    def abort(self):
        self.status = "aborted"