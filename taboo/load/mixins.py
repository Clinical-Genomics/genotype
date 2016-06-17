# -*- coding: utf-8 -*-
import logging

from taboo.store.models import Analysis, Sample

log = logging.getLogger(__name__)


class LoadMixin:

    def delete_analysis(self, old_analysis, log=True):
        """Delete an analysis with related genotypes.

        Args:
            old_analysis (Analysis): analysis record to be deleted
            log (Optional[bool]): store log in sample record
        """
        # store away info about currently loaded analysis
        log_msg = """----------AUTO: replace analysis----------
Source: {analysis.source}
Type: {analysis.type}
Sex: {analysis.sex}
----------  AUTO: end replace  ----------""".format(analysis=old_analysis)
        if old_analysis.sample.comment:
            old_analysis.sample.comment += log_msg
        else:
            old_analysis.sample.comment = log_msg

        # remove old analysis data
        old_analysis.delete()
        self.save()

    def add_analysis(self, new_analysis, replace=False):
        """Add a new analysis to the database.

        The analysis record should only have the `sample_id` field filled in.
        A sample object will be fetched from the database or created.

        Args:
            new_analysis (Analysis): analysis record to be added
            replace (Optional[bool]): replace existing record with new one

        Returns:
            Analysis/None: the analysis if successful, otherwise `None`
        """
        analysis_kwargs = dict(sample_id=new_analysis.sample_id,
                               type=new_analysis.type)
        old_analysis = self.analysis(**analysis_kwargs).first()
        if old_analysis:
            log.debug("found old analysis: %s-%s",
                      new_analysis.sample_id, new_analysis.type)
            if replace:
                log.info("deleting and old analysis: %s-%s",
                         new_analysis.sample_id, new_analysis.type)
                self.delete_analysis(old_analysis)
            else:
                return None

        # check if sample already in database
        sample_obj = Sample.query.get(new_analysis.sample_id)
        if sample_obj:
            log.debug('found sample in database')
            new_analysis.sample = sample_obj
        else:
            sample_obj = Sample(id=new_analysis.sample_id)
            new_analysis.sample = sample_obj

        self.add(new_analysis)
        self.save()
        return new_analysis

    def analysis(self, sample_id, type):
        """Ask the database for a single analysis record.

        You can preferably call `.first()` on the returned value to get the
        analysis record or `None` if not found in the database.

        Args:
            sample_id (str): unique sample id
            type (str): choice of analysis type [genotype, sequence]

        Returns:
            query: SQLAlchemy query object
        """
        query = Analysis.query.filter_by(sample_id=sample_id, type=type)
        return query
