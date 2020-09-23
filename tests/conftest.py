"""Common fixtures for genotype tests"""

import codecs
from functools import partial
from pathlib import Path
from typing import List

import cyvcf2
import pytest
from alchy import Manager
from click.testing import CliRunner

from genotype.cli import root
from genotype.cli.load_cmd import load_cmd
from genotype.init.utils import read_snps
from genotype.store import api
from genotype.store.models import SNP, Analysis, Genotype, Sample


# Name fixtures
@pytest.fixture(name="sample_id")
def fixture_sample_id() -> str:
    """Return a sample id"""
    return "sample"


@pytest.fixture(name="vcf_sample_id")
def fixture_vcf_sample_id(sample_id: str) -> str:
    """Return a sample id that exists in the test VCF"""
    return sample_id


@pytest.fixture(name="excel_sample_prefix")
def excel_sample_prefix() -> str:
    """Return the prefix that is used for samples in the excel sheets"""
    return "ID-CG-"


# Test paths fixtures
@pytest.fixture(name="fixtures_path")
def fixture_fixtures_path() -> Path:
    """Path to dir with fixture files"""
    return Path("tests/fixtures")


# File fixtures
@pytest.fixture(name="snp_path")
def fixture_snp_path(fixtures_path: Path) -> Path:
    """Return the path to a file with snp definitions"""
    return fixtures_path / "snps.grch37.txt"


@pytest.fixture(name="bcf_path")
def fixture_bcf_path(fixtures_path: Path) -> Path:
    """Return the path to a bcf file with variants"""
    return fixtures_path / "single_sequence.bcf"


@pytest.fixture(name="excel_path")
def fixture_excel_path(fixtures_path: Path) -> Path:
    """Return the path to a excel file with snp information for three samples"""
    return fixtures_path / "genotype.xlsx"


@pytest.fixture(name="excel_single_path")
def fixture_excel_single_path(fixtures_path: Path) -> Path:
    """Return the path to a excel file with snp information for one sample"""
    return fixtures_path / "single_genotype.xlsx"


@pytest.fixture(name="config_path")
def fixture_config_path(fixtures_path: Path) -> Path:
    """Return the path to a genotype config file"""
    return fixtures_path / "config.yaml"


# snp fixtures
@pytest.fixture(name="snp_sequence")
def fixture_snp_sequence(snp_path: Path) -> List[str]:
    """Return a list with snp information"""
    with codecs.open(str(snp_path), "r") as sequence:
        lines = [line for line in sequence]
    return lines


@pytest.fixture(name="snp_count")
def fixture_snp_count(snp_sequence: List[str]) -> int:
    """Return the number of SNPs in snp_sequence"""
    return len(snp_sequence)


@pytest.fixture(name="snps")
def fixture_snps(snp_sequence: List[str]) -> List[SNP]:
    """Return a list of created SNPs"""
    return list(read_snps(snp_sequence))


@pytest.fixture(name="vcf")
def fixture_vcf(bcf_path: Path) -> cyvcf2.VCF:
    """Return a VCF object"""
    _vcf = cyvcf2.VCF(str(bcf_path))
    return _vcf


@pytest.yield_fixture(scope="function", name="empty_db")
def fixture_empty_db() -> Manager:
    """Return a manager with a empty instantiated database"""
    _db = api.connect("sqlite://")
    _db.create_all()
    yield _db
    _db.drop_all()


@pytest.yield_fixture(scope="function", name="snp_db")
def fixture_snp_db(empty_db: Manager, snps: List[SNP]) -> Manager:
    """Return a manager with a database populated with snps"""
    empty_db.add_commit(snps)
    return empty_db


@pytest.yield_fixture(scope="function", name="existing_db")
def fixture_existing_db(tmpdir) -> Manager:
    """Return a manager with a existing instantiated database"""
    db_path = "sqlite:///{}".format(tmpdir.join("coverage.sqlite3"))
    genotype_db = api.connect(db_path)
    genotype_db.create_all()
    yield genotype_db
    genotype_db.drop_all()


@pytest.yield_fixture(scope="function", name="sample_db")
def sample_db(snp_db: Manager, sample: Sample) -> Manager:
    """Return a manager with a database populated with snps and a sample with a genotype analysis"""
    snp_db.add_commit(sample)
    return snp_db


@pytest.yield_fixture(scope="function", name="sequence_db")
def fixture_sequence_db(snp_db: Manager, bcf_path: Path, cli_runner: CliRunner) -> Manager:
    """Return a manager with a database populated with snps and a sample with a sequence analysis"""
    cli_runner.invoke(load_cmd, [str(bcf_path)], obj={"db": snp_db})
    return snp_db


@pytest.yield_fixture(scope="function", name="genotype_db")
def fixture_genotype_db(
    snp_db: Manager, excel_single_path: Path, cli_runner: CliRunner, excel_sample_prefix: str
) -> Manager:
    """Return a manager with a database populated with snps and a sample with a genotype analysis"""
    cli_runner.invoke(
        load_cmd, [str(excel_single_path), "-k", excel_sample_prefix], obj={"db": snp_db}
    )
    return snp_db


@pytest.yield_fixture(scope="function", name="sample_db")
def fixture_sample_db(genotype_db: Manager, snps: List[SNP]) -> Manager:
    genotype_db.add_commit(snps)
    yield genotype_db
    genotype_db.drop_all()
    genotype_db.create_all()


@pytest.fixture(name="cli_runner")
def cli_runner() -> CliRunner:
    """Return a CliRunner for testing cli commands"""
    runner = CliRunner()
    return runner


@pytest.fixture
def invoke_cli(cli_runner):
    return partial(cli_runner.invoke, root)


@pytest.fixture(name="genotypes")
def fixture_genotypes() -> dict:
    """Return a dictionary with genotypes"""
    _genotypes = {
        1: Genotype(rsnumber="RS12", allele_1="G", allele_2="A"),
        2: Genotype(rsnumber="RS12", allele_1="G", allele_2="G"),
        "unknown": Genotype(rsnumber="RS13", allele_1="0", allele_2="0"),
    }
    return _genotypes


@pytest.fixture(name="sample")
def fixture_sample(sample_id: str) -> Sample:
    """Return a sample object"""
    genotypes = [
        Genotype(rsnumber="rs9988021", allele_1="G", allele_2="G"),
        Genotype(rsnumber="rs115551684", allele_1="G", allele_2="A"),
        Genotype(rsnumber="rs199560653", allele_1="G", allele_2="G"),
        Genotype(rsnumber="rs5918195", allele_1="T", allele_2="C"),
    ]
    analysis = Analysis(type="genotype", source="file.xlsx", sex="female", genotypes=genotypes)
    _sample = Sample(id=sample_id)
    _sample.analyses.append(analysis)
    return _sample
