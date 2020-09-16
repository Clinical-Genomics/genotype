"""Code that describes the package"""

import io
import os

# Always prefer setuptools over distutils
from setuptools import setup, find_packages

NAME = "genotype"
DESCRIPTION = (
    "genotype provides an automated pipipeline for comparing" "genotypes from different assays."
)
URL = "https://github.com/Clinical-Genomics/genotype"
AUTHOR = "Robin Andeer"
EMAIL = "mans.magnusson@scilifelab.se"

HERE = os.path.abspath(os.path.dirname(__file__))


def parse_reqs(req_path="./requirements.txt"):
    """Recursively parse requirements from nested pip files."""
    install_requires = []
    with io.open(os.path.join(HERE, req_path), encoding="utf-8") as handle:
        # remove comments and empty lines
        lines = (line.strip() for line in handle if line.strip() and not line.startswith("#"))
        for line in lines:
            # check for nested requirements files
            if line.startswith("-r"):
                # recursively call this function
                install_requires += parse_reqs(req_path=line[3:])
            else:
                # add the line as a new requirement
                install_requires.append(line)
    return install_requires


# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(HERE, "README.md"), encoding="utf-8") as f:
        LONG_DESCRIPTION = "\n" + f.read()
except FileNotFoundError:
    LONG_DESCRIPTION = DESCRIPTION


setup(
    name=NAME,
    version="2.5.1",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    # What does your project relate to? Separate with spaces.
    keywords="genotype development",
    author=AUTHOR,
    author_email=EMAIL,
    license="MIT",
    # The project's main homepage
    url=URL,
    packages=find_packages(exclude=("tests*", "docs", "examples")),
    # If there are data files included in your packages that need to be
    # installed, specify them here.
    include_package_data=True,
    package_data={
        "genotype": [
            "server/genotype/templates/genotype/*.html",
        ]
    },
    zip_safe=False,
    # Install requirements loaded from ``requirements.txt``
    install_requires=parse_reqs(),
    entry_points={
        "console_scripts": [
            "genotype = genotype.cli:root",
        ],
        "genotype.subcommands.2": [
            "init = genotype.init.cli:init",
            "load = genotype.load.cli:load",
            "add-sex = genotype.store.cli:add_sex",
            "mip-sex = genotype.store.cli:mip_sex",
            "view = genotype.store.cli:view",
            "match = genotype.match.cli:match",
            "check = genotype.match.cli:check",
            "delete = genotype.load.cli:delete",
            "serve = genotype.server.cli:serve",
            "ls = genotype.store.cli:ls",
            "sample = genotype.store.cli:sample",
            "export-sample = genotype.store.cli:export_sample",
            "export-sample-analysis = genotype.store.cli:export_sample_analysis",
        ],
    },
    # See: http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are:
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",
        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        "Topic :: Software Development",
        # Pick your license as you wish (should match "license" above)
        "License :: OSI Approved :: MIT License",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python :: 3.6",
        "Environment :: Console",
    ],
)
