import inspect
import json
import logging
import sys
import time as time_module
from contextlib import contextmanager
from typing import Callable, Dict, Generator, List, Optional, Tuple, Union

from hkkang_utils.pattern import SingletonABCMetaWithArgs

# Import dataclasses according to Python version
sys_version = sys.version_info
if sys_version[0] == 3 and sys_version[1] >= 7:
    import dataclasses
else:
    try:
        import dataclasses
    except:
        import subprocess

        subprocess.check_call([sys.executable, "-m", "pip", "install", "dataclasses"])
    finally:
        import dataclasses


# Dataclass
@dataclasses.dataclass
class Period:
    start_time: float
    end_time: float

    @property
    def elapsed_time(self) -> float:
        return self.end_time - self.start_time


# Utility functions
def prettify_time(time_in_sec: float) -> str:
    if time_in_sec < 60:
        return f"{time_in_sec:.4f} seconds"
    return f"{minute(time_in_sec):.0f}min {second(time_in_sec):.4f}sec"


def minute(time_in_sec: float) -> float:
    return time_in_sec / 60


def second(time_in_sec: float) -> float:
    return time_in_sec % 60


# Timer class
class TimerMeta(SingletonABCMetaWithArgs):
    _call_cnt: Dict[type, Dict[str, int]] = dict()

    def __call__(cls, class_name=None, func_name=None):
        # Figure out the class name and function name of the caller
        if class_name is None and func_name is None:
            stack = inspect.stack()
            caller_stack_idx = (
                list(map(lambda k: k.function, stack)).index("__call__") + 1
            )
            func_name = stack[caller_stack_idx][3]
            for idx in range(caller_stack_idx, len(stack)):
                if "self" in stack[idx][0].f_locals:
                    class_name = stack[idx][0].f_locals["self"].__class__.__name__
                    if stack[idx][3] != func_name:
                        func_name = f"{stack[idx][3]}.{func_name}"
                    break
        # Initialize the call count if it is not initialized
        if cls not in cls._call_cnt:
            cls._call_cnt[cls] = dict()
        instance_key = cls.__repr_args__(class_name, func_name)
        if instance_key not in cls._call_cnt[cls]:
            cls._call_cnt[cls][instance_key] = 0
        return super().__call__(class_name, func_name)


class Timer(metaclass=TimerMeta):
    """Timer class to measure the elapsed time of a function.

    Example1 (measure the time of code block):
        # Initialize timer
        timer = Timer()
        timer.start()

        # Perform some task
        ...

        timer.stop()

        # Print the elapsed time
        print(f"Elapsed time: {timer.elapsed_time}")

    Example2 (measure the time of code block within a function):
        def some_function():
            # Code block without measuring time
            ...

            # Initialize timer
            timer = Timer()
            timer.start()

            # Perform some task
            ...

            timer.stop()

            # Code block without measuring time
            ...

        # Call the function
        some_function()
        # Call the function
        some_function()

        # Print the total elapsed time
        print(f"Total Elapsed time: {timer.total_elapsed_time}")
        # Print the average elapsed time
        print(f"Average elapsed time: {timer.average_elapsed_time}")
    """

    def __init__(self, class_name: str, func_name: str):
        # Name is used to identify the timer
        self.class_name = class_name
        self.func_name = func_name
        # Time related variables
        self.start_time: Optional[float] = None
        self.measured_times: List[Period] = []
        self.paused_times: List[Period] = []

    @property
    def name(self) -> str:
        if self.class_name is None:
            return self.func_name
        return f"{self.class_name}.{self.func_name}"

    @property
    def logger(self) -> logging.Logger:
        return logging.getLogger(f"Timer.{self.name}")

    @property
    def call_cnt(self) -> int:
        instance_key = Timer.__repr_args__(self.class_name, self.func_name)
        return Timer._call_cnt[Timer][instance_key]

    @call_cnt.setter
    def call_cnt(self, value):
        instance_key = Timer.__repr_args__(self.class_name, self.func_name)
        Timer._call_cnt[Timer][instance_key] = value

    @property
    def elapsed_time(self) -> float:
        last_period = self.measured_times[-1]
        return last_period.elapsed_time

    @property
    def total_elapsed_time(self) -> float:
        return sum([period.elapsed_time for period in self.measured_times])

    @property
    def avg_elapsed_time(self) -> float:
        if self.call_cnt == 0:
            return 0
        return self.total_elapsed_time / self.call_cnt

    # Methods for measuring the time
    @contextmanager
    def measure(
        self, print_measured_time: bool = False
    ) -> Generator["Timer", None, None]:
        # Pre processing
        self.start()
        yield self
        self.stop()
        # Post processing
        if print_measured_time:
            self.show_elapsed_time()

    @contextmanager
    def pause(self) -> Generator["Timer", None, None]:
        # Pre processing
        current_time = time_module.time()
        self.measured_times.append(Period(self.start_time, current_time))
        self.start_time = current_time
        yield self
        # Post processing
        current_time = time_module.time()
        self.paused_times.append(Period(self.start_time, current_time))
        self.start_time = current_time

    def start(self) -> None:
        if self.start_time is not None:
            self.logger.warning(
                "Timer has already been started. Please call stop() first."
            )
        # Increase the call count
        self.call_cnt += 1
        self.start_time = time_module.time()

    def stop(self) -> float:
        current_time = time_module.time()
        if self.start_time is None:
            self.logger.warning(
                "Timer has not been started. Please call start() first."
            )
        self.measured_times.append(Period(self.start_time, current_time))
        self.start_time = None
        return self.elapsed_time

    # Methods for printing the measured time
    def show_elapsed_time(self) -> None:
        self.logger.info(f"Elapsed time: {prettify_time(self.elapsed_time)}")

    def show_total_elapsed_time(self) -> None:
        self.logger.info(
            f"Total elapsed time: {prettify_time(self.total_elapsed_time)}"
        )

    def show_avg_elapsed_time(self) -> None:
        self.logger.info(
            f"Average elapsed time: {prettify_time(self.avg_elapsed_time)}"
        )

    def summarize_measured_time(
        self, silent: bool = False, in_dict: bool = False
    ) -> Union[Dict[str, Union[str, int, float]], Tuple[str, int, float, float]]:
        if in_dict:
            result = {
                "name": self.name,
                "call_cnt": self.call_cnt,
                "avg_elapsed_time": self.avg_elapsed_time,
                "total_elapsed_time": self.total_elapsed_time,
            }
            if not silent:
                self.logger.info(json.dumps(result, indent=4))
        else:
            result = (
                self.name,
                self.call_cnt,
                self.avg_elapsed_time,
                self.total_elapsed_time,
            )
            if not silent:
                self.logger.info(f"Function name: {self.name}")
                self.logger.info(f"Call count: {self.call_cnt}")
                self.show_avg_elapsed_time()
                self.show_total_elapsed_time()
        return result

    @classmethod
    def summarize_measured_times(
        cls, silent: bool = False, in_dict: bool = False
    ) -> List[Tuple[str, int, float, float]]:
        return_values = []
        for timer in Timer._instances[cls].values():
            return_values.append(
                timer.summarize_measured_time(silent=silent, in_dict=in_dict)
            )
        return return_values


# Decorator for timer
def measure_time(func: Callable, print_measured_time: bool = True) -> Callable:
    """Decorator to measure the elapsed time of a function.

    :param func: function to be measured
    :type func: Callable
    :param print_measured_time: whether to print the measured time after the function call, defaults to True
    :type print_measured_time: bool, optional

    Example:
        @measure_time
        def some_function():
            # All the code block within this function will be measured
            ...

        # Calling the function will print the measured time
        some_function()
    """

    def wrapper(*args, **kwargs):
        names = list(filter(lambda n: n != "<locals>", func.__qualname__.split(".")))
        class_name = None if len(names) == 1 else names[0]
        func_name = names[0] if len(names) == 1 else ".".join(names[1:])
        timer = Timer(class_name=class_name, func_name=func_name)
        with timer.measure(print_measured_time=print_measured_time):
            result = func(*args, **kwargs)
        return result

    return wrapper


if __name__ == "__main__":
    timer = Timer()
    print("Done")
