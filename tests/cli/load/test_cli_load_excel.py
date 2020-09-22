"""Test cli command for loading excel files"""

from pathlib import Path

from alchy import Manager
from click.testing import CliRunner

from genotype.cli.load_cmd import load_cmd
from genotype.store.models import SNP, Analysis, Sample


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


def test_load_genotype_analysis_sex(
    cli_runner: CliRunner, excel_single_path: Path, snp_db: Manager, vcf_sample_id: str, caplog
):
    """Test to load a genotype analysis and check if there was any sex added"""
    # GIVEN a database with some SNPs loaded and one sample
    # GIVEN a vcf with one sample

    context = {"db": snp_db}
    # WHEN loading a BCF from the command line (single sample)
    result = cli_runner.invoke(load_cmd, [str(excel_single_path)], obj=context)

    # THEN assert that the sample should have no sex since it has not been set
    sample_obj = Sample.query.first()
    assert sample_obj.sex is None
    # THEN assert that the analysis have a predicted sex since it exists in the excel file
    analysis_obj = Analysis.query.first()
    assert analysis_obj.sex is not None
