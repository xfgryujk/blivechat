<template>
  <yt-live-chat-renderer>
    <!-- <yt-live-chat-ticker-renderer>
      <yt-live-chat-ticker-paid-message-item-renderer style="background-color: rgba(0,184,212,1);">
        <div id="content">
          <span id="fake-avatar"></span>
          <span>$5.00</span>
        </div>
      </yt-live-chat-ticker-paid-message-item-renderer>
      <yt-live-chat-ticker-paid-message-item-renderer style="background-color: rgba(208,0,0,1);">
        <div id="content">
          <span id="fake-avatar"></span>
          <span>$500.00</span>
        </div>
      </yt-live-chat-ticker-paid-message-item-renderer>
    </yt-live-chat-ticker-renderer> -->
    <yt-live-chat-item-list-renderer>
      <template v-for="message in messages">
        <text-message :key="message.id" v-if="message.type == 0"
          :avatarUrl="message.avatarUrl" :time="message.time" :authorName="message.authorName"
          :authorType="message.authorType" :content="message.content" :repeated="message.repeated"
        ></text-message>
        <legacy-paid-message :key="message.id" v-else-if="message.type == 1"
          :avatarUrl="message.avatarUrl" :title="message.title" :content="message.content"
        ></legacy-paid-message>
        <paid-message :key="message.id" v-else
          :price="message.price" :avatarUrl="message.avatarUrl" :authorName="message.authorName"
          :content="message.content"
        ></paid-message>
      </template>
    </yt-live-chat-item-list-renderer>
  </yt-live-chat-renderer>
</template>

<script>
import config from '@/api/config'
import TextMessage from './TextMessage.vue'
import LegacyPaidMessage from './LegacyPaidMessage.vue'
import PaidMessage from './PaidMessage.vue'

const COMMAND_JOIN_ROOM = 0
const COMMAND_ADD_TEXT = 1
const COMMAND_ADD_GIFT = 2
const COMMAND_ADD_VIP = 3

export default {
  name: 'Room',
  components: {
    TextMessage,
    LegacyPaidMessage,
    PaidMessage
  },
  data() {
    let cfg = {...config.DEFAULT_CONFIG}
    cfg.blockKeywords = cfg.blockKeywords.split('\n').filter(val => val)
    cfg.blockUsers = cfg.blockUsers.split('\n').filter(val => val)
    let styleElement = document.createElement('style')
    styleElement.innerText = cfg.css
    document.head.appendChild(styleElement)
    return {
      config: cfg,
      styleElement,
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
        this.styleElement.innerText = cfg.css
        this.config = cfg
      } catch (e) {
        this.$message.error('获取配置失败：' + e)
      }
    }
  },
  beforeDestroy() {
    document.head.removeChild(this.styleElement)
    this.websocket.close()
  },
  updated() {
    window.scrollTo(0, document.body.scrollHeight)
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
      let body = JSON.parse(event.data)
      let message = null
      let time, price
      switch(body.cmd) {
      case COMMAND_ADD_TEXT:
        if (!this.filterTextMessage(body.data) || this.mergeSimilar(body.data.content)) {
          break
        }
        time = new Date(body.data.timestamp * 1000)
        message = {
          id: this.nextId++,
          type: 0, // TextMessage
          avatarUrl: body.data.avatarUrl,
          time: `${time.getHours()}:${time.getMinutes()}`,
          authorName: body.data.authorName,
          authorType: body.data.authorType,
          content: body.data.content,
          repeated: 1
        }
        break
      case COMMAND_ADD_GIFT:
        price = body.data.totalCoin / 1000
        if (price < this.config.minGiftPrice) // 丢人
          break
        message = {
          id: this.nextId++,
          type: 2, // PaidMessage
          price: price,
          avatarUrl: body.data.avatarUrl,
          authorName: body.data.authorName,
          content: `Sent ${body.data.giftName}x${body.data.giftNum}`
        }
        break
      case COMMAND_ADD_VIP:
        message = {
          id: this.nextId++,
          type: 1, // LegacyPaidMessage
          avatarUrl: body.data.avatarUrl,
          title: 'NEW MEMBER!',
          content: `Welcome ${body.data.authorName}`
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

<style src="@/assets/css/room.css"></style>
