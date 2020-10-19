# -*- coding: utf-8 -*-
"""
genotype
~~~~~
Taboo is a tool for comparing genotypes from different assays.

:copyright: (c) 2014 by Robin Andeer
:licence: MIT, see LICENCE for more details
"""
try:
    from importlib import metadata
except ImportError:
    # Running on pre-3.8 Python; use importlib-metadata package
    import importlib_metadata as metadata

__title__ = "genotype"

__version__ = metadata.version(__title__)
