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

export async function getAvatarUrl(uid, username, dm_v2) {
  let res
  try {
    res = (await axios.get('/api/avatar_url', { params: {
      uid: uid,
      username: username,
      dm_v2: dm_v2
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

// 开放平台接口不会发送是否是礼物弹幕，只能用内容判断了
const GIFT_DANMAKU_CONTENTS = new Set([
  // 红包
  '老板大气！点点红包抽礼物',
  '老板大气！点点红包抽礼物！',
  '点点红包，关注主播抽礼物～',
  '喜欢主播加关注，点点红包抽礼物',
  '红包抽礼物，开启今日好运！',
  '中奖喷雾！中奖喷雾！',
  // 节奏风暴
  '前方高能预警，注意这不是演习',
  '我从未见过如此厚颜无耻之人',
  '那万一赢了呢',
  '你们城里人真会玩',
  '左舷弹幕太薄了',
  '要优雅，不要污',
  '我选择狗带',
  '可爱即正义~~',
  '糟了，是心动的感觉！',
  '这个直播间已经被我们承包了！',
  '妈妈问我为什么跪着看直播 w(ﾟДﾟ)w',
  '你们对力量一无所知~(￣▽￣)~',
  // 好像花式夸夸还有，不想花钱收集内容了
])

export function isGiftDanmakuByContent(content) {
  return GIFT_DANMAKU_CONTENTS.has(content)
}
