# -*- coding: utf-8 -*-
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint

from .core import Base


class Sample(Base):
    __tablename__ = 'sample'
    __table_args__ = (UniqueConstraint('sample_id', 'origin', name='_sample_origin'),)

    id = Column(Integer, primary_key=True)
    sample_id = Column(String(32))
    origin = Column(String(10), nullable=False)
    genotypes = relationship('Genotype', order_by='Genotype.rsnumber', backref='sample')

    def stringify(self):
        """Stringify genotypes for the sample."""
        return '-'.join(str(genotype) for genotype in self.genotypes)
