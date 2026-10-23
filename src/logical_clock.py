from threading import Lock

class LogicalClock:
    def __init__(self):
        self._counter = 0
        self._lock = Lock()

    def tick(self):
        with self._lock:
            self._counter +=1
            return self._counter