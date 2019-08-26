from genotype.store.models import Analysis, Genotype, Sample



def build_snp_dict(analysis_id):
    """Building a dict of snps for a specific analysis."""

    snp_dict = {}
    genotypes = Genotype.query.filter(Genotype.analysis_id == analysis_id).all()
    for genotype in genotypes:
        snp_dict[genotype.rsnumber] = [genotype.allele_1, genotype.allele_2]

    return snp_dict


def compare(analysis_1, analysis_2):
    """Compare inernal and external snps"""

    compare_dict = {}

    for snp in set(list(analysis_1.keys()) + list(analysis_2.keys())):
        if analysis_1.get(snp) == analysis_2.get(snp):
            compare_dict[snp] = True
        else:
            compare_dict[snp] = False

    return compare_dict


def prepare_trending(sample_id):
    """Build genotype document for the genotype collection in the trending database"""

    sample = Sample.query.filter(Sample.id == sample_id).first()
    analyses = Analysis.query.filter(Analysis.sample_id == sample_id).all()

    if not sample:
        return {}

    genotype_doc = {
                '_id' : sample.id,
                'status' : sample.status,
                'sample_created_in_genotype_db' : sample.created_at,
                'sex' : sample.sex}

    snps = {}
    for analysis in analyses:
        if analysis.plate_id:
            genotype_doc['plate']= analysis.plate_id
        snps[analysis.type] = build_snp_dict(analysis.id)
        if snps.get('sequence') and snps.get('genotype'):
            snps['comp'] = compare(snps['sequence'], snps['genotype'])

    genotype_doc['snps'] = snps

    return genotype_doc
