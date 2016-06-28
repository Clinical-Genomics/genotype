# -*- coding: utf-8 -*-
import logging
import os

from sqlalchemy import func

from taboo.store.models import Analysis, Sample, SNP

log = logging.getLogger(__name__)


def complete(db):
    """Return samples that have been annotated completely."""
    query = (db.query(Sample).join(Sample.analyses)
                             .group_by(Analysis.sample_id)
                             .having(func.count(Analysis.sample_id) == 2))
    return query


def pending(db):
    """Return samples to be matched."""
    query = complete(db).filter(Sample.status == None, Sample.sex != None)
    return query


def failing(db):
    """Return all samples that have failed some check."""
    query = db.query(Sample).filter_by(status='fail')
    return query


def passing(db):
    """Return all samples that have passed the checks."""
    query = db.query(Sample).filter_by(status='pass')
    return query


def incomplete(db, query=None):
    """Return samples that haven't been annotated completely."""
    query = query or db.query(Sample)
    query = (query.join(Sample.analyses)
                  .group_by(Analysis.sample_id)
                  .having(func.count(Analysis.sample_id) < 2))
    return query


def snps(db):
    """Return all the SNPs in order."""
    query = db.query(SNP).order_by('id')
    return query


def sample(db, sample_id, notfound_cb=None):
    """Get sample from database and abort context if not found."""
    sample_obj = db.query(Sample).get(sample_id)
    if sample_obj is None:
        log.error("sample id not found in database: %s", sample_id)
        if notfound_cb:
            notfound_cb()
    return sample_obj


def plates(db):
    """Return the plate ids loaded in the database."""
    query = (db.query(Analysis.source).distinct()
                                      .filter_by(type='genotype'))
    all_plates = [(os.path.basename(analysis.source), analysis.source)
                  for analysis in query]
    return all_plates


def delete_analysis(db, old_analysis, log=True):
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
----------  AUTO: end replace  ----------\n""".format(analysis=old_analysis)
    if old_analysis.sample.comment:
        old_analysis.sample.comment += log_msg
    else:
        old_analysis.sample.comment = log_msg

    # remove old analysis data
    old_analysis.delete()
    db.commit()


def add_analysis(db, new_analysis, replace=False):
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
    old_analysis = analysis(**analysis_kwargs).first()
    if old_analysis:
        log.debug("found old analysis: %s-%s",
                  new_analysis.sample_id, new_analysis.type)
        if replace:
            log.info("deleting and old analysis: %s-%s",
                     new_analysis.sample_id, new_analysis.type)
            delete_analysis(old_analysis)
        else:
            return None

    # check if sample already in database
    sample_obj = db.query(Sample).get(new_analysis.sample_id)
    if sample_obj:
        log.debug('found sample in database')
        new_analysis.sample = sample_obj
    else:
        sample_obj = Sample(id=new_analysis.sample_id)
        new_analysis.sample = sample_obj

    db.add_commit(new_analysis)
    return new_analysis


def analysis(db, sample_id, type):
    """Ask the database for a single analysis record.

    You can preferably call `.first()` on the returned value to get the
    analysis record or `None` if not found in the database.

    Args:
        sample_id (str): unique sample id
        type (str): choice of analysis type [genotype, sequence]

    Returns:
        query: SQLAlchemy query object
    """
    query = db.query(Analysis).filter_by(sample_id=sample_id, type=type)
    return query
