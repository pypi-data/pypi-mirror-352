# !/usr/bin/env python
# encoding: utf-8

from ckan.plugins import toolkit


def validate_by_schema(context, data_dict, default_schema):
    """
    Validate the data_dict against a schema. If a schema is not available in the context
    (under the key 'schema') then the default schema is used.

    If the data_dict fails the validation process a ValidationError is raised, otherwise
    the potentially updated data_dict is returned.

    :param context: the ckan context dict
    :param data_dict: the dict to validate
    :param default_schema: the default schema to use if the context doesn't have one
    """
    schema = context.get('schema', default_schema)
    data_dict, errors = toolkit.navl_validate(data_dict, schema, context)
    if errors:
        raise toolkit.ValidationError(errors)
    return data_dict
