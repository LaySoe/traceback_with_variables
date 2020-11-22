import sys
from typing import NoReturn

from traceback_with_variables.print import print_tb, Format


def global_print_tb(fmt: Format = Format()) -> NoReturn:
    sys.excepthook = lambda e_cls, e, tb: print_tb(e=e, tb=tb, fmt=fmt)  # noqa


def global_print_tb_in_ipython(fmt: Format = Format()) -> NoReturn:
    try:
        import IPython
    except ModuleNotFoundError:
        raise ValueError("IPython not found")

    IPython.core.interactiveshell.InteractiveShell.showtraceback = \
        lambda self, *args, **kwargs: print_tb(num_skipped_frames=1, fmt=fmt)  # noqa
