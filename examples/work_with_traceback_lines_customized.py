from traceback_with_variables import iter_tb_lines, Format, ColorSchemes


def main():
    try:
        n = 0
        print(1 / n)

    except Exception as e:
        lines = list(iter_tb_lines(
            e=e,
            tb=None,
            fmt=Format(
                before=3,
                after=1,
                max_value_str_len=100,
                max_exc_str_len=1000,
                ellipsis_='...',
                color_scheme=ColorSchemes.synthwave,
            ),
        ))

        # requests.post('http://myreport.mysite.com/report', data={'lines': lines})


main()
