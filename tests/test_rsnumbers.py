# -*- coding: utf-8 -*-
from taboo import rsnumbers


def test_parse(rshandle):
    rsmap = rsnumbers.parse(rshandle)
    assert len(rsmap) == 4
    assert rsmap['rs10144418'] == 'T'
