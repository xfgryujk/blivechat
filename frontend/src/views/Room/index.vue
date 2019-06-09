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
          :authorType="message.authorType" :content="message.content"
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
    return {
      websocket: null,
      messages: [],
      nextId: 0
    }
  },
  created() {
    // 开发时使用localhost:80
    const url = process.env.NODE_ENV === 'development' ? 'ws://localhost/chat' : `ws://${window.location.host}/chat`
    this.websocket = new WebSocket(url)
    this.websocket.onopen = () => this.websocket.send(JSON.stringify({
      cmd: COMMAND_JOIN_ROOM,
      data: {
        roomId: parseInt(this.$route.params.roomId)
      }
    }))
    this.websocket.onmessage = (event) => {
      let body = JSON.parse(event.data)
      let message = null
      let time, price
      switch(body.cmd) {
      case COMMAND_ADD_TEXT:
        time = new Date(body.data.timestamp * 1000)
        message = {
          id: this.nextId++,
          type: 0, // TextMessage
          avatarUrl: body.data.avatarUrl,
          time: `${time.getHours()}:${time.getMinutes()}`,
          authorName: body.data.authorName,
          authorType: body.data.authorType,
          content: body.data.content
        }
        break
      case COMMAND_ADD_GIFT:
        price = body.data.totalCoin / 1000
        if (price < 6.911) // 丢人
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
        if (this.messages.length > 50)
          this.messages.shift()
      }
    }
  },
  beforeDestroy() {
    this.websocket.close()
  },
  updated() {
      window.scrollTo(0, document.body.scrollHeight)
  }
}
</script>

<style src="../../assets/room.css"></style>
