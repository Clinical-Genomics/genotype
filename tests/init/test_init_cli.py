"""Test to initialize databases"""

from pathlib import Path

from click.testing import CliRunner
from alchy import Manager

from genotype.store.models import Sample, SNP
from genotype.cli.base_cmd import root
from genotype.cli.init_cmd import init_cmd


def test_init(cli_runner: CliRunner, existing_db: Manager, snp_path: Path, snp_count: int):
    """Test to initialize a database with some snps"""
    # GIVEN an empty exising database
    db_uri = existing_db.engine.url
    assert Sample.query.count() == 0
    assert SNP.query.count() == 0

    # WHEN running 'init' subcommand in CLI
    result = cli_runner.invoke(root, ["-d", db_uri, "init", str(snp_path)])

    # THEN it should work and populate the database with SNPs
    assert result.exit_code == 0
    assert SNP.query.count() == snp_count


def test_init_already_initialised(
    cli_runner: CliRunner, existing_db: Manager, snp_count: int, snp_path: str
):
    """Test to intitialize a database that is already initialized"""
    # GIVEN a database which is already set up
    db_uri = existing_db.engine.url
    cli_runner.invoke(root, ["-d", db_uri, "init", str(snp_path)])
    assert SNP.query.count() == snp_count
    # WHEN running 'init' subcommand again
    result = cli_runner.invoke(root, ["-d", db_uri, "init", str(snp_path)])
    # THEN it should abort and log a warning
    assert result.exit_code != 0
    assert "WARNING" in result.output


def test_reset_initialized(
    cli_runner: CliRunner, genotype_db: Manager, snp_count: int, snp_path: str
):
    """Test to re initialise a database by using the 'reset' flag"""
    # GIVEN a database which is already set up
    context = {"db": genotype_db}
    assert SNP.query.count() == snp_count

    # WHEN running 'init' subcommand again **with reset flag**
    result = cli_runner.invoke(init_cmd, ["--reset", str(snp_path)], obj=context)

    # THEN it should tear down the db first and work!
    assert result.exit_code == 0
    assert SNP.query.count() == snp_count
