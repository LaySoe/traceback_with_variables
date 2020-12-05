import argparse
import inspect
import sys
import traceback
from types import TracebackType
from typing import Any, Iterator, Union, Optional, TextIO, NoReturn

from traceback_with_variables.color import ColorScheme, ColorSchemes, supports_ansi


Traceback = Union[inspect.Traceback, TracebackType]


class Format:
    def __init__(
        self,
        max_value_str_len: int = 1000,
        max_exc_str_len: int = 10000,
        ellipsis_: str = '...',
        before: int = 0,
        after: int = 0,
        color_scheme: Optional[ColorScheme] = None,
    ):
        self.max_value_str_len = max_value_str_len
        self.max_exc_str_len = max_exc_str_len
        self.ellipsis_ = ellipsis_
        self.before = before
        self.after = after
        self.color_scheme = color_scheme

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> NoReturn:
        parser.add_argument("--max-value-str-len", type=int, default=1000)
        parser.add_argument("--max-exc-str-len", type=int, default=10000)
        parser.add_argument("--ellipsis", default="...")
        parser.add_argument("--before", type=int, default=0)
        parser.add_argument("--after", type=int, default=0)
        parser.add_argument("--color-scheme", default='auto',
                            choices=[a for a in dir(ColorSchemes) if not a.startswith('_')])

    @classmethod
    def parse(cls, ns: argparse.Namespace) -> 'Format':
        return Format(
            max_value_str_len=ns.max_value_str_len,
            max_exc_str_len=ns.max_exc_str_len,
            ellipsis_=ns.ellipsis,
            before=ns.before,
            after=ns.after,
            color_scheme=getattr(ColorSchemes, ns.color_scheme),
        )


def iter_tb_lines(
    e: Optional[Exception] = None,
    tb: Optional[Traceback] = None,
    num_skipped_frames: int = 0,
    fmt: Format = Format(),
    for_file: Optional[TextIO] = None,
    __force_bug_mode: int = 0,  # for tests only
) -> Iterator[str]:
    try:
        if tb and not e:
            raise ValueError('`e` is None, but `tb` is not None')
        e_: Exception = e or sys.exc_info()[1] or getattr(sys, 'last_value', None)
        if not e_:
            raise ValueError('cannot print Traceback, no exception happened or passed')
        tb_: Traceback = tb or sys.exc_info()[2] or getattr(sys, 'last_traceback', None)

        c: ColorScheme = fmt.color_scheme or \
            (ColorSchemes.common if (for_file and supports_ansi(for_file)) else ColorSchemes.none)

        yield f'{c.c}Traceback with variables (most recent call last):{c.e}'

        for frame, filename, line_num, func_name, code_lines, before in \
                inspect.getinnerframes(tb_, context=max(fmt.before, fmt.after) + 1)[num_skipped_frames:]:
            yield f'{c.c}  File "{c.f_}{filename}{c.c_}", line {c.ln_}{line_num}{c.c_}, in {c.fn_}{func_name}{c.e}'

            if code_lines:
                code_lines = code_lines[max(0, before - fmt.before):before + 1 + fmt.after]
                code_lines = [line.replace('\t', '    ').rstrip() for line in code_lines]
                min_indent = min(len(line) - len(line.lstrip(' ')) for line in code_lines)

                for i, line in enumerate(code_lines):
                    prefix = '  '
                    if fmt.after or fmt.before:
                        prefix = '> ' if max(0, before - fmt.before) + i == before else '. '

                    yield f'{c.c}  {prefix}{c.fs_}{line[min_indent:]}{c.e}'

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
