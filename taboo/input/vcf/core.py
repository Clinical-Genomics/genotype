# -*- coding: utf-8 -*-
import codecs
from collections import OrderedDict
import logging

import vcf_parser
from sqlalchemy.exc import IntegrityError

from taboo._compat import zip, itervalues
import taboo.store
import taboo.rsnumbers
from taboo.store.utils import build_genotype, build_sample

logger = logging.getLogger(__name__)


def load_vcf(store, vcf_path, rsnumber_stream, experiment='sequencing',
             source=None):
    """Load samples with genotypes from a VCF file.

    Args:
        experiment (str): identifier for variant experiment (maf, mip, etc.)
    """
    # parse some meta data
    parser = vcf_parser.VCFParser(infile=vcf_path, split_variants=True)

    # build samples and add to session
    samples = [build_sample(experiment, individual,
                            source=(source or vcf_path))
               for individual in parser.individuals]
    store.add(*samples)

    try:
        # commit samples to get ids
        store.save()
    except IntegrityError as exception:
        logger.error("Sample (%s, %s) already loaded loaded into database",
                     *exception.params)
        store.session.rollback()
        raise exception

    # build mapper between samples and primary keys
    sample_dict = OrderedDict((sample.sample_id, sample.id)
                              for sample in samples)

    # read in rsnumbers
    rsnumbers = (row[0] for row in taboo.rsnumbers.read(rsnumber_stream))
    rsnumber_matcher = taboo.rsnumbers.matcher(rsnumbers)

    # start processing variants
    # skip header lines
    with codecs.open(vcf_path, 'r') as handle:
        content_lines = (line for line in handle if not line.startswith('#'))

        # split columns
        content_rows = (line.split('\t') for line in content_lines)

        # extract rsnumbers
        relevant_rows = (row for row in content_rows if row[2] in
                         rsnumber_matcher)

        variant_inputs = (format_genotype(sample_dict, variant_row)
                          for variant_row in relevant_rows)
        variant_inputs_flat = (item for sublist in variant_inputs
                               for item in sublist)

        # build genotypes and add to session
        genotypes = [build_genotype(**variant) for variant in
                     variant_inputs_flat]

    store.add(*genotypes)

    try:
        # commit the genotypes
        store.save()
    except IntegrityError as exception:
        # we are not handling multiple alleles because we don't expect any
        logger.error('Multiple alleles detected, aborting')
        store.session.rollback()

        # remove uploaded samples
        for sample in samples:
            store.session.delete(sample)
        store.save()

        raise exception

    return samples


def format_genotype(sample_dict, variant_row):
    """Format variant dict for database input.

    Will accept any number of individuals with genotypes.
    """
    rsnumber = variant_row[2]
    ref = variant_row[3]
    alt_str = variant_row[4]

    # handle '<NON_REF>'
    alt_parts = alt_str.split(',')
    alt = alt_parts[0]
    assert alt != '<NON_REF>', ("Invalid genotype position: {}"
                                .format(variant_row))

    genotypes = variant_row[9:]
    gt_mapper = {'0': ref, '1': alt, '.': 'N'}

    for sample_id, genotype_str in zip(itervalues(sample_dict), genotypes):
        # convert to base in genotype call
        genotype_parts = genotype_str.split(':')
        genotype = genotype_parts[0].split('/')
        allele_1 = gt_mapper[genotype[0]]
        allele_2 = gt_mapper[genotype[1]]

        variant_dict = {'rsnumber': rsnumber, 'sample_id': sample_id,
                        'allele_1': allele_1, 'allele_2': allele_2}
        yield variant_dict
