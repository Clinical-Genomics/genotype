# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from .models import Base


class Store(object):

  """SQLAlchemy-based database object.

  Bundles functionality required to setup and interact with a database.

  Examples:
    >>> store = Store('data.sqlite3')
    >>> store.set_up()

  .. note::

    For testing pourposes use ``:memory:`` as the ``path`` argument to
    set up in-memory (temporary) database.

  Args:
    uri (str, optional): path/URI to the database to connect to
    dialect (str, optional): connector + type of database:
      'sqlite'/'mysql'
    debug (bool, optional): whether to output logging information

  Attributes:
    uri (str): path/URI to the database to connect to
    engine (class): SQLAlchemy engine, defines what database to use
    session (class): SQLAlchemy ORM session, manages persistance
    query (method): SQLAlchemy ORM query builder method
  """

  def __init__(self, uri=None, dialect='sqlite', debug=False):
    super(Store, self).__init__()
    self.uri = uri
    self.db_dialect = dialect

    if uri:
      self.connect(uri, dialect=dialect, debug=debug)

  def connect(self, uri, dialect=None, debug=False):
    """Configure connection to a SQL database.

    Args:
      uri (str): path/URI to the database to connect to
      dialect (str, optional): connector + type of database:
        'sqlite'/'mysql'
      debug (bool, optional): whether to output logging information
    """
    kwargs = {'echo': debug, 'convert_unicode': True}

    db_dialect = dialect or self.db_dialect

    # connect to the SQL database
    if db_dialect == 'sqlite':
      # conform to the slightly awkward sqlite adapter syntax (///)
      auth_path = "sqlite:///%s" % uri

    elif 'mysql' in db_dialect:
      # build URI for MySQL containing:
      # <connector>+<sql_type>://<username>:<password>@<server>/<database>
      auth_path = "%(type)s://%(uri)s" % dict(type=db_dialect, uri=uri)

      kwargs['pool_recycle'] = 3600

    else:
      raise NotImplementedError(
        'Only "sqlite" and "mysql" are supported database dialects.')

    self.engine = create_engine(auth_path, **kwargs)

    # make sure the same engine is propagated to the Base classes
    Base.metadata.bind = self.engine

    # start a session
    self.session = scoped_session(sessionmaker(bind=self.engine))

    # shortcut to query method
    self.query = self.session.query

    return self

  @property
  def dialect(self):
    """Return database dialect name used for the current connection.

    Dynamic attribute.

    Returns:
      str: name of dialect used for database connection
    """
    return self.engine.dialect.name

  def set_up(self):
    """Initialize a new database with the default tables and columns.

    Returns:
      Store: self
    """
    # create the tables
    Base.metadata.create_all(self.engine)

    return self

  def tear_down(self):
    """Tear down the database (tables and columns).

    Returns:
      Store: self
    """
    # drop/delete the tables
    Base.metadata.drop_all(self.engine)

    return self

  def add(self, model):
    self.session.add(model)

    return self

  def save(self):
    """Manually persist changes. Chainable.

    Returns:
      Store: ``self`` for chainability
    """
    # commit/persist dirty changes to the database
    self.session.flush()
    self.session.commit()

    return self
