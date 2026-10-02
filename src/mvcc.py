class MVCC:
    def __init__(self):
        self.versions = {}
        self.next_version_id = 1

    def write_version(self, key, value, transaction_id):
        if key not in self.versions:
            self.versions[key] = []

        version_id = self.next_version_id

        self.versions[key].append({
        "value": value,
        "transaction_id": transaction_id,
        "version_id": version_id
        })

        self.next_version_id += 1

    def read_latest_version(self, key):
        if key not in self.versions:
            return None
        return self.versions[key][-1]

