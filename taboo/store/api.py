# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from .models import Analysis, Base, Genotype, Sample


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

    def sample(self, sample_id, check=False):
        """Get a sample based on the unique id"""
        sample_q = self.session.query(Sample).filter_by(sample_id=sample_id)
        return sample_q.first() if check else sample_q.one()

    def analysis(self, sample_id, experiment, check=False):
        """Get an analysis (SNP calling) from the databse."""
        analysis_q = (self.session.query(Analysis)
                                  .join(Analysis.sample)
                                  .filter(Analysis.experiment == experiment,
                                          Sample.sample_id == sample_id))
        return analysis_q.first() if check else analysis_q.one()

    def get_or_create(self, model, **fields):
        """Fecth an original or create a new record."""
        if model == 'sample':
            sample_id = fields['sample_id']
            model_obj = (self.session.query(Sample)
                             .filter_by(sample_id=sample_id).first())

        if model_obj is None:
            model_obj = Sample(**fields)
            self.add(model_obj)
            self.save()

        return model_obj

    def add_analysis(self, sample_obj, experiment, source, sex=None):
        """Add a new analysis to the database."""
        analysis_obj = Analysis(sample=sample_obj, experiment=experiment,
                                source=source, sex=sex)
        # self.add(analysis_obj)
        # self.save()
        return analysis_obj

    def analyses(self, sample_ids=None, source=None, experiment=None):
        """Fetch analyses from database."""
        objects = self.session.query(Analysis)
        if sample_ids:
            objects = (objects.join(Analysis.sample)
                              .filter(Sample.sample_id.in_(sample_ids)))
        if source:
            objects = objects.filter_by(source=source)
        if experiment:
            objects = objects.filter_by(experiment=experiment)
        return objects

    def samples(self, sample_ids=None):
        """Fetch samples."""
        objects = self.session.query(Sample)
        if sample_ids:
            objects = objects.filter(Sample.sample_id.in_(sample_ids))
        return objects

    def remove_sample(self, sample_id):
        """Remove a sample including loaded analyses."""
        sample_obj = self.sample(sample_id)

        for analysis in sample_obj.analyses:
            self.remove(sample_id, analysis.experiment)

        self.session.delete(sample_obj)
        self.save()

    def experiments(self, experiment='genotyping'):
        """Return ids for all genotyping plates in the datbase."""
        analysis_objs = (self.session.query(Analysis)
                                     .filter_by(experiment=experiment)
                                     .group_by(Analysis.source))
        analysis_ids = [analysis.source for analysis in analysis_objs]
        return analysis_ids

    def remove(self, sample_id, experiment):
        """Remove sample and genotypes from the database."""
        analysis_obj = self.analysis(sample_id, experiment)
        self.session.query(Genotype).filter_by(analysis_id=analysis_obj.id).delete()
        self.session.delete(analysis_obj)
        self.save()

    def add_sex(self, sample_id, expected_sex, seq_sex=None):
        """Add excepted and sequencing sex result."""
        sample_obj = self.sample(sample_id)
        sample_obj.expected_sex = expected_sex

        if seq_sex:
            analyses = sample_obj.analysis_dict
            if 'sequencing' not in analyses:
                raise ValueError('need to load sequencing results')
            analyses['sequencing'].sex = seq_sex

        self.save()
