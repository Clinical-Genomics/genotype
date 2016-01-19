# -*- coding: utf-8 -*-
from sqlalchemy import Column, String, Integer, ForeignKey
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
    __table_args__ = (UniqueConstraint('sample_id', 'rsnumber',
                                       name='_sample_rsnumber'),)

    id = Column(Integer, primary_key=True)
    rsnumber = Column(String(10))
    sample_id = Column(Integer, ForeignKey('sample.id'))
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
    __table_args__ = (UniqueConstraint('sample_id', 'experiment',
                                       name='_sample_origin'),)

    id = Column(Integer, primary_key=True)
    sample_id = Column(String(32), nullable=False)
    experiment = Column(String(10), nullable=False)
    source = Column(String(128))
    genotypes = relationship('Genotype', order_by='Genotype.rsnumber',
                             backref='sample')
    # intended choices: female, male, unknown, conflict
    sex = Column(String(32))

    def stringify(self):
        """Stringify genotypes for the sample.

        Returns:
            str: serialized representation of related genotypes
        """
        return '-'.join(str(genotype) for genotype in self.genotypes)
