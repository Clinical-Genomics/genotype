# -*- coding: utf-8 -*-
"""
FIN: put data into a database
  - every SNP position compared between samples
  - SQ

/mnt/hds/proj/bioinfo/MIP_ANALYSIS/analysis/exomes/${FAMILY}/mosaik/GATK/000186Tfam_sorted_pmd_rreal_brecal_gvcf_vrecal_BOTH.vcf
"""
from __future__ import absolute_import, unicode_literals
from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base

# base for declaring a mapping
Base = declarative_base()


class Comparison(Base):
  __tablename__ = 'comparison'

  id = Column(Integer, primary_key=True)
  created_at = Column(DateTime, default=datetime.now)
  rs_number = Column(String(32))
  concordance = Column(String(32))

  original_id = Column(String(32))
  compared_id = Column(String(32))

  original_genotype = Column(String(10))
  compared_genotype = Column(String(10))

  original_quality = Column(Integer)
  compared_quality = Column(Integer)

  def __init__(self, rs_number, concordance, original_id, compared_id,
               original_genotype, compared_genotype, original_quality,
               compared_quality):

    self.rs_number = rs_number
    self.concordance = concordance
    self.original_id = original_id
    self.compared_id = compared_id
    self.original_genotype = original_genotype
    self.compared_genotype = compared_genotype
    self.original_quality = original_quality
    self.compared_quality = compared_quality
