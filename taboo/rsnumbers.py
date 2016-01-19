# -*- coding: utf-8 -*-
"""
Provide an interface and helper functions to deal with the rsnumbers file.
"""


def parse(rs_handle):
    """Read RS numbers into a dict."""
    rows = (line.strip().split('\t') for line in rs_handle)
    rs_map = {row[0]: row[1] for row in rows}
    return rs_map
