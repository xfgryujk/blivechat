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
    this.websocket = new WebSocket(`ws://${window.location.host}/chat`)
    // 测试用
    // this.websocket = new WebSocket('ws://localhost/chat')
    this.websocket.onopen = () => this.websocket.send(JSON.stringify({
      cmd: COMMAND_JOIN_ROOM,
      data: {
        roomId: parseInt(this.$route.params.roomId)
      }
    }))
    this.websocket.onmessage = (event) => {
      let body = JSON.parse(event.data)
      let message = null
      let time
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
        break;
      case COMMAND_ADD_GIFT:
        message = {
          id: this.nextId++,
          type: 2, // PaidMessage
          price: body.data.totalCoin / 1000,
          avatarUrl: body.data.avatarUrl,
          authorName: body.data.authorName,
          content: `Sent ${body.data.giftName}x${body.data.giftNum}`
        }
        break;
      case COMMAND_ADD_VIP:
        message = {
          id: this.nextId++,
          type: 1, // LegacyPaidMessage
          avatarUrl: body.data.avatarUrl,
          title: 'NEW MEMBER!',
          content: `Welcome ${body.data.authorName}`
        }
        break;
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

<style>
yt-live-chat-text-message-renderer {
  position: relative;
  display: -ms-flexbox;
  display: -webkit-flex;
  display: flex;
  -ms-flex-direction: row;
  -webkit-flex-direction: row;
  flex-direction: row;
  -ms-flex-align: start;
  -webkit-align-items: flex-start;
  align-items: flex-start;
  padding: 4px 24px;
}

yt-live-chat-text-message-renderer #content {
  -ms-align-self: center;
  -webkit-align-self: center;
  align-self: center;
  overflow: hidden;
}

yt-live-chat-text-message-renderer #timestamp {
  display: none;
  margin-right: 8px;
}

yt-live-chat-text-message-renderer #author-name {
  margin-right: 8px;
  font-weight: 500;
}

yt-live-chat-text-message-renderer #author-photo {
  display: inline-block;
  background-color: transparent;
  -ms-flex: none;
  -webkit-flex: none;
  flex: none;
}

yt-live-chat-text-message-renderer #author-badges {
  vertical-align: text-bottom;
  display: -ms-inline-flexbox;
  display: -webkit-inline-flex;
  display: inline-flex;
}

yt-live-chat-text-message-renderer #message {
  color: #fff;
  font-size: 12px;
  line-height: 16px;
  word-wrap: break-word;
}

yt-live-chat-author-badge-renderer {
  display: block;
  width: 16px;
  height: 16px;
  background-color: currentColor;
  margin-right: 4px;
  border-radius: 16px;
}

yt-live-chat-legacy-paid-message-renderer {
  position: relative;
  overflow: hidden;
  margin: 8px 24px;
  padding: 8px 16px;
  background-color: #0f9d58;
  border-radius: 4px;
  color: #fff;
  font-size: 14px;
  min-height: 40px;
  display: -ms-flexbox;
  display: -webkit-flex;
  display: flex;
  -ms-flex-direction: row;
  -webkit-flex-direction: row;
  flex-direction: row;
  -ms-flex-align: center;
  -webkit-align-items: center;
  align-items: center;
  box-shadow: 0 2px 2px 0 rgba(0, 0, 0, 0.14), 0 1px 5px 0 rgba(0, 0, 0, 0.12), 0 3px 1px -2px rgba(0, 0, 0, 0.2);
}

yt-live-chat-legacy-paid-message-renderer #author-photo {
  background-color: transparent;
  margin-right: 16px;
  overflow: hidden;
  -ms-flex: none;
  -webkit-flex: none;
  flex: none;
  -ms-align-self: flex-start;
  -webkit-align-self: flex-start;
  align-self: flex-start;
}

yt-live-chat-legacy-paid-message-renderer #content {
  -ms-flex: 1 1 0.000000001px;
  -webkit-flex: 1;
  flex: 1;
  -webkit-flex-basis: 0.000000001px;
  flex-basis: 0.000000001px;
}

yt-live-chat-legacy-paid-message-renderer #event-text {
  font-weight: 500;
}

yt-live-chat-legacy-paid-message-renderer #detail-text {
  word-wrap: break-word;
}

yt-live-chat-paid-message-renderer {
  position: relative;
  border-radius: 4px;
  margin: 8px 24px;
  font-size: 15px;
  display: -ms-flexbox;
  display: -webkit-flex;
  display: flex;
  -ms-flex-direction: column;
  -webkit-flex-direction: column;
  flex-direction: column;
  box-shadow: 0 2px 2px 0 rgba(0, 0, 0, 0.14), 0 1px 5px 0 rgba(0, 0, 0, 0.12), 0 3px 1px -2px rgba(0, 0, 0, 0.2);
}

yt-live-chat-paid-message-renderer #header {
  position: relative;
  font-weight: 500;
  padding: 8px 16px;
  min-height: 20px;
  display: -ms-flexbox;
  display: -webkit-flex;
  display: flex;
  -ms-flex-direction: row;
  -webkit-flex-direction: row;
  flex-direction: row;
  -ms-flex-align: center;
  -webkit-align-items: center;
  align-items: center;
  border-top-left-radius: 4px;
  border-top-right-radius: 4px;
}

yt-live-chat-paid-message-renderer #header-content {
  display: -ms-flexbox;
  display: -webkit-flex;
  display: flex;
  -ms-flex-direction: column;
  -webkit-flex-direction: column;
  flex-direction: column;
  -ms-flex-pack: justify;
  -webkit-justify-content: space-between;
  justify-content: space-between;
  -ms-flex: 1 1 0.000000001px;
  -webkit-flex: 1;
  flex: 1;
  -webkit-flex-basis: 0.000000001px;
  flex-basis: 0.000000001px;
}

yt-live-chat-paid-message-renderer #author-photo {
  background-color: transparent;
  -ms-flex: none;
  -webkit-flex: none;
  flex: none;
}

yt-live-chat-paid-message-renderer #author-name {
  font-size: 14px;
}

yt-live-chat-paid-message-renderer #content {
  padding: 4px 16px 8px 16px;
  word-wrap: break-word;
  word-break: break-word;
  border-bottom-left-radius: 4px;
  border-bottom-right-radius: 4px;
}

yt-live-chat-ticker-paid-message-item-renderer {
  display: inline-block;
  height: 24px;
  border-radius: 200px;
  padding: 4px;
}

yt-live-chat-ticker-paid-message-item-renderer #content {
  display: -ms-flexbox;
  display: -webkit-flex;
  display: flex;
  -ms-flex-direction: row;
  -webkit-flex-direction: row;
  flex-direction: row;
  -ms-flex-align: center;
  -webkit-align-items: center;
  align-items: center;
  margin-right: 4px;
}

yt-live-chat-ticker-paid-message-item-renderer #fake-avatar {
  display: inline-block;
  background-color: red;
  width: 24px;
  height: 24px;
  margin-right: 4px;
  border-radius: 24px;

}

/* 以下为自动生成：https://chatv2.septapus.com/ */

/* @import url("https://fonts.googleapis.com/css?family=Changa One"); */
/* @import url("https://fonts.googleapis.com/css?family=Imprima"); */
@import url("https://fonts.lug.ustc.edu.cn/css?family=Changa One");
@import url("https://fonts.lug.ustc.edu.cn/css?family=Imprima");

/* Background colors*/
body {
  overflow: hidden;
  background-color: rgba(0,0,0,0);
}
/* Transparent background. */
yt-live-chat-renderer {
  background-color: transparent !important;
}
yt-live-chat-text-message-renderer,
yt-live-chat-text-message-renderer[is-highlighted] {
  background-color: transparent !important;
}

yt-live-chat-text-message-renderer[author-type="owner"],
yt-live-chat-text-message-renderer[author-type="owner"][is-highlighted] {
  background-color: transparent !important;
}

yt-live-chat-text-message-renderer[author-type="moderator"],
yt-live-chat-text-message-renderer[author-type="moderator"][is-highlighted] {
  background-color: transparent !important;
}

yt-live-chat-text-message-renderer[author-type="member"],
yt-live-chat-text-message-renderer[author-type="member"][is-highlighted] {
  background-color: transparent !important;
}


yt-live-chat-author-chip #author-name {
  background-color: transparent !important;
}
/* Outlines */
yt-live-chat-renderer * {
  text-shadow: -2px -2px #000000,-2px -1px #000000,-2px 0px #000000,-2px 1px #000000,-2px 2px #000000,-1px -2px #000000,-1px -1px #000000,-1px 0px #000000,-1px 1px #000000,-1px 2px #000000,0px -2px #000000,0px -1px #000000,0px 0px #000000,0px 1px #000000,0px 2px #000000,1px -2px #000000,1px -1px #000000,1px 0px #000000,1px 1px #000000,1px 2px #000000,2px -2px #000000,2px -1px #000000,2px 0px #000000,2px 1px #000000,2px 2px #000000;
  font-family: "Imprima";
  font-size: 18px !important;
  line-height: 18px !important;
}

yt-live-chat-text-message-renderer #content,
yt-live-chat-legacy-paid-message-renderer #content {
  overflow: initial !important;
}

/* Hide scrollbar. */
yt-live-chat-item-list-renderer #items{
  overflow: hidden !important;
}

yt-live-chat-item-list-renderer #item-scroller{
  overflow: hidden !important;
}

/* Hide header and input. */
yt-live-chat-header-renderer,
yt-live-chat-message-input-renderer {
  display: none !important;
}

/* Reduce side padding. */
yt-live-chat-text-message-renderer,
yt-live-chat-legacy-paid-message-renderer {
    padding-left: 4px !important;
  padding-right: 4px !important;
}

yt-live-chat-paid-message-renderer #header {
    padding-left: 4px !important;
  padding-right: 4px !important;
}

/* Avatars. */
yt-live-chat-text-message-renderer #author-photo,
yt-live-chat-paid-message-renderer #author-photo,
yt-live-chat-legacy-paid-message-renderer #author-photo {
  
  width: 24px !important;
  height: 24px !important;
  border-radius: 24px !important;
  margin-right: 6px !important;
  background-size: cover;
}

/* Hide badges. */
yt-live-chat-text-message-renderer #author-badges {
  display: none !important;
  vertical-align: text-top !important;
}

/* Timestamps. */
yt-live-chat-text-message-renderer #timestamp {
  
  color: #999999 !important;
  font-family: "Imprima";
  font-size: 16px !important;
  line-height: 16px !important;
}

/* Badges. */
yt-live-chat-text-message-renderer #author-name[type="owner"],
yt-live-chat-text-message-renderer yt-live-chat-author-badge-renderer[type="owner"] {
  color: #ffd600 !important;
}

yt-live-chat-text-message-renderer #author-name[type="moderator"],
yt-live-chat-text-message-renderer yt-live-chat-author-badge-renderer[type="moderator"] {
  color: #5e84f1 !important;
}

yt-live-chat-text-message-renderer #author-name[type="member"],
yt-live-chat-text-message-renderer yt-live-chat-author-badge-renderer[type="member"] {
  color: #0f9d58 !important;
}

/* Channel names. */
yt-live-chat-text-message-renderer #author-name {
  color: #cccccc !important;
  font-family: "Changa One";
  font-size: 20px !important;
  line-height: 20px !important;
}

yt-live-chat-text-message-renderer #author-name::after {
  content: ":";
  margin-left: 2px;
}

/* Messages. */
yt-live-chat-text-message-renderer #message,
yt-live-chat-text-message-renderer #message * {
  color: #ffffff !important;
  font-family: "Imprima";
  font-size: 18px !important;
  line-height: 18px !important;
}


/* SuperChat/Fan Funding Messages. */
yt-live-chat-paid-message-renderer #author-name,
yt-live-chat-paid-message-renderer #author-name *,
yt-live-chat-legacy-paid-message-renderer #event-text,
yt-live-chat-legacy-paid-message-renderer #event-text * {
  color: #ffffff !important;
  font-family: "Changa One";
  font-size: 20px !important;
  line-height: 20px !important;
}

yt-live-chat-paid-message-renderer #purchase-amount,
yt-live-chat-paid-message-renderer #purchase-amount *,
yt-live-chat-legacy-paid-message-renderer #detail-text,
yt-live-chat-legacy-paid-message-renderer #detail-text * {
  color: #ffffff !important;
  font-family: "Imprima";
  font-size: 18px !important;
  line-height: 18px !important;
}

yt-live-chat-paid-message-renderer #content,
yt-live-chat-paid-message-renderer #content * {
  color: #ffffff !important;
  font-family: "Imprima";
  font-size: 18px !important;
  line-height: 18px !important;
}

yt-live-chat-paid-message-renderer {
  margin: 4px 0 !important;
}

yt-live-chat-legacy-paid-message-renderer {
  background-color: #0f9d58 !important;
  margin: 4px 0 !important;
}

yt-live-chat-text-message-renderer a,
yt-live-chat-legacy-paid-message-renderer a {
  text-decoration: none !important;
}

yt-live-chat-text-message-renderer[is-deleted],
yt-live-chat-legacy-paid-message-renderer[is-deleted] {
  display: none !important;
}

yt-live-chat-ticker-renderer {
  background-color: transparent !important;
  box-shadow: none !important;
}
yt-live-chat-ticker-renderer {
  display: none !important;
}


yt-live-chat-ticker-paid-message-item-renderer,
yt-live-chat-ticker-paid-message-item-renderer *,
yt-live-chat-ticker-sponsor-item-renderer,
yt-live-chat-ticker-sponsor-item-renderer * {
  color: #ffffff !important;
  font-family: "Imprima";
}

yt-live-chat-mode-change-message-renderer, 
yt-live-chat-viewer-engagement-message-renderer, 
yt-live-chat-restricted-participation-renderer {
  display: none !important;
}
</style>
