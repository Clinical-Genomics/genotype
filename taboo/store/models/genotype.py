# -*- coding: utf-8 -*-
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.schema import UniqueConstraint

from .core import Base


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
