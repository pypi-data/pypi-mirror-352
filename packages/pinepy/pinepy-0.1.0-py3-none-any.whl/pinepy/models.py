import logging
import sys
from abc import ABCMeta, abstractmethod
from typing import Any, Literal, TypeAlias

import polars as pl

DataRow: TypeAlias = pl.DataFrame

FrameCols: TypeAlias = Literal["open", "high", "low", "close", "volume", "ts"]


class ColName:
    open = "open"
    high = "high"
    low = "low"
    close = "close"
    volume = "volume"
    ts = "ts"


_bar_columns = [
    i
    for i in [
        ColName.open,
        ColName.high,
        ColName.low,
        ColName.close,
        ColName.volume,
        ColName.ts,
    ]
]
_must_have_set = set(_bar_columns)
WRONG_COLUMN = ValueError("data must have columns: {}".format(_bar_columns))

_logger = logging.getLogger("strategy")
_handler = logging.StreamHandler(stream=sys.stdout)
_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
_logger.addHandler(_handler)
_logger.setLevel(logging.DEBUG)


class FrameWindow:
    def __init__(self, data: pl.DataFrame):
        if not _must_have_set.issubset(set(data.columns)):
            raise WRONG_COLUMN
        self.data = data


class LiveFrame:
    def __init__(
        self,
        open: float,
        high: float,
        low: float,
        close: float,
        volume: float,
        ts: int,
        addl: dict[str, Any] | None = None,
    ):
        self.ts = ts
        self.row = {
            ColName.open: open,
            ColName.high: high,
            ColName.low: low,
            ColName.close: close,
            ColName.volume: volume,
            ColName.ts: ts,
        }
        if addl is not None:
            self.row.update(addl)


class Indicator(metaclass=ABCMeta):
    def _slice(self, head: int):
        self.head = head

    @abstractmethod
    def var(self) -> Any:
        pass

    @abstractmethod
    def _tail(self, tail: int):
        pass

    @abstractmethod
    def _live_next(self, data_row: pl.DataFrame):
        pass

    @abstractmethod
    def _init(self, data: pl.DataFrame):
        pass


class Strategy(metaclass=ABCMeta):
    """
    you can choose which time to init broker,
    for example, you can init broker in __init__, then you can use self.broker in next() with fixed logic
    or you can init when you create different variable of Strategy to backtest or live trade,
    and recognize the condition(backtest or live trade) in next() to use different broker
    """

    @property
    def Log(self) -> logging.Logger:
        return _logger

    def _live_next(self, tick_append: LiveFrame):
        row = pl.DataFrame(tick_append.row)
        for i in self._indicators:
            i._live_next(row)

    def _init(self, data: pl.DataFrame):
        self._indicators = self.use_indicators()
        for i in self._indicators:
            i._init(data)

    def _slice(self, head: int):
        for i in self._indicators:
            i._slice(head)

    def _tail(self, tail: int):
        for i in self._indicators:
            i._tail(tail)

    @abstractmethod
    def warm_up(self) -> int:
        pass

    @abstractmethod
    def use_indicators(self) -> list[Indicator]:
        pass

    @abstractmethod
    def next(
        self,
        open: pl.Series,
        high: pl.Series,
        low: pl.Series,
        close: pl.Series,
        volume: pl.Series,
        ts: pl.Series,
        addl: pl.DataFrame,
        bar_index: int,
        live_latest: bool,
    ):
        pass
