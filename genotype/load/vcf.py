"""Functions for loading VCF information"""

import logging
import os
from collections import namedtuple
from typing import Iterable, List

from cyvcf2 import VCF, Variant

from genotype.compat import itervalues
from genotype.store.models import SNP, Analysis, Genotype

Result = namedtuple("Result", ["sample", "genotypes"])
RawGenotype = namedtuple("RawGenotype", ["sample", "allele_1", "allele_2"])

LOG = logging.getLogger(__name__)


def load_vcf(vcf_file: str, snps: List[SNP]) -> List[Analysis]:
    """Load genotypes from a BCF/VCF.gz file."""
    vcf = VCF(vcf_file)
    # generate Analysis records for each included sample
    source = os.path.abspath(vcf_file)
    analyses = {
        sample_id: Analysis(type="sequence", source=source, sample_id=sample_id)
        for sample_id in vcf.samples
    }
    for snp in snps:
        variant = fetch_snp(vcf, snp)
        if variant is None:
            # assume REF/REF
            for analysis in itervalues(analyses):
                genotype = Genotype(rsnumber=snp.id, allele_1=snp.ref, allele_2=snp.ref)
                analysis.genotypes.append(genotype)
        else:
            raw_genotypes = variant_genotypes(vcf.samples, variant)
            for raw_gt in raw_genotypes:
                genotype = Genotype(
                    rsnumber=snp.id, allele_1=raw_gt.allele_1, allele_2=raw_gt.allele_2
                )
                analysis = analyses[raw_gt.sample]
                analysis.genotypes.append(genotype)
    return itervalues(analyses)


def variant_genotypes(sample_ids: List[str], variant: Variant) -> Iterable[RawGenotype]:
    """Build Genotype objects from a BCF variant."""
    for sample_id, bases in zip(sample_ids, variant.gt_bases):
        bases = bases.replace("|", "/")
        allele_1, allele_2 = bases.split("/")
        yield RawGenotype(sample_id, allele_1, allele_2)


def fetch_snp(vcf: VCF, snp: SNP) -> Variant:
    """Fetch an SNP from the BCF file by position."""
    pos_str = "{chrom}:{pos}-{pos}".format(chrom=snp.chrom, pos=snp.pos)
    variants = list(vcf(pos_str))
    if len(variants) == 0:
        LOG.debug(f"No variant found for {pos_str}")
        return None

    elif len(variants) == 1:
        # everything OK
        variant = variants[0]
        return variant
    # weird SNP position lookup, not even possible; right?
    raise ValueError(
        f"Multiple variants ({len(variants)}) found for SNP at position {pos_str}: {return_multiple_variant_alleles(variants=variants)}."
    )


def return_multiple_variant_alleles(variants: List[Variant]) -> str:
    """Takes in a list of Variant, returns all allele variants as str"""
    multiple_variant_alleles: List = []
    for variant in variants:
        multiple_variant_alleles.append(f"{variant.REF}/{','.join(variant.ALT)}")
    return ", ".join(multiple_variant_alleles)
