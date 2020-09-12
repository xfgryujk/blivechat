<template>
  <yt-live-chat-ticker-renderer>
    <div id="container" dir="ltr" class="style-scope yt-live-chat-ticker-renderer">
      <div id="items" class="style-scope yt-live-chat-ticker-renderer">
        <template v-for="message in messages">
          <yt-live-chat-ticker-paid-message-item-renderer :key="message.id" v-if="needToShow(message)"
            tabindex="0" class="style-scope yt-live-chat-ticker-renderer" style="overflow: hidden;"
            @click="onItemClick(message)"
          >
            <div id="container" dir="ltr" class="style-scope yt-live-chat-ticker-paid-message-item-renderer"
              :style="{
                background: getBgColor(message),
              }"
            >
              <div id="content" class="style-scope yt-live-chat-ticker-paid-message-item-renderer" :style="{
                color: getColor(message)
              }">
                <img-shadow id="author-photo" height="24" width="24" class="style-scope yt-live-chat-ticker-paid-message-item-renderer"
                  :imgUrl="message.avatarUrl"
                ></img-shadow>
                <span id="text" dir="ltr" class="style-scope yt-live-chat-ticker-paid-message-item-renderer">{{getText(message)}}</span>
              </div>
            </div>
          </yt-live-chat-ticker-paid-message-item-renderer>
        </template>
      </div>
    </div>
    <template v-if="pinnedMessage">
      <membership-item :key="pinnedMessage.id" v-if="pinnedMessage.type === MESSAGE_TYPE_MEMBER"
        class="style-scope yt-live-chat-ticker-renderer"
        :avatarUrl="pinnedMessage.avatarUrl" :authorName="pinnedMessage.authorName" :privilegeType="pinnedMessage.privilegeType"
        :title="pinnedMessage.title" :time="pinnedMessage.time"
      ></membership-item>
      <paid-message :key="pinnedMessage.id" v-else
        class="style-scope yt-live-chat-ticker-renderer"
        :price="pinnedMessage.price" :avatarUrl="pinnedMessage.avatarUrl" :authorName="pinnedMessage.authorName"
        :time="pinnedMessage.time" :content="showContent"
      ></paid-message>
    </template>
  </yt-live-chat-ticker-renderer>
</template>

<script>
import * as config from '@/api/config'
import {formatCurrency} from '@/utils'
import ImgShadow from './ImgShadow.vue'
import MembershipItem from './MembershipItem.vue'
import PaidMessage from './PaidMessage.vue'
import * as constants from './constants'

export default {
  name: 'Ticker',
  components: {
    ImgShadow,
    MembershipItem,
    PaidMessage
  },
  props: {
    messages: Array,
    showGiftName: {
      type: Boolean,
      default: config.DEFAULT_CONFIG.showGiftName
    }
  },
  data() {
    return {
      MESSAGE_TYPE_MEMBER: constants.MESSAGE_TYPE_MEMBER,

      curTime: new Date(),
      updateTimerId: window.setInterval(this.updateProgress.bind(this), 1000),
      pinnedMessage: null
    }
  },
  computed: {
    showContent() {
      if (!this.pinnedMessage) {
        return ''
      }
      if (this.pinnedMessage.type === constants.MESSAGE_TYPE_GIFT) {
        return constants.getGiftShowContent(this.pinnedMessage, this.showGiftName)
      } else {
        return constants.getShowContent(this.pinnedMessage)
      }
    }
  },
  beforeDestroy() {
    window.clearInterval(this.updateTimerId)
  },
  methods: {
    needToShow(message) {
      let pinTime
      if (message.type === constants.MESSAGE_TYPE_MEMBER) {
        pinTime = 2
      } else {
        let config = constants.getPriceConfig(message.price)
        pinTime = config.pinTime
      }
      return (new Date() - message.addTime) / (60 * 1000) < pinTime
    },
    getBgColor(message) {
      let color1, color2, pinTime
      if (message.type === constants.MESSAGE_TYPE_MEMBER) {
        color1 = 'rgba(15,157,88,1)'
        color2 = 'rgba(11,128,67,1)'
        pinTime = 2
      } else {
        let config = constants.getPriceConfig(message.type === constants.MESSAGE_TYPE_MEMBER ? 28 : message.price)
        color1 = config.colors.contentBg
        color2 = config.colors.headerBg
        pinTime = config.pinTime
      }
      let progress = (1 - (this.curTime - message.addTime) / (60 * 1000) / pinTime) * 100
      if (progress < 0) {
        progress = 0
      } else if (progress > 100) {
        progress = 100
      }
      return `linear-gradient(90deg, ${color1}, ${color1} ${progress}%, ${color2} ${progress}%, ${color2})`
    },
    getColor(message) {
      if (message.type === constants.MESSAGE_TYPE_MEMBER) {
        return 'rgb(255,255,255)'
      }
      return constants.getPriceConfig(message.price).colors.header
    },
    getText(message) {
      if (message.type === constants.MESSAGE_TYPE_MEMBER) {
        return 'Member'
      }
      return 'CN¥' + formatCurrency(message.price)
    },
    updateProgress() {
      this.curTime = new Date()
      for (let i = 0; i < this.messages.length;) {
        let pinTime
        if (this.messages[i].type === constants.MESSAGE_TYPE_MEMBER) {
          pinTime = 2
        } else {
          let config = constants.getPriceConfig(this.messages[i].price)
          pinTime = config.pinTime
        }
        if ((this.curTime - this.messages[i].addTime) / (60 * 1000) >= pinTime) {
          if (this.pinnedMessage == this.messages[i]) {
            this.pinnedMessage = null
          }
          this.messages.splice(i, 1)
        } else {
          i++
        }
      }
    },
    onItemClick(message) {
      if (this.pinnedMessage == message) {
        this.pinnedMessage = null
      } else {
        this.pinnedMessage = message
      }
    }
  }
}
</script>

<style src="@/assets/css/youtube/yt-live-chat-ticker-renderer.css"></style>
<style src="@/assets/css/youtube/yt-live-chat-ticker-paid-message-item-renderer.css"></style>
