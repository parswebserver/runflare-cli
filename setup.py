from distutils.core import setup

import setuptools

from runflare import VERSION

setup(
    name='runflare',
    packages=setuptools.find_packages(exclude=['tests', 'tests.*']),
    version=VERSION,
    description='Official CLI for runflare PaaS',
    author='RUNFLARE DEVELOPMENT TEAM',
    install_requires=[
        'certifi==2021.10.8',
        'charset-normalizer==2.0.7',
        'colorama==0.4.4',
        'fire==0.4.0',
        'halo==0.0.31',
        'idna==3.2',
        'log-symbols==0.0.14',
        'prompt-toolkit==1.0.14',
        'Pygments==2.10.0',
        'PyInquirer==1.0.3',
        'pytz==2021.3',
        'regex==2021.10.8',
        'requests==2.26.0',
        'requests-toolbelt==0.9.1',
        'six==1.16.0',
        'spinners==0.0.24',
        'termcolor==1.1.0',
        'tzdata==2021.2.post0',
        'tzlocal==3.0',
        'urllib3==1.26.7',
        'wcwidth==0.2.5',
        'websockets==10.0',
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