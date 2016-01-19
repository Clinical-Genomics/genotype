# -*- coding: utf-8 -*-
import pytest
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm.exc import NoResultFound


def test_setup(db):
    # before tables are set up
    assert db.engine.table_names() == []

    # test from scratch
    db.setup()
    assert db.engine.table_names() == ['genotype', 'sample']


def test_setup_reset(test_db):
    assert test_db.sample('sample1', 'sequencing', check=True)
    test_db.setup(reset=True)
    assert test_db.sample('sample1', 'sequencing', check=True) is None


def test_tear_down(test_db):
    assert test_db.sample('sample1', 'sequencing', check=True)
    test_db.tear_down()
    with pytest.raises(OperationalError):
        assert test_db.sample('sample1', 'sequencing', check=True) is None
    assert test_db.engine.table_names() == []


def test_sample(test_db):
    # test existing sample
    sample_obj = test_db.sample('sample1', 'sequencing')
    assert sample_obj.sample_id == 'sample1'

    # test missing sample
    with pytest.raises(NoResultFound):
        test_db.sample('sampleQue', 'sequencing')

    # test checking existance of sample
    sample_obj = test_db.sample('sampleQue', 'sequencing', check=True)
    assert sample_obj is None


def test_remove(test_db):
    assert test_db.sample('sample1', 'sequencing')
    test_db.remove('sample1', 'sequencing')
    assert test_db.sample('sampleQue', 'sequencing', check=True) is None
