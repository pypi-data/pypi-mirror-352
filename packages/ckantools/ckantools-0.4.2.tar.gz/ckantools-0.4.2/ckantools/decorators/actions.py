# !/usr/bin/env python
# encoding: utf-8

import copy
import inspect

from ckan.plugins import toolkit

from ckantools.validators import validate_by_schema


def action(schema, helptext, *decorators, get=False):
    """
    Decorator that indicates that the function being decorated is an action function. By
    wrapping a function with this decorator and then passing the module to the
    create_actions function in this module, the developer gains the benefits of:

        - automatic validation against the given schema
        - automatic access check whenever action is called
        - attachment of the given help text to the action function
        - decoration of the action with the given decorators

    :param schema: the schema dict to validate the data_dict's passed to this action against
    :type schema: dict
    :param helptext: the help text to associate with the action when it is presented to action API users
    :type helptext: str
    :param get: convenience arg for applying toolkit.side_effect_free (i.e. make action GET-able)
    :type get: bool
    :param *decorators: a list of decorators to apply to the resulting action function passed to CKAN
    :type *decorators: func
    :return: a wrapper function
    :rtype: func
    """

    def wrapper(function):
        function.is_action = True
        function.load_action_schema = True
        function.action_schema = schema
        function.action_help = helptext
        function.action_decorators = list(decorators)
        if get:
            function.action_decorators.append(toolkit.side_effect_free)
        return function

    return wrapper


def basic_action(function):
    """
    Load an action without loading the schema, helptext, etc.

    Useful for chained actions.

    :param function: the function being decorated
    :type function: func
    :return: the same function (not wrapped), with attributes added
    :rtype: func
    """
    function.is_action = True
    function.load_action_schema = False

    return function


def is_action(function):
    """
    Determines whether the given function is an action or not. This is simply based on
    the existance of the is_action attribute which is set in the action decorator above.

    :param function: the function to check
    :type function: func
    :return: True if the function is an action function, False if not
    :rtype: bool
    """
    return getattr(function, 'is_action', False)


def wrap_action_function(action_name, function):
    """
    Wrap an action function with useful processes and return it. An action function is a
    function with the action decorator (see the action function decorator in this
    module). Primarily, this allows the following:

        - passing values from the data_dict as proper function parameters thus turning
          code like the following:

            def action(context, data_dict):
                some_param = data_dict.get('some_param', 382)

          into:

            def action(some_param=382):
                ...

          Values are pulled from the data_dict and defaults are used if given in the
          action function definition.
        - Injection of the `context`, `data_dict` and `original_data_dict` variables
          through their inclusion in the action function definition. The
          original_data_dict is a copy of the dict_dict before it is passed to the
          validate function and therefore provides direct access to exactly what was
          passed when the action was called. To specify these parameters you must
          include them as args, not kwargs.
        - automatic validation using the schema provided with the action function
        - automatic access check
        - attachment of doc which lives separately to the action function, this keeps
          the doc for end users and the doc for other developers separate (as the doc
          exists in the code for the actual action function but is then replaced with
          the provided help text when passed to CKAN).

    :param action_name: the name of the action
    :type action_name: str
    :param function: the action function itself that we will be wrapping
    :type function: func
    :return: the wrapped action function
    :rtype: func
    """
    arg_spec = inspect.getfullargspec(function)
    if arg_spec.defaults is not None:
        # the default list is used to determine which args are required and which aren't
        required_args = arg_spec.args[: -len(arg_spec.defaults)]
        # create a dict of optional args -> their default values
        optional_args = dict(zip(reversed(arg_spec.args), reversed(arg_spec.defaults)))
    else:
        required_args = arg_spec.args
        optional_args = {}

    # use the action function definition to determine which variables the developer
    # wants injected
    to_inject = []
    for param in ['context', 'data_dict', 'original_data_dict']:
        if param in required_args:
            # make sure the param is removed from the required args otherwise when the
            # action is run we'll attempt to access it from the data_dict...
            required_args.remove(param)
            to_inject.append(param)

    def action_function(context, data_dict, **kw):
        original_data_dict = copy.deepcopy(data_dict)
        data_dict = validate_by_schema(context, data_dict, function.action_schema)
        toolkit.check_access(action_name, context, data_dict)

        params = {}
        for param_name in to_inject:
            # to avoid having an festival of ifs, use locals()!
            params[param_name] = locals()[param_name]
        for arg in required_args:
            params[arg] = data_dict[arg]
        for arg, default_value in optional_args.items():
            params[arg] = data_dict.get(arg, default_value)
        return function(**params)

    # add the help as the doc so that CKAN finds it and uses it as the help text
    action_function.__doc__ = function.action_help.strip()

    # apply the decorators to the action function we've created
    for action_decorator in function.action_decorators:
        action_function = action_decorator(action_function)

    return action_function
