# -*- coding: utf-8 -*-
from genotype.store.trending import build_snp_dict, compare, prepare_trending
from genotype.store.models import Sample, Genotype, Analysis


def test_prepare_trending(genotype_db):
    # GIVEN a sample id that exits in the database
    sample_id = 'test'
    sample_sex = 'male'
    sample_status = 'pass'
    sample = Sample(id=sample_id)
    sample.status = sample_status
    sample.sex = sample_sex
    genotype_db.add_commit(sample)
    date_time = sample.created_at

    # WHEN running prepare_trending
    genotype_doc = prepare_trending(sample_id)

    # THEN it should return a document ...
    doc = {'_id': sample_id,
            'sample_created_in_genotype_db': date_time,
            'sex': sample_sex,
            'snps': {},
            'status': sample_status}

    assert genotype_doc == doc


def test_prepare_trending_no_sample(genotype_db):
    # GIVEN a sample id that is not in the database
    sample_id = 'test_2'

    # WHEN running prepare_trending
    genotype_doc = prepare_trending(sample_id)

    # THEN it shoould return a empty document 
    assert genotype_doc == {}


def test_build_snp_dict(genotype_db):
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

    # WHEN running build_snp_dict for that analysis_id
    snp_dict = build_snp_dict(analysis_id)

    # THEN it shoould return a dict holding the rs numbers and allels from the two genotypes
    assert snp_dict == {'rs1': ['T', 'C'], 'rs2': ['A', 'G']}


def test_build_snp_dict_wrong_analysis(genotype_db):
    # GIVEN a analysis_id that does not exist in the database
    analysis_id = 1

    # WHEN running build_snp_dict for that analysis_id
    snp_dict = build_snp_dict(analysis_id)

    # THEN it shoould return a empty dict
    assert snp_dict == {}


def test_compare(genotype_db):
    # GIVEN two analysis dicts like this:
    analysis_1 = {'rs1': ['T', 'C'], 'rs2': ['A', 'G']}
    analysis_2 = {'rs1': ['A', 'C'], 'rs2': ['A', 'G']}

    # WHEN running compare
    compare_dict = compare(analysis_1, analysis_2)

    # THEN it shoould return a compare_dict like this: 
    assert compare_dict == {'rs1': False, 'rs2': True}

def test_compare_wrong_key(genotype_db):
    # GIVEN two analysis dicts like this:
    analysis_1 = {'rs1': ['T', 'C'], 'rs2': ['A', 'G']}
    analysis_2 = {'rs5': ['A', 'C'], 'rs2': ['A', 'G']}

    # WHEN running compare
    compare_dict = compare(analysis_1, analysis_2)

    # THEN it shoould return a compare_dict like this: 
    assert compare_dict == {'rs1': False, 'rs2': True, 'rs5': False}



