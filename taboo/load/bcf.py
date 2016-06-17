# -*- coding: utf-8 -*-
import os
from collections import namedtuple

import pysam

from taboo.compat import iteritems, itervalues
from taboo.store.models import Analysis, Genotype

Result = namedtuple('Result', ['sample', 'genotypes'])
RawGenotype = namedtuple('RawGenotype', ['sample', 'allele_1', 'allele_2'])


def load_bcf(bcf_file, snps):
    """Load genotypes from a BCF file.

    Args:
        bcf_file (path): path to to BCF file (indexed)
        snps (List[SNP]): list of SNPs to consider

    Returns:
        List[Analysis]: list of Analysis records
    """
    bcf = pysam.VariantFile(bcf_file, 'rb')
    sample_ids = parse_sampleids(bcf)
    # generate Analysis records for each included sample
    source = os.path.abspath(bcf_file)
    analyses = {sample_id: Analysis(type='sequence', source=source,
                                    sample_id=sample_id)
                for sample_id in sample_ids}
    for snp in snps:
        variant = fetch_snp(bcf, snp)
        if variant is None:
            # assume REF/REF
            for analysis in itervalues(analyses):
                genotype = Genotype(rsnumber=snp.id, allele_1=snp.ref,
                                    allele_2=snp.ref)
                analysis.genotypes.append(genotype)
        else:
            raw_genotypes = variant_genotypes(variant)
            for raw_gt in raw_genotypes:
                genotype = Genotype(rsnumber=snp.id, allele_1=raw_gt.allele_1,
                                    allele_2=raw_gt.allele_2)
                analysis = analyses[raw_gt.sample]
                analysis.genotypes.append(genotype)
    return itervalues(analyses)


def variant_genotypes(variant):
    """Build Genotype objects from a BCF variant."""
    for sample_id, sample in iteritems(variant.samples):
        allele_1 = ('0' if sample.allele_indices[0] is None else
                    variant.alleles[sample.allele_indices[0]])
        allele_2 = ('0' if sample.allele_indices[1] is None else
                    variant.alleles[sample.allele_indices[1]])
        yield RawGenotype(sample_id, allele_1, allele_2)


def fetch_snp(bcf, snp):
    """Fetch an SNP from the BCF file by position."""
    variants = list(bcf.fetch(snp.chrom, snp.pos - 1, snp.pos))
    if len(variants) == 1:
        # everything OK
        variant = variants[0]
        return variant
    elif len(variants) == 0:
        return None
    else:  # pragma: no cover
        # weird SNP position lookup, not even possible; right?
        raise ValueError('multiple variants found for SNP')


def parse_sampleids(bcf):
    """Build new Sample models from BCF file."""
    sample_ids = bcf.next().samples.keys()
    return sample_ids
