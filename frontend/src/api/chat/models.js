import { getUuid4Hex } from '@/utils'
import * as constants from '@/components/ChatRenderer/constants'
import * as chat from '.'

export class AddTextMsg {
  constructor({
    avatarUrl = chat.DEFAULT_AVATAR_URL,
    timestamp = new Date().getTime() / 1000,
    authorName = '',
    authorType = constants.AUTHOR_TYPE_NORMAL,
    content = '',
    privilegeType = 0,
    isGiftDanmaku = false,
    authorLevel = 1,
    isNewbie = false,
    isMobileVerified = true,
    medalLevel = 0,
    id = getUuid4Hex(),
    translation = '',
    emoticon = null,
    // 给模板用的字段
    uid = '',
    medalName = '',
  } = {}) {
    this.avatarUrl = avatarUrl
    this.timestamp = timestamp
    this.authorName = authorName
    this.authorType = authorType
    this.content = content
    this.privilegeType = privilegeType
    this.isGiftDanmaku = isGiftDanmaku
    this.authorLevel = authorLevel
    this.isNewbie = isNewbie
    this.isMobileVerified = isMobileVerified
    this.medalLevel = medalLevel
    this.id = id
    this.translation = translation
    this.emoticon = emoticon
    // 给模板用的字段
    this.uid = uid
    this.medalName = medalName
  }
}

export class AddGiftMsg {
  constructor({
    id = getUuid4Hex(),
    avatarUrl = chat.DEFAULT_AVATAR_URL,
    timestamp = new Date().getTime() / 1000,
    authorName = '',
    totalCoin = 0,
    totalFreeCoin = 0,
    giftName = '',
    num = 1,
    // 给模板用的字段
    giftId = 0,
    giftIconUrl = '',
    uid = '',
    privilegeType = 0,
    medalLevel = 0,
    medalName = '',
  } = {}) {
    this.id = id
    this.avatarUrl = avatarUrl
    this.timestamp = timestamp
    this.authorName = authorName
    this.totalCoin = totalCoin
    this.totalFreeCoin = totalFreeCoin
    this.giftName = giftName
    this.num = num
    // 给模板用的字段
    this.giftId = giftId
    this.giftIconUrl = giftIconUrl
    this.uid = uid
    this.privilegeType = privilegeType
    this.medalLevel = medalLevel
    this.medalName = medalName
  }
}

export class AddMemberMsg {
  constructor({
    id = getUuid4Hex(),
    avatarUrl = chat.DEFAULT_AVATAR_URL,
    timestamp = new Date().getTime() / 1000,
    authorName = '',
    privilegeType = 1,
    // 给模板用的字段
    num = 1,
    unit = '月',
    total_coin = 0,
    uid = '',
    medalLevel = 0,
    medalName = '',
  } = {}) {
    this.id = id
    this.avatarUrl = avatarUrl
    this.timestamp = timestamp
    this.authorName = authorName
    this.privilegeType = privilegeType
    // 给模板用的字段
    this.num = num
    this.unit = unit
    this.totalCoin = total_coin
    this.uid = uid
    this.medalLevel = medalLevel
    this.medalName = medalName
  }
}

export class AddSuperChatMsg {
  constructor({
    id = getUuid4Hex(),
    avatarUrl = chat.DEFAULT_AVATAR_URL,
    timestamp = new Date().getTime() / 1000,
    authorName = '',
    price = 0,
    content = '',
    translation = '',
    // 给模板用的字段
    uid = '',
    privilegeType = 0,
    medalLevel = 0,
    medalName = '',
  } = {}) {
    this.id = id
    this.avatarUrl = avatarUrl
    this.timestamp = timestamp
    this.authorName = authorName
    this.price = price
    this.content = content
    this.translation = translation
    // 给模板用的字段
    this.uid = uid
    this.privilegeType = privilegeType
    this.medalLevel = medalLevel
    this.medalName = medalName
  }
}

export class DelSuperChatMsg {
  constructor({
    ids = [],
  } = {}) {
    this.ids = ids
  }
}

export class UpdateTranslationMsg {
  constructor({
    id = getUuid4Hex(),
    translation = '',
  } = {}) {
    this.id = id
    this.translation = translation
  }
}

export const FATAL_ERROR_TYPE_AUTH_CODE_ERROR = 1
export const FATAL_ERROR_TYPE_TOO_MANY_RETRIES = 2
export const FATAL_ERROR_TYPE_TOO_MANY_CONNECTIONS = 3

export class ChatClientFatalError extends Error {
  constructor(type, message) {
    super(message)
    this.type = type
  }
}

export class DebugMsg {
  constructor({
    content = '',
  } = {}) {
    this.content = content
  }
}
