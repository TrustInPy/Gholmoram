import time
from collections import deque


class FailMeter:
    def __init__(self, count, window):
        """
        Arguments
            `count`: number of tolerable occurrences
            `window`: time window (seconds)
        """
        self._max_count = count
        self._window = window
        self._oc = deque()  # Occurrences

    def trigger(self):
        """
        Report occurrence of failure.

        Returns
            `True` if the threshold is exceeded
            `False` if the threshold is not exceeded yet
        """
        self._oc.append(int(time.time()))
        return self._check()

    def _check(self):
        self._cleanup()
        if len(self._oc) > self._max_count:
            return True
        return False

    def _cleanup(self):
        now = int(time.time())
        while True:
            if self._oc[0] < now - self._window:
                self._oc.popleft()
            else:
                break
