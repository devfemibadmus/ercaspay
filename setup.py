from setuptools import setup, find_packages
import codecs
import os


with codecs.open("C:\\Users\\devfe\\Desktop\\ercaspay\\Readme.md", encoding="utf-8") as fh:
    long_description = "\n" + fh.read()


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