# -*- coding: utf-8 -*-
import os
from collections import namedtuple

from cyvcf2 import VCF

from genotype.compat import itervalues
from genotype.store.models import Analysis, Genotype

Result = namedtuple('Result', ['sample', 'genotypes'])
RawGenotype = namedtuple('RawGenotype', ['sample', 'allele_1', 'allele_2'])


def load_vcf(vcf_file, snps):
    """Load genotypes from a BCF/VCF.gz file.

    Args:
        vcf_file (path): path to to BCF/VCF.gz file (indexed)
        snps (List[SNP]): list of SNPs to consider

    Returns:
        List[Analysis]: list of Analysis records
    """
    vcf = VCF(vcf_file)
    # generate Analysis records for each included sample
    source = os.path.abspath(vcf_file)
    analyses = {sample_id: Analysis(type='sequence', source=source,
                                    sample_id=sample_id)
                for sample_id in vcf.samples}
    for snp in snps:
        variant = fetch_snp(vcf, snp)
        if variant is None:
            # assume REF/REF
            for analysis in itervalues(analyses):
                genotype = Genotype(rsnumber=snp.id, allele_1=snp.ref,
                                    allele_2=snp.ref)
                analysis.genotypes.append(genotype)
        else:
            raw_genotypes = variant_genotypes(vcf.samples, variant)
            for raw_gt in raw_genotypes:
                genotype = Genotype(rsnumber=snp.id, allele_1=raw_gt.allele_1,
                                    allele_2=raw_gt.allele_2)
                analysis = analyses[raw_gt.sample]
                analysis.genotypes.append(genotype)
    return itervalues(analyses)


def variant_genotypes(sample_ids, variant):
    """Build Genotype objects from a BCF variant."""
    for sample_id, bases in zip(sample_ids, variant.gt_bases):
        allele_1, allele_2 = bases.split('/')
        yield RawGenotype(sample_id, allele_1, allele_2)


def fetch_snp(vcf, snp):
    """Fetch an SNP from the BCF file by position."""
    pos_str = "{chrom}:{pos}-{pos}".format(chrom=snp.chrom, pos=snp.pos)
    variants = list(vcf(pos_str))
    if len(variants) == 1:
        # everything OK
        variant = variants[0]
        return variant
    elif len(variants) == 0:
        return None
    else:  # pragma: no cover
        # weird SNP position lookup, not even possible; right?
        raise ValueError('multiple variants found for SNP')
