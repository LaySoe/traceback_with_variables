import logging
import sys
from contextlib import contextmanager
from functools import wraps
from typing import NoReturn, Union, TextIO, Optional, Callable

from traceback_with_variables.core import iter_tb_lines, Format, OptionalTraceback


class LoggerAsFile:
    def __init__(self, logger: logging.Logger, separate_lines: bool = False):
        self.logger = logger
        self.separate_lines = separate_lines
        self.lines = []

    def flush(self) -> NoReturn:
        if self.lines:
            self.logger.error('\n    '.join(self.lines))

    def write(self, text: str) -> NoReturn:
        if self.separate_lines:
            self.logger.error(text.rstrip('\n'))
        else:
            self.lines.append(text.rstrip('\n'))


def print_tb(
    e: Optional[Exception] = None,
    tb: OptionalTraceback = None,
    num_skipped_frames: int = 0,
    fmt: Format = Format(),
    file_: Union[TextIO, LoggerAsFile] = sys.stderr,
) -> NoReturn:
    for line in iter_tb_lines(
        e=e,
        tb=tb,
        num_skipped_frames=num_skipped_frames,
        fmt=fmt,
        for_file=file_,
    ):
        file_.write(line + '\n')

    file_.flush()


@contextmanager
def printing_tb(
    reraise: bool = True,
    file_: Union[TextIO, LoggerAsFile] = sys.stderr,
    skip_cur_frame: bool = False,
    fmt: Format = Format(),
):
    try:
        yield

    except Exception as e:
        print_tb(
            e=e,
            tb=None,
            num_skipped_frames=2 if skip_cur_frame else 1,
            fmt=fmt,
            file_=file_
        )

        if reraise:
            raise e


def prints_tb(
    func__for_noncall_case_only: Optional[Callable] = None,  # to call without "()"
    file_: Union[TextIO, LoggerAsFile] = sys.stderr,
    fmt: Format = Format(),
):
    if func__for_noncall_case_only:
        return prints_tb(file_=file_, fmt=fmt)(func__for_noncall_case_only)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with printing_tb(
                reraise=True,
                file_=file_,
                skip_cur_frame=True,
                fmt=fmt,
            ):
                return func(*args, **kwargs)

        return wrapper

    return decorator
