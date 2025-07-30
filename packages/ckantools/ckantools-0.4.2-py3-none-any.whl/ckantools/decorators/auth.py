# !/usr/bin/env python
# encoding: utf-8

from functools import wraps

from ckan.plugins import toolkit


def auth(proxy=None, keymapping=None, anon=False):
    """
    Decorator that indicates that the function being decorated is an auth function.

    :param proxy: a name or list of names of auth functions that should be called before
        this one (optional)
    :param keymapping: a dict remapping names of keys from this data_dict to the proxy
        function(s) data_dict; e.g. if the parameter 'id' is called 'resource_id' in the
        proxy function, the keymapping would be {'id': 'resource_id'} (optional)
    :param anon: allow anonymous access (optional)
    :return: a wrapper function
    """

    def wrapper(function):
        function.is_auth = True
        if anon:
            function = toolkit.auth_allow_anonymous_access(function)

        @wraps(function)
        def wrapped(*args):
            if len(args) == 2:
                context, data_dict = args
            elif len(args) == 3:
                next_auth, context, data_dict = args
            else:
                raise ValueError('Incorrect number of arguments.')
            if proxy:
                if isinstance(proxy, str):
                    proxy_list = [proxy]
                else:
                    proxy_list = proxy
                for proxy_name in proxy_list:
                    check(proxy_name, context, data_dict, keymapping)
            return function(*args)

        return wrapped

    return wrapper


def check(proxy, context, data_dict, keymapping=None):
    """
    Check that the current user has the given access in the given context. The resource
    id is extracted from the data dict and therefore must be present.

    :param proxy: the name of the other auth function to check
    :param context: the context dict
    :param data_dict: the data dict
    :param keymapping: a dict of data_dict key to auth function key, e.g. if the proxied
        function requires 'id' but the data_dict contains that value as 'resource_id'
    :return: a dict containing a "success" key with a boolean value indicating whether
        the current user has the required access. If the user does not then an
        additional "msg" key is returned in this dict which contains a user-friendly
        message.
    """
    data_dict_copy = data_dict.copy() if data_dict else {}
    keymapping = keymapping or {}
    for this_key, other_key in keymapping.items():
        if this_key is None:
            del data_dict_copy[other_key]
        else:
            data_dict_copy[other_key] = data_dict_copy[this_key]

    user = context.get('user')
    authorized = toolkit.check_access(proxy, context, data_dict_copy)

    if authorized:
        return {'success': True}

    return {
        'success': False,
        'msg': toolkit._(f'User {user} not authorised to perform this action.'),
    }


def is_auth(function):
    """
    Determines whether the given function is an auth function or not. This is simply
    based on the existance of the is_auth attribute which is set in the decorator above.

    :param function: the function to check
    :return: True if the function is an auth function, False if not
    """
    return getattr(function, 'is_auth', False)
