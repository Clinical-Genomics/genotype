# -*- coding: utf-8 -*-
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint

from .core import Base


class Sample(Base):
    id = Column(Integer, primary_key=True)
    sample_id = Column(String(32))
    origin = Column(String(10), nullable=False)
    positions = relationship('Position', backref='sample')

    UniqueConstraint('sample_id', 'origin', name='_sample_origin')
