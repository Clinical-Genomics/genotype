"""Test the CLI load functions"""

import logging
from pathlib import Path

from alchy import Manager
from click.testing import CliRunner
from cyvcf2 import VCF

from genotype.cli.load_cmd import load_cmd
from genotype.store.models import SNP, Analysis, Sample


def test_load_bcf_analysis(
    cli_runner: CliRunner, bcf_path: Path, snp_ctx: dict, vcf_sample_id: str, caplog
):
    # GIVEN a database with some SNPs loaded and one sample
    assert SNP.query.count() > 0
    assert Sample.query.count() == 0
    assert Analysis.query.count() == 0
    # GIVEN a vcf with one sample
    vcf_obj = VCF(str(bcf_path))
    assert len(vcf_obj.samples) == 1

    # WHEN loading a BCF from the command line (single sample)
    result = cli_runner.invoke(load_cmd, [str(bcf_path)], obj=snp_ctx)

    # THEN assert the command works
    assert result.exit_code == 0
    # THEN assert that one sample was added
    assert Sample.query.count() == 1
    # THEN assert one analysis was added
    assert Analysis.query.count() == 1

    new_analysis = Analysis.query.first()
    assert Sample.query.get(vcf_sample_id).analyses[0] == new_analysis


def test_load_bcf_analysis_sex(
    cli_runner: CliRunner, bcf_path: Path, snp_ctx: dict, vcf_sample_id: str, caplog
):
    """Test to load a sequence analysis and check if there was any sex added"""
    # GIVEN a database with some SNPs loaded and one sample
    # GIVEN a vcf with one sample

    # WHEN loading a BCF from the command line (single sample)
    cli_runner.invoke(load_cmd, [str(bcf_path)], obj=snp_ctx)

    sample_obj = Sample.query.first()
    # THEN assert that the sample has no sex since there is no such information
    assert sample_obj.sex is None
    # THEN assert that the analysis have no sex
    analysis_obj = Analysis.query.first()
    assert analysis_obj.sex is None


def test_load_bcf_analysis_exists(
    cli_runner: CliRunner, bcf_path: Path, sequence_ctx: dict, vcf_sample_id: str, caplog
):
    caplog.set_level(logging.DEBUG)
    # GIVEN the database is already loaded with one analysis
    analysis_obj = Analysis.query.first()
    assert analysis_obj
    assert analysis_obj.type == "sequence"
    cli_runner.invoke(load_cmd, [str(bcf_path)], obj=sequence_ctx)

    # WHEN loading the same resource again (same sample id)
    result = cli_runner.invoke(load_cmd, [str(bcf_path)], obj=sequence_ctx)

    # THEN it should exit successfully but log a warning
    assert result.exit_code == 0
    assert "found previous analysis, skip" in caplog.text


def test_load_unknown_format(cli_runner: CliRunner, config_path: Path, snp_ctx: dict, caplog):
    caplog.set_level(logging.DEBUG)
    # GIVEN a database with some SNPs loaded
    assert SNP.query.count() > 0

    # WHEN loading an and using a file in unknown format
    result = cli_runner.invoke(load_cmd, [str(config_path)], obj=snp_ctx)

    # THEN it should exit with non zero exit code
    assert result.exit_code == 1
    # THEN the correct information should be displayed
    assert f"unknown input format: {config_path}" in caplog.text
