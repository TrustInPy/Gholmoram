import time
from collections import deque


class FailMeter:
    def __init__(self, threshold, window):
        """
        Args:
            `threshold`: number of tolerable occurrences
            `window`: time window (seconds)
        """
        self.__threshold = threshold
        self.__window = window
        self.__oc = deque()  # Occurrences

    def trigger(self):
        """
        Report occurrence of failure.

        Returns:
            `True` if the threshold is exceeded
            `False` if the threshold is not exceeded yet
        """
        self.__oc.append(int(time.time()))
        return self.__check()

    def __check(self):
        self.__cleanup()
        if len(self.__oc) > self.__threshold:
            return True
        return False

    def __cleanup(self):
        now = int(time.time())
        while True:
            if self.__oc[0] < now - self.__window:
                self.__oc.popleft()
            else:
                break
