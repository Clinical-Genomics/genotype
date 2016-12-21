# -*- coding: utf-8 -*-
"""
genotype.compat
~~~~~~~~~~~~~
Python 2.7.x, 3.2+ compatability module.
"""
import operator
import sys

is_py2 = sys.version_info[0] == 2

if not is_py2:  # pragma: no cover
    # Python 3
    zip = zip
    range = range

    # strings and ints
    unichr = chr
    text_type = str
    string_types = (str,)
    integer_types = (int,)

    # lazy iterators
    from itertools import filterfalse
    iteritems = operator.methodcaller('items')
    iterkeys = operator.methodcaller('keys')
    itervalues = operator.methodcaller('values')

else:
    # Python 2

    # strings and ints
    text_type = unicode
    string_types = (str, unicode)
    integer_types = (int, long)

    # lazy iterators
    range = xrange
    from itertools import izip as zip, ifilterfalse as filterfalse
    iteritems = operator.methodcaller('iteritems')
    iterkeys = operator.methodcaller('iterkeys')
    itervalues = operator.methodcaller('itervalues')
