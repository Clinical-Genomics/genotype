# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from .models import Base, Sample, Genotype


class Database(object):
    """Interface to genotype database."""
    def __init__(self, db_path, connect=True):
        super(Database, self).__init__()
        self.db_path = db_path

        if connect:
            self.connect()

    def connect(self):
        """Connect to a SQLite database."""
        adaptor_path = "sqlite:///{}".format(self.db_path)

        engine = create_engine(adaptor_path)
        # connect the engine to the ORM models
        Base.metadata.bind = engine

        # start a sesion
        self.session = scoped_session(sessionmaker(bind=engine))

        return self.session

    def setup(self):
        """Setup a new database."""
        # create all the tables
        Base.metadata.create_all(self.session.bind)

    def tear_down(self):
        """Tear down a database."""
        # create all the tables
        Base.metadata.drop_all(self.session.bind)

    def save(self):
        """Manually persist changes made to various elements."""
        # commit/persist dirty changes to the database
        self.session.flush()
        self.session.commit()

    def add(self, *records):
        """Add new records to the current session transaction.

        Args:
          records (list): new ORM objects instances
        """
        # add all records to the session object
        self.session.add_all(records)

    def sample(self, sample_id, experiment, check=False):
        """Get a sample based on the unique id"""
        sample_q = (self.session.query(Sample)
                        .filter_by(sample_id=sample_id, experiment=experiment))
        if check:
            return sample_q.first()
        else:
            return sample_q.one()

    def remove(self, sample_id, experiment):
        """Remove sample and genotypes from the database."""
        sample_obj = (self.session.query(Sample)
                          .filter_by(sample_id=sample_id, experiment=experiment)
                          .one())
        self.session.query(Genotype).filter_by(sample_id=sample_obj.id).delete()
        self.session.delete(sample_obj)
        self.session.flush()
