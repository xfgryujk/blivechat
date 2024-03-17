# -*- coding: utf-8 -*-
import dataclasses
import enum
from typing import *

__all__ = (
    'RoomKeyType',
    'RoomKey',
    'Command',
    'ExtraData',
    'AddRoomMsg',
    'RoomInitMsg',
    'DelRoomMsg',
    'OpenPluginAdminUiMsg',
    'AuthorType',
    'GuardLevel',
    'ContentType',
    'AddTextMsg',
    'AddGiftMsg',
    'AddMemberMsg',
    'AddSuperChatMsg',
    'DelSuperChatMsg',
    'UpdateTranslationMsg',
)


class RoomKeyType(enum.IntEnum):
    ROOM_ID = 1
    AUTH_CODE = 2


class RoomKey(NamedTuple):
    """用来标识一个房间"""
    type: RoomKeyType
    value: Union[int, str]

    def __str__(self):
        res = str(self.value)
        if self.type == RoomKeyType.AUTH_CODE:
            # 身份码要脱敏
            res = '***' + res[-3:]
        return res
    __repr__ = __str__

    @classmethod
    def from_dict(cls, data: dict):
        type_ = RoomKeyType(data['type'])
        value = data['value']
        if type_ == RoomKeyType.ROOM_ID:
            if not isinstance(value, int):
                raise TypeError(f'Type of value is {type(value)}, value={value}')
        elif type_ == RoomKeyType.AUTH_CODE:
            if not isinstance(value, str):
                raise TypeError(f'Type of value is {type(value)}, value={value}')
        return cls(type=type_, value=value)

    def to_dict(self):
        return {'type': self.type, 'value': self.value}


class Command(enum.IntEnum):
    HEARTBEAT = 0
    BLC_INIT = 1
    ADD_ROOM = 2
    ROOM_INIT = 3
    DEL_ROOM = 4
    OPEN_PLUGIN_ADMIN_UI = 5

    # 从插件发送到blivechat的请求
    LOG_REQ = 30
    ADD_TEXT_REQ = 31

    # 房间内消息
    ADD_TEXT = 50
    ADD_GIFT = 51
    ADD_MEMBER = 52
    ADD_SUPER_CHAT = 53
    DEL_SUPER_CHAT = 54
    UPDATE_TRANSLATION = 55


@dataclasses.dataclass
class ExtraData:
    """一些消息共用的附加信息"""

    room_id: Optional[int] = None
    """房间ID"""
    room_key: Optional[RoomKey] = None
    """blivechat用来标识一个房间的key"""
    is_from_plugin: bool = False
    """
    消息是插件生成的

    如果你的插件既要监听消息，又要生成消息，注意判断这个以避免死循环
    """

    @classmethod
    def from_dict(cls, data: dict):
        room_key_dict = data.get('roomKey', None)
        if room_key_dict is not None:
            room_key = RoomKey.from_dict(room_key_dict)
        else:
            room_key = None

        return cls(
            room_id=data.get('roomId', None),
            room_key=room_key,
            is_from_plugin=data.get('isFromPlugin', False),
        )


@dataclasses.dataclass
class _EmptyMsg:
    @classmethod
    def from_command(cls, _data: dict):
        return cls()


@dataclasses.dataclass
class AddRoomMsg(_EmptyMsg):
    """
    添加房间消息。房间信息在extra里

    此时room_id是None，因为还没有初始化
    """


@dataclasses.dataclass
class RoomInitMsg:
    """
    房间初始化消息。房间信息在extra里

    一个房间创建后可能被多次初始化，处理时注意去重
    """

    is_success: bool = False

    @classmethod
    def from_command(cls, data: dict):
        return cls(
            is_success=data['isSuccess'],
        )


@dataclasses.dataclass
class DelRoomMsg(_EmptyMsg):
    """
    删除房间消息。房间信息在extra里

    注意此时room_id可能是None
    """


@dataclasses.dataclass
class OpenPluginAdminUiMsg(_EmptyMsg):
    """用户请求打开当前插件的管理界面消息"""


class AuthorType(enum.IntEnum):
    NORMAL = 0
    GUARD = 1
    """舰队"""
    ADMIN = 2
    """房管"""
    ROOM_OWNER = 3
    """主播"""


class GuardLevel(enum.IntEnum):
    """舰队等级"""

    NONE = 0
    LV3 = 1
    """总督"""
    LV2 = 2
    """提督"""
    LV1 = 3
    """舰长"""


class ContentType(enum.IntEnum):
    TEXT = 0
    EMOTICON = 1


@dataclasses.dataclass
class AddTextMsg:
    """弹幕消息"""

    avatar_url: str = ''
    """用户头像URL"""
    timestamp: int = 0
    """时间戳（秒）"""
    author_name: str = ''
    """用户名"""
    author_type: int = AuthorType.NORMAL.value
    """用户类型，见AuthorType"""
    content: str = ''
    """弹幕内容"""
    privilege_type: int = GuardLevel.NONE.value
    """舰队等级，见GuardLevel"""
    is_gift_danmaku: bool = False
    """是否礼物弹幕"""
    author_level: int = 1
    """用户等级"""
    is_newbie: bool = False
    """是否正式会员"""
    is_mobile_verified: bool = True
    """是否绑定手机"""
    medal_level: int = 0
    """勋章等级，如果没戴当前房间勋章则为0"""
    id: str = ''
    """消息ID"""
    translation: str = ''
    """弹幕内容翻译"""
    content_type: int = ContentType.TEXT.value
    """内容类型，见ContentType"""
    content_type_params: Union[dict, list] = dataclasses.field(default_factory=dict)
    """跟内容类型相关的参数"""
    uid: str = ''
    """用户Open ID或ID"""
    medal_name: str = ''
    """勋章名"""

    @classmethod
    def from_command(cls, data: list):
        content_type = data[13]
        content_type_params = data[14]
        if content_type == ContentType.EMOTICON:
            content_type_params = {'url': content_type_params[0]}

        return cls(
            avatar_url=data[0],
            timestamp=data[1],
            author_name=data[2],
            author_type=data[3],
            content=data[4],
            privilege_type=data[5],
            is_gift_danmaku=bool(data[6]),
            author_level=data[7],
            is_newbie=bool(data[8]),
            is_mobile_verified=bool(data[9]),
            medal_level=data[10],
            id=data[11],
            translation=data[12],
            content_type=content_type,
            content_type_params=content_type_params,
            uid=data[16],
            medal_name=data[17],
        )


@dataclasses.dataclass
class AddGiftMsg:
    """礼物消息"""

    id: str = ''
    """消息ID"""
    avatar_url: str = ''
    """用户头像URL"""
    timestamp: int = 0
    """时间戳（秒）"""
    author_name: str = ''
    """用户名"""
    total_coin: int = 0
    """总价付费瓜子数，1000金瓜子 = 1元"""
    total_free_coin: int = 0
    """总价免费瓜子数"""
    gift_name: str = ''
    """礼物名"""
    num: int = 0
    """数量"""
    gift_id: int = 0
    """礼物ID"""
    gift_icon_url: str = ''
    """礼物图标URL"""
    uid: str = ''
    """用户Open ID或ID"""
    privilege_type: int = GuardLevel.NONE.value
    """舰队等级，见GuardLevel"""
    medal_level: int = 0
    """勋章等级，如果没戴当前房间勋章则为0"""
    medal_name: str = ''
    """勋章名"""

    @classmethod
    def from_command(cls, data: dict):
        return cls(
            id=data['id'],
            avatar_url=data['avatarUrl'],
            timestamp=data['timestamp'],
            author_name=data['authorName'],
            total_coin=data['totalCoin'],
            total_free_coin=data['totalFreeCoin'],
            gift_name=data['giftName'],
            num=data['num'],
            gift_id=data['giftId'],
            gift_icon_url=data['giftIconUrl'],
            uid=data['uid'],
            privilege_type=data['privilegeType'],
            medal_level=data['medalLevel'],
            medal_name=data['medalName'],
        )


@dataclasses.dataclass
class AddMemberMsg:
    """上舰消息"""

    id: str = ''
    """消息ID"""
    avatar_url: str = ''
    """用户头像URL"""
    timestamp: int = 0
    """时间戳（秒）"""
    author_name: str = ''
    """用户名"""
    privilege_type: int = GuardLevel.NONE.value
    """舰队等级，见GuardLevel"""
    num: int = 0
    """数量"""
    unit: str = ''
    """单位（月）"""
    total_coin: int = 0
    """总价付费瓜子数，1000金瓜子 = 1元"""
    uid: str = ''
    """用户Open ID或ID"""
    medal_level: int = 0
    """勋章等级，如果没戴当前房间勋章则为0"""
    medal_name: str = ''
    """勋章名"""

    @classmethod
    def from_command(cls, data: dict):
        return cls(
            id=data['id'],
            avatar_url=data['avatarUrl'],
            timestamp=data['timestamp'],
            author_name=data['authorName'],
            privilege_type=data['privilegeType'],
            num=data['num'],
            unit=data['unit'],
            total_coin=data['total_coin'],
            uid=data['uid'],
            medal_level=data['medalLevel'],
            medal_name=data['medalName'],
        )


@dataclasses.dataclass
class AddSuperChatMsg:
    """醒目留言消息"""

    id: str = ''
    """消息ID"""
    avatar_url: str = ''
    """用户头像URL"""
    timestamp: int = 0
    """时间戳（秒）"""
    author_name: str = ''
    """用户名"""
    price: int = 0
    """价格（元）"""
    content: str = ''
    """内容"""
    translation: str = ''
    """内容翻译"""
    uid: str = ''
    """用户Open ID或ID"""
    privilege_type: int = GuardLevel.NONE.value
    """舰队等级，见GuardLevel"""
    medal_level: int = 0
    """勋章等级，如果没戴当前房间勋章则为0"""
    medal_name: str = ''
    """勋章名"""

    @classmethod
    def from_command(cls, data: dict):
        return cls(
            id=data['id'],
            avatar_url=data['avatarUrl'],
            timestamp=data['timestamp'],
            author_name=data['authorName'],
            price=data['price'],
            content=data['content'],
            translation=data['translation'],
            uid=data['uid'],
            privilege_type=data['privilegeType'],
            medal_level=data['medalLevel'],
            medal_name=data['medalName'],
        )


@dataclasses.dataclass
class DelSuperChatMsg:
    """删除醒目留言消息"""

    ids: List[str] = dataclasses.field(default_factory=list)
    """醒目留言ID数组"""

    @classmethod
    def from_command(cls, data: dict):
        return cls(
            ids=data['ids'],
        )


@dataclasses.dataclass
class UpdateTranslationMsg:
    """更新内容翻译消息"""

    id: str = ''
    """消息ID"""
    translation: str = ''
    """内容翻译"""

    @classmethod
    def from_command(cls, data: list):
        return cls(
            id=data[0],
            translation=data[1],
        )
