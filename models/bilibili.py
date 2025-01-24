# -*- coding: utf-8 -*-
import datetime
import sqlalchemy
from sqlalchemy.orm import Mapped, mapped_column
import models.database


class BilibiliUser(models.database.OrmBase):
    """
    Bilibili 用户模型，用于存储用户信息。
    """
    __tablename__ = 'bilibili_users'

    # 用户 ID，主键
    uid: Mapped[int] = mapped_column(
        sqlalchemy.BigInteger, 
        primary_key=True, 
        comment="用户唯一标识符 (UID)"
    )

    # 用户头像 URL
    avatar_url: Mapped[str] = mapped_column(
        sqlalchemy.String(255),  # 将最大长度改为 255，兼容性更强
        nullable=False,          # 确保头像链接不能为空
        comment="用户头像 URL"
    )

    # 数据更新时间
    update_time: Mapped[datetime.datetime] = mapped_column(
        sqlalchemy.DateTime, 
        default=datetime.datetime.utcnow,  # 默认使用 UTC 时间
        onupdate=datetime.datetime.utcnow, # 自动更新时间戳
        nullable=False, 
        comment="记录的最后更新时间"
    )
