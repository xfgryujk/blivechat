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
  }
}

export class AddGiftMsg {
  constructor({
    id = getUuid4Hex(),
    avatarUrl = chat.DEFAULT_AVATAR_URL,
    timestamp = new Date().getTime() / 1000,
    authorName = '',
    totalCoin = 0,
    giftName = '',
    num = 1,
  } = {}) {
    this.id = id
    this.avatarUrl = avatarUrl
    this.timestamp = timestamp
    this.authorName = authorName
    this.totalCoin = totalCoin
    this.giftName = giftName
    this.num = num
  }
}

export class AddMemberMsg {
  constructor({
    id = getUuid4Hex(),
    avatarUrl = chat.DEFAULT_AVATAR_URL,
    timestamp = new Date().getTime() / 1000,
    authorName = '',
    privilegeType = 1,
  } = {}) {
    this.id = id
    this.avatarUrl = avatarUrl
    this.timestamp = timestamp
    this.authorName = authorName
    this.privilegeType = privilegeType
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
  } = {}) {
    this.id = id
    this.avatarUrl = avatarUrl
    this.timestamp = timestamp
    this.authorName = authorName
    this.price = price
    this.content = content
    this.translation = translation
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

export class ChatClientFatalError extends Error {
  constructor(type, message) {
    super(message)
    this.type = type
  }
}
