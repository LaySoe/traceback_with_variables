>>> from traceback_with_variables import print_tb

>>> def f(n):
....  return 1 / n
....

>>> f(0)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "<stdin>", line 2, in f
ZeroDivisionError: division by zero

>>> print_tb()

>>> # can be used in regular code too
