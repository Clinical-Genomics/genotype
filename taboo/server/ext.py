# -*- coding: utf-8 -*-
from flask_alchy import Alchy

from taboo.store.models import Model

db = Alchy(Model=Model)
