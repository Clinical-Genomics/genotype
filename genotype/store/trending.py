"""Functions to create trending specific data."""
import logging
from genotype.store.models import Analysis, Genotype, Sample

LOG = logging.getLogger(__name__)


def build_snp_dict(analysis_id : str)-> dict:
    """Building a dict of snps for a specific analysis."""

    snp_dict = {}   

    genotypes = Genotype.query.filter(Genotype.analysis_id == analysis_id).all()
    if not genotypes:
        LOG.warning('Did not find Genotype data for analysis_id %s', (analysis_id))
    for genotype in genotypes:
        snp_dict[genotype.rsnumber] = [genotype.allele_1, genotype.allele_2]

    return snp_dict


def compare(analysis_1 : dict, analysis_2 : dict)-> dict:
    """Compare inernal and external snps"""

    compare_dict = {}

    for snp in set(list(analysis_1.keys()) + list(analysis_2.keys())):
        if analysis_1.get(snp) == analysis_2.get(snp):
            compare_dict[snp] = True
        else:
            compare_dict[snp] = False

    return compare_dict


def prepare_trending(sample_id : str = None, sample : Sample = None)-> dict:
    """Build genotype document"""

    if sample_id:
        sample = Sample.query.get(sample_id)

    if not sample:
        return {}

    analyses = Analysis.query.filter(Analysis.sample_id == sample.id).all()
    genotype_doc = {
                '_id': sample.id,
                'status': sample.status,
                'sample_created_in_genotype_db': sample.created_at.isoformat(),
                'sex': sample.sex}

    snps = {}
    for analysis in analyses:
        if analysis.plate_id:
            genotype_doc['plate'] = analysis.plate_id
        snps[analysis.type] = build_snp_dict(analysis.id)
        if snps.get('sequence') and snps.get('genotype'):
            snps['comp'] = compare(snps['sequence'], snps['genotype'])

    genotype_doc['snps'] = snps

    return genotype_doc
