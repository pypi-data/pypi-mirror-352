from typing import Literal


def convert_from_ns(time_ns: float, unit: Literal["ns", "ms", "sec", "min"] = "sec") -> float:
    """Convert nanoseconds to specified time unit.

    Args:
        time (float): Time in nanoseconds.
        unit (Literal[&quot;ns&quot;, &quot;ms&quot;, &quot;sec&quot;, &quot;min&quot;], optional):
        Time unit to convert to. Defaults to "sec".

    Returns:
        float: Converted time.
    """

    match unit:
        case "ns":
            return float(time_ns)
        case "ms":
            return time_ns / (10 ** 3)
        case "sec":
            return time_ns / (10 ** 9)
        case "min":
            return time_ns / (10 ** 9) / 60
        case _:
            raise ValueError("Invalid format: Format must be one of [\"ns\", \"ms\", \"sec\" or \"min\"].")
