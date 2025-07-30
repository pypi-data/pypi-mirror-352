import csv
import sys
from typing import Any, Dict, List, Literal

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

    
    def average(self, unit: Literal["ns", "ms", "sec", "min"] = "sec") -> float:
        """Returns the average elapsed time of timers.

        Args:
            unit (Literal[&quot;ns&quot;, &quot;ms&quot;, &quot;sec&quot;, &quot;min&quot;], optional):
            Unit of time to be used. Defaults to "sec".
        
        Returns:
            float: Average elasped time.
        """
        ave = sum([timer.get("ns") for timer in self._timers.values()]) / len(self)
        return convert_from_ns(ave, unit=unit)


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

    def to_csv(self, unit: Literal["ns", "ms", "sec", "min"] = "sec") -> None:
        """Print timers to stdout in csv format.

        Args:
            unit (Literal[&quot;ns&quot;, &quot;ms&quot;, &quot;sec&quot;, &quot;min&quot;], optional):
            Unit of time to be used. Defaults to "sec".
        """
        headers = ["Timer", "Elasped Time"]
        data: List[List[Any]] = [[name, timer.get(unit=unit)] for name, timer in self._timers.items()]
        
        writer = csv.writer(sys.stdout)
        writer.writerow(headers)
        writer.writerows(data)
