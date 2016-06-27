# -*- coding: utf-8 -*-
from flask.ext.alchy import Alchy

from taboo.store.api import TabooDB
from taboo.store.models import Model


class FlaskTaboo(Alchy, TabooDB):
    pass

api = FlaskTaboo(Model=Model)
