import axios from 'axios'

export const DEFAULT_AVATAR_URL = '//static.hdslb.com/images/member/noface.gif'

export function processAvatarUrl (avatarUrl) {
  // 去掉协议，兼容HTTP、HTTPS
  let m = avatarUrl.match(/(?:https?:)?(.*)/)
  if (m) {
    avatarUrl = m[1]
  }
  // 缩小图片加快传输
  if (!avatarUrl.endsWith('noface.gif')) {
    avatarUrl += '@48w_48h'
  }
  return avatarUrl
}

export async function getAvatarUrl (uid) {
  let res
  try {
    res = (await axios.get('/api/avatar_url', {params: {
      uid: uid
    }})).data
  } catch {
    return DEFAULT_AVATAR_URL
  }
  return res.avatarUrl
}
