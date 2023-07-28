# -*- coding: utf-8 -*-
import datetime

import sqlalchemy
from sqlalchemy.orm import Mapped, mapped_column

import models.database


class BilibiliUser(models.database.OrmBase):
    __tablename__ = 'bilibili_users'
    uid: Mapped[int] = mapped_column(sqlalchemy.BigInteger, primary_key=True)  # 创建表后最好手动改成unsigned
    avatar_url: Mapped[str] = mapped_column(sqlalchemy.String(100))
    update_time: Mapped[datetime.datetime]
