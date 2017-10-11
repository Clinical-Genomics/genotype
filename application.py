# -*- coding: utf-8 -*-
import os

from genotype.server.app import create_app

config = {
    'GENOTYPE_INCLUDE_KEY': '-CG-',
    'GENOTYPE_GENOTYPE_DIR': os.environ.get('GENOTYPE_GENOTYPE_DIR'),
    'GENOTYPE_MAX_NOCALLS': 15,
    'GENOTYPE_MAX_MISMATCH': 3,
    'GENOTYPE_MIN_MATCHES': 35,
    'SQLALCHEMY_DATABASE_URI': os.environ['SQLALCHEMY_DATABASE_URI'],
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,

    # user management
    'GOOGLE_OAUTH_CLIENT_ID': os.environ['GOOGLE_OAUTH_CLIENT_ID'],
    'GOOGLE_OAUTH_CLIENT_SECRET': os.environ['GOOGLE_OAUTH_CLIENT_SECRET'],
}

application = create_app(config_obj=config)
