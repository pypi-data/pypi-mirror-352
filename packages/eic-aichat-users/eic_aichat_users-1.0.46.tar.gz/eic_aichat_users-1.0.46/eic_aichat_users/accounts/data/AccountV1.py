# -*- coding: utf-8 -*-
from typing import Any, Optional
from datetime import datetime

from pip_services4_data.data import IStringIdentifiable
from pip_services4_data.keys import IdGenerator


class AccountV1(IStringIdentifiable):
    def __init__(
        self,
        id: Optional[str] = None,
        login: Optional[str] = None,
        name: Optional[str] = None,
        language: Optional[str] = None,
        theme: Optional[str] = None,
        time_zone: Optional[str] = None,
        create_time: Optional[datetime] = None,
        deleted: Optional[bool] = False,
        active: Optional[bool] = True,
        about: Optional[str] = None,
        custom_hdr: Optional[Any] = None,
        custom_dat: Optional[Any] = None
    ):
        self.id: str = id or IdGenerator.next_long()
        self.login = login
        self.name = name
        self.create_time = create_time or datetime.now()
        self.deleted = deleted
        self.active = active
        self.about = about
        self.time_zone = time_zone
        self.language = language
        self.theme = theme
        self.custom_hdr = custom_hdr
        self.custom_dat = custom_dat

    def to_dict(self):
        return {
            "id": self.id,
            "login": self.login,
            "name": self.name,
            "language": self.language,
            "theme": self.theme,
            "time_zone": self.time_zone,
            "create_time": self.create_time.isoformat() if isinstance(self.create_time, datetime) else self.create_time,
            "deleted": self.deleted,
            "active": self.active,
            "about": self.about,
            "custom_hdr": self.custom_hdr,
            "custom_dat": self.custom_dat
        }
