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

    def _convert_to_public(self, value: any) -> any:
        if value is None:
            return None
        
        user_password = UserPasswordV1(
            id=value.get('_id'),
            password=value.get('password')
        )
        user_password.change_time = value.get('change_time')
        user_password.locked = value.get('locked', False)
        user_password.lock_time = value.get('lock_time')
        user_password.fail_count = value.get('fail_count', 0)
        user_password.fail_time = value.get('fail_time')
        user_password.rec_code = value.get('rec_code')
        user_password.rec_expire_time = value.get('rec_expire_time')
        user_password.custom_hdr = value.get('custom_hdr')
        user_password.custom_dat = value.get('custom_dat')
        return user_password