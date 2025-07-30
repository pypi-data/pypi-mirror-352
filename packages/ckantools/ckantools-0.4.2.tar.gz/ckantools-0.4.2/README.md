<!--header-start-->
<img src="https://data.nhm.ac.uk/images/nhm_logo.svg" align="left" width="150px" height="100px" hspace="40"/>

# ckantools

[![CKAN](https://img.shields.io/badge/ckan-2.9.5-orange.svg?style=flat-square)](https://github.com/ckan/ckan)
[![Python](https://img.shields.io/badge/python-3.6%20%7C%203.7%20%7C%203.8-blue.svg?style=flat-square)](https://www.python.org/)

_Utilities and common methods for CKAN extensions._

<!--header-end-->

# Overview

<!--overview-start-->
A collection of methods, decorators, and anything else that might be useful.

_ckantools is still very much in development, and is prone to frequent changes that may or may not work._

<!--overview-end-->

# Installation

<!--installation-start-->
```shell
pip install ckantools
```

<!--installation-end-->

# Usage

See the full usage docs on [readthedocs.io](https://ckantools.readthedocs.io).

<!--usage-start-->
## Actions

Use the `@action` decorator to add actions:
```python
# logic/actions/module_name.py

from ckantools.decorators import action

@action(schema, helptext, get=False, *other_decorators)
def example_action(parameter_1, parameter_2):
    # ...
```

Or the `@basic_action` decorator if you want to load the action but don't want any of the other features (schema loading, auto auth, etc):
```python
from ckantools.decorators import basic_action

@basic_action
def example_action(context, data_dict):
    # ...
```

And then load the action(s) in `plugin.py`:
```python
# plugin.py

from .logic.actions import module_name
from ckantools.loaders import create_actions
from ckan.plugins import implements, interfaces, SingletonPlugin

class ExamplePlugin(SingletonPlugin):
    implements(interfaces.IActions)

    # IActions
    def get_actions(self):
        return create_actions(module_name)
```

## Auth

Loading auth functions is similar to actions, i.e. use the `@auth` decorator.

```python
# logic/auth/module_name.py

from ckantools.decorators import auth

@auth(anon=True)
def example_action(context, data_dict):
    return {'success': True}

@auth('example_action')
def other_action(context, data_dict):
    # checks access to example_action first
    return {'success': True}
```

The auth functions can then be loaded in `plugin.py`:
```python
# plugin.py

from .logic.auth import module_name
from ckantools.loaders import create_auth
from ckan.plugins import implements, interfaces, SingletonPlugin

class ExamplePlugin(SingletonPlugin):
    implements(interfaces.IActions)

    # IAuthFunctions
    def get_auth_functions(self):
        return create_auth(module_name)
```

<!--usage-end-->
