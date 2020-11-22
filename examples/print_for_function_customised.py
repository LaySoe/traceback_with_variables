import logging


from traceback_with_variables import prints_tb, Format, ColorSchemes, LoggerAsFile


@prints_tb(
    fmt=Format(
        num_context_lines=3,
        max_value_str_len=100,
        max_exc_str_len=1000,
        ellipsis_='...',
        color_scheme=ColorSchemes.synthwave,
    ),
    file_=LoggerAsFile(logging.getLogger('main'), separate_lines=True)
)
def f(n):
    print(1 / n)


f(0)