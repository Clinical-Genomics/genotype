"""Export functions."""
import logging
from genotype.store.models import Analysis, Genotype, Sample

LOG = logging.getLogger(__name__)


def get_sample(sample: Sample = None) -> dict:
    """Get data from sample table in dict format.
    
    Args:
        sample(Sample)
    Returns:
        sample_dict(dict):  Eg: {"status": null, 
                                "sample_created_in_genotype_db": "2019-09-02", 
                                "sex": "female", 
                                "comment": "Lorem ipsum"}"""

    sample_dict = {
                'status': sample.status,
                'sample_created_in_genotype_db': sample.created_at.date().isoformat(),
                'sex': sample.sex,
                'comment': sample.comment}

    return sample_dict


def _get_snp_dict(analysis_id: str) -> dict:
    """Builds a dict of snps for a specific analysis.

    Returns:
        snp_dict(dict): Eg: {'rs10144418': ['T', 'C'], 'rs1037256': ['G', 'A'],...
    """

    snp_dict = {}
    genotypes = Genotype.query.filter(Genotype.analysis_id == analysis_id).all()
    if not genotypes:
        LOG.warning('Did not find Genotype data for analysis_id %s', (analysis_id))
    for genotype in genotypes:
        snp_dict[genotype.rsnumber] = [genotype.allele_1, genotype.allele_2]
    return snp_dict


def _get_equality(analysis_1: dict, analysis_2: dict) -> dict:
    """Compares the two input dictionaries and generates a new dictionary, 
    representing the equality between the two.
    
    Args:
        analysis_1(dict): Eg: {'rs10144418': ['T', 'C'], 'rs1037256': ['G', 'A'],... }
        analysis_2(dict): Eg: {'rs10144418': ['A', 'C'], 'rs1037256': ['G', 'A'],... }
    Returns:
        compare_dict(dict): Eg: {'rs10144418': False, 'rs1037256': True,... }
        """

    compare_dict = {}

    for snp in set(list(analysis_1.keys()) + list(analysis_2.keys())):
        if analysis_1.get(snp) == analysis_2.get(snp):
            compare_dict[snp] = True
        else:
            compare_dict[snp] = False

    return compare_dict


def get_analysis_equalities(sample: Sample = None) -> dict:
    """Get a dict with the genotype analysises and the comparison dict for a sample
    
    Args:
        sample(Sample)
    Returns:
        analysis_equalities(dict): Eg:
                                    {'plate': 'ID43', 
                                    'snps': {'genotype': {'rs10144418': ['C', 'C'],...},
                                            'sequence': {'rs10144418': ['T', 'C'], ...},
                                            'comp': {'rs10144418': True, ...}
                                            }
                                    }
    """

    analyses = Analysis.query.filter(Analysis.sample_id == sample.id).all()
    analysis_equalities = {}

    snps = {}
    for analysis in analyses:
        if analysis.plate_id:
            analysis_equalities['plate'] = analysis.plate.plate_id
        snps[analysis.type] = _get_snp_dict(analysis.id)
        if snps.get('sequence') and snps.get('genotype'):
            snps['comp'] = _get_equality(snps['sequence'], snps['genotype'])

    analysis_equalities['snps'] = snps
    return analysis_equalities
