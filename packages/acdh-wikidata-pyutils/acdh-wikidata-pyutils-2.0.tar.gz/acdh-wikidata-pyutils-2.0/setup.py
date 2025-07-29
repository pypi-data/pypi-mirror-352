#!/usr/bin/env python

"""The setup script."""

from setuptools import find_packages, setup

with open("README.md") as readme_file:
    readme = readme_file.read()


requirements = [
    "acdh-arche-assets>=3.6,<4",
    "typing-extensions>=4.12.2,<5",
    "Wikidata>=0.7.0,<1",
    "requests",
]

setup_requirements = []

test_requirements = []

setup(
    author="Peter Andorfer",
    author_email="peter.andorfer@oeaw.ac.at",
    python_requires=">=3.10",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
    ],
    description="Python package to fetch data from Wikidata",
    install_requires=requirements,
    license="MIT license",
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    name="acdh-wikidata-pyutils",
    packages=find_packages(
        include=["acdh_wikidata_pyutils", "acdh_wikidata_pyutils.*"]
    ),
    setup_requires=setup_requirements,
    url="https://github.com/acdh-oeaw/acdh-wikidata-pyutils",
    version="v2.0",
    zip_safe=False,
)
