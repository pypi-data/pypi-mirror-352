# !/usr/bin/env python
# encoding: utf-8

import json

from ckan.plugins import toolkit


def list_of_dicts_validator(value, context):
    """
    Validates that the value passed can be a list of dicts, either because it is or
    because it is once it's been parsed as JSON.

    :param value: the value
    :param context: the context
    :return: the value as a list of dicts
    """
    # if the value is a string parse it as json first
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except ValueError:
            raise toolkit.Invalid('Cannot parse JSON')
    # now check that the value is a list and all the elements in the list are dicts
    if isinstance(value, list) and all(isinstance(item, dict) for item in value):
        return value
    # if we reach here the value is rubbish, error out
    raise toolkit.Invalid('Value must be a list of dictionaries')


def list_of_strings(delimiter=','):
    """
    Creates a converter/validator function which when given a value return a list or
    raises an error if a list can't be created from the value. If the value passed in is
    a list already it is returned with no modifications, if it's a string then the
    delimiter is used to split the string and the result is returned. If the value is
    neither a list or a string then an error is raised.

    :param delimiter: the string to delimit the value on, if it's a string; defaults to
        a comma
    :return: a list
    """

    def validator(value):
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return value.split(delimiter)
        raise toolkit.Invalid('Invalid list of strings')

    return validator


def list_validator(value, context):
    """
    Checks that the given value is a list. If it is then it is allowed to pass, if not
    an Invalid error is raised. If the value is a string then we attempt to parse it as
    a JSON serialised list and raise an exception if we can't.

    :param value: the value to check
    :param context: the context in which to check
    :return:
    """
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except ValueError:
            raise toolkit.Invalid('Cannot parse JSON list')
    if isinstance(value, list):
        return value
    raise toolkit.Invalid('Value must be a list')


class BaseArgs:
    """
    A class defining a group of related parameters passed to an action.

    Simplifies action definitions if there are many possible arguments, and allows for
    additional validation based on the collection of parameters.
    """

    fields = {}
    defaults = {}

    def __init__(self, **kwargs):
        data, errors = toolkit.navl_validate(kwargs, self.fields)
        if len(errors) == 1:
            raise errors[0]
        if len(errors) > 0:
            raise toolkit.Invalid(
                f'{len(errors)} errors when creating {self.__name__}.'
            )
        for field in self.fields:
            input_value = data.get(field, self.defaults.get(field))
            setattr(self, field, input_value)
        self.validate()

    def validate(self):
        """
        Additional validation.
        """


def object_validator(object_class: type):
    """
    Creates a validator to check a JSON dict against a class inheriting from BaseArgs.
    If valid, it also loads that JSON dict as an instance of the class.

    :param object_class: a class inheriting from BaseArgs
    :return: a validator instance
    """

    def _object_validator(value, context):
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except ValueError:
                raise toolkit.Invalid('Cannot parse JSON')
        if isinstance(value, dict):
            try:
                return object_class(**value)
            except Exception as e:
                raise toolkit.Invalid(
                    f'{object_class.__name__} could not be created ({e})'
                )
        else:
            raise toolkit.Invalid('Value must be a dict')

    return _object_validator
