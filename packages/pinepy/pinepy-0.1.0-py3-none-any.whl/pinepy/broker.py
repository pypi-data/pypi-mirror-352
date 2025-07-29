from math import sqrt
from typing import Any

import polars as pl


class OrderRecords:
    def __init__(self) -> None:
        self.records = pl.DataFrame(
            schema={
                "ts": pl.Int64,
                "id": pl.Int64,
                "side": pl.Int64,
                "price": pl.Float64,
                "amt": pl.Float64,
                "close": pl.Boolean,
                "cleared": pl.Boolean,
                "cash": pl.Float64,
                "profit": pl.Float64,
                "profit%": pl.Float64,
                "comment": pl.Utf8,
            }
        )

    def append(
        self,
        id: int,
        side: int,
        ts: int,
        price: float,
        amt: float,
        comment: str,
        close: bool,
        cleared: bool,
        cash: float,
        profit: float,
        profit_percent: float,
    ):
        p = pl.DataFrame(
            {
                "ts": int(ts),
                "id": int(id),
                "side": int(side),
                "price": float(price),
                "amt": float(amt),
                "close": bool(close),
                "cleared": bool(cleared),
                "cash": float(cash),
                "profit": float(profit),
                "profit%": float(profit_percent),
                "comment": str(comment),
            }
        )
        self.records.vstack(
            p,
            in_place=True,
        )


class TradeStats:
    def __init__(self, records: OrderRecords):
        self.sqn = 0.0
        self.sharpe = 0.0
        self.max_drawdown = 0.0
        self.avg_drawdown = 0.0
        self.win_rate = 0.0
        self.profit_factor = 0.0
        self.avg_profit_percent = 0.0
        self.avg_duration = 0.0
        self.profit_percent = 0.0
        self.exposure_percent = 0.0
        # calc
        r = records.records
        self.profit_percent = r["profit%"].sum()
        grouped = r.group_by("id").agg(
            total_profit=pl.col("profit").sum(),
        )
        # sqn
        n_trades = grouped.height
        if n_trades > 0:
            mean_profit = grouped["total_profit"].mean()
            std_profit = grouped["total_profit"].std()
            if isinstance(mean_profit, float) and isinstance(std_profit, float):
                if std_profit == 0:
                    self.sqn = float("inf") if mean_profit > 0 else 0.0
                else:
                    self.sqn = sqrt(n_trades) * (mean_profit / std_profit)
        else:
            self.sqn = 0.0
        # win rate
        total_trades = grouped.height
        winning_trades = grouped.filter(pl.col("total_profit") > 0).height
        win_rate = winning_trades / total_trades if total_trades > 0 else 0.0
        self.win_rate = win_rate
        # profit factor
        total_gains = grouped.filter(pl.col("total_profit") > 0)["total_profit"].sum()
        total_losses = abs(
            grouped.filter(pl.col("total_profit") < 0)["total_profit"].sum()
        )
        profit_factor = total_gains / total_losses if total_losses > 0 else float("inf")
        self.profit_factor = profit_factor
        # avg profit percent
        trade_count = r["id"].max()
        if isinstance(trade_count, int):
            self.avg_profit_percent = self.profit_percent / trade_count


class Broker:
    def __init__(
        self,
        cash: float = 100000,
        amt_precision: int = 3,
    ):
        # init user choose params
        self._cash = cash
        self._amt_precision = amt_precision
        # init status
        self._position_amt = 0.0
        self._entry_price = 0.0
        self._entry_cash = 0.0
        self._increment_id = 0
        self._records = OrderRecords()

    def stats(self) -> TradeStats:
        return TradeStats(self._records)

    def not_holding(self) -> bool:
        return self._position_amt == 0

    def _close(
        self,
        ts: int,
        price: float,
        position_side: int,
        comment: str,
        ratio: float = 1,
    ):
        if self._position_amt == 0:
            return False
        position_side = 1 if position_side > 0 else -1
        if ratio > 1:
            ratio = 1
        if ratio < 0:
            ratio = 0
        exec_amt = position_side * _precision_decimal(
            ratio * self._position_amt, self._amt_precision
        )
        # change status
        self._position_amt -= exec_amt
        profit = exec_amt * (price - self._entry_price)
        self._cash = self._entry_cash + profit
        # add record
        self._records.append(
            id=self._increment_id,
            side=position_side,
            ts=ts,
            price=price,
            amt=exec_amt,
            comment=comment,
            close=True,
            cleared=True if self._position_amt == 0 else False,
            cash=self._cash,
            profit=profit,
            profit_percent=(profit / self._entry_cash) * 100,
        )

    def _open(
        self,
        ts: int,
        price: float,
        position_side: int,
        comment: str,
        sizing: float = 1,
    ) -> bool | Any:
        position_side = 1 if position_side > 0 else -1
        if self._position_amt * position_side > 0:
            return False
        elif self._position_amt * position_side < 0:
            self._close(ts, price, -position_side, "reverse", 1)
        if sizing > 1:
            sizing = 1
        if sizing < 0:
            sizing = 0
        exec_amt = (
            position_side
            * _precision_decimal(self._cash / price, self._amt_precision)
            * sizing
        )
        # change status
        self._increment_id += 1
        self._entry_cash = self._cash
        self._cash -= abs(exec_amt * price)
        self._position_amt = exec_amt
        self._entry_price = price
        # add record
        self._records.append(
            id=self._increment_id,
            side=position_side,
            ts=ts,
            price=price,
            amt=exec_amt,
            comment=comment,
            close=False,
            cleared=False,
            cash=self._entry_cash,
            profit=0,
            profit_percent=0,
        )


class DefaultBroker(Broker):
    def __init__(self, cash=100000, amt_precision=3):
        super().__init__(cash, amt_precision)

    def open(
        self,
        ts: int,
        price: float,
        position_side: int,
        comment: str,
        sizing: float = 1,
    ) -> bool | Any:
        return super()._open(ts, price, position_side, comment, sizing)

    def close(
        self,
        ts: int,
        price: float,
        position_side: int,
        comment: str,
        ratio: float = 1,
    ):
        return super()._close(ts, price, position_side, comment, ratio)


def _precision_decimal(num, precision=2):
    return int(num * (10**precision)) / (10**precision)
