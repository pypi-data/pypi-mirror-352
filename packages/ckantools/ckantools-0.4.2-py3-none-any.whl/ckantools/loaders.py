# !/usr/bin/env python
# encoding: utf-8

import inspect

from ckantools.decorators.actions import is_action, wrap_action_function
from ckantools.decorators.auth import is_auth
from ckantools.decorators.validators import is_validator


def create_actions(*modules):
    """
    Finds action functions in the given modules and returns a name -> function dict.
    Actions are found by finding all functions in each module that meet the is_action
    function criteria (see the is_action function in this module).

    :param modules: the modules to search through
    :return: an actions dict
    """
    actions = {}

    for module in modules:
        # actions must be functions and pass the is_action function's tests
        functions = inspect.getmembers(
            module, lambda f: inspect.isfunction(f) and is_action(f)
        )
        for function_name, function in functions:
            if getattr(function, 'load_action_schema', False):
                actions[function_name] = wrap_action_function(function_name, function)
            else:
                actions[function_name] = function

    return actions


def create_auth(*modules):
    """
    Finds auth functions in the given modules and returns a name -> function dict. Auths
    are found by finding all functions in each module that meet the is_auth function
    criteria (see the is_auth function in this module).

    :param modules: the modules to search through
    :return: an auths dict
    """
    auth = {}

    for module in modules:
        # auths must be functions and pass the is_auth function's tests
        functions = inspect.getmembers(
            module, lambda f: inspect.isfunction(f) and is_auth(f)
        )
        for function_name, function in functions:
            auth[function_name] = function

    return auth


def create_validators(*modules):
    """
    Finds validator functions in the given modules and returns a name -> function dict.
    Validators are found by finding all functions in each module that meet the
    is_validator function criteria (see the is_validator function).

    :param modules: the modules to search through
    :return: a validators dict
    """
    validators = {}

    for module in modules:
        functions = inspect.getmembers(
            module, lambda f: inspect.isfunction(f) and is_validator(f)
        )
        for function_name, function in functions:
            validators[function_name] = function

    return validators
