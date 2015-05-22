# -*- coding: utf-8 -*-
"""
Provide an interface and helper functions to deal with the rsnumbers file.
"""

def read(stream, separator='\t'):
    """Read in a file with rsnumbers."""
    lines = (line.strip() for line in stream)
    rows = (line.split(separator) for line in lines)
    return rows


def dictify(rows, id_idx=0, ref_idx=1):
    """Make a dict matching rsnumbers with corresponding ancestral allele."""
    mapper = {row[id_idx]:row[ref_idx] for row in rows}
    return mapper


def matcher(rsnumbers):
    """Match efficiently against a list of rsnumbers."""
    return set(rsnumbers)
