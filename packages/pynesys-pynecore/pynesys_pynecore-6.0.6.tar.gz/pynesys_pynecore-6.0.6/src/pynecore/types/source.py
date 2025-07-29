from .series import Series
from .na import NA


class Source(Series[float]):
    """
    Represents a built-in source like "open", "high", "low", "close", "hl2", etc.
    """

    # noinspection PyMissingConstructor
    def __init__(self, name: str) -> None:
        self.name = name

    def __getitem__(self, index: int) -> float | NA[float]:
        return NA(float)
