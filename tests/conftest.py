# -*- coding: utf-8 -*-
import pytest

from taboo.store import Database
from taboo.store.models import Sample


@pytest.yield_fixture(scope='session')
def rshandle():
    with open('tests/fixtures/rsnumbers.grch37.txt') as handle:
        yield handle


@pytest.yield_fixture(scope='function')
def db():
    """Initialize a testing datbase."""
    _db = Database(':memory:')
    yield _db
    _db.tear_down()


@pytest.yield_fixture(scope='function')
def test_db(db):
    """Initialize database with some data."""
    db.setup()
    db.add(Sample(sample_id='sample1', experiment='sequencing'))
    db.save()
    yield db
    pass
