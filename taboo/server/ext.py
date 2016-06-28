# -*- coding: utf-8 -*-
from flask.ext.alchy import Alchy

from taboo.store.models import Model

db = Alchy(Model=Model)
