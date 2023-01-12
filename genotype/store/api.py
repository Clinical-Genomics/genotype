"""API to the genotype store"""

import logging
from datetime import datetime
from typing import Optional

from alchy import Manager
from sqlalchemy import func, or_

from genotype.store.models import SNP, Analysis, Genotype, Model, Plate, Sample

log = logging.getLogger(__name__)


def connect(uri: str) -> Manager:
    log.debug("open connection to database: %s", uri)
    manager = Manager(config=dict(SQLALCHEMY_DATABASE_URI=uri), Model=Model)
    return manager


def complete():
    """Return samples that have been annotated completely."""
    query = (
        Sample.query.join(Sample.analyses)
        .group_by(Analysis.sample_id)
        .having(func.count(Analysis.sample_id) == 2)
    )
    return query


def pending():
    """Return samples to be matched."""
    query = complete().filter(Sample.status == None, Sample.sex != None)
    return query


def failing():
    """Return all samples that have failed some check."""
    query = Sample.query.filter_by(status="fail")
    return query


def get_samples_after(date: datetime):
    """Return samples created since date"""
    query = Sample.query.filter(Sample.created_at > date)
    return query


def passing():
    """Return all samples that have passed the checks."""
    query = Sample.query.filter_by(status="pass")
    return query


def incomplete(query=None, since=None):
    """Return samples that haven't been annotated completely."""
    base_query = query or Sample.query
    base_query = base_query.join(Sample.analyses).order_by(Analysis.created_at.desc())
    # filter analyses on which are lacking genotypes
    base_query = base_query.group_by(Analysis.sample_id).having(func.count(Analysis.sample_id) < 2)
    if since:
        base_query = base_query.filter(Analysis.created_at > since)
    return base_query


def missing_genotypes(session, analysis_type, since=None):
    """Return analyses where the complementing genotype info is missing."""
    subquery = (
        session.query(Analysis, Sample.sex.label("sample_sex"))
        .join(Analysis.sample)
        .order_by(Analysis.created_at.desc())
        .group_by(Analysis.sample_id)
        .having(func.count(Analysis.sample_id) < 2)
        .subquery()
    )
    query = session.query(subquery).filter(subquery.c.type != analysis_type)
    if since:
        query = query.filter(Analysis.created_at > since)
    return query


def missing_sex(since=None):
    """Return Samples lacking sex but having all genotypes."""
    nosex_filter = or_(Sample.sex == None, Analysis.sex == None)
    query = (
        Sample.query.join(Sample.analyses)
        .order_by(Analysis.created_at.desc())
        .filter(nosex_filter)
        .group_by(Analysis.sample_id)
        .having(func.count(Analysis.sample_id) == 2)
    )
    if since:
        query = query.filter(Analysis.created_at > since)
    return query


def snps():
    """Return all the SNPs in order."""
    query = SNP.query.order_by("id")
    return query


def validate_sample_id(sample_id: str) -> bool:
    """Validate whether the provided user-provided sample_id is not malicious"""
    for char in sample_id:
        if not ord(char) >= 48 and ord(char) <= 57 and not ord(char) >= 65 and ord(char) <= 90:
            return False
    return True


def sample(sample_id: str, notfound_cb=None) -> Sample:
    """Get sample from database and abort context if not found."""
    sample_obj = Sample.query.get(sample_id)
    if sample_obj is None:
        if validate_sample_id(sample_id):
            log.error(f"sample id not found in database: {sample_id}")
        return notfound_cb() if notfound_cb else notfound_cb
    return sample_obj


def samples(plate_id=None, no_status=False):
    """List samples in the database."""
    query = Sample.query
    if plate_id:
        query = query.join(Sample.analyses).filter(Analysis.source.like("%{}\_%".format(plate_id)))
    if no_status:
        query = query.filter(Sample.status == None)
    return query


def plates():
    """Return the plate ids loaded in the database."""
    query = Plate.query
    return query


def plate(plate_id):
    """Return the plate with the given id."""
    query = Plate.query.filter_by(plate_id=plate_id)
    return query.first()


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
----------  AUTO: end replace  ----------\n""".format(
        analysis=old_analysis
    )
    if old_analysis.sample.comment:
        old_analysis.sample.comment += log_msg
    else:
        old_analysis.sample.comment = log_msg

    # remove old analysis data
    old_analysis.delete()
    db.commit()


def add_analysis(db: Manager, new_analysis: Analysis, replace: bool = False) -> Optional[Analysis]:
    """Add a new analysis to the database.

    The analysis record should only have the `sample_id` field filled in.
    A sample object will be fetched from the database or created.

    Args:
        new_analysis (Analysis): analysis record to be added
        replace (Optional[bool]): replace existing record with new one

    Returns:
        Analysis/None: the analysis if successful, otherwise `None`
    """
    analysis_kwargs = dict(sample_id=new_analysis.sample_id, type=new_analysis.type)
    old_analysis = analysis(**analysis_kwargs).first()
    if old_analysis:
        log.debug("found old analysis: %s-%s", new_analysis.sample_id, new_analysis.type)
        if replace:
            log.info("deleting old analysis: %s-%s", new_analysis.sample_id, new_analysis.type)
            delete_analysis(db, old_analysis)
        else:
            return None

    # check if sample already in database
    sample_obj = Sample.query.get(new_analysis.sample_id)
    if sample_obj:
        log.debug("found sample in database")
        new_analysis.sample = sample_obj
    else:
        sample_obj = Sample(id=new_analysis.sample_id)
        new_analysis.sample = sample_obj

    db.add_commit(new_analysis)
    return new_analysis


def analysis(sample_id, type):
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


def genotypes_by_analysis(session, analysis_id):
    """Ask the database for the genotype records with a specific analysis id.

    Args:
        analysis_id (str): unique analysis id

    Returns:
        query: SQLAlchemy query object
    """
    query = session.query(Genotype).filter(Genotype.analysis_id == analysis_id).all()

    return query


def analysis_by_sample(session, sample_id):
    """Ask the database for the genotype records with a specific analysis id.

    Args:
        sample_id (str): unique sample id

    Returns:
        query: SQLAlchemy query object
    """
    query = session.query(Analysis).filter(Analysis.sample_id == sample_id).all()

    return query
