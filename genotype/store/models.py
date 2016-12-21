# -*- coding: utf-8 -*-
from collections import Counter
from datetime import datetime
import json

from alchy import ModelBase, make_declarative_base
from housekeeper.server.admin import UserManagementMixin
from sqlalchemy import Column, ForeignKey, types
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint

from genotype.constants import SEXES, TYPES
from genotype.exc import UnknownAllelesError, InsufficientAnalysesError
from genotype.match.core import compare_analyses


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError('Type not serializable')


class JsonModel(ModelBase):

    def to_json(self, pretty=False):
        """Serialize Model to JSON."""
        kwargs = dict(indent=4, sort_keys=True) if pretty else dict()
        return json.dumps(self.to_dict(), default=json_serial, **kwargs)


Model = make_declarative_base(Base=JsonModel)


class Genotype(Model):

    """Represent a genotype call for a position.

    Attributes:
        rsnumber (str): SNP id
        analysis (Analysis): related Analysis model
        allele_1 (str): first allele base
        allele_2 (str): second allele base
    """

    __table_args__ = (UniqueConstraint('analysis_id', 'rsnumber',
                                       name='_analysis_rsnumber'),)

    id = Column(types.Integer, primary_key=True)
    rsnumber = Column(types.String(10))
    analysis_id = Column(types.Integer, ForeignKey('analysis.id'))
    allele_1 = Column(types.String(1))
    allele_2 = Column(types.String(1))

    @property
    def alleles(self):
        """Return sorted because we are not dealing with phased data."""
        alleles = sorted([self.allele_1, self.allele_2])
        return alleles

    def __eq__(self, other):
        """Compare if two genotypes are the same."""
        if '0' in self.alleles or '0' in other.alleles:
            raise UnknownAllelesError()
        return self.alleles == other.alleles

    def stringify(self):
        """Stringify genotype."""
        return "{}{}".format(*self.alleles)

    @property
    def is_ok(self):
        """Check that the allele determination is okey."""
        if '0' in self.alleles:
            return False
        else:
            return True


class Analysis(Model):

    """Represent a SNP analysis (genotyping, sequencing).

    Attributes:
        type (str): 'sequence' or 'genotype'
        source (str): where the genotypes originated from
        sex (str): prediction of 'male', 'female', or 'unknown'
        sample (Sample): related sample object
        genotypes (List[Genotype]): related genotypes from the analysis
    """

    __table_args__ = (UniqueConstraint('sample_id', 'type',
                                       name='_sample_type'),)

    id = Column(types.Integer, primary_key=True)
    type = Column(types.Enum(*TYPES), nullable=False)
    source = Column(types.Text())
    sex = Column(types.Enum(*SEXES))
    sample_id = Column(types.String(32), ForeignKey('sample.id'))
    created_at = Column(types.DateTime, default=datetime.now)
    plate_id = Column(ForeignKey('plate.id'))

    genotypes = relationship('Genotype', order_by='Genotype.rsnumber',
                             cascade='all,delete', backref='analysis')

    def __str__(self):
        """Stringify genotypes."""
        genotype_strs = [gt.stringify() for gt in self.genotypes]
        parts = [self.sample_id, self.type, self.sex or '[sex]'] + genotype_strs
        return '\t'.join(parts)

    def check(self):
        """Check that genotypes look okey."""
        calls = ['known' if genotype.is_ok else 'unknown' for genotype
                 in self.genotypes]
        counter = Counter(calls)
        return counter


class Sample(Model):

    """Represent a sample.

    Attributes:
        id (str): unique sample id
        status (str): status of sample comparison
        comment (str): comments about pass/fail, also stores overwrites
    """

    id = Column(types.String(32), primary_key=True)
    status = Column(types.Enum('pass', 'fail', 'cancel'))
    comment = Column(types.Text(convert_unicode=True))
    sex = Column(types.Enum(*SEXES))
    created_at = Column(types.DateTime, default=datetime.now)

    analyses = relationship('Analysis', cascade='all,delete', backref='sample')

    def __str__(self):
        """Stringify sample record."""
        parts = [self.id, self.status or '[status]', self.sex or '[sex]']
        return '\t'.join(parts)

    def update_status(self, new_status, comment_update):
        """Update the status with a required comment."""
        comment_update = u"""MANUAL STATUS UPDATE: {old} -> {new}
Date: {date}
{comment}""".format(old=self.status, new=new_status, date=datetime.now(),
                    comment=comment_update)
        self.status = new_status
        if self.comment:
            self.comment = u"{}\n\n{}".format(self.comment, comment_update)
        else:
            self.comment = comment_update

    def analysis(self, type):
        """Return the analysis corresponding to the given type."""
        for analysis in self.analyses:
            if analysis.type == type:
                return analysis

    def compare(self):
        """Compare genotypes across related analyses."""
        if len(self.analyses) < 2:
            raise InsufficientAnalysesError()
        return compare_analyses(*self.analyses)

    def genotype_comparisons(self):
        """Return compared genotypes."""
        genotype_pairs = zip(self.analysis('genotype').genotypes,
                             self.analysis('sequence').genotypes)
        for gt1, gt2 in genotype_pairs:
            if '0' in gt1.alleles or '0' in gt2.alleles:
                yield gt1, gt2, 'unknown'
            elif gt1.alleles == gt2.alleles:
                yield gt1, gt2, 'match'
            else:
                yield gt1, gt2, 'mismatch'

    def check_sex(self):
        """Check that the sex determination is okey."""
        assert self.sex is not None, "need to set expected sex on sample"
        assert self.sex is not 'unknown', "need to specify known sex on sample"
        sexes = list(self.sexes)
        if len(sexes) == 1:
            raise ValueError("need to add sex information to analyses")
        elif 'unkonwn' in sexes:
            return False
        uniq_sexes = set(sexes)
        if len(uniq_sexes) == 1:
            return True
        else:
            return False

    @property
    def sexes(self):
        """Return all the sex determinations."""
        if self.sex:
            yield self.sex
        for analysis in self.analyses:
            if analysis.sex:
                yield analysis.sex


class SNP(Model):

    """Represent a SNP position under investigation."""

    id = Column(types.String(32), primary_key=True)
    ref = Column(types.String(1))
    chrom = Column(types.String(5))
    pos = Column(types.Integer)


class User(Model, UserManagementMixin):

    plates = relationship('Plate', backref='user')


class Plate(Model):

    """Describe a MAF plate of samples and it's status."""

    id = Column(types.Integer, primary_key=True)
    created_at = Column(types.DateTime, default=datetime.now)
    plate_id = Column(types.String(16), unique=True, nullable=False)

    signed_by = Column(ForeignKey('user.id'))
    signed_at = Column(types.DateTime)
    method_document = Column(types.Integer, default=1477)
    method_version = Column(types.Integer)

    analyses = relationship('Analysis', backref='plate')
