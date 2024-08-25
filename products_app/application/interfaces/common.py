from typing import Protocol
import datetime as dt


class UUIDGenerator(Protocol):
    def __call__(self) -> str: ...


class DateTimeNowGenerator(Protocol):
    def __call__(self) -> dt.datetime: ...
