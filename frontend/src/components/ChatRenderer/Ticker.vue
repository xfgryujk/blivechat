<template>
  <yt-live-chat-ticker-renderer :hidden="showMessages.length === 0">
    <div id="container" dir="ltr" class="style-scope yt-live-chat-ticker-renderer">
      <transition-group tag="div" :css="false" @enter="onTickerItemEnter" @leave="onTickerItemLeave"
        id="items" class="style-scope yt-live-chat-ticker-renderer"
      >
        <yt-live-chat-ticker-paid-message-item-renderer v-for="message in showMessages" :key="message.raw.id"
          tabindex="0" class="style-scope yt-live-chat-ticker-renderer" style="overflow: hidden;"
          @click="onItemClick(message.raw)"
        >
          <div id="container" dir="ltr" class="style-scope yt-live-chat-ticker-paid-message-item-renderer" :style="{
            background: message.bgColor,
          }">
            <div id="content" class="style-scope yt-live-chat-ticker-paid-message-item-renderer" :style="{
              color: message.color
            }">
              <img-shadow id="author-photo" height="24" width="24" class="style-scope yt-live-chat-ticker-paid-message-item-renderer"
                :imgUrl="message.raw.avatarUrl"
              ></img-shadow>
              <span id="text" dir="ltr" class="style-scope yt-live-chat-ticker-paid-message-item-renderer">{{message.text}}</span>
            </div>
          </div>
        </yt-live-chat-ticker-paid-message-item-renderer>
      </transition-group>
    </div>
    <template v-if="pinnedMessage">
      <membership-item :key="pinnedMessage.id" v-if="pinnedMessage.type === MESSAGE_TYPE_MEMBER"
        class="style-scope yt-live-chat-ticker-renderer"
        :avatarUrl="pinnedMessage.avatarUrl" :authorName="getShowAuthorName(pinnedMessage)" :privilegeType="pinnedMessage.privilegeType"
        :title="pinnedMessage.title" :time="pinnedMessage.time"
      ></membership-item>
      <paid-message :key="pinnedMessage.id" v-else
        class="style-scope yt-live-chat-ticker-renderer"
        :price="pinnedMessage.price" :avatarUrl="pinnedMessage.avatarUrl" :authorName="getShowAuthorName(pinnedMessage)"
        :time="pinnedMessage.time" :content="pinnedMessageShowContent"
      ></paid-message>
    </template>
  </yt-live-chat-ticker-renderer>
</template>

<script>
import * as chatConfig from '@/api/chatConfig'
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
      default: chatConfig.DEFAULT_CONFIG.showGiftName
    }
  },
  data() {
    return {
      MESSAGE_TYPE_MEMBER: constants.MESSAGE_TYPE_MEMBER,

      curTime: new Date(),
      updateTimerId: window.setInterval(this.updateProgress, 1000),
      pinnedMessage: null
    }
  },
  computed: {
    showMessages() {
      let res = []
      for (let message of this.messages) {
        if (!this.needToShow(message)) {
          continue
        }
        res.push({
          raw: message,
          bgColor: this.getBgColor(message),
          color: this.getColor(message),
          text: this.getText(message)
        })
      }
      return res
    },
    pinnedMessageShowContent() {
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
    async onTickerItemEnter(el, done) {
      let width = el.clientWidth
      if (width === 0) {
        // CSS指定了不显示固定栏
        done()
        return
      }
      el.style.width = 0
      await this.$nextTick()
      el.style.width = `${width}px`
      window.setTimeout(done, 200)
    },
    onTickerItemLeave(el, done) {
      el.classList.add('sliding-down')
      window.setTimeout(() => {
        el.classList.add('collapsing')
        el.style.width = 0
        window.setTimeout(() => {
          el.classList.remove('sliding-down')
          el.classList.remove('collapsing')
          el.style.width = 'auto'
          done()
        }, 200)
      }, 200)
    },

    getShowAuthorName: constants.getShowAuthorName,
    needToShow(message) {
      let pinTime = this.getPinTime(message)
      return (new Date() - message.addTime) / (60 * 1000) < pinTime
    },
    getBgColor(message) {
      let color1, color2
      if (message.type === constants.MESSAGE_TYPE_MEMBER) {
        color1 = 'rgba(15,157,88,1)'
        color2 = 'rgba(11,128,67,1)'
      } else {
        let config = constants.getPriceConfig(message.price)
        color1 = config.colors.contentBg
        color2 = config.colors.headerBg
      }
      let pinTime = this.getPinTime(message)
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
    getPinTime(message) {
      if (message.type === constants.MESSAGE_TYPE_MEMBER) {
        return 2
      }
      return constants.getPriceConfig(message.price).pinTime
    },
    updateProgress() {
      this.curTime = new Date()
      for (let i = 0; i < this.messages.length;) {
        let message = this.messages[i]
        let pinTime = this.getPinTime(message)
        if ((this.curTime - message.addTime) / (60 * 1000) >= pinTime) {
          if (this.pinnedMessage == message) {
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
