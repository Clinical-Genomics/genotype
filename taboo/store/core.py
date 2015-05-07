# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from .models import Base


def connect(db_path):
    """Connect to a SQLite database."""
    adaptor_path = "sqlite:///{}".format(db_path)

    engine = create_engine(adaptor_path)
    # connect the engine to the ORM models
    Base.metadata.bind = engine

    # start a sesion
    session = scoped_session(sessionmaker(bind=engine))

    return session


def setup(db_path):
    """Setup a new database."""
    session = connect(db_path)

    # create all the tables
    Base.metadata.create_all(session.bind)


def tear_down(db_path):
    """Tear down a database."""
    session = connect(db_path)

    # create all the tables
    Base.metadata.drop_all(session.bind)
