import os
import time
from pmutils.units import unitprint, unitprint_block, number_converter


NAN = float("nan")
INF = float("inf")


def timed(f):
    """time a function"""
    def fx(*args, **kwargs):
        f"""
        timed function
        {f.__doc__}"""
        start = time.perf_counter_ns()
        res = f(*args, **kwargs)
        end = time.perf_counter_ns()
        print(f'{f.__name__} took {unitprint((end - start) * 1e-9, "s")}')
        return res

    return fx


def ask_option(question, options, /, ignore_case=True):
    if ignore_case:
        options = map(lambda i: i.lower(), options)
    while True:
        x = input(question)
        if ignore_case:
            x = x.lower()
        if x in options:
            return options.index(x)
        print("Invalid option, please try again ...")


def ask_float(question):
    while (x := number_converter(input(question))) is None:
        print("Number not recognized, please try again ...")


def progress_bar(status, total, passed_time=None):
    """
    Returns a nice progress bar
    :param status: the current position
    :param total: the maximum position
    :param passed_time: the time passed since the start
    :returns: the progress bar
    """
    arrow_base = '=' * int(status / total * 50)
    spaces = ' ' * (50 - len(arrow_base) - 1)

    eta = ""
    elapsed = ""

    percentage = f"{(status / total * 100):8.4f}%"

    if passed_time is not None:
        eta_ = passed_time * (total - status) / (status or NAN)
        if status <= 100e-6:  # Predictions within the first 100us definetly do not make sense
            eta = f"ETA {str(NAN): ^12}"
        else:
            eta = (f"ETA: {eta_ // 3600:2.0f}h "
                   f"{eta_ // 60 % 60:2.0f}m "
                   f"{eta_ % 60:2.0f}s")
        elapsed = (f"Elapsed: "
                   f"{passed_time // 3600:2.0f}h "
                   f"{passed_time // 60 % 60:2.0f}m "
                   f"{passed_time % 60:2.0f}s")
    if status < total:
        return f'\r[{arrow_base}>{spaces}] {percentage} {eta} {elapsed}'
    elif status == total:
        return f'\r[{"="*50}] {percentage} {eta} {elapsed}'
    else:
        return f"\r[{'!' * 50}] {percentage} ETA {str(NAN): ^12} {elapsed}"


class ProgressBar:
    """
    Alive-like progress bar, but with time predictions
    """

    def __init__(self, iterable, expected_iterations):
        self.start_time = time.time()
        self.iterable = iterable
        self.current_iteration = 0
        self.expected_iterations = expected_iterations

    def _print_bar(self):
        print(progress_bar(
            self.current_iteration, 
            self.expected_iterations, 
            time.time() - self.start_time
        ), flush=True, end="")

    def __iter__(self):
        for obj in self.iterable:
            self._print_bar()
            yield obj
            self.current_iteration += 1
            self._print_bar()
        self._print_bar()
        print()

    def __call__(self):
        self.current_iteration += 1
        self._print_bar()
        return self.current_iteration - 1
        

class Namespace(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    def __getattr__(self, item):
        return self.__dict__[item]

    def __delattr__(self, item):
        del self.__dict__[item]
