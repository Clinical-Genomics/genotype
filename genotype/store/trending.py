"""Functions to create trending specific data."""
import logging
from genotype.store.models import Analysis, Genotype, Sample

LOG = logging.getLogger(__name__)


def get_status_over_time(sample_id: str = None, sample: Sample = None) -> dict:
    """Get sample status and sample cration date."""

    if sample_id:
        sample = Sample.query.get(sample_id)

    if not sample:
        return {}

    genotype_dict = {
                '_id': sample.id,
                'status': sample.status,
                'sample_created_in_genotype_db': sample.created_at.date().isoformat(),
                'sex': sample.sex}

    return genotype_dict


def get_snp_dict(analysis_id: str) -> dict:
    """Building a dict of snps for a specific analysis."""

    snp_dict = {}
    genotypes = Genotype.query.filter(Genotype.analysis_id == analysis_id).all()
    if not genotypes:
        LOG.warning('Did not find Genotype data for analysis_id %s', (analysis_id))
    for genotype in genotypes:
        snp_dict[genotype.rsnumber] = [genotype.allele_1, genotype.allele_2]

    return snp_dict


def get_equality(analysis_1: dict, analysis_2: dict) -> dict:
    """Compares the two dictionaries and generates a new dictionary, 
    representing the equality between them.
    
    Args:
        analysis_1(dict):
        analysis_2(dict):
    Returns:
        compare_dict(dict):
        """

    compare_dict = {}

    for snp in set(list(analysis_1.keys()) + list(analysis_2.keys())):
        if analysis_1.get(snp) == analysis_2.get(snp):
            compare_dict[snp] = True
        else:
            compare_dict[snp] = False

    return compare_dict


def get_analysis_equalities(sample_id: str = None, sample: Sample = None) -> dict:
    """Get a dict with genotype analysis.
    
    Args:
        sample(Sample) or sample_id(str)
    Returns:
        analysis_comparison(dict): {}
    """

    if sample_id:
        sample = Sample.query.get(sample_id)

    if not sample:
        return {}

    analyses = Analysis.query.filter(Analysis.sample_id == sample.id).all()
    analysis_comparison = {
                '_id': sample.id,

    snps = {}
    for analysis in analyses:
        if analysis.plate_id:
            analysis_comparison['plate'] = analysis.plate.plate_id
        snps[analysis.type] = get_snp_dict(analysis.id)
        if snps.get('sequence') and snps.get('genotype'):
            snps['comp'] = get_equality(snps['sequence'], snps['genotype'])

    analysis_comparison['snps'] = snps

    return analysis_comparison
