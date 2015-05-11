# -*- coding: utf-8 -*-
import codecs
import logging

import vcf_parser
from sqlalchemy.exc import IntegrityError

from taboo._compat import iteritems
import taboo.store
from taboo.store.utils import build_genotype, build_sample

logger = logging.getLogger(__name__)


def load_vcf(store, vcf_path, rsnumber_stream, origin='sequencing'):
    """Load samples with genotypes from a VCF file.

    Args:
        origin (str): identifier for variant origin (maf, mip, etc.)
    """
    parser = vcf_parser.VCFParser(infile=vcf_path, split_variants=True)

    # build samples and add to session
    samples = [build_sample(origin, individual) for individual in parser.individuals]
    store.add(*samples)

    try:
        # commit samples to get ids
        store.save()
    except IntegrityError as exception:
        logger.error("Sample ({}, {}) already loaded loaded into database"
                     .format(*exception.params))
        store.session.rollback()
        raise exception

    # build mapper between samples and primary keys
    sample_dict = {sample.sample_id: sample.id for sample in samples}

    # start processing variants
    rsnumbers = read_rsnumbers(rsnumber_stream)
    matched_variants = extract_rsnumbers(parser, rsnumbers)
    removed_nonref = (variant for variant in matched_variants
                      if variant['ALT'] != '<NON_REF>')
    variant_inputs = (format_genotype(sample_dict, variant)
                      for variant in removed_nonref)
    variant_inputs_flat = (item for sublist in variant_inputs for item in sublist)

    # build genotypes and add to session
    genotypes = [build_genotype(**variant) for variant in variant_inputs_flat]
    store.add(*genotypes)

    try:
        # commit the genotypes
        store.save()
    except IntegrityError as exception:
        # we are not handling multiple alleles because we don't expect any
        logger.error("Multiple alleles detected, aborting")
        store.session.rollback()

        # remove uploaded samples
        for sample in samples:
            store.session.delete(sample)
        store.save()

        raise exception


def read_rsnumbers(rsnumbers_stream):
    # read in rsnumbers
    return set([rsnumber.strip() for rsnumber in rsnumbers_stream])


def extract_rsnumbers(variants, rsnumbers):
    """Filter variants based on a set of rsnumbers."""
    rsnumber_map = set(rsnumbers)
    matched_variants = (variant for variant in variants
                        if variant.get('ID') in rsnumber_map)

    return matched_variants


def format_genotype(sample_dict, variant):
    """Format variant dict for database input.

    Will accept any number of individuals with genotypes.
    """
    gt_mapper = {
        '0': variant['REF'],
        '1': variant['ALT']
    }

    for sample_id, genotype in iteritems(variant['genotypes']):
        primary_key = sample_dict[sample_id]

        # convert to base in genotype call
        allele_1 = gt_mapper[genotype.allele_1]
        allele_2 = gt_mapper[genotype.allele_2]

        variant_dict = {'rsnumber': variant['ID'], 'sample_id': primary_key,
                        'allele_1': allele_1, 'allele_2': allele_2}
        yield variant_dict
