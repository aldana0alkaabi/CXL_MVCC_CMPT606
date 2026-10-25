from threading import Lock

class LogicalClock:
    def __init__(self, initial_value=0):
        self._counter = initial_value
        self._lock = Lock()

    def tick(self):
        with self._lock:
            self._counter +=1
            return self._counter

    def current(self):
        with self._lock:
            return self._counter

    
    def advance_to(self, value):
        """Advance the clock without moving it backwards."""
        with self._lock:
            if value < self._counter:
                raise ValueError("Cannot move logical clock backwards")
            self._counter = value
