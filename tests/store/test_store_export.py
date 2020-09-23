"""Tests for store export"""

from alchy import Manager

from genotype.store.export import _get_equality, _get_snp_dict, get_analysis_equalities, get_sample
from genotype.store.models import Analysis, Genotype, Sample


def test_get_analysis_equalities(snp_db: Manager):
    # GIVEN a sample with two analyses

    sample_id = "test"
    sample = Sample(id=sample_id)

    analyses = [
        Analysis(id=1, sample_id=sample_id, type="sequence"),
        Analysis(id=2, sample_id=sample_id, type="genotype"),
    ]

    genotypes = [
        Genotype(id=1, analysis_id=1, rsnumber="rs1", allele_1="T", allele_2="C"),
        Genotype(id=2, analysis_id=1, rsnumber="rs2", allele_1="T", allele_2="G"),
        Genotype(id=3, analysis_id=2, rsnumber="rs1", allele_1="C", allele_2="T"),
        Genotype(id=4, analysis_id=2, rsnumber="rs2", allele_1="A", allele_2="G"),
    ]

    snp_db.add_commit(sample, analyses, genotypes)

    # WHEN running get_analysis_equalities
    genotype_doc = get_analysis_equalities(snp_db, sample)

    # THEN it should return a dictionary like this:
    doc = {
        "snps": {
            "genotype": {"rs1": ["C", "T"], "rs2": ["A", "G"]},
            "sequence": {"rs1": ["T", "C"], "rs2": ["T", "G"]},
            "comp": {"rs1": True, "rs2": False},
        }
    }

    assert genotype_doc == doc


def test_get_analysis_equalities_no_analysis(snp_db: Manager):
    # GIVEN a sample with no analysis
    sample = Sample(id="test")
    snp_db.add_commit(sample)

    # WHEN running get_analysis_equalities
    genotype_doc = get_analysis_equalities(snp_db, sample)

    # THEN it should return a dictionary like this:
    doc = {"snps": {}}

    assert genotype_doc == doc


def test_get_sample(snp_db: Manager):
    # GIVEN a sample id that exits in the database

    sample_sex = "male"
    sample_status = "pass"
    sample_comment = "Hpho!"

    sample = Sample(id="test")
    sample.status = sample_status
    sample.sex = sample_sex
    sample.comment = sample_comment
    snp_db.add_commit(sample)
    date_time = sample.created_at

    # WHEN running get_sample
    genotype_doc = get_sample(sample)

    # THEN it should return a dictionary like this:
    doc = {
        "sample_created_in_genotype_db": date_time.date().isoformat(),
        "sex": sample_sex,
        "status": sample_status,
        "comment": sample_comment,
    }

    assert genotype_doc == doc


def test_get_sample_no_atributes(snp_db: Manager):
    # GIVEN a sample id that exits in the database

    sample = Sample(id="test")
    snp_db.add_commit(sample)
    date_time = sample.created_at

    # WHEN running get_sample
    genotype_doc = get_sample(sample)

    # THEN it should return a dictionary like this:
    doc = {
        "comment": None,
        "sex": None,
        "status": None,
        "sample_created_in_genotype_db": date_time.date().isoformat(),
    }

    assert genotype_doc == doc


def test_get_snp_dict(snp_db: Manager):
    # GIVEN two genotypes in the database, with the same analysis_id
    genotypes = [
        Genotype(id=1, analysis_id=1, rsnumber="rs1", allele_1="T", allele_2="C"),
        Genotype(id=2, analysis_id=1, rsnumber="rs2", allele_1="A", allele_2="G"),
    ]
    snp_db.add_commit(genotypes)

    # WHEN running _get_snp_dict for that analysis_id = 1
    snp_dict = _get_snp_dict(snp_db, analysis_id=1)

    # THEN it shoould return a dict holding the rs numbers and allels from the two genotypes
    assert snp_dict == {"rs1": ["T", "C"], "rs2": ["A", "G"]}


def test_get_snp_dict_wrong_analysis(snp_db: Manager):
    # GIVEN a analysis_id that does not exist in the database
    analysis_id = 1

    # WHEN running _get_snp_dict for that analysis_id
    snp_dict = _get_snp_dict(snp_db, analysis_id)

    # THEN it shoould return a empty dict
    assert snp_dict == {}


def test_compare():
    # GIVEN two analysis dicts like this:
    analysis_1 = {"rs1": ["T", "C"], "rs2": ["G", "A"]}
    analysis_2 = {"rs1": ["A", "C"], "rs2": ["A", "G"]}

    # WHEN running _get_equality
    compare_dict = _get_equality(analysis_1, analysis_2)

    # THEN it shoould return a compare_dict like this:
    assert compare_dict == {"rs1": False, "rs2": True}


def test_get_analysis_equalities_one_analysis_missing(snp_db: Manager):
    # GIVEN a sample with two analyses

    sample = Sample(id="test")
    analysis = Analysis(id=1, sample_id="test", type="genotype")
    genotypes = [
        Genotype(id=1, analysis_id=1, rsnumber="rs1", allele_1="C", allele_2="T"),
        Genotype(id=2, analysis_id=1, rsnumber="rs2", allele_1="A", allele_2="G"),
    ]

    snp_db.add_commit(sample, analysis, genotypes)

    # WHEN running get_analysis_equalities
    genotype_doc = get_analysis_equalities(snp_db, sample)

    # THEN it should return a dictionary like this:
    doc = {"snps": {"genotype": {"rs1": ["C", "T"], "rs2": ["A", "G"]}}}

    assert genotype_doc == doc
