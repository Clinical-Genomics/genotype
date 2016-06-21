# -*- coding: utf-8 -*-
from sqlalchemy import func

from taboo.store.models import Analysis, Sample


class MatchMixin:

    def pending(self):
        """Return samples to be matched."""
        query = self.complete().filter(Sample.status == None,
                                       Sample.sex != None)
        return query

    def passing(self):
        """Return all samples that have passed the checks."""
        query = Sample.query.filter_by(status='pass')
        return query

    def failing(self):
        """Return all samples that have failed some check."""
        query = Sample.query.filter_by(status='fail')
        return query

    def complete(self):
        """Return samples that have been annotated completely."""
        query = (Sample.query.join(Sample.analyses)
                       .group_by(Analysis.sample_id)
                       .having(func.count(Analysis.sample_id) == 2))
        return query

    def incomplete(self, query=None):
        """Return samples that haven't been annotated completely."""
        query = query or Sample.query
        query = (query.join(Sample.analyses)
                      .group_by(Analysis.sample_id)
                      .having(func.count(Analysis.sample_id) < 2))
        return query
