<template>
  <chat-renderer :messages="messages" :css="config.css"></chat-renderer>
</template>

<script>
import config from '@/api/config'
import ChatRenderer from '@/components/ChatRenderer'

const COMMAND_JOIN_ROOM = 0
const COMMAND_ADD_TEXT = 1
const COMMAND_ADD_GIFT = 2
const COMMAND_ADD_MEMBER = 3

export default {
  name: 'Room',
  components: {
    ChatRenderer
  },
  data() {
    let cfg = {...config.DEFAULT_CONFIG}
    cfg.blockKeywords = cfg.blockKeywords.split('\n').filter(val => val)
    cfg.blockUsers = cfg.blockUsers.split('\n').filter(val => val)
    return {
      config: cfg,
      websocket: null,
      messages: [],
      nextId: 0
    }
  },
  async created() {
    // 开发时使用localhost:80
    const url = process.env.NODE_ENV === 'development' ? 'ws://localhost/chat' : `ws://${window.location.host}/chat`
    this.websocket = new WebSocket(url)
    this.websocket.onopen = this.onWsOpen.bind(this)
    this.websocket.onmessage = this.onWsMessage.bind(this)

    if (this.$route.query.config_id) {
      try {
        let cfg = await config.getRemoteConfig(this.$route.query.config_id)
        cfg.blockKeywords = cfg.blockKeywords.split('\n').filter(val => val)
        cfg.blockUsers = cfg.blockUsers.split('\n').filter(val => val)
        this.config = cfg
      } catch (e) {
        this.$message.error('获取配置失败：' + e)
      }
    }
  },
  beforeDestroy() {
    this.websocket.close()
  },
  methods: {
    onWsOpen() {
      this.websocket.send(JSON.stringify({
        cmd: COMMAND_JOIN_ROOM,
        data: {
          roomId: parseInt(this.$route.params.roomId)
        }
      }))
    },
    onWsMessage(event) {
      let {cmd, data} = JSON.parse(event.data)
      let message = null
      let time = data.timestamp ? new Date(data.timestamp * 1000) : new Date()
      switch(cmd) {
      case COMMAND_ADD_TEXT:
        if (!this.filterTextMessage(data) || this.mergeSimilar(data.content)) {
          break
        }
        message = {
          id: this.nextId++,
          type: 0, // TextMessage
          avatarUrl: data.avatarUrl,
          time: `${time.getMinutes()}:${time.getSeconds()}`,
          authorName: data.authorName,
          authorType: data.authorType,
          content: data.content,
          privilegeType: data.privilegeType,
          repeated: 1
        }
        break
      case COMMAND_ADD_GIFT: {
        let price = data.totalCoin / 1000
        if (price < this.config.minGiftPrice) // 丢人
          break
        message = {
          id: this.nextId++,
          type: 2, // PaidMessage
          avatarUrl: data.avatarUrl,
          authorName: data.authorName,
          price: price,
          time: `${time.getMinutes()}:${time.getSeconds()}`,
          content: `Sent ${data.giftName}x${data.giftNum}`
        }
        break
      }
      case COMMAND_ADD_MEMBER:
        message = {
          id: this.nextId++,
          type: 1, // LegacyPaidMessage
          avatarUrl: data.avatarUrl,
          time: `${time.getMinutes()}:${time.getSeconds()}`,
          authorName: data.authorName,
          title: 'NEW MEMBER!',
          content: `Welcome ${data.authorName}`
        }
        break
      }
      if (message) {
        this.messages.push(message)
        if (this.messages.length > 50) {
          this.messages.splice(0, this.messages.length - 50)
        }
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
      }
      for (let keyword of this.config.blockKeywords) {
        if (data.content.indexOf(keyword) !== -1) {
          return false
        }
      }
      for (let user of this.config.blockUsers) {
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
      for (let i = this.messages.length - 1; i >= 0 && i >= this.messages.length - 5; i--) {
        let message = this.messages[i]
        if (
          (message.content.indexOf(content) !== -1 || content.indexOf(message.content) !== -1) // 包含对方
          && Math.abs(message.content.length - content.length) < Math.min(message.content.length, content.length) // 长度差比两者长度都小
        ) {
          message.repeated++
          return true
        }
      }
      return false
    }
  }
}
</script>
