import json
from typing import Callable, Dict, List, Literal, Tuple

import pandas as pd
from tabulate import tabulate

from perfed.timer import Timer
from perfed.util import convert_from_ns


class TimerManager:
    """Manages a collection of timers.
    """
    def __init__(self, name: str = "") -> None:
        self._name = name
        self._timers: Dict[str, Timer] = {}

    def __len__(self) -> int:
        return len(self._timers)

    def _create_timer(self, name: str) -> Timer:
        """Create a timer.

        Args:
            name (str): Name of timer

        Raises:
            ValueError: Timer with name already exists.

        Returns:
            Timer: Created timer.
        """
        if name in self._timers:
            raise ValueError(f"Timer with the name: {name} already exists.")

        timer = Timer(name=name)
        self._timers[name] = timer
        return timer

    def start(self, name: str) -> Timer:
        """Create and start a timer.

        Args:
            name (str): Name of timer.

        Returns:
            Timer: Started timer.
        """
        timer = self._create_timer(name)
        timer.start()
        return timer

    def stop(self, name: str) -> None:
        """Stop a timer.

        Args:
            name (str): Name of timer.

        Raises:
            ValueError: Timer with name does not exist.
        """
        if (timer := self._timers.get(name)) is None:
            raise ValueError(f"Timer with the name {name} does not exist.")

        timer.stop()

    def to_tuples(self, unit: Literal["ns", "ms", "sec", "min"] = "sec") -> List[Tuple[str, float]]:
        """Return timers in list of tuples format.

        Args:
            unit (Literal["ns", "ms", "sec", "min"], optional):
                The unit of time to display the durations.
                Accepts "ns" for nanoseconds, "ms" for milliseconds, "sec" for seconds,
                and "min" for minutes. Defaults to "sec".

        Returns:
            List[Tuple[str, float]]: List of tuples with each tuple containing the timer name and its duration.
        """
        return [(name, timer.get(unit=unit)) for name, timer in self._timers.items()]

    def to_dict(self, unit: Literal["ns", "ms", "sec", "min"] = "sec") -> Dict[str, float]:
        """Return timers in dictionary format.

        Args:
            unit (Literal["ns", "ms", "sec", "min"], optional):
                The unit of time to display the durations.
                Accepts "ns" for nanoseconds, "ms" for milliseconds, "sec" for seconds,
                and "min" for minutes. Defaults to "sec".

        Returns:
            Dict[str, float]: Dictionary mapping timer names to their durations.
        """
        return {
            name: timer.get(unit=unit)
            for name, timer in self._timers.items()
        }

    def to_dataframe(self, unit: Literal["ns", "ms", "sec", "min"] = "sec") -> pd.DataFrame:
        """Return timers in dataframe format.

        Args:
            unit (Literal["ns", "ms", "sec", "min"], optional):
                The unit of time to display the durations.
                Accepts "ns" for nanoseconds, "ms" for milliseconds, "sec" for seconds,
                and "min" for minutes. Defaults to "sec".

        Returns:
            pd.Dataframe: A dataframe of the timers.
        """
        return pd.DataFrame({
            "Timer": self._timers.keys(),
            "Duration": [timer.get(unit=unit) for timer in self._timers.values()],
        })

    def save(
        self,
        path: str,
        fmt: Literal["csv", "json"],
        mode: Literal["w", "x", "a"] = "w",
        unit: Literal["ns", "ms", "sec", "min"] = "sec",
    ) -> None:
        """Save timers with their respective durations to file.

        Args:
            path (str):
                File path to save to.
            fmt (Literal[&quot;csv&quot;, &quot;json&quot;]):
                Format of file to save to. Accepts "csv" and "json".
            mode (Literal[&quot;w&quot;, &quot;x&quot;, &quot;a&quot;], optional):
                File write type.
                Accepts "w" for write, "x" for create and write and "a" for append. Defaults to "w".
            unit (Literal["ns", "ms", "sec", "min"], optional):
                The unit of time to display the durations.
                Accepts "ns" for nanoseconds, "ms" for milliseconds, "sec" for seconds,
                and "min" for minutes. Defaults to "sec".

        Raises:
            ValueError: Invalid fmt or mode.
        """
        if mode not in ["w", "x", "a"]:
            raise ValueError('Invalid mode: Mode must be one of ["w", "x" or "a"].')

        with open(path, mode=mode) as fp:
            match fmt:
                case "csv":
                    data = self.to_tuples(unit=unit)
                    for name, duration in data:
                        fp.write(f"{name},{duration}\n")
                case "json":
                    fp.write(json.dumps(self.to_dict(unit=unit)))
                case _:
                    raise ValueError('Invalid format: Format must be one of ["csv", "json"].')

    def show(self, unit: Literal["ns", "ms", "sec", "min"] = "sec", print_fn: Callable = print) -> None:
        """
        Output the timers with their respective durations. Prints to stdout by default.

        Args:
            unit (Literal["ns", "ms", "sec", "min"], optional):
                The unit of time to display the durations.
                Accepts "ns" for nanoseconds, "ms" for milliseconds, "sec" for seconds,
                and "min" for minutes. Defaults to "sec".
            print_fn (Callable, optional):
                A callable function used to output the timers (e.g., `print`, `logger.debug`).
                Defaults to the built-in `print` function.
        """
        headers = ["Timer", "Duration"]
        data = self.to_tuples(unit=unit)
        tabulated = tabulate(data, headers=headers)
        print_fn(tabulated)

    def show_stats(self, unit: Literal["ns", "ms", "sec", "min"] = "sec", print_fn: Callable = print) -> None:
        """
        Output the aggregate stats of the timers. Prints to stdout by default.

        Args:
            unit (Literal["ns", "ms", "sec", "min"], optional):
                The unit of time to display the durations.
                Accepts "ns" for nanoseconds, "ms" for milliseconds, "sec" for seconds,
                and "min" for minutes. Defaults to "sec".
            print_fn (Callable, optional):
                A callable function used to output the stats (e.g., `print`, `logger.debug`).
                Defaults to the built-in `print` function.
        """
        timer_values = [timer.get("ns") for timer in self._timers.values()]
        ave = convert_from_ns(sum(timer_values) / len(self), unit=unit)
        _max = convert_from_ns(max(timer_values), unit=unit)
        _min = convert_from_ns(min(timer_values), unit=unit)

        headers = ["Stat", "Duration"]
        data = [["Average", ave], ["Max", _max], ["Min", _min]]
        tabulated = tabulate(data, headers=headers)
        print_fn(tabulated)
