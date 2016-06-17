# -*- coding: utf-8 -*-
import codecs
from functools import partial

from click.testing import CliRunner
import pysam
import pytest

from taboo.cli import root
from taboo.init.utils import read_snps
from taboo.store.api import TabooDB
from taboo.store.models import SNP, Genotype, Sample, Analysis


@pytest.fixture
def snp_path():
    return 'tests/fixtures/snps.sample.txt'


@pytest.fixture
def bcf_path():
    return 'tests/fixtures/sample.bcf'


@pytest.fixture
def excel_path():
    return 'tests/fixtures/simple.xlsx'


@pytest.fixture
def config_path():
    return 'tests/fixtures/sample/config.yaml'


@pytest.fixture
def snp_sequence(snp_path):
    with codecs.open(snp_path, 'r') as sequence:
        lines = [line for line in sequence]
    return lines


@pytest.fixture
def snps(sample_db):
    return SNP.query.all()


@pytest.fixture
def bcf(bcf_path):
    _bcf = pysam.VariantFile(bcf_path, 'rb')
    return _bcf


@pytest.yield_fixture(scope='function')
def taboo_db():
    _taboo_db = TabooDB('sqlite://')
    _taboo_db.set_up()
    yield _taboo_db
    _taboo_db.tear_down()


@pytest.yield_fixture(scope='function')
def existing_db(tmpdir):
    db_path = tmpdir.join('coverage.sqlite3')
    taboo_db = TabooDB(str(db_path))
    taboo_db.set_up()
    yield taboo_db
    taboo_db.tear_down()


@pytest.yield_fixture(scope='function')
def setexist_db(existing_db, snp_sequence, sample):
    snp_records = read_snps(snp_sequence)
    existing_db.add(snp_records).save()
    existing_db.add(sample).save()
    yield existing_db
    existing_db.tear_down()
    existing_db.set_up()


@pytest.yield_fixture(scope='function')
def sample_db(taboo_db, snp_sequence):
    snp_records = read_snps(snp_sequence)
    taboo_db.add(snp_records).save()
    yield taboo_db
    taboo_db.tear_down()
    taboo_db.set_up()


@pytest.fixture
def cli_runner():
    runner = CliRunner()
    return runner


@pytest.fixture
def invoke_cli(cli_runner):
    return partial(cli_runner.invoke, root)


@pytest.fixture
def genotypes():
    _genotypes = {
        1: Genotype(rsnumber='RS12', allele_1='G', allele_2='A'),
        2: Genotype(rsnumber='RS12', allele_1='G', allele_2='G'),
        'unknown': Genotype(rsnumber='RS13', allele_1='0', allele_2='0')
    }
    return _genotypes


@pytest.fixture
def sample():
    genotypes = [Genotype(rsnumber='rs9988021', allele_1='G', allele_2='G'),
                 Genotype(rsnumber='rs115551684', allele_1='G', allele_2='A'),
                 Genotype(rsnumber='rs199560653', allele_1='G', allele_2='G'),
                 Genotype(rsnumber='rs5918195', allele_1='T', allele_2='C')]
    analysis = Analysis(type='genotype', source='file.xlsx', sex='female',
                        genotypes=genotypes)
    _sample = Sample(id='sample')
    _sample.analyses.append(analysis)
    return _sample
