# -*- coding: utf-8 -*-
import collections
import logging
import os

from alchy import Manager

from taboo.load.mixins import LoadMixin
from taboo.match.mixins import MatchMixin
from .mixins import ModelsMixin
from .models import Model

log = logging.getLogger(__name__)


class TabooDB(Manager, LoadMixin, ModelsMixin, MatchMixin):

    """Manage Taboo database."""

    def __init__(self, uri=None, debug=False, Model=Model):
        self.Model = Model
        self.uri = uri
        if uri:
            self.connect(uri, debug=debug)

    def connect(self, db_uri, debug=False):
        """Configure connection to a SQL database.

        Args:
            db_uri (str): path/URI to the database to connect to
            debug (Optional[bool]): whether to output logging information
        """
        config = {'SQLALCHEMY_ECHO': debug}
        if 'mysql' in db_uri:  # pragma: no cover
            config['SQLALCHEMY_POOL_RECYCLE'] = 3600
        elif '://' not in db_uri:
            # expect only a path to a sqlite database
            db_path = os.path.abspath(os.path.expanduser(db_uri))
            db_uri = "sqlite:///{}".format(db_path)
            self.uri = db_uri

        config['SQLALCHEMY_DATABASE_URI'] = db_uri

        # connect to the SQL database
        super(TabooDB, self).__init__(config=config, Model=self.Model)

        # shortcut to query method
        self.query = self.session.query
        return self

    def set_up(self):
        """Initialize a new database with the default tables and columns.

        Returns:
            TabooDB: self
        """
        # create the tables
        self.create_all()
        tables = self.Model.metadata.tables.keys()
        log.info("created tables: %s", ', '.join(tables))
        return self

    def tear_down(self):
        """Tear down a database (tables and columns).

        Returns:
            TabooDB: self
        """
        # drop/delete the tables
        self.drop_all()
        return self

    def save(self):
        """Manually persist changes made to various elements. Chainable.

        Returns:
            TabooDB: `self` for chainability
        """
        try:
            # commit/persist dirty changes to the database
            self.session.flush()
            self.session.commit()
        except Exception as error:
            log.debug('rolling back failed transaction')
            self.session.rollback()
            raise error
        return self

    def add(self, items):
        """Add one or more new items and commit the changes. Chainable.

        Args:
            items (Model/List[Model]): new ORM object instance or list of

        Returns:
            TabooDB: `self` for chainability
        """
        if isinstance(items, self.Model):
            # Add the record to the session object
            self.session.add(items)
        elif isinstance(items, list):
            # Add all records to the session object
            self.session.add_all(items)
        elif (isinstance(items, collections.Iterable) and
              not isinstance(items, dict)):
            # Iterate over all items
            for element in items:
                self.session.add(element)
        else:
            raise ValueError("unknown object type for 'items'")
        return self
