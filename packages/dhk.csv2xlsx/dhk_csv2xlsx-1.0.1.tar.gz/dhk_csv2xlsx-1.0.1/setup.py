#!/usr/bin/env python
#   -*- coding: utf-8 -*-

from setuptools import setup
from setuptools.command.install import install as _install

class install(_install):
    def pre_install_script(self):
        pass

    def post_install_script(self):
        pass

    def run(self):
        self.pre_install_script()

        _install.run(self)

        self.post_install_script()

if __name__ == '__main__':
    setup(
        name = 'dhk.csv2xlsx',
        version = '1.0.1',
        description = 'Read a CSV file and write an XLSX file with optional formatting.',
        long_description = 'dhk.csv2xlsx\n============\n\n[![GitHub](https://img.shields.io/badge/github-python--csv2xlsx-blue?logo=github)](https://github.com/DavidKiesel/python-csv2xlsx)\n\n[![Latest Version](https://img.shields.io/pypi/v/dhk.csv2xlsx?logo=pypi)](https://pypi.org/project/dhk.csv2xlsx/)\n[![Python Versions](https://img.shields.io/pypi/pyversions/dhk.csv2xlsx?logo=pypi)](https://pypi.org/project/dhk.csv2xlsx/)\n\n[![Downloads Per Day](https://img.shields.io/pypi/dd/dhk.csv2xlsx?logo=pypi)](https://pypi.org/project/dhk.csv2xlsx/)\n[![Downloads Per Week](https://img.shields.io/pypi/dw/dhk.csv2xlsx?logo=pypi)](https://pypi.org/project/dhk.csv2xlsx/)\n[![Downloads Per Month](https://img.shields.io/pypi/dm/dhk.csv2xlsx?logo=pypi)](https://pypi.org/project/dhk.csv2xlsx/)\n\n# Introduction\n\n`dhk.csv2xlsx` is a Python command-line tool for reading a CSV file and writing an XLSX file with optional formatting.\nIt leverages the Python standard library [`csv`](https://docs.python.org/3/library/csv.html) module and the [`XlsxWriter`](https://pypi.org/project/XlsxWriter/) package.\n\n# Simple Installation\n\nA pedestrian command for installing the package is given below.\nAlternatively, for a more rewarding installation exercise, see section [Recommended Installation](#recommended-installation).\n\n```bash\npip install dhk.csv2xlsx\n```\n\n# Usage\n\n```console\n$ csv2xlsx --help\nusage: csv2xlsx [-h] [--settings-file SETTINGS_FILE] [--verbose] [--force]\n                [--output OUTPUT_FILE]\n                CSV_FILE\n\nRead a CSV file and write an XLSX file.\n\npositional arguments:\n  CSV_FILE              CSV file\n\noptions:\n  -h, --help            show this help message and exit\n  --settings-file, -s SETTINGS_FILE\n                        settings file; default: None\n  --verbose, -v         verbose\n  --force, -f           force; suppress prompts\n  --output, -o OUTPUT_FILE\n                        output file; default: CSV_FILE - .csv + .xlsx\n\nExamples:\n\n    csv2xlsx \\\n        CSV_FILE\n\n    csv2xlsx \\\n        --settings-file SETTINGS_FILE \\\n        CSV_FILE\n\n    csv2xlsx \\\n        --settings-file SETTINGS_FILE \\\n        --output OUTPUT \\\n        CSV_FILE\n```\n\n# Recommended Installation\n\n[`pyenv`](https://github.com/pyenv/pyenv) is a tool for installing multiple Python environments and controlling which one is in effect in the current shell.\n\n[`pipx`](https://github.com/pipxproject/pipx) is a tool for installing and running Python applications in isolated environments.\n\nAssuming these have been installed correctly...\n\n## Install Python Under `pyenv`\n\nThe version of Python under which this package was last developed and tested is stored in [`.python-version`](https://raw.githubusercontent.com/DavidKiesel/python-csv2xlsx/refs/heads/main/.python-version).\n\nTo capture this Python version to a shell variable, execute the commands below.\n`PYTHON_VERSION` should be set to something like `3.13.3`.\n\n```bash\nPYTHON_VERSION="$(\n    wget \\\n        -O - \\\n        https://raw.githubusercontent.com/DavidKiesel/python-csv2xlsx/refs/heads/main/.python-version\n)"\n\necho "$PYTHON_VERSION"\n```\n\nTo determine if the `.python-version` version of Python has already been installed under `pyenv`, execute the command below.\nIf it has not been installed, then a warning message will be displayed.\n\n```bash\nPYENV_VERSION="$PYTHON_VERSION" \\\npython --version\n```\n\nIf it has already been installed, then proceed to section [Install Package Using `pipx`](#install-package-using-pipx).\n\nOtherwise, to install the given version of Python under `pyenv`, execute the command below.\n\n```bash\npyenv install "$PYTHON_VERSION"\n```\n\nIf the install was successful, then proceed to section [Install Package Using `pipx`](#install-package-using-pipx).\n\nIf instead there is a warning that the definition was not found, then you will need to upgrade `pyenv`.\n\nIf `pyenv` was installed through a package manager, then consider upgrading it through that package manager.\nFor example, if `pyenv` was installed through `brew`, then execute the commands below.\n\n```bash\nbrew update\n\nbrew upgrade pyenv\n```\n\nAlternatively, you could attempt to upgrade `pyenv` through the command below.\n\n```bash\npyenv update\n```\n\nOnce `pyenv` has been upgraded, to install the given version of Python under `pyenv`, execute the command below.\n\n```bash\npyenv install "$PYTHON_VERSION"\n```\n\n## Install Package Using `pipx`\n\nOnly proceed from here if the instructions in section [Install Python Under `pyenv`](#install-python-under-pyenv) have been completed successfully.\n\nAt this point, shell variable `PYTHON_VERSION` should already contain the appropriate Python version.\nIf not, execute the commands below.\n\n```bash\nPYTHON_VERSION="$(\n    wget \\\n        -O - \\\n        https://raw.githubusercontent.com/DavidKiesel/python-csv2xlsx/refs/heads/main/.python-version\n)"\n\necho "$PYTHON_VERSION"\n```\n\nTo install the package hosted at PyPI using `pipx`, execute the command below.\n\n```bash\npipx \\\n    install \\\n    --python "$(PYENV_VERSION="$PYTHON_VERSION" pyenv which python3)" \\\n    dhk.csv2xlsx\n```\n',
        long_description_content_type = 'text/markdown',
        classifiers = [
            'Development Status :: 3 - Alpha',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10',
            'Programming Language :: Python :: 3.11',
            'Programming Language :: Python :: 3.12',
            'Programming Language :: Python :: 3.13'
        ],
        keywords = '',

        author = 'David Harris Kiesel',
        author_email = 'david.sw@suddenthought.net',
        maintainer = 'David Harris Kiesel',
        maintainer_email = 'david.sw@suddenthought.net',

        license = 'MIT',

        url = 'https://github.com/DavidKiesel/python-csv2xlsx',
        project_urls = {
            'Homepage': 'https://github.com/DavidKiesel/python-csv2xlsx'
        },

        scripts = ['scripts/csv2xlsx'],
        packages = ['dhk.csv2xlsx'],
        namespace_packages = [],
        py_modules = [],
        entry_points = {},
        data_files = [],
        package_data = {},
        install_requires = ['XlsxWriter==3.2.3'],
        dependency_links = [],
        zip_safe = True,
        cmdclass = {'install': install},
        python_requires = '>=3.8',
        obsoletes = [],
    )
