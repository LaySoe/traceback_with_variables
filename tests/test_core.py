import pytest

from traceback_with_variables import core, ColorSchemes, Format

from tests.utils import assert_smart_equals_ref


# test with e=None in except
# test with e=None after except
# test with e=None and tb not None


def test_default():
    check('default', 10001)


def test_ellipsis():
    check('ellipsis', 10000, fmt=Format(ellipsis_='*'))


def test_max_value_str_len():
    check('max_value_str_len', 10000, fmt=Format(max_value_str_len=10))


def test_max_exc_str_len():
    check('max_exc_str_len', 10000, fmt=Format(max_exc_str_len=10))


def test_num_skipped_frames():
    check('num_skipped_frames', 10001, num_skipped_frames=1)


@pytest.mark.parametrize('before', [0, 2, 100])
def test_before(before):
    check(f'before_{before}', 10000, fmt=Format(before=before))


@pytest.mark.parametrize('after', [0, 2, 100])
def test_after(after):
    check(f'after_{after}', 10000, fmt=Format(after=after))


def test_before_after():
    check('before_after', 10000, fmt=Format(before=2, after=2))


def test_color_scheme_common():
    check('color_scheme_common', 10000, fmt=Format(color_scheme=ColorSchemes.common))


def test_color_scheme_synthwave():
    check('color_scheme_synthwave', 10000, fmt=Format(color_scheme=ColorSchemes.synthwave))


def test_color_scheme_nice():
    check('color_scheme_nice', 10000, fmt=Format(color_scheme=ColorSchemes.nice))


def test_force_bug_mode_1():
    check('force_bug_mode_1', 10000, __force_bug_mode=1)


def test_force_bug_mode_2():
    check('force_bug_mode_2', 10000, __force_bug_mode=2)


def check(name, arg, **kwargs):
    try:
        f(arg)
    except Exception as e:  # noqa
        assert_smart_equals_ref('test_core.{}'.format(name), '\n'.join(core.iter_tb_lines(e, **kwargs)))


def f(n: int) -> int:
    s1 = 'short string with n: {}'.format(n)
    l1 = 'long string with 0..n: {}'.format(', '.join(map(str, range(n))))
    us = [Unprintable(), Unprintable(), Unprintable()]

    if n % 10 == 0:
        return 1 // (n * 0)

    if True:
        if n % 2 == 0:
            return f(n - 1)
        else:
            return f(
                n

                - 1
            )


class Unprintable:
    def __repr__(self):
        raise ValueError("please don't print me")
