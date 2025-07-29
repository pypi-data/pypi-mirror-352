import os
import pathlib
from os import path

import pkg_resources
from setuptools import find_packages
from setuptools import setup

# read the contents of your README file
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

version = "0.6.4"

version = f"{version}{os.environ.get('PIP_VERSION_POSTFIX', '')}"

# read the requirements from requirements.txt
requirements = []
with pathlib.Path("requirements.txt").open() as requirements_txt:
    requirements = [
        str(requirement)
        for requirement in pkg_resources.parse_requirements(requirements_txt)
    ]


setup(
    name="python-kacl",
    version=version,
    description='Python module and CLI tool for validating and modifying Changelogs in "keep-a-changelog" format"',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/schmieder.matthias/python-kacl.git",
    author="Matthias Schmieder",
    author_email="schmieder.matthias@gmail.com",
    entry_points={"console_scripts": ["kacl-cli = kacl.kacl_cli:start"]},
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.9",
    install_requires=requirements,
    zip_safe=False,
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Version Control",
    ],
)
