from abc import ABC, abstractmethod


class GCSProgram(ABC):
    def __init__(self):
        self._started = False

    def start(self):
        if not self._started:
            self._start()

    def stop(self):
        if self._started:
            self._stop()

    @abstractmethod
    def _start(self):
        pass

    @abstractmethod
    def _stop(self):
        pass
