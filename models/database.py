# -*- coding: utf-8 -*-
from typing import Optional
import sqlalchemy
import sqlalchemy.orm
import os
import config
import logging

# 定义全局的数据库引擎对象
_engine: Optional[sqlalchemy.Engine] = None

# 定义基础模型类
class OrmBase(sqlalchemy.orm.DeclarativeBase):
    pass


def init():
    """
    初始化数据库连接，支持从环境变量或配置文件中加载数据库连接 URL。
    """
    # 优先从环境变量获取数据库 URL
    database_url = os.getenv('DATABASE_URL', None)

    if not database_url:
        # 从配置文件获取数据库 URL
        cfg = config.get_config()
        database_url = cfg.database_url

    if not database_url:
        raise ValueError("数据库未配置。请通过环境变量 DATABASE_URL 或配置文件提供数据库连接 URL。")

    # 处理 PostgreSQL 数据库 URL，支持 postgres:// 和 postgresql://
    if database_url.startswith("postgres://") or database_url.startswith("postgresql://"):
    print("使用 PostgreSQL 数据库")
    # 替换为 psycopg3 的驱动 URL
    database_url = database_url.replace("postgres://", "postgresql+psycopg://").replace(
        "postgresql://", "postgresql+psycopg://"
    )
    logging.info("使用 PostgreSQL 数据库")
    elif database_url.startswith("sqlite"):
        logging.info("使用 SQLite 数据库")
    else:
        raise ValueError(f"不支持的数据库 URL: {database_url}")

    global _engine
    # 创建数据库引擎
    _engine = sqlalchemy.create_engine(
        database_url,
        pool_size=5,        # 连接池中保持的连接数
        max_overflow=5,     # 临时的额外连接数
        pool_timeout=3,     # 连接超时时间
        pool_recycle=3600,  # 回收超过 1 小时的连接
    )

    # 创建数据库表
    OrmBase.metadata.create_all(_engine)
    logging.info("数据库初始化完成")


def get_session() -> sqlalchemy.orm.Session:
    """
    获取数据库会话，用于执行数据库操作。
    """
    if _engine is None:
        raise ValueError("数据库引擎未初始化，请先调用 init() 方法。")
    return sqlalchemy.orm.Session(_engine)
