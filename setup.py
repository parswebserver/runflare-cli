from distutils.core import setup

import setuptools

from runflare import VERSION

file_obj = open("requirements.txt","r")
requirements = file_obj.readlines()
file_obj.close()

setup(
    name='runflare',
    packages=setuptools.find_packages(exclude=['tests', 'tests.*']),
    version=VERSION,
    description='Official CLI for runflare PaaS',
    author='RUNFLARE DEVELOPMENT TEAM',
    install_requires=requirements,
    author_email='parswebserver@gmail.com',
    url='https://github.com/parswebserver/runflare',
    keywords=['PaaS', 'runflare','Kubernetes'],
    package_data={'': ['.runflare_ignore']},
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