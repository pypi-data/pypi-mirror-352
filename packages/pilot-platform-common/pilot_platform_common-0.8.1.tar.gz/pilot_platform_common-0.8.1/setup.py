# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['common',
 'common.geid',
 'common.jwt_handler',
 'common.lineage',
 'common.logger',
 'common.logging',
 'common.models',
 'common.object_storage_adaptor',
 'common.permissions',
 'common.project',
 'common.vault']

package_data = \
{'': ['*']}

install_requires = \
['aioboto3>=9.6.0,<=13.2.0',
 'httpx>=0.23.0,<=0.28.1',
 'minio>=7.1.8,<8.0.0',
 'pyjwt>=2.6.0,<=2.9.0',
 'python-dotenv>=0.19.1',
 'python-json-logger>=0.1.11,<=2.0.7',
 'redis>=4.5.0,<=6.2.0',
 'starlette<0.47.0',
 'xmltodict>=0.13.0,<=0.14.2']

setup_kwargs = {
    'name': 'pilot-platform-common',
    'version': '0.8.1',
    'description': 'Centralize cross-service functionality shared across all Pilot Platform services.',
    'long_description': '# common\n\n[![Run Tests](https://github.com/PilotDataPlatform/common/actions/workflows/run-tests.yml/badge.svg?branch=develop)](https://github.com/PilotDataPlatform/common/actions/workflows/run-tests.yml)\n[![Python](https://img.shields.io/badge/python-3.8-brightgreen.svg)](https://www.python.org/)\n[![PyPI](https://img.shields.io/pypi/v/pilot-platform-common.svg)](https://pypi.org/project/pilot-platform-common/)\n\nImportable package responsible for cross-service tasks within the Pilot Platform (e.g. logging, Vault connection, etc.).\n\n\n## Getting Started\n\n### Installation & Quick Start\nThe latest version of the common package is available on [PyPi](https://pypi.org/project/pilot-platform-common/) and can be installed into another service via Pip.\n\nPip install from PyPi:\n```\npip install pilot-platform-common\n```\n\nIn `pyproject.toml`:\n```\npilot-platform-common = "^<VERSION>"\n```\n\nPip install from a local `.whl` file:\n```\npip install pilot_platform_common-<VERSION>-py3-none-any.whl\n```\n\n## Contribution\n\nYou can contribute the project in following ways:\n\n* Report a bug.\n* Suggest a feature.\n* Open a pull request for fixing issues or adding functionality. Please consider using [pre-commit](https://pre-commit.com) in this case.\n* For general guidelines on how to contribute to the project, please take a look at the [contribution guide](CONTRIBUTING.md).\n',
    'author': 'Indoc Systems',
    'author_email': 'None',
    'maintainer': 'Matvey Loshakov',
    'maintainer_email': 'mloshakov@indocresearch.org',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<3.11',
}


setup(**setup_kwargs)
