# -*- coding: utf-8 -*-
from typing import Optional
from datetime import datetime

from pip_services4_data.data import IStringIdentifiable


class UserPasswordInfoV1(IStringIdentifiable):
    def __init__(
        self,
        id: Optional[str] = None,
        change_time: Optional[datetime] = None,
        locked: bool = False,
        lock_time: Optional[datetime] = None
    ):
        self.id: Optional[str] = id
        self.change_time: Optional[datetime] = change_time
        self.locked: bool = locked
        self.lock_time: Optional[datetime] = lock_time
        

    def to_dict(self):
        return {
            "id": self.id,
            "change_time": self.change_time.isoformat() if self.change_time else None,
            "locked": self.locked,
            "lock_time": self.lock_time.isoformat() if self.lock_time else None
        }