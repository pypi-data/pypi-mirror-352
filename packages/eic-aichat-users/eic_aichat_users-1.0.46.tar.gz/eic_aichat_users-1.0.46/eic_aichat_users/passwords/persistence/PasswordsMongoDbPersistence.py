# -*- coding: utf-8 -*-
from typing import Optional
from pip_services4_components.context import IContext
from pip_services4_mongodb.persistence import IdentifiableMongoDbPersistence

from .IPasswordsPersistence import IPasswordsPersistence
from ..data.version1.UserPasswordV1 import UserPasswordV1


class PasswordsMongoDbPersistence(IdentifiableMongoDbPersistence, IPasswordsPersistence):
    
    def __init__(self):
        super().__init__('passwords')
        self._max_page_size = 1000
