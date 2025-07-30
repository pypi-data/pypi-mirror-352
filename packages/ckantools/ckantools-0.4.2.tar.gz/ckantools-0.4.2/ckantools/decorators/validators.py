# !/usr/bin/env python
# encoding: utf-8


def validator(function):
    """
    Decorator that indicates that the function being decorated is a validator function.
    """
    function.is_validator = True
    return function


def is_validator(function):
    """
    Determines whether the given function is an validator function or not. This is
    simply based on the existance of the is_validator attribute which is set in the
    decorator above.

    :param function: the function to check
    :return: True if the function is an validator function, False if not
    """
    return getattr(function, 'is_validator', False)
