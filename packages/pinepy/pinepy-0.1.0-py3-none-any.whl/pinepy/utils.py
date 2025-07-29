from typing import Callable, TypeAlias

import polars as pl

from .models import ColName

Num: TypeAlias = int | float
NumList: TypeAlias = list[Num] | pl.Series
CalcBar: TypeAlias = Callable[[pl.DataFrame], list[float]]


def crossover(series1: NumList, series2: NumList | Num) -> bool:
    try:
        if isinstance(series2, Num):
            return series1[-1] > series2 and series1[-2] < series2
        else:
            return series1[-1] > series2[-1] and series1[-2] < series2[-2]
    except IndexError:
        return False


def crossunder(series1: NumList, series2: NumList | Num) -> bool:
    try:
        if isinstance(series2, Num):
            return series1[-1] < series2 and series1[-2] > series2
        else:
            return series1[-1] < series2[-1] and series1[-2] > series2[-2]
    except IndexError:
        return False


def cross(series1: NumList, series2: NumList | Num) -> bool:
    return crossover(series1, series2) or crossunder(series1, series2)


def between(this: Num, up: Num, down: Num) -> bool:
    if this <= up and this >= down:
        return True
    return False


def hlc3() -> CalcBar:
    def calc_hlc(data: pl.DataFrame) -> list[float]:
        return data.select(
            pl.mean_horizontal(
                pl.col([ColName.close, ColName.high, ColName.low]).alias("hlc")
            )
        )["hlc"].to_list()

    return calc_hlc
