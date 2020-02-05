<template>
  <chat-renderer ref="renderer" :maxNumber="config.maxNumber"></chat-renderer>
</template>

<script>
import {mergeConfig, toBool, toInt} from '@/utils'
import * as config from '@/api/config'
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
    this.updateConfig()
  },
  beforeDestroy() {
    this.isDestroying = true
    this.websocket.close()
  },
  methods: {
    updateConfig() {
      let cfg = {}
      // 留空的使用默认值
      for (let i in this.$route.query) {
        if (this.$route.query[i] !== '') {
          cfg[i] = this.$route.query[i]
        }
      }
      cfg = mergeConfig(cfg, config.DEFAULT_CONFIG)

      cfg.minGiftPrice = toInt(cfg.minGiftPrice, config.DEFAULT_CONFIG.minGiftPrice)
      cfg.mergeSimilarDanmaku = toBool(cfg.mergeSimilarDanmaku)
      cfg.showDanmaku = toBool(cfg.showDanmaku)
      cfg.showGift = toBool(cfg.showGift)
      cfg.maxNumber = toInt(cfg.maxNumber, config.DEFAULT_CONFIG.maxNumber)
      cfg.blockGiftDanmaku = toBool(cfg.blockGiftDanmaku)
      cfg.blockLevel = toInt(cfg.blockLevel, config.DEFAULT_CONFIG.blockLevel)
      cfg.blockNewbie = toBool(cfg.blockNewbie)
      cfg.blockNotMobileVerified = toBool(cfg.blockNotMobileVerified)
      cfg.blockMedalLevel = toInt(cfg.blockMedalLevel, config.DEFAULT_CONFIG.blockMedalLevel)

      this.config = cfg
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
      switch (cmd) {
      case COMMAND_ADD_TEXT:
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
          medalLevel: data[10]
        }
        if (!this.config.showDanmaku || !this.filterTextMessage(data) || this.mergeSimilarText(data.content)) {
          break
        }
        message = {
          id: `text_${this.nextId++}`,
          type: constants.MESSAGE_TYPE_TEXT,
          avatarUrl: data.avatarUrl,
          time: new Date(data.timestamp * 1000),
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
        if (this.mergeSimilarGift(data.authorName, price)) {
          break
        }
        message = {
          id: `gift_${this.nextId++}`,
          type: constants.MESSAGE_TYPE_SUPER_CHAT,
          avatarUrl: data.avatarUrl,
          authorName: data.authorName,
          price: price,
          time: new Date(data.timestamp * 1000),
          content: '' // 有了SC，礼物不需要内容了
        }
        break
      }
      case COMMAND_ADD_MEMBER:
        if (!this.config.showGift || !this.filterNewMemberMessage(data)) {
          break
        }
        message = {
          id: `member_${this.nextId++}`,
          type: constants.MESSAGE_TYPE_MEMBER,
          avatarUrl: data.avatarUrl,
          time: new Date(data.timestamp * 1000),
          authorName: data.authorName,
          title: 'NEW MEMBER!',
          content: `Welcome ${data.authorName}!`
        }
        break
      case COMMAND_ADD_SUPER_CHAT:
        if (!this.config.showGift || !this.filterSuperChatMessage(data)) {
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
          time: new Date(data.timestamp * 1000),
          content: data.content.trim()
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
      return this.filterNewMemberMessage(data)
    },
    filterNewMemberMessage(data) {
      for (let user of this.blockUsers) {
        if (data.authorName === user) {
          return false
        }
      }
      return true
    },
    mergeSimilarText(content) {
      if (!this.config.mergeSimilarDanmaku) {
        return false
      }
      return this.$refs.renderer.mergeSimilarText(content)
    },
    mergeSimilarGift(authorName, price) {
      if (!this.config.mergeSimilarDanmaku) {
        return false
      }
      return this.$refs.renderer.mergeSimilarGift(authorName, price)
    }
  }
}
</script>
