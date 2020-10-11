const COMMAND_HEARTBEAT = 0
const COMMAND_JOIN_ROOM = 1
const COMMAND_ADD_TEXT = 2
const COMMAND_ADD_GIFT = 3
const COMMAND_ADD_MEMBER = 4
const COMMAND_ADD_SUPER_CHAT = 5
const COMMAND_DEL_SUPER_CHAT = 6
const COMMAND_UPDATE_TRANSLATION = 7

export default class ChatClientRelay {
  constructor (roomId, autoTranslate) {
    this.roomId = roomId
    this.autoTranslate = autoTranslate

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
  }

  start () {
    this.wsConnect()
  }

  stop () {
    this.isDestroying = true
    if (this.websocket) {
      this.websocket.close()
    }
  }

  wsConnect () {
    if (this.isDestroying) {
      return
    }
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
    // 开发时使用localhost:12450
    const host = process.env.NODE_ENV === 'development' ? 'localhost:12450' : window.location.host
    const url = `${protocol}://${host}/api/chat`
    this.websocket = new WebSocket(url)
    this.websocket.onopen = this.onWsOpen.bind(this)
    this.websocket.onclose = this.onWsClose.bind(this)
    this.websocket.onmessage = this.onWsMessage.bind(this)
    this.heartbeatTimerId = window.setInterval(this.sendHeartbeat.bind(this), 10 * 1000)
  }

  sendHeartbeat () {
    this.websocket.send(JSON.stringify({
      cmd: COMMAND_HEARTBEAT
    }))
  }

  onWsOpen () {
    this.retryCount = 0
    this.websocket.send(JSON.stringify({
      cmd: COMMAND_JOIN_ROOM,
      data: {
        roomId: this.roomId,
        config: {
          autoTranslate: this.autoTranslate
        }
      }
    }))
  }

  onWsClose () {
    this.websocket = null
    if (this.heartbeatTimerId) {
      window.clearInterval(this.heartbeatTimerId)
      this.heartbeatTimerId = null
    }
    if (this.isDestroying) {
      return
    }
    window.console.log(`掉线重连中${++this.retryCount}`)
    window.setTimeout(this.wsConnect.bind(this), 1000)
  }

  onWsMessage (event) {
    let {cmd, data} = JSON.parse(event.data)
    switch (cmd) {
    case COMMAND_ADD_TEXT: {
      if (!this.onAddText) {
        break
      }
      data = {
        avatarUrl: data[0],
        timestamp: data[1],
        authorName: data[2],
        authorType: data[3],
        content: data[4],
        privilegeType: data[5],
        isGiftDanmaku: !!data[6],
        authorLevel: data[7],
        isNewbie: !!data[8],
        isMobileVerified: !!data[9],
        medalLevel: data[10],
        id: data[11],
        translation: data[12]
      }
      this.onAddText(data)
      break
    }
    case COMMAND_ADD_GIFT: {
      if (this.onAddGift) {
        this.onAddGift(data)
      }
      break
    }
    case COMMAND_ADD_MEMBER: {
      if (this.onAddMember) {
        this.onAddMember(data)
      }
      break
    }
    case COMMAND_ADD_SUPER_CHAT: {
      if (this.onAddSuperChat) {
        this.onAddSuperChat(data)
      }
      break
    }
    case COMMAND_DEL_SUPER_CHAT: {
      if (this.onDelSuperChat) {
        this.onDelSuperChat(data)
      }
      break
    }
    case COMMAND_UPDATE_TRANSLATION: {
      if (!this.onUpdateTranslation) {
        break
      }
      data = {
        id: data[0],
        translation: data[1]
      }
      this.onUpdateTranslation(data)
      break
    }
    }
  }
}
