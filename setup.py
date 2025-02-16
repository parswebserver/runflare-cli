from distutils.core import setup
import os
import setuptools

from runflare import VERSION

setup(
    name='runflare',
    packages=setuptools.find_packages(exclude=['tests', 'tests.*']),
    version=VERSION,
    description='Official CLI for runflare PaaS',
    author='RUNFLARE DEVELOPMENT TEAM',
    install_requires=[
        'setuptools==69.0.3',
    ],
    author_email='parswebserver@gmail.com',
    url='https://github.com/parswebserver/runflare-cli',
    keywords=['PaaS', 'runflare','Kubernetes'],
    package_data={'.runflare_ignore': ['runflare/.runflare_ignore']},
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Utilities"
    ],
    entry_points='''
        [console_scripts]
        runflare=runflare.runflare:run
    ''',
)
