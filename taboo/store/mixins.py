# -*- coding: utf-8 -*-
import logging

from .models import Sample, SNP

log = logging.getLogger(__name__)


class ModelsMixin:

    def snps(self):
        """Return all the SNPs in order."""
        query = SNP.query.order_by('id')
        return query

    def sample(self, sample_id, notfound_cb=None):
        """Get sample from database and abort context if not found."""
        sample_obj = Sample.query.get(sample_id)
        if sample_obj is None:
            log.error("sample id not found in database: %s", sample_id)
            if notfound_cb:
                notfound_cb()
        return sample_obj
