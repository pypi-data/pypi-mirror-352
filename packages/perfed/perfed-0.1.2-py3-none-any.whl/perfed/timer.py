import time
from typing import Literal

from perfed.util import convert_from_ns


class Timer:
    """A single timer.
    """
    def __init__(self, name: str) -> None:
        self._name: str = name
        self._start: int = -1
        self._stop: int = -1

    def start(self) -> None:
        """Start timer. Ignores multiple starts.
        """
        if self._start < 0:
            self._start = time.perf_counter_ns()

    def stop(self) -> None:
        """Stop timer. Ignores multiple stops.
        """
        if self._stop < 0:
            self._stop = time.perf_counter_ns()

    def __enter__(self) -> None:
        self.start()

    def __exit__(self, _type, _value, _traceback) -> bool:
        self.stop()
        return True

    def get(self, unit: Literal["ns", "ms", "sec", "min"] = "sec") -> float:
        """Get timer duration.

        Args:
            unit (Literal["ns", "ms", "sec", "min"], optional):
                The unit of time to return the timer duration in.
                Accepts "ns" for nanoseconds, "ms" for milliseconds, "sec" for seconds,
                and "min" for minutes. Defaults to "sec".

        Raises:
            RuntimeError: Timer has not been started.

        Returns:
            float: Timer duration.
        """
        if self._start < 0:
            raise RuntimeError("Timer has not been started.")

        curr_stop = self._stop if self._stop > 0 else time.perf_counter_ns()
        timer_value = curr_stop - self._start

        return convert_from_ns(time_ns=timer_value, unit=unit)
