import * as constants from '@/components/ChatRenderer/constants'
import * as chat from '.'
import * as chatModels from './models'

const NAMES = [
  '成龙',
  '杨戬',
  '孙悟空',
  '哈基米',
  '大张伟',
  '周冠宇',
  '五条悟',
  '博丽灵梦',
  '御剑侍伶',
  '田所浩二',
  '小岛秀夫',
  '長崎そよ',
  '柚木つばめ',
  '空條承太郎',
  'みもりあいの',
  'ディオ・ブランドー',
  'Dante',
  'xQcOW',
  'Makarov',
  'xfgryujk',
  'Jim Hacker',
  'Rick Astley',
  'Tifa Lockhart',
  'Arthur Morgan',
]

const CONTENTS = [
  '草',
  '会赢的',
  '让我看看',
  '卑鄙的外乡人',
  '我不做人了，JOJO',
  '已经没有什么好怕的了',
  '你这猴子，真令我欢喜',
  '[dog]文本[比心]表情[喝彩]',
  '阿祖，投降吧，外面全是警察',
  '無駄無駄無駄無駄無駄無駄無駄無駄',
  '我衰咗三年，我等緊個機會，爭番口氣',
  '因为你的缘故，我的心中萌生了多余的情感',
  '迷えば、敗れる',
  '逃げるんだよォ！',
  '届かない恋をしていても',
  'なんで春日影やったの！？',
  'kksk',
  'Y.M.C.A.',
  '8888888888',
  'text[吃瓜]emoticon',
  'Remember... no Russian',
  'Never gonna give you up',
  'DU↗DU→DU↗DU↓ Max Verstappen',
  'Farewell, ashen one. May the flame guide thee',
  'Hey Vergil, your portal opening days are over. Give me the Yamato',
]

const EMOTICONS = [
  '233',
  'miaoa',
  'lipu',
  'huangdou_xihuan',
  'sakaban_jiayu_yutou',
].map(name => `/static/img/emoticons/${name}.png`)

const AUTHOR_TYPES = [
  { weight: 10, value: constants.AUTHOR_TYPE_NORMAL },
  { weight: 5, value: constants.AUTHOR_TYPE_MEMBER },
  { weight: 2, value: constants.AUTHOR_TYPE_ADMIN },
  { weight: 1, value: constants.AUTHOR_TYPE_OWNER }
]

function randGuardInfo() {
  let authorType = randomChoose(AUTHOR_TYPES)
  let privilegeType
  if (authorType === constants.AUTHOR_TYPE_MEMBER) {
    privilegeType = randInt(1, 3)
  } else if (authorType === constants.AUTHOR_TYPE_ADMIN) {
    privilegeType = randInt(0, 3)
  } else {
    privilegeType = 0
  }
  return { authorType, privilegeType }
}

const GIFT_INFO_LIST = [
  { giftName: '辣条', totalFreeCoin: 1000, num: 10 },
  { giftName: 'B坷垃', totalCoin: 9900 },
  { giftName: '礼花', totalCoin: 28000 },
  { giftName: '花式夸夸', totalCoin: 39000 },
  { giftName: '天空之翼', totalCoin: 100000 },
  { giftName: '摩天大楼', totalCoin: 450000 },
  { giftName: '小电视飞船', totalCoin: 1245000 }
]

const SC_PRICES = [
  30, 50, 100, 200, 500, 1000
]

const MESSAGE_GENERATORS = [
  // 文字
  {
    weight: 20,
    value() {
      return {
        type: constants.MESSAGE_TYPE_TEXT,
        message: new chatModels.AddTextMsg({
          ...randGuardInfo(),
          authorName: randomChoose(NAMES),
          content: randomChoose(CONTENTS),
          isGiftDanmaku: randInt(1, 10) <= 1,
          authorLevel: randInt(1, 60),
          isNewbie: randInt(1, 10) <= 1,
          isMobileVerified: randInt(1, 10) <= 9,
          medalLevel: randInt(0, 40),
        })
      }
    }
  },
  // 表情
  {
    weight: 5,
    value() {
      return {
        type: constants.MESSAGE_TYPE_TEXT,
        message: new chatModels.AddTextMsg({
          ...randGuardInfo(),
          authorName: randomChoose(NAMES),
          authorLevel: randInt(1, 60),
          isNewbie: randInt(1, 10) <= 1,
          isMobileVerified: randInt(1, 10) <= 9,
          medalLevel: randInt(0, 40),
          emoticon: randomChoose(EMOTICONS),
        })
      }
    }
  },
  // 礼物
  {
    weight: 1,
    value() {
      return {
        type: constants.MESSAGE_TYPE_GIFT,
        message: new chatModels.AddGiftMsg({
          ...randomChoose(GIFT_INFO_LIST),
          authorName: randomChoose(NAMES),
        })
      }
    }
  },
  // SC
  {
    weight: 3,
    value() {
      return {
        type: constants.MESSAGE_TYPE_SUPER_CHAT,
        message: new chatModels.AddSuperChatMsg({
          authorName: randomChoose(NAMES),
          price: randomChoose(SC_PRICES),
          content: randomChoose(CONTENTS),
        })
      }
    }
  },
  // 新舰长
  {
    weight: 1,
    value() {
      return {
        type: constants.MESSAGE_TYPE_MEMBER,
        message: new chatModels.AddMemberMsg({
          authorName: randomChoose(NAMES),
          privilegeType: randInt(1, 3)
        })
      }
    }
  }
]

function randomChoose(nodes) {
  if (nodes.length === 0) {
    return null
  }
  for (let node of nodes) {
    if (node.weight === undefined || node.value === undefined) {
      return nodes[randInt(0, nodes.length - 1)]
    }
  }

  let totalWeight = 0
  for (let node of nodes) {
    totalWeight += node.weight
  }
  let remainWeight = randInt(1, totalWeight)
  for (let node of nodes) {
    remainWeight -= node.weight
    if (remainWeight > 0) {
      continue
    }
    if (node.value instanceof Array) {
      return randomChoose(node.value)
    }
    return node.value
  }
  return null
}

function randInt(min, max) {
  return Math.floor(min + ((max - min + 1) * Math.random()))
}

export default class ChatClientTest {
  constructor() {
    this.msgHandler = chat.getDefaultMsgHandler()

    this.timerId = null
  }

  start() {
    this.refreshTimer()
  }

  stop() {
    if (this.timerId) {
      window.clearTimeout(this.timerId)
      this.timerId = null
    }
  }

  refreshTimer() {
    // 模仿B站的消息间隔模式
    let sleepTime
    if (randInt(0, 4) == 0) {
      sleepTime = randInt(1000, 2000)
    } else {
      sleepTime = randInt(0, 400)
    }
    if (this.timerId) {
      window.clearTimeout(this.timerId)
    }
    this.timerId = window.setTimeout(this.onTimeout.bind(this), sleepTime)
  }

  onTimeout() {
    this.refreshTimer()

    let { type, message } = randomChoose(MESSAGE_GENERATORS)()
    switch (type) {
    case constants.MESSAGE_TYPE_TEXT:
      this.msgHandler.onAddText(message)
      break
    case constants.MESSAGE_TYPE_GIFT:
      this.msgHandler.onAddGift(message)
      break
    case constants.MESSAGE_TYPE_MEMBER:
      this.msgHandler.onAddMember(message)
      break
    case constants.MESSAGE_TYPE_SUPER_CHAT:
      this.msgHandler.onAddSuperChat(message)
      break
    }
  }
}
