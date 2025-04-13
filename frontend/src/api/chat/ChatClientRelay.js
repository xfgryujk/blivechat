import { getBaseUrl } from '@/api/base'
import * as chat from '.'
import * as chatModels from './models'

const COMMAND_HEARTBEAT = 0
const COMMAND_JOIN_ROOM = 1
const COMMAND_ADD_TEXT = 2
const COMMAND_ADD_GIFT = 3
const COMMAND_ADD_MEMBER = 4
const COMMAND_ADD_SUPER_CHAT = 5
const COMMAND_DEL_SUPER_CHAT = 6
const COMMAND_UPDATE_TRANSLATION = 7
const COMMAND_FATAL_ERROR = 8

// const CONTENT_TYPE_TEXT = 0
const CONTENT_TYPE_EMOTICON = 1

const RECEIVE_TIMEOUT = 15 * 1000

export default class ChatClientRelay {
  constructor(roomKey, autoTranslate) {
    this.roomKey = roomKey
    this.autoTranslate = autoTranslate

    this.msgHandler = chat.getDefaultMsgHandler()

    this.websocket = null
    this.retryCount = 0
    this.totalRetryCount = 0
    this.isDestroying = false
    this.receiveTimeoutTimerId = null
  }

  start() {
    this.wsConnect()
  }

  stop() {
    this.isDestroying = true
    if (this.websocket) {
      this.websocket.close()
    }
  }

  addDebugMsg(content) {
    this.msgHandler.onDebugMsg(new chatModels.DebugMsg({ content }))
  }

  wsConnect() {
    if (this.isDestroying) {
      return
    }

    this.addDebugMsg('Connecting')

    let baseUrl = getBaseUrl()
    if (baseUrl === null) {
      this.addDebugMsg('No available endpoint')
      window.setTimeout(() => this.onWsClose(), 0)
      return
    }
    let url = baseUrl.replace(/^http(s?):/, 'ws$1:')
    url += '/api/chat'

    this.websocket = new WebSocket(url)
    this.websocket.onopen = this.onWsOpen.bind(this)
    this.websocket.onclose = this.onWsClose.bind(this)
    this.websocket.onmessage = this.onWsMessage.bind(this)
  }

  onWsOpen() {
    this.addDebugMsg('Connected and authenticating')

    this.websocket.send(JSON.stringify({
      cmd: COMMAND_JOIN_ROOM,
      data: {
        roomKey: this.roomKey,
        config: {
          autoTranslate: this.autoTranslate
        }
      }
    }))
    this.refreshReceiveTimeoutTimer()
  }

  refreshReceiveTimeoutTimer() {
    if (this.receiveTimeoutTimerId) {
      window.clearTimeout(this.receiveTimeoutTimerId)
    }
    this.receiveTimeoutTimerId = window.setTimeout(this.onReceiveTimeout.bind(this), RECEIVE_TIMEOUT)
  }

  onReceiveTimeout() {
    this.receiveTimeoutTimerId = null
    console.warn('接收消息超时')
    this.addDebugMsg('Receiving message timed out')

    if (this.websocket) {
      if (this.websocket.onclose) {
        window.setTimeout(() => this.onWsClose(), 0)
      }
      // 直接丢弃阻塞的websocket，不等onclose回调了
      this.websocket.onopen = this.websocket.onclose = this.websocket.onmessage = null
      this.websocket.close()
    }
  }

  onWsClose() {
    this.addDebugMsg('Disconnected')

    this.websocket = null
    if (this.receiveTimeoutTimerId) {
      window.clearTimeout(this.receiveTimeoutTimerId)
      this.receiveTimeoutTimerId = null
    }

    if (this.isDestroying) {
      return
    }
    this.retryCount++
    this.totalRetryCount++
    console.warn(`掉线重连中 retryCount=${this.retryCount}, totalRetryCount=${this.totalRetryCount}`)

    // 防止无限重连的保险措施。30次重连大概会断线500秒，应该够了
    if (this.totalRetryCount > 30) {
      this.stop()
      let error = new chatModels.ChatClientFatalError(
        chatModels.FATAL_ERROR_TYPE_TOO_MANY_RETRIES, 'The connection has lost too many times'
      )
      this.msgHandler.onFatalError(error)
      return
    }

    this.addDebugMsg('Scheduling reconnection')

    // 这边不用判断页面是否可见，因为发心跳包不是由定时器触发的，即使是不活动页面也不会心跳超时
    window.setTimeout(this.wsConnect.bind(this), this.getReconnectInterval())
  }

  getReconnectInterval() {
    // 不用retryCount了，防止意外的连接成功，导致retryCount重置
    let interval = Math.min(1000 + ((this.totalRetryCount - 1) * 2000), 20 * 1000)
    // 加上随机延迟，防止同时请求导致雪崩
    interval += Math.random() * 3000
    return interval
  }

  onWsMessage(event) {
    let { cmd, data } = JSON.parse(event.data)
    switch (cmd) {
    case COMMAND_HEARTBEAT: {
      this.refreshReceiveTimeoutTimer()

      // 不能由定时器触发发心跳包，因为浏览器会把不活动页面的定时器调到1分钟以上
      this.websocket.send(JSON.stringify({
        cmd: COMMAND_HEARTBEAT
      }))
      break
    }
    case COMMAND_ADD_TEXT: {
      let emoticon = null
      let contentType = data[13]
      let contentTypeParams = data[14]
      if (contentType === CONTENT_TYPE_EMOTICON) {
        emoticon = contentTypeParams[0]
      }

      let content = data[4]
      data = new chatModels.AddTextMsg({
        avatarUrl: data[0],
        timestamp: data[1],
        authorName: data[2],
        authorType: data[3],
        content: content,
        privilegeType: data[5],
        isGiftDanmaku: Boolean(data[6]) || chat.isGiftDanmakuByContent(content),
        authorLevel: data[7],
        isNewbie: Boolean(data[8]),
        isMobileVerified: Boolean(data[9]),
        medalLevel: data[10],
        id: data[11],
        translation: data[12],
        emoticon: emoticon,
        uid: data[16],
        medalName: data[17],
      })
      this.msgHandler.onAddText(data)
      break
    }
    case COMMAND_ADD_GIFT: {
      data = new chatModels.AddGiftMsg(data)
      this.msgHandler.onAddGift(data)
      break
    }
    case COMMAND_ADD_MEMBER: {
      data = new chatModels.AddMemberMsg(data)
      this.msgHandler.onAddMember(data)
      break
    }
    case COMMAND_ADD_SUPER_CHAT: {
      data = new chatModels.AddSuperChatMsg(data)
      this.msgHandler.onAddSuperChat(data)
      break
    }
    case COMMAND_DEL_SUPER_CHAT: {
      data = new chatModels.DelSuperChatMsg(data)
      this.msgHandler.onDelSuperChat(data)
      break
    }
    case COMMAND_UPDATE_TRANSLATION: {
      data = new chatModels.UpdateTranslationMsg({
        id: data[0],
        translation: data[1]
      })
      this.msgHandler.onUpdateTranslation(data)
      break
    }
    case COMMAND_FATAL_ERROR: {
      this.stop()
      let error = new chatModels.ChatClientFatalError(data.type, data.msg)
      this.msgHandler.onFatalError(error)
      break
    }
    }

    // 至少成功处理1条消息
    if (cmd !== COMMAND_FATAL_ERROR) {
      this.retryCount = 0
    }
  }
}
