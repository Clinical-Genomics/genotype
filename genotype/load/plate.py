# -*- coding: utf-8 -*-
from path import Path

from genotype.store.models import Plate


def extract_plateid(excel_path):
    """Extract ID from Excel book path."""
    name = Path(excel_path).basename()
    plate_id = name.split('_', 1)[0]
    return plate_id


def link_plate(analysis_obj):
    """Link plate to an analysis."""
    plate_id = extract_plateid(analysis_obj.source)
    plate_obj = Plate.query.filter_by(plate_id=plate_id).first()
    analysis_obj.plate = plate_obj
