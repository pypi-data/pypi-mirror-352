import logging
import sys
from queue import Queue
from threading import Event, Thread
from typing import Callable, Generator, TypeAlias

import polars as pl

from .models import ColName, FrameWindow, LiveFrame, Strategy, _bar_columns

OutputHandler: TypeAlias = Callable[[LiveFrame], None]
ErrHandler: TypeAlias = Callable[[Exception], None]

_logger = logging.getLogger("pinepy")
_handler = logging.StreamHandler(stream=sys.stdout)
_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
_logger.addHandler(_handler)
_logger.setLevel(logging.DEBUG)


class LiveTransport:
    def __init__(
        self,
        err_handler: ErrHandler,
    ):
        self._input = Queue[LiveFrame]()
        self._event = Event()
        self._output: Queue[Exception] = Queue[Exception]()

        self.err_handler = err_handler
        self._on_output()

    def _put_err(self, err: Exception):
        self._output.put_nowait(err)

    def append_frame(self, frame: LiveFrame):
        self._input.put(frame)

    def _on_output(self):
        def handle_output():
            while not self._event.is_set():
                output = self._output.get()
                self.err_handler(output)

        Thread(target=handle_output).start()

    def stop(self):
        self._event.set()


class FrameEngine:
    def _roll_window(
        self,
        strategy: Strategy,
        window: FrameWindow,
        warm_window: FrameWindow | None = None,
    ):
        data = window.data
        warm_index = strategy.warm_up()
        end_index = warm_index
        if warm_window is not None:
            data = warm_window.data.tail(warm_index).vstack(data, in_place=True)
        strategy._init(data)
        while end_index < data.height:
            data_partial = data.slice(0, end_index + 1)
            strategy._slice(end_index + 1)
            strategy.next(
                open=data_partial[ColName.open],
                high=data_partial[ColName.high],
                low=data_partial[ColName.low],
                close=data_partial[ColName.close],
                volume=data_partial[ColName.volume],
                ts=data_partial[ColName.ts],
                addl=data_partial.select(pl.exclude(_bar_columns)),
                bar_index=end_index,
                live_latest=False,
            )
            end_index += 1

    def backtest(
        self, strategy: Strategy, window_generator: Generator[FrameWindow, None, None]
    ):
        """
        warm window could bigger than all window, backtest cannot tell it in advance
        """
        last_window: FrameWindow | None = None
        for window in window_generator:
            if last_window is None and window.data.height < strategy.warm_up():
                _logger.warning(
                    "Warm up window is smaller than warm up period, "
                    "would not run for the first window"
                )
            self._roll_window(strategy, window, last_window)
            last_window = window

    def live(
        self,
        strategy: Strategy,
        warm_frames: FrameWindow,
        err_handler: ErrHandler,
        window_size: int = 500,
    ) -> LiveTransport:
        self._roll_window(strategy, warm_frames)
        data = warm_frames.data
        bar_index = len(data) - 1
        warm = strategy.warm_up()
        transport = LiveTransport(err_handler)
        if strategy.warm_up() > window_size:
            window_size = strategy.warm_up() + 10

        def run_loop():
            nonlocal data, bar_index
            while not transport._event.is_set():
                try:
                    tick_append: LiveFrame = transport._input.get()
                    data.vstack(pl.DataFrame(tick_append.row), in_place=True)
                    strategy._live_next(tick_append)
                    strategy._slice(data.height)
                    bar_index += 1
                    if data.height > warm:
                        strategy.next(
                            open=data[ColName.open],
                            high=data[ColName.high],
                            low=data[ColName.low],
                            close=data[ColName.close],
                            volume=data[ColName.volume],
                            ts=data[ColName.ts],
                            addl=data.select(pl.exclude(_bar_columns)),
                            bar_index=bar_index,
                            live_latest=True,
                        )
                    if data.shape[0] >= 2 * window_size:
                        data = data.tail(window_size)
                        strategy._tail(window_size)
                except Exception as e:
                    transport._put_err(e)

        Thread(target=run_loop).start()
        return transport
