"""
For the simplest usage possible. Just import it
"""

from traceback_with_variables.color import ColorSchemes
from traceback_with_variables.global_hooks import global_print_tb_in_ipython, Format


global_print_tb_in_ipython(fmt=Format(color_scheme=ColorSchemes.common))
