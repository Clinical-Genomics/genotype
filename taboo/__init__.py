# -*- coding: utf-8 -*-
"""
taboo
~~~~~
Taboo is a tool for comparing genotypes from different assays.

:copyright: (c) 2014 by Robin Andeer
:licence: MIT, see LICENCE for more details
"""
import logging

__all__ = [
  '__title__', '__summary__', '__uri__', '__version__', '__author__',
  '__email__', '__license__', '__copyright__', '__banner__'
]

# Generate your own AsciiArt at:
# patorjk.com/software/taag/#f=Calvin%20S&t=Taboo ID Typing Pipeline
__banner__ = r"""
╔╦╗┌─┐┌┐ ┌─┐┌─┐
 ║ ├─┤├┴┐│ ││ │  by Robin Andeer
 ╩ ┴ ┴└─┘└─┘└─┘
"""

__title__ = 'taboo'
__summary__ = 'tool for comparing genotypes from different assays.'
__uri__ = 'https://github.com/Clinical-Genomics/taboo'

__version__ = '0.3.1'

__author__ = 'Robin Andeer'
__email__ = 'robin.andeer@scilifelab.se'

__license__ = 'MIT'
__copyright__ = 'Copyright 2015 Robin Andeer'

# the user should dictate what happens when a logging event occurs
logging.getLogger(__name__).addHandler(logging.NullHandler())
