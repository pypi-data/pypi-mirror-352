from typing import Any

__all__ = ["labyr", "LabyrGame"]


class LabyrGame:
    def __init__(self) -> None:
        self.tvar = 123

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        print("hello from labyr! " + str(self.tvar) + "\nUt et eiusmod enim do dolor.")


labyr = LabyrGame()
