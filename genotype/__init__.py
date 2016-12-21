# -*- coding: utf-8 -*-
"""
genotype
~~~~~
Taboo is a tool for comparing genotypes from different assays.

:copyright: (c) 2014 by Robin Andeer
:licence: MIT, see LICENCE for more details
"""
import logging
from pkg_resources import get_distribution, DistributionNotFound

__title__ = 'genotype'
__summary__ = 'tool for comparing genotypes from different assays.'
__uri__ = 'https://github.com/Clinical-Genomics/genotype'

try:
    __version__ = get_distribution(__title__).version
except DistributionNotFound:
    __version__ = None

__author__ = 'Robin Andeer'
__email__ = 'robin.andeer@scilifelab.se'

__license__ = 'MIT'
__copyright__ = 'Copyright 2015 Robin Andeer'

# the user should dictate what happens when a logging event occurs
logging.getLogger(__name__).addHandler(logging.NullHandler())
