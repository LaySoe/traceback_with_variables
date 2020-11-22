from traceback_with_variables import iter_tb_lines


def main():
    try:
        n = 0
        print(1 / n)

    except Exception as e:
        lines = list(iter_tb_lines())

        # requests.post('http://myreport.mysite.com/report', data={'lines': lines})


main()
