import axios from 'axios'

import { getUuid4Hex } from '@/utils'
import * as chat from '.'
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
    return true
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
      buvid: '',
    }
    this.websocket.send(this.makePacket(authParams, base.OP_AUTH))
  }

  async danmuMsgCallback(command) {
    if (!this.onAddText) {
      return
    }
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

    let data = {
      avatarUrl: await chat.getAvatarUrl(uid),
      timestamp: info[0][4] / 1000,
      authorName: info[2][1],
      authorType: authorType,
      content: info[1],
      privilegeType: privilegeType,
      isGiftDanmaku: Boolean(info[0][9]),
      authorLevel: info[4][0],
      isNewbie: info[2][5] < 10000,
      isMobileVerified: Boolean(info[2][6]),
      medalLevel: roomId === this.roomId ? medalLevel : 0,
      id: getUuid4Hex(),
      translation: '',
      emoticon: info[0][13].url || null,
    }
    this.onAddText(data)
  }

  sendGiftCallback(command) {
    if (!this.onAddGift) {
      return
    }
    let data = command.data
    if (data.coin_type !== 'gold') { // 丢人
      return
    }

    data = {
      id: getUuid4Hex(),
      avatarUrl: chat.processAvatarUrl(data.face),
      timestamp: data.timestamp,
      authorName: data.uname,
      totalCoin: data.total_coin,
      giftName: data.giftName,
      num: data.num
    }
    this.onAddGift(data)
  }

  async guardBuyCallback(command) {
    if (!this.onAddMember) {
      return
    }

    let data = command.data
    data = {
      id: getUuid4Hex(),
      avatarUrl: await chat.getAvatarUrl(data.uid),
      timestamp: data.start_time,
      authorName: data.username,
      privilegeType: data.guard_level
    }
    this.onAddMember(data)
  }

  superChatMessageCallback(command) {
    if (!this.onAddSuperChat) {
      return
    }

    let data = command.data
    data = {
      id: data.id.toString(),
      avatarUrl: chat.processAvatarUrl(data.user_info.face),
      timestamp: data.start_time,
      authorName: data.user_info.uname,
      price: data.price,
      content: data.message,
      translation: ''
    }
    this.onAddSuperChat(data)
  }

  superChatMessageDeleteCallback(command) {
    if (!this.onDelSuperChat) {
      return
    }

    let ids = []
    for (let id of command.data.ids) {
      ids.push(id.toString())
    }
    this.onDelSuperChat({ ids })
  }
}

const CMD_CALLBACK_MAP = {
  DANMU_MSG: ChatClientDirectWeb.prototype.danmuMsgCallback,
  SEND_GIFT: ChatClientDirectWeb.prototype.sendGiftCallback,
  GUARD_BUY: ChatClientDirectWeb.prototype.guardBuyCallback,
  SUPER_CHAT_MESSAGE: ChatClientDirectWeb.prototype.superChatMessageCallback,
  SUPER_CHAT_MESSAGE_DELETE: ChatClientDirectWeb.prototype.superChatMessageDeleteCallback
}
