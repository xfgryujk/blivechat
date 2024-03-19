import { BrotliDecode } from './brotli_decode'
import { inflate } from 'pako'

import * as chat from '..'
import * as chatModels from '../models'

const HEADER_SIZE = 16

export const WS_BODY_PROTOCOL_VERSION_NORMAL = 0
export const WS_BODY_PROTOCOL_VERSION_HEARTBEAT = 1
export const WS_BODY_PROTOCOL_VERSION_DEFLATE = 2
export const WS_BODY_PROTOCOL_VERSION_BROTLI = 3

export const OP_HANDSHAKE = 0
export const OP_HANDSHAKE_REPLY = 1
export const OP_HEARTBEAT = 2
export const OP_HEARTBEAT_REPLY = 3
export const OP_SEND_MSG = 4
export const OP_SEND_MSG_REPLY = 5
export const OP_DISCONNECT_REPLY = 6
export const OP_AUTH = 7
export const OP_AUTH_REPLY = 8
export const OP_RAW = 9
export const OP_PROTO_READY = 10
export const OP_PROTO_FINISH = 11
export const OP_CHANGE_ROOM = 12
export const OP_CHANGE_ROOM_REPLY = 13
export const OP_REGISTER = 14
export const OP_REGISTER_REPLY = 15
export const OP_UNREGISTER = 16
export const OP_UNREGISTER_REPLY = 17
// B站业务自定义OP
// export const MinBusinessOp = 1000
// export const MaxBusinessOp = 10000

export const AUTH_REPLY_CODE_OK = 0
export const AUTH_REPLY_CODE_TOKEN_ERROR = -101

const HEARTBEAT_INTERVAL = 10 * 1000
const RECEIVE_TIMEOUT = HEARTBEAT_INTERVAL + (5 * 1000)

let textEncoder = new TextEncoder()
let textDecoder = new TextDecoder()

export default class ChatClientOfficialBase {
  constructor() {
    this.CMD_CALLBACK_MAP = {}

    this.msgHandler = chat.getDefaultMsgHandler()

    this.needInitRoom = true
    this.websocket = null
    this.retryCount = 0
    this.totalRetryCount = 0
    this.isDestroying = false
    this.heartbeatTimerId = null
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

  async initRoom() {
    throw Error('Not implemented')
  }

  makePacket(data, operation) {
    if (typeof data === 'object') {
      data = JSON.stringify(data)
    }
    let bodyArr = textEncoder.encode(data)

    let headerBuf = new ArrayBuffer(HEADER_SIZE)
    let headerView = new DataView(headerBuf)
    headerView.setUint32(0, HEADER_SIZE + bodyArr.byteLength)  // pack_len
    headerView.setUint16(4, HEADER_SIZE)                       // raw_header_size
    headerView.setUint16(6, 1)                                 // ver
    headerView.setUint32(8, operation)                         // operation
    headerView.setUint32(12, 1)                                // seq_id

    // 这里如果直接返回 new Blob([headerBuf, bodyArr])，在Chrome抓包会显示空包，实际上是有数据的，为了调试体验最好还是拷贝一遍
    let headerArr = new Uint8Array(headerBuf)
    let packetArr = new Uint8Array(bodyArr.length + headerArr.length)
    packetArr.set(headerArr)
    packetArr.set(bodyArr, headerArr.length)
    return packetArr
  }

  sendAuth() {
    throw Error('Not implemented')
  }

  async wsConnect() {
    if (this.isDestroying) {
      return
    }

    await this.onBeforeWsConnect()
    if (this.isDestroying) {
      return
    }

    this.websocket = new WebSocket(this.getWsUrl())
    this.websocket.binaryType = 'arraybuffer'
    this.websocket.onopen = this.onWsOpen.bind(this)
    this.websocket.onclose = this.onWsClose.bind(this)
    this.websocket.onmessage = this.onWsMessage.bind(this)
  }

  async onBeforeWsConnect() {
    if (!this.needInitRoom) {
      return
    }

    let res
    try {
      res = await this.initRoom()
    } catch (e) {
      res = false
      console.error('initRoom exception:', e)
      if (e instanceof chatModels.ChatClientFatalError) {
        this.stop()
        this.msgHandler.onFatalError(e)
      }
    }

    if (!res) {
      this.onWsClose()
      throw Error('initRoom failed')
    }
    this.needInitRoom = false
  }

  getWsUrl() {
    throw Error('Not implemented')
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

    this.delayReconnect()
  }

  delayReconnect() {
    if (document.visibilityState === 'visible') {
      window.setTimeout(this.wsConnect.bind(this), this.getReconnectInterval())
      return
    }

    // 页面不可见就先不重连了，即使重连也会心跳超时
    let listener = () => {
      if (document.visibilityState !== 'visible') {
        return
      }
      document.removeEventListener('visibilitychange', listener)
      this.wsConnect()
    }
    document.addEventListener('visibilitychange', listener)
  }

  getReconnectInterval() {
    // 不用retryCount了，防止意外的连接成功，导致retryCount重置
    let interval = Math.min(1000 + ((this.totalRetryCount - 1) * 2000), 20 * 1000)
    // 加上随机延迟，防止同时请求导致雪崩
    interval += Math.random() * 3000
    return interval
  }

  onWsMessage(event) {
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
      this.refreshReceiveTimeoutTimer()
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
      } else if (ver == WS_BODY_PROTOCOL_VERSION_DEFLATE) {
        // web端已经不用zlib压缩了，但是开放平台会用
        body = inflate(body)
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
        this.needInitRoom = true
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
    let callback = this.CMD_CALLBACK_MAP[cmd]
    if (callback) {
      callback.call(this, command)
    }
  }
}
