import axios from 'axios'

import * as chat from '.'
import * as chatModels from './models'
import * as base from './ChatClientOfficialBase'
import ChatClientOfficialBase from './ChatClientOfficialBase'

export default class ChatClientDirectWeb extends ChatClientOfficialBase {
  constructor(roomId) {
    super()
    this.CMD_CALLBACK_MAP = CMD_CALLBACK_MAP

    // 调用initRoom后初始化，如果失败，使用这里的默认值
    this.roomId = roomId
    this.roomOwnerUid = -1
    this.hostServerList = [
      { host: "broadcastlv.chat.bilibili.com", port: 2243, wss_port: 443, ws_port: 2244 }
    ]
    this.hostServerToken = null
    this.buvid = ''
  }

  async initRoom() {
    let res
    try {
      res = (await axios.get('/api/room_info', { params: {
        roomId: this.roomId
      } })).data
    } catch {
      return true
    }
    this.roomId = res.roomId
    this.roomOwnerUid = res.ownerUid
    if (res.hostServerList.length !== 0) {
      this.hostServerList = res.hostServerList
    }
    this.hostServerToken = res.hostServerToken
    this.buvid = res.buvid
    return true
  }

  async onBeforeWsConnect() {
    // 重连次数太多则重新init_room，保险
    let reinitPeriod = Math.max(3, (this.hostServerList || []).length)
    if (this.retryCount > 0 && this.retryCount % reinitPeriod === 0) {
      this.needInitRoom = true
    }
    return super.onBeforeWsConnect()
  }

  getWsUrl() {
    let hostServer = this.hostServerList[this.retryCount % this.hostServerList.length]
    return `wss://${hostServer.host}:${hostServer.wss_port}/sub`
  }

  sendAuth() {
    let authParams = {
      uid: 0,
      roomid: this.roomId,
      protover: 3,
      platform: 'web',
      type: 2,
      buvid: this.buvid,
    }
    if (this.hostServerToken !== null) {
      authParams.key = this.hostServerToken
    }
    this.websocket.send(this.makePacket(authParams, base.OP_AUTH))
  }

  async danmuMsgCallback(command) {
    let info = command.info

    let roomId, medalLevel
    if (info[3]) {
      roomId = info[3][3]
      medalLevel = info[3][0]
    } else {
      roomId = medalLevel = 0
    }

    let uid = info[2][0]
    let isAdmin = info[2][2]
    let privilegeType = info[7]
    let authorType
    if (uid === this.roomOwnerUid) {
      authorType = 3
    } else if (isAdmin) {
      authorType = 2
    } else if (privilegeType !== 0) {
      authorType = 1
    } else {
      authorType = 0
    }

    let authorName = info[2][1]
    let content = info[1]
    let data = new chatModels.AddTextMsg({
      avatarUrl: await chat.getAvatarUrl(uid, authorName),
      timestamp: info[0][4] / 1000,
      authorName: authorName,
      authorType: authorType,
      content: content,
      privilegeType: privilegeType,
      isGiftDanmaku: Boolean(info[0][9]) || chat.isGiftDanmakuByContent(content),
      authorLevel: info[4][0],
      isNewbie: info[2][5] < 10000,
      isMobileVerified: Boolean(info[2][6]),
      medalLevel: roomId === this.roomId ? medalLevel : 0,
      emoticon: info[0][13].url || null,
    })
    this.msgHandler.onAddText(data)
  }

  sendGiftCallback(command) {
    let data = command.data
    let isPaidGift = data.coin_type === 'gold'
    data = new chatModels.AddGiftMsg({
      avatarUrl: chat.processAvatarUrl(data.face),
      timestamp: data.timestamp,
      authorName: data.uname,
      totalCoin: isPaidGift ? data.total_coin : 0,
      totalFreeCoin: !isPaidGift ? data.total_coin : 0,
      giftName: data.giftName,
      num: data.num
    })
    this.msgHandler.onAddGift(data)
  }

  async guardBuyCallback(command) {
    let data = command.data
    data = new chatModels.AddMemberMsg({
      avatarUrl: await chat.getAvatarUrl(data.uid, data.username),
      timestamp: data.start_time,
      authorName: data.username,
      privilegeType: data.guard_level
    })
    this.msgHandler.onAddMember(data)
  }

  superChatMessageCallback(command) {
    let data = command.data
    data = new chatModels.AddSuperChatMsg({
      id: data.id.toString(),
      avatarUrl: chat.processAvatarUrl(data.user_info.face),
      timestamp: data.start_time,
      authorName: data.user_info.uname,
      price: data.price,
      content: data.message,
    })
    this.msgHandler.onAddSuperChat(data)
  }

  superChatMessageDeleteCallback(command) {
    let ids = []
    for (let id of command.data.ids) {
      ids.push(id.toString())
    }
    let data = new chatModels.DelSuperChatMsg({ ids })
    this.msgHandler.onDelSuperChat(data)
  }
}

const CMD_CALLBACK_MAP = {
  DANMU_MSG: ChatClientDirectWeb.prototype.danmuMsgCallback,
  SEND_GIFT: ChatClientDirectWeb.prototype.sendGiftCallback,
  GUARD_BUY: ChatClientDirectWeb.prototype.guardBuyCallback,
  SUPER_CHAT_MESSAGE: ChatClientDirectWeb.prototype.superChatMessageCallback,
  SUPER_CHAT_MESSAGE_DELETE: ChatClientDirectWeb.prototype.superChatMessageDeleteCallback
}
