# -*- coding: utf-8 -*-
import codecs
from functools import partial

from click.testing import CliRunner
import cyvcf2
import pytest

from taboo.cli import root
from taboo.init.utils import read_snps
from taboo.store import api
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
def vcf(bcf_path):
    _vcf = cyvcf2.VCF(bcf_path)
    return _vcf


@pytest.yield_fixture(scope='function')
def taboo_db():
    _taboo_db = api.connect('sqlite://')
    _taboo_db.create_all()
    yield _taboo_db
    _taboo_db.drop_all()


@pytest.yield_fixture(scope='function')
def existing_db(tmpdir):
    db_path = "sqlite:///{}".format(tmpdir.join('coverage.sqlite3'))
    taboo_db = api.connect(db_path)
    taboo_db.create_all()
    yield taboo_db
    taboo_db.drop_all()


@pytest.yield_fixture(scope='function')
def setexist_db(existing_db, snp_sequence, sample):
    snp_records = read_snps(snp_sequence)
    existing_db.add_commit(*snp_records)
    existing_db.add_commit(sample)
    yield existing_db
    existing_db.drop_all()
    existing_db.create_all()


@pytest.yield_fixture(scope='function')
def sample_db(taboo_db, snp_sequence):
    snp_records = read_snps(snp_sequence)
    taboo_db.add_commit(*snp_records)
    yield taboo_db
    taboo_db.drop_all()
    taboo_db.create_all()


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
