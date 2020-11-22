import argparse
import inspect
import sys
import traceback
from types import TracebackType
from typing import Any, Iterator, Union, Optional, TextIO, NoReturn

from traceback_with_variables.color import ColorScheme, ColorSchemes, supports_ansi


OptionalTraceback = Optional[Union[inspect.Traceback, TracebackType]]


class Format:
    def __init__(
        self,
        max_value_str_len: int = 1000,
        max_exc_str_len: int = 10000,
        ellipsis_: str = '...',
        num_context_lines: int = 1,
        color_scheme: Optional[ColorScheme] = None,
    ):
        self.max_value_str_len = max_value_str_len
        self.max_exc_str_len = max_exc_str_len
        self.ellipsis_ = ellipsis_
        self.num_context_lines = num_context_lines
        self.color_scheme = color_scheme

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> NoReturn:
        parser.add_argument("--max-value-str-len", type=int, default=1000)
        parser.add_argument("--max-exc-str-len", type=int, default=10000)
        parser.add_argument("--ellipsis", default="...")
        parser.add_argument("--num-context-lines", type=int, default=1)
        parser.add_argument("--color-scheme", default='auto',
                            choices=['auto'] + [a for a in dir(ColorSchemes) if not a.startswith('_')])

    @classmethod
    def parse(cls, ns: argparse.Namespace) -> 'Format':
        return Format(
            max_value_str_len=ns.max_value_str_len,
            max_exc_str_len=ns.max_exc_str_len,
            ellipsis_=ns.ellipsis,
            num_context_lines=ns.num_context_lines,
            color_scheme=None if ns.color_scheme == 'auto' else getattr(ColorSchemes, ns.color_scheme),
        )


def iter_tb_lines(
    e: Optional[Exception] = None,
    tb: OptionalTraceback = None,
    num_skipped_frames: int = 0,
    fmt: Format = Format(),
    for_file: Optional[TextIO] = None,
    __force_bug_mode: int = 0,  # for tests only
) -> Iterator[str]:
    e_: Exception = e or sys.exc_info()[1]
    tb_: Union[inspect.Traceback, TracebackType] = tb or sys.exc_info()[2]
    c: ColorScheme = fmt.color_scheme or \
        (ColorSchemes.common if (for_file and supports_ansi(for_file)) else ColorSchemes.none)

    try:
        yield f'{c.c}Traceback with variables (most recent call last):{c.e}'

        for frame, filename, line_num, func_name, code_lines, func_line_num in \
                inspect.getinnerframes(tb_, context=fmt.num_context_lines)[num_skipped_frames:]:
            yield f'{c.c}  File "{c.f_}{filename}{c.c_}", line {c.ln_}{line_num}{c.c_}, in {c.fn_}{func_name}{c.e}'

            if code_lines:
                yield f'{c.c}    {c.fs_}{"".join(code_lines).strip()}{c.e}'

            try:
                for var_name, var in frame.f_locals.items():
                    var_str = _to_cropped_str(var, fmt.max_value_str_len, fmt.max_exc_str_len, fmt.ellipsis_)
                    var_lines = var_str.split('\n')
                    yield f'{c.c}      {c.n_}{var_name}{c.c_} = {c.v_}{var_lines[0] if var_lines else var_str}{c.e}'
                    for line in var_lines[1:]:
                        yield f'{c.c}      {c.v_}{line}{c.e}'

                if __force_bug_mode == 1:
                    raise ValueError('force_bug_mode')

            except:  # noqa # indicates a bug in this lib
                yield '    <traceback-with-variables: exception while printing variables>'
                yield f'    {traceback.format_exc()}'

        yield f'{c.ec}{e_.__class__.__module__}.{e_.__class__.__name__}:{c.et_} {e_}{c.e}'

        if __force_bug_mode == 2:
            raise ValueError('force_bug_mode')

    except:  # noqa # indicates a bug in this lib
        yield '    <traceback-with-variables: exception while printing variables>'
        yield f'{traceback.format_exc()}'


def _crop(line: str, max_len: int, ellipsis_: str) -> str:
    if len(line) <= max_len or max_len < 0:
        return line

    return line[:max_len] + ellipsis_


def _to_cropped_str(obj: Any, max_value_str_len: int, max_exc_str_len: int, ellipsis_: str) -> str:
    try:
        return _crop(repr(obj), max_value_str_len, ellipsis_)

    except:  # noqa
        return _crop(
            '<exception while printing> ' + traceback.format_exc(chain=False).replace('\n', '\n  '),
            max_exc_str_len,
            ellipsis_,
        )
