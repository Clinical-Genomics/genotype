# -*- coding: utf-8 -*-
from datetime import datetime

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint

# base for declaring a mapping
Base = declarative_base()


class Genotype(Base):

    """Represent a genotype call for a position.

    For any given position and sample, only one genotype call be linked.

    Args:
        rsnumber (str): reference cluster id for the SNP
        sample (Sample): related ``Sample`` model
        allele_1 (str): first base in the call
        allele_2 (str): second base in the call
    """

    __tablename__ = 'genotype'
    __table_args__ = (UniqueConstraint('analysis_id', 'rsnumber',
                                       name='_sample_rsnumber'),)

    id = Column(Integer, primary_key=True)
    rsnumber = Column(String(10))
    analysis_id = Column(Integer, ForeignKey('analysis.id'))
    allele_1 = Column(String(1))
    allele_2 = Column(String(1))

    def __str__(self):
        """Stringify genotype call.

        Returns:
            str: serialized representation of the genotype
        """
        # assume we aren't dealing with stranded data
        genotypes = sorted([self.allele_1, self.allele_2])
        return ''.join(genotypes)


class Sample(Base):

    """Represent a sample linked to a list of genotypes.

    The ``sample_id`` together with the experiment should for a unique
    combination.

    Args:
        sample_id (str): display name to use for sample
        experiment (str): type of experiment, e.g. 'sequencing'
        source (str): unique id to identify the source of the data
        genotypes (list): list of ``Genotype`` models
    """

    __tablename__ = 'sample'

    id = Column(Integer, primary_key=True)
    sample_id = Column(String(32), unique=True)
    expected_sex = Column(String(32))
    created_at = Column(DateTime, default=datetime.now)

    analyses = relationship('Analysis', backref='sample')
    results = relationship('Result', backref='sample')

    def is_ready(self):
        """Check if both experiments are loaded for the sample."""
        experiments = [analysis.experiment for analysis in self.analyses]
        return 'sequencing' in experiments and 'genotyping' in experiments

    @property
    def analysis_dict(self):
        """Dictify loaded analyses."""
        return {analysis.experiment: analysis for analysis in self.analyses}

    def sexes(self):
        """Return sex determinations from loaded analyses."""
        sexes = {analysis.experiment: (analysis.sex or 'not set')
                 for analysis in self.analyses}
        return sexes

    def same_sex(self):
        """Determine if the sex is the same for analyses."""
        sexes = self.sexes().values()

        if 'not set' in sexes:
            return 'unknown'

        elif len(sexes) != 2:
            return 'N/A'

        elif len(set(sexes)) == 1:
            return 'success'

        else:
            return 'fail'

    def is_success(self):
        """Check if a comparison was made successfully."""
        if not self.results:
            return False
        else:
            return True

    def matches(self):
        """Return the matching sample ids."""
        return [result.sample.sample_id for result in self.results]


class Result(Base):

    """Represent the result of a sample check."""

    __tablename__ = 'result'

    id = Column(Integer, primary_key=True)
    matches = Column(Integer)
    mismatches = Column(Integer)
    unknowns = Column(Integer)

    analysis_id = Column(Integer, ForeignKey('analysis.id'))
    sample_id = Column(Integer, ForeignKey('sample.id'))


class Analysis(Base):

    """Represent a SNP calling analysis performed on a Sample."""

    __tablename__ = 'analysis'
    __table_args__ = (UniqueConstraint('sample_id', 'experiment',
                                       name='_sample_exp'),)

    id = Column(Integer, primary_key=True)
    experiment = Column(String(32), nullable=False)
    source = Column(String(128))
    # intended choices: female, male, unknown, conflict
    sex = Column(String(32))

    sample_id = Column(Integer, ForeignKey('sample.id'))

    genotypes = relationship('Genotype', order_by='Genotype.rsnumber',
                             backref='analysis')
    results = relationship('Result', backref='analysis')

    def stringify(self):
        """Stringify genotypes for the sample.

        Returns:
            str: serialized representation of related genotypes
        """
        return '-'.join(str(genotype) for genotype in self.genotypes)
