# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from .cli import compare
from .core import compare_vcfs
from .plugins import concordance, gt_type, identity
from .utils import read_vcfs
