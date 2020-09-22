"""Test the CLI load functions"""
import logging
from pathlib import Path

from alchy import Manager
from click.testing import CliRunner
from cyvcf2 import VCF

from genotype.cli.load_cmd import load_cmd
from genotype.store.models import SNP, Analysis, Sample


def test_load_bcf_analysis(
    cli_runner: CliRunner, bcf_path: Path, snp_db: Manager, vcf_sample_id: str, caplog
):
    # GIVEN a database with some SNPs loaded and one sample
    assert SNP.query.count() > 0
    assert Sample.query.count() == 0
    assert Analysis.query.count() == 0
    # GIVEN a vcf with one sample
    vcf_obj = VCF(str(bcf_path))
    assert len(vcf_obj.samples) == 1

    context = {"db": snp_db}

    # WHEN loading a BCF from the command line (single sample)
    result = cli_runner.invoke(load_cmd, [str(bcf_path)], obj=context)

    # THEN assert the command works
    assert result.exit_code == 0
    # THEN assert that one sample was added
    assert Sample.query.count() == 1
    # THEN assert one analysis was added
    assert Analysis.query.count() == 1

    new_analysis = Analysis.query.first()
    assert Sample.query.get(vcf_sample_id).analyses[0] == new_analysis


def test_load_bcf_analysis_exists(
    cli_runner: CliRunner, bcf_path: Path, sequence_db: Manager, vcf_sample_id: str, caplog
):
    caplog.set_level(logging.DEBUG)
    # GIVEN the database is already loaded with one analysis
    analysis_obj = Analysis.query.first()
    assert analysis_obj
    assert analysis_obj.type == "sequence"
    context = {"db": sequence_db}
    cli_runner.invoke(load_cmd, [str(bcf_path)], obj=context)

    # WHEN loading the same resource again (same sample id)
    result = cli_runner.invoke(load_cmd, [str(bcf_path)], obj=context)

    # THEN it should exit succesfully but log a warning
    assert result.exit_code == 0
    assert "found previous analysis, skip" in caplog.text


def test_load_genotype_analysis(cli_runner: CliRunner, excel_single_path: Path, snp_db: Manager):
    """Test to load a genotype analysis from a excel document"""
    # GIVEN a database with some SNPs loaded and no samples
    assert SNP.query.count() > 0
    assert Sample.query.count() == 0
    context = {"db": snp_db}

    # WHEN loading an Excel book from the command line (multi-sample)
    result = cli_runner.invoke(load_cmd, [str(excel_single_path), "-k", "ID-CG-"], obj=context)

    # THEN it works and loads a sample with an analysis
    assert result.exit_code == 0
    assert Sample.query.count() > 0
    analysis_obj = Analysis.query.first()
    assert analysis_obj.type == "genotype"


def test_load_genotype_analysis_existing_sequence(
    cli_runner: CliRunner, excel_single_path: Path, sequence_db: Manager
):
    """Test to load a genotype analysis from a excel document when the sequence analysis exists"""

    # GIVEN a database with some SNPs loaded and one sample
    assert SNP.query.count() > 0
    assert Sample.query.count() == 1
    assert Analysis.query.count() == 1
    context = {"db": sequence_db}

    # WHEN loading an Excel book from the command line (multi-sample)
    result = cli_runner.invoke(load_cmd, [str(excel_single_path), "-k", "ID-CG-"], obj=context)

    # THEN it works and loads a sample with an analysis
    assert result.exit_code == 0
    # THEN assert that there is still one sample in the database
    assert Sample.query.count() == 1
    # THEN assert that two analysies exist
    assert Analysis.query.count() == 2


def test_load_unknown_format(cli_runner: CliRunner, config_path: Path, snp_db: Manager, caplog):
    caplog.set_level(logging.DEBUG)
    # GIVEN a database with some SNPs loaded
    assert SNP.query.count() > 0

    context = {"db": snp_db}
    # WHEN loading an and using a file in unknown format
    result = cli_runner.invoke(load_cmd, [str(config_path)], obj=context)

    # THEN it should exit with non zero exit code
    assert result.exit_code == 1
    # THEN the correct information should be displayed
    assert f"unknown input format: {config_path}" in caplog.text
