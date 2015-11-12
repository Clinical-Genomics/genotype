# -*- coding: utf-8 -*-
import codecs
import logging
import os

import vcf_parser
from sqlalchemy.exc import IntegrityError

import taboo.store
from taboo.store.models import Sample, Genotype
import taboo.rsnumbers

logger = logging.getLogger(__name__)


def load_vcf(store, vcf_path, rsnumber_stream, experiment='sequencing',
             source=None, force=False):
    """Load samples with genotypes from a VCF file.

    Args:
        experiment (str): identifier for variant experiment (maf, mip, etc.)
    """
    source_id = source or os.path.basename(vcf_path)

    # parse some meta data
    parser = vcf_parser.VCFParser(infile=vcf_path, split_variants=True)

    # build samples and add to session
    samples = [{'sample': Sample(sample_id=individual, experiment=experiment,
                                 source=source_id),
                'inputs': []}
               for individual in parser.individuals]

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

        variant_inputs = (format_genotype(variant_row) for variant_row
                          in relevant_rows)

        for positions in variant_inputs:
            for index, position in enumerate(positions):
                samples[index]['inputs'].append(position)

    for entity in samples:
        sample = entity['sample']
        genotypes = [Genotype(sample=sample, **genotype)
                     for genotype in entity['inputs']]

        sample_exists = store.sample(sample.sample_id, experiment, check=True)
        if sample_exists:
            logger.warn("sample already added: %s", sample.sample_id)
            if force:
                logger.info('removing existing sample')
                store.remove(sample.sample_id, experiment)

        if (not sample_exists) or force:
            try:
                store.add(sample, *genotypes)
                # commit the genotypes
                store.save()
                logger.info("added sample: %s", sample.sample_id)
                yield sample
            except IntegrityError as exception:
                store.session.rollback()
                logger.error('unknown exception, multiple alleles?')
                raise exception


def format_genotype(variant_row):
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

    for genotype_str in genotypes:
        # convert to base in genotype call
        genotype_parts = genotype_str.split(':')
        genotype = genotype_parts[0].split('/')
        allele_1 = gt_mapper[genotype[0]]
        allele_2 = gt_mapper[genotype[1]]

        variant_dict = {'rsnumber': rsnumber, 'allele_1': allele_1,
                        'allele_2': allele_2}
        yield variant_dict
