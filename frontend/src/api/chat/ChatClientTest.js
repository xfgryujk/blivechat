import {getUuid4Hex} from '@/utils'
import * as constants from '@/components/ChatRenderer/constants'
import * as avatar from './avatar'

const NAMES = [
  'xfgryujk', 'Simon', 'Il Harper', 'Kinori', 'shugen', 'yuyuyzl', '3Shain', '光羊', '黑炎', 'Misty', '孤梦星影',
  'ジョナサン・ジョースター', 'ジョセフ・ジョースター', 'ディオ・ブランドー', '空條承太郎', '博丽灵梦', '雾雨魔理沙',
  'Rick Astley'
]

const CONTENTS = [
  '草', 'kksk', '8888888888', '888888888888888888888888888888', '老板大气，老板身体健康',
  'The quick brown fox jumps over the lazy dog', "I can eat glass, it doesn't hurt me",
  '我不做人了，JOJO', '無駄無駄無駄無駄無駄無駄無駄無駄', '欧啦欧啦欧啦欧啦欧啦欧啦欧啦欧啦', '逃げるんだよォ！',
  '嚯，朝我走过来了吗，没有选择逃跑而是主动接近我么', '不要停下来啊', '已经没有什么好怕的了',
  'I am the bone of my sword. Steel is my body, and fire is my blood.', '言いたいことがあるんだよ！',
  '我忘不掉夏小姐了。如果不是知道了夏小姐，说不定我已经对这个世界没有留恋了', '迷えば、敗れる',
  'Farewell, ashen one. May the flame guide thee', '竜神の剣を喰らえ！', '竜が我が敌を喰らう！',
  '有一说一，这件事大家懂的都懂，不懂的，说了你也不明白，不如不说', '让我看看', '我柜子动了，我不玩了'
]

const EMOTICONS = [
  "https://i0.hdslb.com/bfs/live/a98e35996545509188fe4d24bd1a56518ea5af48.png",
  "https://i0.hdslb.com/bfs/live/2af0e252cc3082384edf8165751f6a49eaf76d94.png",
  "https://i0.hdslb.com/bfs/live/6a034cfac8631035f5877d722379914f628cf120.png",
  "https://i0.hdslb.com/bfs/live/625989e78079e3dc38d75cb9ac392fe8c1aa4a75.png",
  "https://i0.hdslb.com/bfs/live/eff44c1fc03311573e8817ca8010aca72404f65c.png",
  "https://i0.hdslb.com/bfs/live/a9e2acaf72b663c6ad9c39cda4ae01470e13d845.png",
  "https://i0.hdslb.com/bfs/live/7251dc7df587388a3933743bf38394d12a922cd7.png",
  "https://i0.hdslb.com/bfs/live/88b49dac03bfd5d4cb49672956f78beb2ebd0d0b.png",
  "https://i0.hdslb.com/bfs/live/0e28444c8e2faef3169e98e1a41c487144d877d4.png",
  "https://i0.hdslb.com/bfs/live/aa48737f877cd328162696a4f784b85d4bfca9ce.png",
  "https://i0.hdslb.com/bfs/live/61e790813c51eab55ebe0699df1e9834c90b68ba.png",
  "https://i0.hdslb.com/bfs/live/343f7f7e87fa8a07df63f9cba6b776196d9066f0.png",
  "https://i0.hdslb.com/bfs/live/7b7a2567ad1520f962ee226df777eaf3ca368fbc.png",
  "https://i0.hdslb.com/bfs/live/39e518474a3673c35245bf6ef8ebfff2c003fdc3.png",
  "https://i0.hdslb.com/bfs/live/9029486931c3169c3b4f8e69da7589d29a8eadaa.png",
  "https://i0.hdslb.com/bfs/live/328e93ce9304090f4035e3aa7ef031d015bbc915.png",
  "https://i0.hdslb.com/bfs/live/aa93b9af7ba03b50df23b64e9afd0d271955cd71.png",
  "https://i0.hdslb.com/bfs/live/18af5576a4582535a3c828c3ae46a7855d9c6070.png",
  "https://i0.hdslb.com/bfs/live/4cf43ac5259589e9239c4e908c8149d5952fcc32.png",
  "https://i0.hdslb.com/bfs/live/40db7427f02a2d9417f8eeed0f71860dfb28df5a.png",
  "https://i0.hdslb.com/bfs/live/1ba5126b10e5efe3e4e29509d033a37f128beab2.png",
  "https://i0.hdslb.com/bfs/live/ff840c706fffa682ace766696b9f645e40899f67.png",
  "https://i0.hdslb.com/bfs/live/08f1aebaa4d9c170aa79cbafe521ef0891bdf2b5.png",
  "https://i0.hdslb.com/bfs/live/c2650bf9bbc79b682a4b67b24df067fdd3e5e9ca.png",
  "https://i0.hdslb.com/bfs/live/c3326ceb63587c79e5b4106ee4018dc59389b5c0.png",
  "https://i0.hdslb.com/bfs/live/7db4188c050f55ec59a1629fbc5a53661e4ba780.png",
  "https://i0.hdslb.com/bfs/live/cc2652cef69b22117f1911391567bd2957f27e08.png",
]

const AUTHOR_TYPES = [
  {weight: 10, value: constants.AUTHRO_TYPE_NORMAL},
  {weight: 5, value: constants.AUTHRO_TYPE_MEMBER},
  {weight: 2, value: constants.AUTHRO_TYPE_ADMIN},
  {weight: 1, value: constants.AUTHRO_TYPE_OWNER}
]

function randGuardInfo () {
  let authorType = randomChoose(AUTHOR_TYPES)
  let privilegeType
  if (authorType === constants.AUTHRO_TYPE_MEMBER || authorType === constants.AUTHRO_TYPE_ADMIN) {
    privilegeType = randInt(1, 3)
  } else {
    privilegeType = 0
  }
  return {authorType, privilegeType}
}

const GIFT_INFO_LIST = [
  {giftName: 'B坷垃', totalCoin: 9900},
  {giftName: '礼花', totalCoin: 28000},
  {giftName: '花式夸夸', totalCoin: 39000},
  {giftName: '天空之翼', totalCoin: 100000},
  {giftName: '摩天大楼', totalCoin: 450000},
  {giftName: '小电视飞船', totalCoin: 1245000}
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
        message: {
          ...randGuardInfo(),
          avatarUrl: avatar.DEFAULT_AVATAR_URL,
          timestamp: new Date().getTime() / 1000,
          authorName: randomChoose(NAMES),
          content: randomChoose(CONTENTS),
          isGiftDanmaku: randInt(1, 10) <= 1,
          authorLevel: randInt(0, 60),
          isNewbie: randInt(1, 10) <= 9,
          isMobileVerified: randInt(1, 10) <= 9,
          medalLevel: randInt(0, 40),
          id: getUuid4Hex(),
          translation: ''
        }
      }
    }
  },
  // 表情
  {
    weight: 5,
    value() {
      return {
        type: constants.MESSAGE_TYPE_TEXT,
        message: {
          ...randGuardInfo(),
          avatarUrl: avatar.DEFAULT_AVATAR_URL,
          timestamp: new Date().getTime() / 1000,
          authorName: randomChoose(NAMES),
          content: '',
          emoticon: randomChoose(EMOTICONS),
          isGiftDanmaku: false,
          authorLevel: randInt(0, 60),
          isNewbie: randInt(1, 10) <= 9,
          isMobileVerified: randInt(1, 10) <= 9,
          medalLevel: randInt(0, 40),
          id: getUuid4Hex(),
          translation: ''
        }
      }
    }
  },
  // 礼物
  {
    weight: 1,
    value() {
      return {
        type: constants.MESSAGE_TYPE_GIFT,
        message: {
          ...randomChoose(GIFT_INFO_LIST),
          id: getUuid4Hex(),
          avatarUrl: avatar.DEFAULT_AVATAR_URL,
          timestamp: new Date().getTime() / 1000,
          authorName: randomChoose(NAMES),
          num: 1
        }
      }
    }
  },
  // SC
  {
    weight: 3,
    value() {
      return {
        type: constants.MESSAGE_TYPE_SUPER_CHAT,
        message: {
          id: getUuid4Hex(),
          avatarUrl: avatar.DEFAULT_AVATAR_URL,
          timestamp: new Date().getTime() / 1000,
          authorName: randomChoose(NAMES),
          price: randomChoose(SC_PRICES),
          content: randomChoose(CONTENTS),
          translation: ''
        }
      }
    }
  },
  // 新舰长
  {
    weight: 1,
    value() {
      return {
        type: constants.MESSAGE_TYPE_MEMBER,
        message: {
          id: getUuid4Hex(),
          avatarUrl: avatar.DEFAULT_AVATAR_URL,
          timestamp: new Date().getTime() / 1000,
          authorName: randomChoose(NAMES),
          privilegeType: randInt(1, 3)
        }
      }
    }
  }
]

function randomChoose (nodes) {
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

function randInt (min, max) {
  return Math.floor(min + (max - min + 1) * Math.random())
}

export default class ChatClientTest {
  constructor () {
    this.minSleepTime = 800
    this.maxSleepTime = 1200

    this.onAddText = null
    this.onAddGift = null
    this.onAddMember = null
    this.onAddSuperChat = null
    this.onDelSuperChat = null
    this.onUpdateTranslation = null

    this.timerId = null
  }

  start () {
    this.refreshTimer()
  }

  stop () {
    if (this.timerId) {
      window.clearTimeout(this.timerId)
      this.timerId = null
    }
  }

  refreshTimer () {
    this.timerId = window.setTimeout(this.onTimeout.bind(this), randInt(this.minSleepTime, this.maxSleepTime))
  }

  onTimeout () {
    this.refreshTimer()

    let {type, message} = randomChoose(MESSAGE_GENERATORS)()
    switch (type) {
    case constants.MESSAGE_TYPE_TEXT:
      this.onAddText(message)
      break
    case constants.MESSAGE_TYPE_GIFT:
      this.onAddGift(message)
      break
    case constants.MESSAGE_TYPE_MEMBER:
      this.onAddMember(message)
      break
    case constants.MESSAGE_TYPE_SUPER_CHAT:
      this.onAddSuperChat(message)
      break
    }
  }
}
