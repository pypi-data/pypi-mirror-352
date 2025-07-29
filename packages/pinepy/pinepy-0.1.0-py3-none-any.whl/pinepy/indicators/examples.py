from polars import DataFrame
from talipp import indicators
from talipp.ohlcv import OHLCVFactory

from ..models import ColName, Indicator
from ..utils import CalcBar


class EMA(Indicator):
    def __init__(
        self,
        ema_len: int = 3,
        calc: CalcBar | None = None,
    ):
        self.len = ema_len
        if calc is None:

            def c(data: DataFrame):
                return data[ColName.close].to_list()

            self.calc = c
        else:
            self.calc = calc

    def var(self):
        return self.ema.output_values[: self.head]

    def _init(self, data: DataFrame):
        self.ema = indicators.EMA(self.len, self.calc(data))

    def _live_next(self, data_row: DataFrame):
        return super()._live_next(data_row)

    def _tail(self, tail: int):
        self.ema.purge_oldest(len(self.ema.output_values) - tail)


class SMA(Indicator):
    def __init__(
        self,
        sma_len: int = 3,
        calc: CalcBar | None = None,
    ):
        self.len = sma_len
        if calc is None:

            def c(data: DataFrame):
                return data[ColName.close].to_list()

            self.calc = c
        else:
            self.calc = calc

    def var(self):
        return self.sma.output_values[: self.head]

    def _live_next(self, data_row: DataFrame):
        self.sma.add(*self.calc(data_row))

    def _tail(self, tail: int):
        self.sma.purge_oldest(len(self.sma.output_values) - tail)

    def _init(self, data: DataFrame):
        self.sma = indicators.SMA(self.len, self.calc(data))


class HeikinAshi(Indicator):
    def _live_next(self, data_row: DataFrame):
        open, high, low, close = (
            data_row[ColName.open][-1],
            data_row[ColName.high][-1],
            data_row[ColName.low][-1],
            data_row[ColName.close][-1],
        )
        hopen, hclose = (
            (self.hopen[-1] + self.hclose[-1]) / 2,
            (open + high + low + close) / 4,
        )
        hhigh, hlow = (
            max(high, hopen, hclose),
            min(low, hopen, hclose),
        )
        self.hopen.append(hopen)
        self.hclose.append(hclose)
        self.hhigh.append(hhigh)
        self.hlow.append(hlow)

    def _tail(self, tail: int):
        self.hclose = self.hclose[-tail:]
        self.hopen = self.hopen[-tail:]
        self.hhigh = self.hhigh[-tail:]
        self.hlow = self.hlow[-tail:]

    def _init(self, data: DataFrame):
        self.hclose, self.hopen, self.hhigh, self.hlow = [], [], [], []
        for i in range(data.height):
            self.hopen.append(
                0 if i == 0 else (self.hopen[i - 1] + self.hclose[i - 1]) / 2
            )
            self.hclose.append(
                (
                    data[ColName.close][i]
                    + data[ColName.open][i]
                    + data[ColName.high][i]
                    + data[ColName.low][i]
                )
                / 4
            )
            self.hhigh.append(max(data[ColName.high][i], self.hopen[i], self.hclose[i]))
            self.hlow.append(min(data[ColName.low][i], self.hopen[i], self.hclose[i]))

    def var(self):
        return (
            self.hopen[: self.head],
            self.hhigh[: self.head],
            self.hlow[: self.head],
            self.hclose[: self.head],
        )


class CCI(Indicator):
    def __init__(
        self,
        cci_len: int = 14,
        cci_ma_len: int = 3,
    ):
        self.len = cci_len
        self.ma_len = cci_ma_len

    def var(self):
        return self.cci.output_values[: self.head], self.cci_ma.output_values[
            : self.head
        ]

    def _init(self, data: DataFrame):
        self.cci = indicators.CCI(
            period=self.len,
            input_values=OHLCVFactory.from_dict(
                {
                    "high": data[ColName.high].to_list(),
                    "low": data[ColName.low].to_list(),
                    "close": data[ColName.close].to_list(),
                }
            ),
        )
        self.cci_ma = indicators.SMA(
            period=self.ma_len, input_values=self.cci.output_values
        )

    def _live_next(self, data_row: DataFrame):
        self.cci.add(
            OHLCVFactory.from_dict(
                {
                    "high": data_row[ColName.high].to_list(),
                    "low": data_row[ColName.low].to_list(),
                    "close": data_row[ColName.close].to_list(),
                }
            )
        )
        self.cci_ma.add(self.cci.output_values[-1])

    def _tail(self, tail: int):
        self.cci.purge_oldest(len(self.cci.output_values) - tail)
        self.cci_ma.purge_oldest(len(self.cci_ma.output_values) - tail)
