# -*- coding: utf-8 -*-
from taboo.store.models import SNP


def read_snps(sequence):
    """Parse TAB-separated file with SNP information."""
    # remove comment lines and split into rows
    rows = (line.strip().split('\t') for line in sequence
            if line and not line.startswith('#'))
    for row in rows:
        # convert row to SNP object
        yield SNP(id=row[0], ref=row[1], chrom=row[2], pos=int(row[3]))
