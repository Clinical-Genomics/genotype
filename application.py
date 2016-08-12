# -*- coding: utf-8 -*-
import os

from taboo.server import create_app

config = {
    'TABOO_INCLUDE_KEY': '-CG-',
    'TABOO_GENOTYPE_DIR': os.environ.get('TABOO_GENOTYPE_DIR'),
    'TABOO_MAX_NOCALLS': 15,
    'TABOO_MAX_MISMATCH': 3,
    'TABOO_MIN_MATCHES': 35,
    'SQLALCHEMY_DATABASE_URI': os.environ['SQLALCHEMY_DATABASE_URI'],
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'TABOO_NO_SAVE': os.environ.get('TABOO_NO_SAVE'),
}

application = create_app('taboo', config_obj=config)
