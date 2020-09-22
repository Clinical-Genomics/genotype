"""Fixtures for the load functions"""

from typing import List

import pytest
from alchy import Manager

from genotype.store import api
from genotype.store.models import Analysis, Genotype, Sample


@pytest.fixture(name="genotype_obj")
def fixture_genotype_obj() -> Genotype:
    """Return a genotype object"""
    return Genotype(rsnumber="rs12", allele_1="A", allele_2="T")


@pytest.fixture(name="new_genotype_obj")
def fixture_new_genotype_obj() -> Genotype:
    """Return a genotype object"""
    return Genotype(rsnumber="rs12", allele_1="A", allele_2="T")


@pytest.fixture(name="genotypes")
def fixture_genotypes(genotype_obj) -> List[Genotype]:
    """Return a list of genotype objects"""
    return [genotype_obj]


@pytest.fixture(name="new_genotypes")
def fixture_new_genotypes(new_genotype_obj) -> List[Genotype]:
    """Return a list of genotype objects"""
    return [new_genotype_obj]


@pytest.fixture(name="analysis_obj")
def fixture_analysis_obj(sample_id: str, genotypes: List[Genotype]) -> Analysis:
    """Return a analysis object"""
    return Analysis(type="genotype", sample_id=sample_id, genotypes=genotypes)


@pytest.fixture(name="analysis_db")
def fixture_analysis_db(analysis_obj: Analysis, genotype_db: Manager) -> Manager:
    """Return a analysis object"""
    api.add_analysis(genotype_db, analysis_obj)
    return genotype_db
