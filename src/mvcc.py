try:
    from .cxl_shared_memory import CXLSharedMemory
except ImportError:
    from cxl_shared_memory import CXLSharedMemory

class MVCC:
    def __init__(self, shared_memory=None, host_id=0):
        self.shared_memory = (
            shared_memory if shared_memory is not None
            else CXLSharedMemory()
        )
        self.host_id = host_id

    def write_version(self, key, value, transaction_id):
        return self.shared_memory.write(
            host_id=self.host_id,
            key=key,
            value=value,
            transaction_id=transaction_id   
        )

    def read_latest_version(self, key):
        return self.shared_memory.read_latest(key)
    

