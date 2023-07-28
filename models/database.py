# -*- coding: utf-8 -*-
from typing import *

import sqlalchemy.orm

import config

_engine: Optional[sqlalchemy.Engine] = None


class OrmBase(sqlalchemy.orm.DeclarativeBase):
    pass


def init(_debug):
    cfg = config.get_config()
    global _engine
    # engine = sqlalchemy.create_engine(cfg.database_url, echo=debug)
    _engine = sqlalchemy.create_engine(cfg.database_url)

    OrmBase.metadata.create_all(_engine)


def get_session() -> sqlalchemy.orm.Session:
    return sqlalchemy.orm.Session(_engine)
