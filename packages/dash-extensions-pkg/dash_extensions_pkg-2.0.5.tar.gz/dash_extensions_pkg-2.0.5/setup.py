import json
from setuptools import setup, find_packages


with open('package.json') as f:
    package = json.load(f)

setup(
    name="dash-extensions-pkg",
    version="2.0.5",
    author=package['author'],
    packages=find_packages(include=["dash_extensions*"]),
    include_package_data=True,
    license=package['license'],
    description=package.get('description', "dash-extensions-pkg"),
    install_requires=[],
    classifiers=[
        'Framework :: Dash',
    ],
)
