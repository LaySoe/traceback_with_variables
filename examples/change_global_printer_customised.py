from traceback_with_variables import global_print_tb, Format, ColorSchemes


global_print_tb(fmt=Format(
    before=3,
    after=1,
    max_value_str_len=100,
    max_exc_str_len=1000,
    ellipsis_='...',
    color_scheme=ColorSchemes.synthwave,
))


def main():

    n = 0
    print(1 / n)


main()
