from typing import Dict, Literal

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

    def show(self, unit: Literal["ns", "ms", "sec", "min"] = "sec") -> None:
        """Print timers to stdout.

        Args:
            unit (Literal[&quot;ns&quot;, &quot;ms&quot;, &quot;sec&quot;, &quot;min&quot;], optional):
            Unit of time to be used. Defaults to "sec".
        """
        headers = ["Timer", "Elasped Time"]
        data = [[name, timer.get(unit=unit)] for name, timer in self._timers.items()]
        tabulated = tabulate(data, headers=headers)
        print(tabulated)

    def show_stats(self, unit: Literal["ns", "ms", "sec", "min"] = "sec") -> None:
        """Print stats of timers to stdout.

        Args:
            unit (Literal[&quot;ns&quot;, &quot;ms&quot;, &quot;sec&quot;, &quot;min&quot;], optional):
            Unit of time to be used. Defaults to "sec".
        """
        timer_values = [timer.get("ns") for timer in self._timers.values()]
        ave = convert_from_ns(sum(timer_values) / len(self), unit=unit)
        _max = convert_from_ns(max(timer_values), unit=unit)
        _min = convert_from_ns(min(timer_values), unit=unit)

        headers = ["Stat", "Value"]
        data = [["Average", ave], ["Max", _max], ["Min", _min]]
        tabulated = tabulate(data, headers=headers)
        print(tabulated)

    def to_dataframe(self, unit: Literal["ns", "ms", "sec", "min"] = "sec") -> pd.DataFrame:
        """Return timers in dataframe format.

        Args:
            unit (Literal[&quot;ns&quot;, &quot;ms&quot;, &quot;sec&quot;, &quot;min&quot;], optional):
            Unit of time to be used. Defaults to "sec".

        Returns:
            pd.Dataframe: A dataframe of the timers.
        """
        return pd.DataFrame({
            "Timer": self._timers.keys(),
            "Elasped Time": [timer.get(unit=unit) for timer in self._timers.values()],
        })
