import logging


from traceback_with_variables import printing_tb, Format, ColorSchemes, LoggerAsFile


def f(n):
    print(1 / n)


def main():
    with printing_tb(
        fmt=Format(
            before=3,
            after=1,
            max_value_str_len=100,
            max_exc_str_len=1000,
            ellipsis_='...',
            color_scheme=ColorSchemes.synthwave,
        ),
        skip_cur_frame=True,  # e.g. no info about 'x'
        reraise=False,  # i.e. program won't fail, exceptions stay inside
        file_=LoggerAsFile(logging.getLogger('main'), separate_lines=True)
    ):
        x = 1
        f(x - 1)


main()
