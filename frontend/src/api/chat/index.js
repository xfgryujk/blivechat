import axios from 'axios'

export const FATAL_ERROR_TYPE_AUTH_CODE_ERROR = 1

export class ChatClientFatalError extends Error {
  constructor(type, message) {
    super(message)
    this.type = type
  }
}

export const DEFAULT_AVATAR_URL = '//static.hdslb.com/images/member/noface.gif'

export function processAvatarUrl(avatarUrl) {
  // 去掉协议，兼容HTTP、HTTPS
  let m = avatarUrl.match(/(?:https?:)?(.*)/)
  if (m) {
    avatarUrl = m[1]
  }
  return avatarUrl
}

export async function getAvatarUrl(uid, username) {
  let res
  try {
    res = (await axios.get('/api/avatar_url', { params: {
      uid: uid,
      username: username
    } })).data
  } catch {
    return DEFAULT_AVATAR_URL
  }
  return res.avatarUrl
}

export async function getTextEmoticons() {
  let res
  try {
    res = (await axios.get('/api/text_emoticon_mappings')).data
  } catch {
    return []
  }
  return res.textEmoticons
}
