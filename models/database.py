# -*- coding: utf-8 -*-

import contextlib
from typing import *

import sqlalchemy.ext.declarative
import sqlalchemy.orm

import config

OrmBase = sqlalchemy.ext.declarative.declarative_base()
engine = None
DbSession: Optional[Type[sqlalchemy.orm.Session]] = None


def init(debug):
    cfg = config.get_config()
    global engine, DbSession
    # engine = sqlalchemy.create_engine(cfg.database_url, echo=debug)
    engine = sqlalchemy.create_engine(cfg.database_url)
    DbSession = sqlalchemy.orm.sessionmaker(bind=engine)

    OrmBase.metadata.create_all(engine)


@contextlib.contextmanager
def get_session():
    session = DbSession()
    try:
        yield session
    except:
        session.rollback()
        raise
    finally:
        session.close()
