import os
from codecs import open
from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))

os.chdir(here)

with open(os.path.join(here, "Readme.md"), "r", encoding="utf-8") as fp:
    long_description = fp.read()



# Setting up
setup(
    name="ercaspay",
    version='1.0.0.3',
    author="Dev Femi Badmus",
    author_email="devfemibadmus@gmail.com",
    description='ercaspay plugin',
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    package_data={
        "ercaspay": ["templates/*", "static/*"],
    },
    install_requires=[
        'requests',
        'pycryptodome',
    ],
    entry_points={
        "console_scripts": [
            "ercaspay=ercaspay:function",
        ],
    },
    project_urls={
        "Slack": "https://app.slack.com/client/T083P8D99EY/C083LL3NMDZ",
        "Documentation": "https://ercaspay.com",
        "Source Code": "https://github.com/devfemibadmus/ercaspay",
    },
    keywords=['ercaspay', 'ercas payment plugin'],
    url="https://github.com/devfemibadmus/ercaspay",
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)