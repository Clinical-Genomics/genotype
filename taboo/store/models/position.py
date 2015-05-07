# -*- coding: utf-8 -*-
from sqlalchemy import Column, String, Integer, ForeignKey

from .core import Base


class Position(Base):
    id = Column(Integer, primary_key=True)
    rsnumber = Column(String(10))
    sample_id = Column(Integer, ForeignKey('sample.id'))
    genotype = Column(String(2))
