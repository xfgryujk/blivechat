# -*- coding: utf-8 -*-
import sqlalchemy

import models.database


class BilibiliUser(models.database.OrmBase):
    __tablename__ = 'bilibili_users'
    uid = sqlalchemy.Column(sqlalchemy.BigInteger, primary_key=True)  # 创建表后最好手动改成unsigned
    avatar_url = sqlalchemy.Column(sqlalchemy.String(100))
    update_time = sqlalchemy.Column(sqlalchemy.DateTime)
