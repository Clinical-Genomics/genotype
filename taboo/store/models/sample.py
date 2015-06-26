# -*- coding: utf-8 -*-
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint

from .core import Base


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

    def stringify(self):
        """Stringify genotypes for the sample.

        Returns:
            str: serialized representation of related genotypes
        """
        return '-'.join(str(genotype) for genotype in self.genotypes)
