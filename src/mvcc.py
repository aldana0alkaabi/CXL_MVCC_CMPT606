class MVCC:
    def __init__(self):
        self.versions = {}
        self.next_version_id = 1

    def write_version(self, key, value, transaction_id):
        if key not in self.versions:
            self.versions[key] = []

        version_id = len(self.versions[key]) + 1

        self.versions[key].append({
        "value": value,
        "transaction_id": transaction_id,
        "version_id": version_id
        })

        self.next_version_id += 1

