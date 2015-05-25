# -*- coding: utf-8 -*-
import os
import taboo.store


class TestStore:
    db_path = 'tests/test.sqlite3'
    store = None

    def setup(self):
        """Setup database for testing."""
        self.store = taboo.store.Database(self.db_path)
        self.store.setup()

    def teardown(self):
        """Remve the database file."""
        os.remove(self.db_path)

    def test_setup(self):
        """Test that the setup created a new database."""
        assert os.path.exists(self.db_path)
