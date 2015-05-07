# -*- coding: utf-8 -*-
import os
import taboo.store


def test_setup():
    """Test setting up the database."""
    db_path = 'tests/test.sqlite3'
    db = taboo.store.setup(db_path)

    assert os.path.exists(db_path)
