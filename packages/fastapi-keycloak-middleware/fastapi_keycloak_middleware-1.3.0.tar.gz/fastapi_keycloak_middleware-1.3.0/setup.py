# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fastapi_keycloak_middleware',
 'fastapi_keycloak_middleware.decorators',
 'fastapi_keycloak_middleware.dependencies',
 'fastapi_keycloak_middleware.schemas']

package_data = \
{'': ['*']}

install_requires = \
['fastapi>=0.73.0', 'python-keycloak>=4.1,<6']

setup_kwargs = {
    'name': 'fastapi-keycloak-middleware',
    'version': '1.3.0',
    'description': 'Middleware for FastAPI to authenticate a user against keycloak',
    'long_description': '[![Documentation Status](https://readthedocs.org/projects/fastapi-keycloak-middleware/badge/?version=latest)](https://fastapi-keycloak-middleware.readthedocs.io/en/latest/?badge=latest)\n[![License: MIT](https://img.shields.io/badge/License-MIT-brightgreen.svg)](https://opensource.org/licenses/MIT)\n![GitHub issues](https://img.shields.io/github/issues/waza-ari/fastapi-keycloak-middleware)\n![GitHub release (latest by date)](https://img.shields.io/github/v/release/waza-ari/fastapi-keycloak-middleware)\n![GitHub top language](https://img.shields.io/github/languages/top/waza-ari/fastapi-keycloak-middleware)\n[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/waza-ari/fastapi-keycloak-middleware/development.svg)](https://results.pre-commit.ci/latest/github/waza-ari/fastapi-keycloak-middleware/development)\n\n\n# FastAPI Keycloak Middleware\n\n**Full documentation** is [available at Read The Docs](https://fastapi-keycloak-middleware.readthedocs.io/en/latest/)\n\nThis package provides a middleware for [FastAPI](http://fastapi.tiangolo.com)  that\nsimplifies integrating with [Keycloak](http://keycloak.org) for\nauthentication and authorization. It supports OIDC and supports validating access\ntokens, reading roles and basic authentication. In addition it provides several\ndecorators and dependencies to easily integrate into your FastAPI application.\n\nIt relies on the [python-keycloak](http://python-keycloak.readthedocs.io) package,\nwhich is the only dependency outside of the FastAPI ecosystem which would be installed\nanyway. Shoutout to the author of [fastapi-auth-middleware](https://github.com/code-specialist/fastapi-auth-middleware)\nwhich served as inspiration for this package and some of its code.\n\nIn the future, I plan to add support for fine grained authorization using Keycloak\nAuthorization services.\n\n## Motivation\n\nUsing FastAPI and Keycloak quite a lot, and keeping to repeat myself quite a lot when\nit comes to authentiating users, I decided to create this library to help with this.\n\nThere is a clear separation between the authentication and authorization:\n\n- **Authentication** is about verifying the identity of the user\n  (who they are). This is done by an authentication backend\n  that verifies the users access token obtained from the\n  identity provider (Keycloak in this case).\n- **Authorization** is about deciding which resources can be\n  accessed. This package providers convenience decoraters to\n  enforce certain roles or permissions on FastAPI endpoints.\n\n## Installation\n\nInstall the package using poetry:\n\n```bash\npoetry add fastapi-keycloak-middleware\n```\n\nor `pip`:\n\n```bash\npip install fastapi-keycloak-middleware\n```\n\n## Features\n\nThe package helps with:\n\n* An easy to use middleware that validates the request for an access token\n* Validation can done in one of two ways:\n   * Validate locally using the public key obtained from Keycloak\n   * Validate using the Keycloak token introspection endpoint\n* Using Starlette authentication mechanisms to store both the user object as well as the authorization scopes in the Request object\n* Ability to provide custom callback functions to retrieve the user object (e.g. from your database) and to provide an arbitrary mapping to authentication scopes (e.g. roles to permissions)\n* A decorator to use previously stored information to enforce certain roles or permissions on FastAPI endpoints\n* Convenience dependencies to retrieve the user object or the authorization result after evaluation within the FastAPI endpoint\n\n## Acknowledgements\n\nThis package is heavily inspired by [fastapi-auth-middleware](https://github.com/code-specialist/fastapi-auth-middleware)\nwhich provides some of the same functionality but without the direct integration\ninto Keycloak. Thanks for writing and providing this great piece of software!\n\n## Contributing\n\nThe client is written in pure Python.\nAny changes or pull requests are more than welcome, but please adhere to the code style.\n\nRuff is used both for code formatting and linting. Before committing, please run the following command to ensure\nthat your code is properly formatted:\n\n```bash\nruff check .\nruff format .\n```\n\nA pre-commit hook configuration is supplied as part of the project.\n\n## Development\n\nThis project is using [Act](https://github.com/nektos/act) to handle local development tasks. It is used\nto work locally and also to test Github actions before deploying them.\n',
    'author': 'Daniel Herrmann',
    'author_email': 'daniel.herrmann1@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
