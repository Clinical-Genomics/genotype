# -*- coding: utf-8 -*-
import codecs
import logging
import os

import vcf_parser
from sqlalchemy.exc import IntegrityError
import pysam

import taboo.store
from taboo.store.models import Genotype
import taboo.rsnumbers

logger = logging.getLogger(__name__)


def load_vcf(store, vcf_path, rsnumber_stream, experiment='sequencing',
             source=None, force=False):
    """Load samples with genotypes from a VCF file.

    Args:
        experiment (str): identifier for variant experiment (maf, mip, etc.)
    """
    source_id = source or os.path.abspath(vcf_path)

    # parse some meta data
    parser = vcf_parser.VCFParser(infile=vcf_path, split_variants=True)
    samples = {sample_id: store.get_or_create('sample', sample_id=sample_id)
               for sample_id in parser.individuals}

    # read in rsnumbers
    rsnumber_matcher = taboo.rsnumbers.parse(rsnumber_stream)

    # start processing variants
    # skip header lines
    analyses = [{'sample_id': sample_id, 'genotypes': []}
                for sample_id in samples.keys()]
    with codecs.open(vcf_path, 'r') as handle:
        content_lines = (line for line in handle if not line.startswith('#'))

        # split columns
        content_rows = [line.split('\t') for line in content_lines]

        # extract rsnumbers
        relevant_rows = [row for row in content_rows if row[2] in
                         rsnumber_matcher]

        variant_inputs = [format_genotype(variant_row) for variant_row
                          in relevant_rows]

        for positions in variant_inputs:
            for index, position in enumerate(positions):
                analyses[index]['genotypes'].append(position)

    for analysis in analyses:
        sample_obj = samples[analysis['sample_id']]
        sample_id = sample_obj.sample_id
        analysis_exists = store.analysis(sample_id, experiment, check=True)

        if analysis_exists:
            logger.warn("analysis already added: %s", sample_id)
            if force:
                logger.info('removing existing analysis')
                store.remove(sample_id, experiment)

        if (not analysis_exists) or force:
            analysis_obj = store.add_analysis(sample_obj, experiment, source_id)
            new_genotypes = [Genotype(**gt) for gt in analysis['genotypes']]
            if len(new_genotypes) == 0:
                logger.warn("no genotypes found, skipping: %s", sample_id)
                continue
            analysis_obj.genotypes = new_genotypes

            store.add(analysis_obj)
            try:
                store.save()
            except IntegrityError as exception:
                store.session.rollback()
                logger.error('unknown exception, multiple alleles?')
                raise exception
            yield analysis_obj


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


def load_bcf(store, bcf_file, rs_stream, experiment='sequencing', force=False):
    """Parse variants from an indexed BCF file."""
    rsnumbers = taboo.rsnumbers.parse(rs_stream)
    bcf = pysam.VariantFile(bcf_file, 'rb')

    source_id = os.path.abspath(bcf_file)

    # parse some meta data
    samples = {sample_id: store.get_or_create('sample', sample_id=sample_id)
               for sample_id in bcf.next().samples.keys()}

    analyses = [{'sample_id': sample_id, 'genotypes': []}
                for sample_id in samples.keys()]

    for rsnumber in rsnumbers.values():
        variants = bcf.fetch(rsnumber.chrom, rsnumber.pos - 1, rsnumber.pos)
        if len(variants) == 1:
            variant = variants[0]
            variant_inputs = [{'rsnumber': rsnumber.id,
                               'allele_1': sample.alleles[0],
                               'allele_2': sample.alleles[1]}
                              for sample in variant.samples]
        elif len(variants) == 0:
            # ref/ref
            variant_inputs = [{'rsnumber': rsnumber.id,
                               'allele_1': rsnumber.ref,
                               'allele_1': rsnumber.ref}
                              for sample_id in samples.keys()]
        else:
            # error
            raise ValueError('wierd rsnumber position lookup')

        for positions in variant_inputs:
            for index, position in enumerate(positions):
                analyses[index]['genotypes'].append(position)

    for analysis in analyses:
        sample_obj = samples[analysis['sample_id']]
        sample_id = sample_obj.sample_id
        analysis_exists = store.analysis(sample_id, experiment, check=True)

        if analysis_exists:
            logger.warn("analysis already added: %s", sample_id)
            if force:
                logger.info('removing existing analysis')
                store.remove(sample_id, experiment)

        if (not analysis_exists) or force:
            analysis_obj = store.add_analysis(sample_obj, experiment, source_id)
            new_genotypes = [Genotype(**gt) for gt in analysis['genotypes']]
            if len(new_genotypes) == 0:
                logger.warn("no genotypes found, skipping: %s", sample_id)
                continue
            analysis_obj.genotypes = new_genotypes

            store.add(analysis_obj)
            try:
                store.save()
            except IntegrityError as exception:
                store.session.rollback()
                logger.error('unknown exception, multiple alleles?')
                raise exception
            yield analysis_obj
