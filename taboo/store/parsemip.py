# -*- coding: utf-8 -*-


def parse_mipsex(qcm_data):
    """Parse out sample sex from qc metrics data."""
    samples_sex = parse_samples(qcm_data)
    sexes = {sample_id: sex for sample_id, sex in samples_sex}
    return sexes


def parse_samples(qcm_data):
    """Parse out the relevant sample information."""
    fam_key = qcm_data.keys()[0]
    for segment_id, values in qcm_data[fam_key].items():
        if segment_id != fam_key:
            # sample data entry, find main section
            for sebsection_id, data in values.items():
                if '_lanes_' in sebsection_id:
                    yield segment_id, data['ChanjoSexCheck']['gender']
