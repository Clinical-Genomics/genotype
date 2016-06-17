# -*- coding: utf-8 -*-
from taboo.store.models import Sample


class MatchMixin:

    def pending(self):
        """Return samples to be matched."""
        query = Sample.query.filter(Sample.status == None)
        for sample in query:
            if sample.sex and len(sample.analyses) == 2:
                yield sample

    def passing(self):
        """Return all samples that have passed the checks."""
        query = Sample.query.filter_by(status='pass')
        return query

    def failing(self):
        """Return all samples that have failed some check."""
        query = Sample.query.filter_by(status='fail')
        return query
