"""Fixtures for the cli tests"""

from typing import Dict

import pytest
from alchy import Manager


@pytest.fixture(name="sequence_ctx")
def fixture_sequence_ctx(sequence_db: Manager) -> Dict[str, Manager]:
    """Return a context with a sequence database"""
    return {"db": sequence_db}


@pytest.fixture(name="snp_ctx")
def fixture_snp_ctx(snp_db: Manager) -> Dict[str, Manager]:
    """Return a context with a database only initialized with snps"""
    return {"db": snp_db}
