# -*- coding: utf-8 -*-
"""Tests for store export"""
from genotype.store.export import get_analysis_equalities, _get_equality, _get_snp_dict, get_sample
from genotype.store.models import Sample, Genotype, Analysis


def test_get_analysis_equalities(genotype_db):
    # GIVEN a sample with two analyses

    sample_id = 'test'
    sample = Sample(id=sample_id)
    genotype_db.add_commit(sample)

    analysis_id = 1
    analysis = Analysis(id=analysis_id)
    analysis.sample_id = sample_id
    analysis.type = 'sequence'
    genotype_db.add_commit(analysis)
    genotype_1 = Genotype(id=1)
    genotype_1.analysis_id = analysis_id
    genotype_1.rsnumber = 'rs1'
    genotype_1.allele_1 = 'T'
    genotype_1.allele_2 = 'C'
    genotype_2 = Genotype(id=2)
    genotype_2.analysis_id = analysis_id
    genotype_2.rsnumber = 'rs2'
    genotype_2.allele_1 = 'T'
    genotype_2.allele_2 = 'G'

    analysis_id = 2
    analysis = Analysis(id=analysis_id)
    analysis.sample_id = sample_id
    analysis.type = 'genotype'
    genotype_db.add_commit(analysis)
    genotype_3 = Genotype(id=3)
    genotype_3.analysis_id = analysis_id
    genotype_3.rsnumber = 'rs1'
    genotype_3.allele_1 = 'T'
    genotype_3.allele_2 = 'C'
    genotype_4 = Genotype(id=4)
    genotype_4.analysis_id = analysis_id
    genotype_4.rsnumber = 'rs2'
    genotype_4.allele_1 = 'A'
    genotype_4.allele_2 = 'G'

    genotype_db.add_commit(genotype_1, genotype_2, genotype_3, genotype_4)

    # WHEN running get_analysis_equalities
    genotype_doc = get_analysis_equalities(genotype_db, sample)

    # THEN it should return a dictionary like this:
    doc = {'snps': {'genotype': {'rs1': ['T', 'C'], 'rs2': ['A', 'G']},
                    'sequence': {'rs1': ['T', 'C'], 'rs2': ['T', 'G']},
                    'comp': {'rs1': True, 'rs2': False}}}

    assert genotype_doc == doc


def test_get_analysis_equalities_no_analysis(genotype_db):
    # GIVEN a sample with no analysis
    sample = Sample(id='test')
    genotype_db.add_commit(sample)

    # WHEN running get_analysis_equalities
    genotype_doc = get_analysis_equalities(genotype_db, sample)

    # THEN it should return a dictionary like this:
    doc = {'snps': {}}

    assert genotype_doc == doc


def test_get_sample(genotype_db):
    # GIVEN a sample id that exits in the database

    sample_sex = 'male'
    sample_status = 'pass'
    sample_comment = 'Hpho!'

    sample = Sample(id='test')
    sample.status = sample_status
    sample.sex = sample_sex
    sample.comment = sample_comment
    genotype_db.add_commit(sample)
    date_time = sample.created_at

    # WHEN running get_sample
    genotype_doc = get_sample(sample)

    # THEN it should return a dictionary like this:
    doc = {'sample_created_in_genotype_db': date_time.date().isoformat(),
           'sex': sample_sex,
           'status': sample_status,
           'comment': sample_comment}

    assert genotype_doc == doc


def test_get_sample_no_atributes(genotype_db):
    # GIVEN a sample id that exits in the database

    sample = Sample(id='test')
    genotype_db.add_commit(sample)
    date_time = sample.created_at

    # WHEN running get_sample
    genotype_doc = get_sample(sample)

    # THEN it should return a dictionary like this:
    doc = {'comment': None,
           'sex': None,
           'status': None,
           'sample_created_in_genotype_db': date_time.date().isoformat()}

    assert genotype_doc == doc


def test_get_snp_dict(genotype_db):
    # GIVEN two genotypes in the database, with the same analysis_id
    analysis_id = 1
    genotype_1 = Genotype(id=1)
    genotype_1.analysis_id = analysis_id
    genotype_1.rsnumber = 'rs1'
    genotype_1.allele_1 = 'T'
    genotype_1.allele_2 = 'C'
    genotype_2 = Genotype(id=2)
    genotype_2.analysis_id = analysis_id
    genotype_2.rsnumber = 'rs2'
    genotype_2.allele_1 = 'A'
    genotype_2.allele_2 = 'G'
    genotype_db.add_commit(genotype_1, genotype_2)

    # WHEN running _get_snp_dict for that analysis_id
    snp_dict = _get_snp_dict(genotype_db, analysis_id)

    # THEN it shoould return a dict holding the rs numbers and allels from the two genotypes
    assert snp_dict == {'rs1': ['T', 'C'], 'rs2': ['A', 'G']}


def test_get_snp_dict_wrong_analysis(genotype_db):
    # GIVEN a analysis_id that does not exist in the database
    analysis_id = 1

    # WHEN running _get_snp_dict for that analysis_id
    snp_dict = _get_snp_dict(genotype_db, analysis_id)

    # THEN it shoould return a empty dict
    assert snp_dict == {}


def test_compare():
    # GIVEN two analysis dicts like this:
    analysis_1 = {'rs1': ['T', 'C'], 'rs2': ['A', 'G']}
    analysis_2 = {'rs1': ['A', 'C'], 'rs2': ['A', 'G']}

    # WHEN running _get_equality
    compare_dict = _get_equality(analysis_1, analysis_2)

    # THEN it shoould return a compare_dict like this:
    assert compare_dict == {'rs1': False, 'rs2': True}


def test_get_equality_wrong_key():
    # GIVEN two analysis dicts like this:
    analysis_1 = {'rs1': ['T', 'C'], 'rs2': ['A', 'G']}
    analysis_2 = {'rs5': ['A', 'C'], 'rs2': ['A', 'G']}

    # WHEN running _get_equality
    compare_dict = _get_equality(analysis_1, analysis_2)

    # THEN it shoould return a compare_dict like this:
    assert compare_dict == {'rs1': False, 'rs2': True, 'rs5': False}
