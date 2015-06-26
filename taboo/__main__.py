#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
taboo.__main__
~~~~~~~~~~~~~~~~
The main entry point for the command line interface.

Invoke as ``taboo`` (if installed)
or ``python -m taboo`` (no install required).
"""
from __future__ import absolute_import, unicode_literals
import sys

import taboo.cli


if __name__ == '__main__':
  # exit using whatever exit code the CLI returned
  sys.exit(taboo.cli.cli())
