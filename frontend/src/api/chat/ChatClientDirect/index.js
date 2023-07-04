import axios from 'axios'

import { BrotliDecode } from './brotli_decode'
import { getUuid4Hex } from '@/utils'
import * as avatar from '../avatar'

const HEADER_SIZE = 16

// const WS_BODY_PROTOCOL_VERSION_NORMAL = 0
// const WS_BODY_PROTOCOL_VERSION_HEARTBEAT = 1
// const WS_BODY_PROTOCOL_VERSION_DEFLATE = 2
const WS_BODY_PROTOCOL_VERSION_BROTLI = 3

// const OP_HANDSHAKE = 0
// const OP_HANDSHAKE_REPLY = 1
const OP_HEARTBEAT = 2
const OP_HEARTBEAT_REPLY = 3
// const OP_SEND_MSG = 4
const OP_SEND_MSG_REPLY = 5
// const OP_DISCONNECT_REPLY = 6
const OP_AUTH = 7
const OP_AUTH_REPLY = 8
// const OP_RAW = 9
// const OP_PROTO_READY = 10
// const OP_PROTO_FINISH = 11
// const OP_CHANGE_ROOM = 12
// const OP_CHANGE_ROOM_REPLY = 13
// const OP_REGISTER = 14
// const OP_REGISTER_REPLY = 15
// const OP_UNREGISTER = 16
// const OP_UNREGISTER_REPLY = 17
// B站业务自定义OP
// const MinBusinessOp = 1000
// const MaxBusinessOp = 10000

const AUTH_REPLY_CODE_OK = 0
// const AUTH_REPLY_CODE_TOKEN_ERROR = -101

const HEARTBEAT_INTERVAL = 10 * 1000
const RECEIVE_TIMEOUT = HEARTBEAT_INTERVAL + (5 * 1000)

let textEncoder = new TextEncoder()
let textDecoder = new TextDecoder()

export default class ChatClientDirect {
  constructor(roomId) {
    // 调用initRoom后初始化，如果失败，使用这里的默认值
    this.roomId = roomId
    this.roomOwnerUid = 0
    this.hostServerList = [
      { host: "broadcastlv.chat.bilibili.com", port: 2243, wss_port: 443, ws_port: 2244 }
    ]

    this.onAddText = null
    this.onAddGift = null
    this.onAddMember = null
    this.onAddSuperChat = null
    this.onDelSuperChat = null
    this.onUpdateTranslation = null

    this.websocket = null
    this.retryCount = 0
    this.isDestroying = false
    this.heartbeatTimerId = null
    this.receiveTimeoutTimerId = null
  }

  async start() {
    await this.initRoom()
    this.wsConnect()
  }

  stop() {
    this.isDestroying = true
    if (this.websocket) {
      this.websocket.close()
    }
  }

  async initRoom() {
    let res
    try {
      res = (await axios.get('/api/room_info', { params: {
        roomId: this.roomId
      } })).data
    } catch {
      return
    }
    this.roomId = res.roomId
    this.roomOwnerUid = res.ownerUid
    if (res.hostServerList.length !== 0) {
      this.hostServerList = res.hostServerList
    }
  }

  makePacket(data, operation) {
    let body = textEncoder.encode(JSON.stringify(data))
    let header = new ArrayBuffer(HEADER_SIZE)
    let headerView = new DataView(header)
    headerView.setUint32(0, HEADER_SIZE + body.byteLength)   // pack_len
    headerView.setUint16(4, HEADER_SIZE)                     // raw_header_size
    headerView.setUint16(6, 1)                               // ver
    headerView.setUint32(8, operation)                       // operation
    headerView.setUint32(12, 1)                              // seq_id
    return new Blob([header, body])
  }

  sendAuth() {
    let authParams = {
      uid: this.roomOwnerUid,
      roomid: this.roomId,
      protover: 3,
      platform: 'danmuji',
      type: 2
    }
    this.websocket.send(this.makePacket(authParams, OP_AUTH))
  }

  wsConnect() {
    if (this.isDestroying) {
      return
    }
    let hostServer = this.hostServerList[this.retryCount % this.hostServerList.length]
    const url = `wss://${hostServer.host}:${hostServer.wss_port}/sub`
    this.websocket = new WebSocket(url)
    this.websocket.binaryType = 'arraybuffer'
    this.websocket.onopen = this.onWsOpen.bind(this)
    this.websocket.onclose = this.onWsClose.bind(this)
    this.websocket.onmessage = this.onWsMessage.bind(this)
  }

  onWsOpen() {
    this.sendAuth()
    this.heartbeatTimerId = window.setInterval(this.sendHeartbeat.bind(this), HEARTBEAT_INTERVAL)
    this.refreshReceiveTimeoutTimer()
  }

  sendHeartbeat() {
    this.websocket.send(this.makePacket({}, OP_HEARTBEAT))
  }

  refreshReceiveTimeoutTimer() {
    if (this.receiveTimeoutTimerId) {
      window.clearTimeout(this.receiveTimeoutTimerId)
    }
    this.receiveTimeoutTimerId = window.setTimeout(this.onReceiveTimeout.bind(this), RECEIVE_TIMEOUT)
  }

  onReceiveTimeout() {
    console.warn('接收消息超时')
    this.discardWebsocket()
  }

  discardWebsocket() {
    if (this.receiveTimeoutTimerId) {
      window.clearTimeout(this.receiveTimeoutTimerId)
      this.receiveTimeoutTimerId = null
    }

    // 直接丢弃阻塞的websocket，不等onclose回调了
    this.websocket.onopen = this.websocket.onclose = this.websocket.onmessage = null
    this.websocket.close()
    this.onWsClose()
  }

  onWsClose() {
    this.websocket = null
    if (this.heartbeatTimerId) {
      window.clearInterval(this.heartbeatTimerId)
      this.heartbeatTimerId = null
    }
    if (this.receiveTimeoutTimerId) {
      window.clearTimeout(this.receiveTimeoutTimerId)
      this.receiveTimeoutTimerId = null
    }

    if (this.isDestroying) {
      return
    }
    this.retryCount++
    console.warn('掉线重连中', this.retryCount)
    window.setTimeout(this.wsConnect.bind(this), 1000)
  }

  onWsMessage(event) {
    this.refreshReceiveTimeoutTimer()
    if (!(event.data instanceof ArrayBuffer)) {
      console.warn('未知的websocket消息类型，data=', event.data)
      return
    }

    let data = new Uint8Array(event.data)
    this.parseWsMessage(data)

    // 至少成功处理1条消息
    this.retryCount = 0
  }

  parseWsMessage(data) {
    let offset = 0
    let dataView = new DataView(data.buffer)
    let packLen = dataView.getUint32(0)
    let rawHeaderSize = dataView.getUint16(4)
    // let ver = dataView.getUint16(6)
    let operation = dataView.getUint32(8)
    // let seqId = dataView.getUint32(12)

    switch (operation) {
    case OP_AUTH_REPLY:
    case OP_SEND_MSG_REPLY: {
      // 业务消息，可能有多个包一起发，需要分包
      while (true) { // eslint-disable-line no-constant-condition
        let body = new Uint8Array(data.buffer, offset + rawHeaderSize, packLen - rawHeaderSize)
        this.parseBusinessMessage(dataView, body)

        offset += packLen
        if (offset >= data.byteLength) {
          break
        }

        dataView = new DataView(data.buffer, offset)
        packLen = dataView.getUint32(0)
        rawHeaderSize = dataView.getUint16(4)
      }
      break
    }
    case OP_HEARTBEAT_REPLY: {
      // 服务器心跳包，包含人气值，这里没用
      break
    }
    default: {
      // 未知消息
      let body = new Uint8Array(data.buffer, offset + rawHeaderSize, packLen - rawHeaderSize)
      console.warn('未知包类型，operation=', operation, dataView, body)
      break
    }
    }
  }

  parseBusinessMessage(dataView, body) {
    let ver = dataView.getUint16(6)
    let operation = dataView.getUint32(8)

    switch (operation) {
    case OP_SEND_MSG_REPLY: {
      // 业务消息
      if (ver == WS_BODY_PROTOCOL_VERSION_BROTLI) {
        // 压缩过的先解压
        body = BrotliDecode(body)
        this.parseWsMessage(body)
      } else {
        // 没压缩过的直接反序列化
        if (body.length !== 0) {
          try {
            body = JSON.parse(textDecoder.decode(body))
            this.handlerCommand(body)
          } catch (e) {
            console.error('body=', body)
            throw e
          }
        }
      }
      break
    }
    case OP_AUTH_REPLY: {
      // 认证响应
      body = JSON.parse(textDecoder.decode(body))
      if (body.code !== AUTH_REPLY_CODE_OK) {
        console.error('认证响应错误，body=', body)
        // 这里应该重新获取token再重连的，但前端没有用到token，所以不重新init了
        this.discardWebsocket()
        throw new Error('认证响应错误')
      }
      this.sendHeartbeat()
      break
    }
    default: {
      // 未知消息
      console.warn('未知包类型，operation=', operation, dataView, body)
      break
    }
    }
  }

  handlerCommand(command) {
    let cmd = command.cmd || ''
    let pos = cmd.indexOf(':')
    if (pos != -1) {
      cmd = cmd.substr(0, pos)
    }
    let callback = CMD_CALLBACK_MAP[cmd]
    if (callback) {
      callback.call(this, command)
    }
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
      avatarUrl: await avatar.getAvatarUrl(uid),
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
      emoticon: info[0][13].url || null
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
      avatarUrl: avatar.processAvatarUrl(data.face),
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
      avatarUrl: await avatar.getAvatarUrl(data.uid),
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
      avatarUrl: avatar.processAvatarUrl(data.user_info.face),
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
  DANMU_MSG: ChatClientDirect.prototype.danmuMsgCallback,
  SEND_GIFT: ChatClientDirect.prototype.sendGiftCallback,
  GUARD_BUY: ChatClientDirect.prototype.guardBuyCallback,
  SUPER_CHAT_MESSAGE: ChatClientDirect.prototype.superChatMessageCallback,
  SUPER_CHAT_MESSAGE_DELETE: ChatClientDirect.prototype.superChatMessageDeleteCallback
}
