# -*- coding: utf-8 -*-
from typing import *
import sqlalchemy.orm
import sqlalchemy
import os
import config

_engine: Optional[sqlalchemy.Engine] = None

class OrmBase(sqlalchemy.orm.DeclarativeBase):
    pass

def init():
    # 优先从环境变量获取 database_url
    database_url = os.getenv('DATABASE_URL', None)

    if not database_url:
        # 如果环境变量中没有，则使用 config 文件中的数据库 URL
        cfg = config.get_config()
        database_url = cfg.get('database_url')

    if not database_url:
        raise ValueError("数据库未配置-->No database URL provided. Please set it either in the environment or config.")

    global _engine

    # 判断数据库类型
    if database_url.startswith("sqlite"):
        # 使用 SQLite
        _engine = sqlalchemy.create_engine(
            database_url,
            pool_size=5,  # 保持的连接数
            max_overflow=5,  # 临时的额外连接数
            pool_timeout=3,  # 连接数达到最大时获取新连接的超时时间
            pool_recycle=60 * 60,  # 回收超过1小时的连接
        )
    elif database_url.startswith("postgresql"):
        # 使用 PostgreSQL
        _engine = sqlalchemy.create_engine(
            database_url,
            pool_size=5,  # 保持的连接数
            max_overflow=5,  # 临时的额外连接数
            pool_timeout=3,  # 连接数达到最大时获取新连接的超时时间
            pool_recycle=60 * 60,  # 回收超过1小时的连接
        )
    else:
        raise ValueError(f"Unsupported database URL scheme: {database_url}")

    OrmBase.metadata.create_all(_engine)

def get_session() -> sqlalchemy.orm.Session:
    return sqlalchemy.orm.Session(_engine)
