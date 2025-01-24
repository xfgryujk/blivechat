# -*- coding: utf-8 -*-
from typing import *

import sqlalchemy.orm

import config

_engine: Optional[sqlalchemy.Engine] = None


class OrmBase(sqlalchemy.orm.DeclarativeBase):
    pass


def init():
    database_url = os.getenv('DATABASE_URL', None)

    if not database_url:
        cfg = config.get_config()
        database_url = cfg.database_url

    if not database_url:
        raise ValueError("数据库未配置-->No database URL provided. Please set it either in the environment or config.")

    if not (database_url.startswith("sqlite") or database_url.startswith("postgresql")):
        raise ValueError(f"不支持的数据库url-->Unsupported database URL scheme: {database_url}")

    global _engine
    _engine = sqlalchemy.create_engine(
        database_url,
        pool_size=5,
        max_overflow=5,
        pool_timeout=3,
        pool_recycle=60 * 60,
    )

    OrmBase.metadata.create_all(_engine)
