class Signal:
    def __init__(self) -> None:
        self._done = False

    def do(self):
        self._done = True

    @property
    def did(self):
        return self._done
