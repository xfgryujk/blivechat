<template>
  <chat-renderer ref="renderer" :css="config.css" :maxNumber="config.maxNumber"></chat-renderer>
</template>

<script>
import config from '@/api/config'
import ChatRenderer from '@/components/ChatRenderer'
import * as constants from '@/components/ChatRenderer/constants'

const COMMAND_HEARTBEAT = 0
const COMMAND_JOIN_ROOM = 1
const COMMAND_ADD_TEXT = 2
const COMMAND_ADD_GIFT = 3
const COMMAND_ADD_MEMBER = 4
const COMMAND_ADD_SUPER_CHAT = 5
const COMMAND_DEL_SUPER_CHAT = 6

export default {
  name: 'Room',
  components: {
    ChatRenderer
  },
  data() {
    return {
      config: {...config.DEFAULT_CONFIG},

      websocket: null,
      retryCount: 0,
      isDestroying: false,
      heartbeatTimerId: null,

      nextId: 0,
    }
  },
  computed: {
    blockKeywords() {
      return this.config.blockKeywords.split('\n').filter(val => val)
    },
    blockUsers() {
      return this.config.blockUsers.split('\n').filter(val => val)
    }
  },
  created() {
    this.wsConnect()
    if (this.$route.query.config_id) {
      this.updateConfig(this.$route.query.config_id)
    }
  },
  beforeDestroy() {
    this.isDestroying = true
    this.websocket.close()
  },
  methods: {
    async updateConfig(configId) {
      try {
        this.config = await config.getRemoteConfig(configId)
      } catch (e) {
        this.$message.error('获取配置失败：' + e)
      }
    },
    wsConnect() {
      const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
      // 开发时使用localhost:12450
      const host = process.env.NODE_ENV === 'development' ? 'localhost:12450' : window.location.host
      const url = `${protocol}://${host}/chat`
      this.websocket = new WebSocket(url)
      this.websocket.onopen = this.onWsOpen
      this.websocket.onclose = this.onWsClose
      this.websocket.onmessage = this.onWsMessage
      this.heartbeatTimerId = window.setInterval(this.sendHeartbeat, 10 * 1000)
    },
    sendHeartbeat() {
      this.websocket.send(JSON.stringify({
        cmd: COMMAND_HEARTBEAT
      }))
    },
    onWsOpen() {
      this.retryCount = 0
      this.websocket.send(JSON.stringify({
        cmd: COMMAND_JOIN_ROOM,
        data: {
          roomId: parseInt(this.$route.params.roomId)
        }
      }))
    },
    onWsClose() {
      if (this.heartbeatTimerId) {
        window.clearInterval(this.heartbeatTimerId)
        this.heartbeatTimerId = null
      }
      if (this.isDestroying) {
        return
      }
      window.console.log(`掉线重连中${++this.retryCount}`)
      this.wsConnect()
    },
    onWsMessage(event) {
      let {cmd, data} = JSON.parse(event.data)
      let message = null
      let time = data.timestamp ? new Date(data.timestamp * 1000) : new Date()
      switch (cmd) {
      case COMMAND_ADD_TEXT:
        if (!this.config.showDanmaku || !this.filterTextMessage(data) || this.mergeSimilar(data.content)) {
          break
        }
        message = {
          id: `text_${this.nextId++}`,
          type: constants.MESSAGE_TYPE_TEXT,
          avatarUrl: data.avatarUrl,
          time: time,
          authorName: data.authorName,
          authorType: data.authorType,
          content: data.content,
          privilegeType: data.privilegeType,
          repeated: 1
        }
        break
      case COMMAND_ADD_GIFT: {
        if (!this.config.showGift) {
          break
        }
        let price = data.totalCoin / 1000
        if (price < this.config.minGiftPrice) { // 丢人
          break
        }
        message = {
          id: `gift_${this.nextId++}`,
          type: constants.MESSAGE_TYPE_SUPER_CHAT,
          avatarUrl: data.avatarUrl,
          authorName: data.authorName,
          price: price,
          time: time,
          content: '' // 有了SC，礼物不需要内容了
        }
        break
      }
      case COMMAND_ADD_MEMBER:
        if (!this.config.showGift || !this.filterSuperChatMessage(data)) {
          break
        }
        message = {
          id: `member_${this.nextId++}`,
          type: constants.MESSAGE_TYPE_MEMBER,
          avatarUrl: data.avatarUrl,
          time: time,
          authorName: data.authorName,
          title: 'NEW MEMBER!',
          content: `Welcome ${data.authorName}!`
        }
        break
      case COMMAND_ADD_SUPER_CHAT:
        if (!this.config.showGift) {
          break
        }
        if (data.price < this.config.minGiftPrice) { // 丢人
          break
        }
        message = {
          id: `sc_${data.id}`,
          type: constants.MESSAGE_TYPE_SUPER_CHAT,
          avatarUrl: data.avatarUrl,
          authorName: data.authorName,
          price: data.price,
          time: time,
          content: data.content
        }
        break
      case COMMAND_DEL_SUPER_CHAT:
        for (let id of data.ids) {
          id = `sc_${id}`
          this.$refs.renderer.delMessage(id)
        }
        break
      }
      if (message) {
        this.$refs.renderer.addMessage(message)
      }
    },
    filterTextMessage(data) {
      if (this.config.blockGiftDanmaku && data.isGiftDanmaku) {
        return false
      } else if (this.config.blockLevel > 0 && data.authorLevel < this.config.blockLevel) {
        return false
      } else if (this.config.blockNewbie && data.isNewbie) {
        return false
      } else if (this.config.blockNotMobileVerified && !data.isMobileVerified) {
        return false
      } else if (this.config.blockMedalLevel > 0 && data.medalLevel < this.config.blockMedalLevel) {
        return false
      }
      return this.filterSuperChatMessage(data)
    },
    filterSuperChatMessage(data) {
      for (let keyword of this.blockKeywords) {
        if (data.content.indexOf(keyword) !== -1) {
          return false
        }
      }
      for (let user of this.blockUsers) {
        if (data.authorName === user) {
          return false
        }
      }
      return true
    },
    mergeSimilar(content) {
      if (!this.config.mergeSimilarDanmaku) {
        return false
      }
      return this.$refs.renderer.mergeSimilar(content)
    }
  }
}
</script>
