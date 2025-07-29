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
        version = '1.0.0',
        description = 'Read a CSV file and write an XLSX file with optional formatting.',
        long_description = '\n    Read a CSV file and write an XLSX file with optional formatting.\n    ',
        long_description_content_type = None,
        classifiers = [
            'Development Status :: 3 - Alpha',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
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
