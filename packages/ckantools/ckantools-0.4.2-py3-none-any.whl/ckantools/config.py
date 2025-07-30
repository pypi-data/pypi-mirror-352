# !/usr/bin/env python
# encoding: utf-8

from ckan.plugins import toolkit


def get_setting(*config_names, default=None):
    """
    Get a configuration value, with multiple backup options if the first isn't set. e.g.
    `get_setting('ckanext.my_ext.site_name', 'ckan.site_title', default='Unknown')` will
    check `ckanext.my_ext.site_name` first, then `ckanext.site_title` if that's not set,
    and finally use the default if neither is set.

    :param config_names: the names of the config settings to check, in descending order
        of priority
    :param default: the value to use if none of the config values are set
    :return: the value of one of the config settings, or the default if none are set
    """
    for c in config_names:
        setting = toolkit.config.get(c)
        if setting is not None:
            return setting
    return default


def get_debug(default=True):
    """
    Get the debug value from the config. Checks both `debug` and `DEBUG` and returns the
    default if neither is set.

    :param default: returns this if neither is set
    :return: True if debug mode is enabled
    """
    return toolkit.asbool(get_setting('debug', 'DEBUG', default=default))
