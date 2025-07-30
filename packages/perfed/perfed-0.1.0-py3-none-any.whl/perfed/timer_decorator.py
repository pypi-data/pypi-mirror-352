from typing import Any, Callable, Dict

from perfed.timer_manager import TimerManager


class TimerDecorator:
    """Manages a collection of timer managers for use when decorating functions.
    """
    _decorated_managers: Dict[str, TimerManager] = {}

    @classmethod
    def decorate(cls, name: str) -> Callable:
        if name in cls._decorated_managers:
            raise ValueError(f"TimerManager with the name: {name} already exists.")

        timer_manager = TimerManager(name=name)
        cls._decorated_managers[name] = timer_manager

        def wrapper(func) -> Callable:
            def inner(*args, **kwargs) -> Any:
                timer_name = f"{name}({len(timer_manager) + 1})"
                timer_manager.start(timer_name)
                res = func(*args, **kwargs)
                timer_manager.stop(timer_name)
                return res
            return inner
        return wrapper
    
    @classmethod
    def get_manager(cls, name: str) -> TimerManager:
        if (manager := cls._decorated_managers.get(name)) is None:
            raise ValueError(f"Manager with the name {name} does not exist.")

        return manager