import axios from 'axios'

import * as chat from '.'
import * as base from './ChatClientOfficialBase'
import ChatClientOfficialBase from './ChatClientOfficialBase'

const GAME_HEARTBEAT_INTERVAL = 20 * 1000

export default class ChatClientDirectOpenLive extends ChatClientOfficialBase {
  constructor(roomOwnerAuthCode) {
    super()
    this.CMD_CALLBACK_MAP = CMD_CALLBACK_MAP

    this.roomOwnerAuthCode = roomOwnerAuthCode

    // 调用initRoom后初始化
    this.roomOwnerUid = null
    this.hostServerUrlList = []
    this.authBody = null
    this.gameId = null

    this.gameHeartbeatTimerId = null
  }

  stop() {
    super.stop()

    if (this.gameHeartbeatTimerId) {
      window.clearInterval(this.gameHeartbeatTimerId)
      this.gameHeartbeatTimerId = null
    }
    this.endGame()
  }

  async initRoom() {
    if (!await this.startGame()) {
      return false
    }

    if (this.gameId && this.gameHeartbeatTimerId === null) {
      this.gameHeartbeatTimerId = window.setInterval(this.sendGameHeartbeat.bind(this), GAME_HEARTBEAT_INTERVAL)
    }
    return true
  }

  async startGame() {
    let res
    try {
      res = (await axios.post('/api/open_live/start_game', {
        code: this.roomOwnerAuthCode,
        app_id: 0
      })).data
      if (res.code !== 0) {
        let msg = `code=${res.code}, message=${res.message}, request_id=${res.request_id}`
        if (res.code === 7007) {
          // 身份码错误
          throw new chat.ChatClientFatalError(chat.FATAL_ERROR_TYPE_AUTH_CODE_ERROR, msg)
        }
        throw Error(msg)
      }
    } catch (e) {
      console.error('startGame failed:', e)
      if (e instanceof chat.ChatClientFatalError) {
        throw e
      }
      return false
    }

    let data = res.data
    this.gameId = data.game_info.game_id
    let websocketInfo = data.websocket_info
    this.authBody = websocketInfo.auth_body
    this.hostServerUrlList = websocketInfo.wss_link
    let anchorInfo = data.anchor_info
    // this.roomId = anchorInfo.room_id
    this.roomOwnerUid = anchorInfo.uid
    return true
  }

  async endGame() {
    if (!this.gameId) {
      return true
    }

    try {
      let res = (await axios.post('/api/open_live/end_game', {
        app_id: 0,
        game_id: this.gameId
      })).data
      if (res.code !== 0) {
        if (res.code === 7000 || res.code === 7003) {
          // 项目已经关闭了也算成功
          return true
        }
        throw Error(`code=${res.code}, message=${res.message}, request_id=${res.request_id}`)
      }
    } catch (e) {
      console.error('endGame failed:', e)
      return false
    }
    return true
  }

  async sendGameHeartbeat() {
    if (!this.gameId) {
      return false
    }

    // 保存一下，防止await之后gameId改变
    let gameId = this.gameId
    try {
      let res = (await axios.post('/api/open_live/game_heartbeat', {
        game_id: this.gameId
      })).data
      if (res.code !== 0) {
        console.error(`sendGameHeartbeat failed: code=${res.code}, message=${res.message}, request_id=${res.request_id}`)

        if (res.code === 7003 && this.gameId === gameId) {
          // 项目异常关闭，可能是心跳超时，需要重新开启项目
          this.needInitRoom = true
          this.discardWebsocket()
        }

        return false
      }
    } catch (e) {
      console.error('sendGameHeartbeat failed:', e)
      return false
    }
    return true
  }

  async onBeforeWsConnect() {
    // 重连次数太多则重新init_room，保险
    let reinitPeriod = Math.max(3, (this.hostServerUrlList || []).length)
    if (this.retryCount > 0 && this.retryCount % reinitPeriod === 0) {
      this.needInitRoom = true
    }
    return super.onBeforeWsConnect()
  }

  getWsUrl() {
    return this.hostServerUrlList[this.retryCount % this.hostServerUrlList.length]
  }

  sendAuth() {
    this.websocket.send(this.makePacket(this.authBody, base.OP_AUTH))
  }

  async dmCallback(command) {
    if (!this.onAddText) {
      return
    }
    let data = command.data

    let authorType
    if (data.uid === this.roomOwnerUid) {
      authorType = 3
    } else if (data.guard_level !== 0) {
      authorType = 1
    } else {
      authorType = 0
    }

    let emoticon = null
    if (data.dm_type === 1) {
      emoticon = data.emoji_img_url
    }

    data = {
      avatarUrl: chat.processAvatarUrl(data.uface),
      timestamp: data.timestamp,
      authorName: data.uname,
      authorType: authorType,
      content: data.msg,
      privilegeType: data.guard_level,
      isGiftDanmaku: false,
      authorLevel: 1,
      isNewbie: false,
      isMobileVerified: true,
      medalLevel: data.fans_medal_wearing_status ? data.fans_medal_level : 0,
      id: data.msg_id,
      translation: '',
      emoticon: emoticon,
    }
    this.onAddText(data)
  }

  sendGiftCallback(command) {
    if (!this.onAddGift) {
      return
    }
    let data = command.data
    if (!data.paid) { // 丢人
      return
    }

    data = {
      id: data.msg_id,
      avatarUrl: chat.processAvatarUrl(data.uface),
      timestamp: data.timestamp,
      authorName: data.uname,
      totalCoin: data.price,
      giftName: data.gift_name,
      num: data.gift_num
    }
    this.onAddGift(data)
  }

  async guardCallback(command) {
    if (!this.onAddMember) {
      return
    }

    let data = command.data
    data = {
      id: data.msg_id,
      avatarUrl: chat.processAvatarUrl(data.user_info.uface),
      timestamp: data.timestamp,
      authorName: data.user_info.uname,
      privilegeType: data.guard_level
    }
    this.onAddMember(data)
  }

  superChatCallback(command) {
    if (!this.onAddSuperChat) {
      return
    }

    let data = command.data
    data = {
      id: data.message_id.toString(),
      avatarUrl: chat.processAvatarUrl(data.uface),
      timestamp: data.start_time,
      authorName: data.uname,
      price: data.rmb,
      content: data.message,
      translation: ''
    }
    this.onAddSuperChat(data)
  }

  superChatDelCallback(command) {
    if (!this.onDelSuperChat) {
      return
    }

    let ids = []
    for (let id of command.data.message_ids) {
      ids.push(id.toString())
    }
    this.onDelSuperChat({ ids })
  }
}

const CMD_CALLBACK_MAP = {
  LIVE_OPEN_PLATFORM_DM: ChatClientDirectOpenLive.prototype.dmCallback,
  LIVE_OPEN_PLATFORM_SEND_GIFT: ChatClientDirectOpenLive.prototype.sendGiftCallback,
  LIVE_OPEN_PLATFORM_GUARD: ChatClientDirectOpenLive.prototype.guardCallback,
  LIVE_OPEN_PLATFORM_SUPER_CHAT: ChatClientDirectOpenLive.prototype.superChatCallback,
  LIVE_OPEN_PLATFORM_SUPER_CHAT_DEL: ChatClientDirectOpenLive.prototype.superChatDelCallback
}
