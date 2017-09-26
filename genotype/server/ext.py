# -*- coding: utf-8 -*-
from flask_alchy import Alchy

from genotype.store.models import Model, User
from .admin import UserManagement

db = Alchy(Model=Model)
user = UserManagement(db, User)
