# -*- coding: utf-8 -*-
"""
Provide an interface and helper functions to deal with the rsnumbers file.
"""
from collections import namedtuple

RSNumber = namedtuple('RSNumber', ['id', 'ref', 'chrom', 'pos'])


def parse(rs_handle):
    """Read RS numbers into a dict."""
    rows = (line.strip().split('\t') for line in rs_handle)
    rs_map = {row[0]: RSNumber(id=row[0], ref=row[1], chrom=row[2], pos=row[3])
              for row in rows}
    return rs_map
