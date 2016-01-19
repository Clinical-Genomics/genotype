# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from .models import Base, Genotype, Sample


class Database(object):

    """Interface to genotype database."""

    def __init__(self, db_path, connect=True):
        super(Database, self).__init__()
        self.db_path = db_path
        self.engine = None
        self.session = None

        if connect:
            self.connect()

    def connect(self):
        """Connect to a SQLite database."""
        adaptor_path = "sqlite:///{}".format(self.db_path)

        self.engine = create_engine(adaptor_path)
        # connect the engine to the ORM models
        Base.metadata.bind = self.engine

        # start a sesion
        self.session = scoped_session(sessionmaker(bind=self.engine))

        return self.session

    def setup(self, reset=False):
        """Setup a new database."""
        if reset:
            self.tear_down()

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

    def samples(self, sample_ids=None, source=None, experiment=None):
        """Fetch samples from database."""
        samples = self.session.query(Sample)
        if sample_ids:
            samples = samples.filter(Sample.sample_id.in_(sample_ids))
        if source:
            samples = samples.filter_by(source=source)
        if experiment:
            samples = samples.filter_by(experiment=experiment)
        return samples

    def remove(self, sample_id, experiment):
        """Remove sample and genotypes from the database."""
        sample_obj = (self.session.query(Sample)
                          .filter_by(sample_id=sample_id, experiment=experiment)
                          .one())
        self.session.query(Genotype).filter_by(sample_id=sample_obj.id).delete()
        self.session.delete(sample_obj)
        self.session.flush()
