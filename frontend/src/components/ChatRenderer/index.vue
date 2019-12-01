<template>
  <yt-live-chat-renderer class="style-scope yt-live-chat-app" style="--scrollbar-width:11px;" hide-timestamps>
    <ticker class="style-scope yt-live-chat-renderer" :messages="paidMessages" :hidden="paidMessages.length === 0"></ticker>
    <yt-live-chat-item-list-renderer class="style-scope yt-live-chat-renderer" allow-scroll>
      <div id="item-scroller" ref="scroller" class="style-scope yt-live-chat-item-list-renderer animated" @scroll="onScroll">
        <div ref="itemOffset" id="item-offset" class="style-scope yt-live-chat-item-list-renderer" style="height: 0px;">
          <div ref="items" id="items" class="style-scope yt-live-chat-item-list-renderer" style="overflow: hidden"
            :style="{transform: `translateY(${Math.floor(scrollPixelsRemaining)}px)`}"
          >
            <template v-for="message in messages">
              <text-message :key="message.id" v-if="message.type === MESSAGE_TYPE_TEXT"
                class="style-scope yt-live-chat-item-list-renderer"
                :avatarUrl="message.avatarUrl" :time="message.time" :authorName="message.authorName"
                :authorType="message.authorType" :content="message.content" :privilegeType="message.privilegeType"
                :repeated="message.repeated"
              ></text-message>
              <legacy-paid-message :key="message.id" v-else-if="message.type === MESSAGE_TYPE_MEMBER"
                class="style-scope yt-live-chat-item-list-renderer"
                :avatarUrl="message.avatarUrl" :title="message.title" :content="message.content"
                :time="message.time"
              ></legacy-paid-message>
              <paid-message :key="message.id" v-else-if="message.type === MESSAGE_TYPE_SUPER_CHAT"
                class="style-scope yt-live-chat-item-list-renderer"
                :price="message.price" :avatarUrl="message.avatarUrl" :authorName="message.authorName"
                :time="message.time" :content="message.content"
              ></paid-message>
            </template>
          </div>
        </div>
      </div>
    </yt-live-chat-item-list-renderer>
  </yt-live-chat-renderer>
</template>

<script>
import config from '@/api/config'
import Ticker from './Ticker.vue'
import TextMessage from './TextMessage.vue'
import LegacyPaidMessage from './LegacyPaidMessage.vue'
import PaidMessage from './PaidMessage.vue'
import * as constants from './constants'

const CHAT_SMOOTH_ANIMATION_TIME_MS = 84
const SCROLLED_TO_BOTTOM_EPSILON = 15

export default {
  name: 'ChatRenderer',
  components: {
    Ticker,
    TextMessage,
    LegacyPaidMessage,
    PaidMessage
  },
  props: {
    css: String,
    maxNumber: {
      type: Number,
      default: config.DEFAULT_CONFIG.maxNumber
    }
  },
  data() {
    let styleElement = document.createElement('style')
    document.head.appendChild(styleElement)
    return {
      MESSAGE_TYPE_TEXT: constants.MESSAGE_TYPE_TEXT,
      MESSAGE_TYPE_MEMBER: constants.MESSAGE_TYPE_MEMBER,
      MESSAGE_TYPE_SUPER_CHAT: constants.MESSAGE_TYPE_SUPER_CHAT,

      styleElement,
      messages: [],                        // 显示的消息
      paidMessages: [],                    // 固定在上方的消息

      smoothedMessageQueue: [],            // 平滑消息队列，由外部调用addMessages等方法添加
      emitSmoothedMessageTimerId: null,    // 消费平滑消息队列的定时器ID
      enqueueIntervals: [],                // 最近进队列的时间间隔，用来估计下次进队列的时间
      lastEnqueueTime: null,               // 上次进队列的时间
      estimatedEnqueueInterval: null,      // 估计的下次进队列时间间隔

      messagesBuffer: [],                  // 暂时未显示的消息，当不能自动滚动时会积压在这
      preinsertHeight: 0,                  // 插入新消息之前items的高度
      isSmoothed: true,                    // 是否平滑滚动，当消息太快时不平滑滚动
      chatRateMs: 1000,                    // 用来计算消息速度
      scrollPixelsRemaining: 0,            // 平滑滚动剩余像素
      scrollTimeRemainingMs: 0,            // 平滑滚动剩余时间
      lastSmoothChatMessageAddMs: null,    // 上次showNewMessages时间
      smoothScrollRafHandle: null,         // 平滑滚动requestAnimationFrame句柄
      lastSmoothScrollUpdate: null,        // 平滑滚动上一帧时间

      atBottom: true                       // 滚动到底部，用来判断能否自动滚动
    }
  },
  computed: {
    canScrollToBottom() {
      return this.atBottom/* || this.allowScroll*/
    }
  },
  mounted() {
    this.styleElement.innerText = this.css
    this.scrollToBottom()
  },
  beforeDestroy() {
    document.head.removeChild(this.styleElement)
    if (this.emitSmoothedMessageTimerId) {
      window.clearTimeout(this.emitSmoothedMessageTimerId)
      this.emitSmoothedMessageTimerId = null
    }
    this.clearMessages()
  },
  watch: {
    css(val) {
      this.styleElement.innerText = val
    }
  },
  methods: {
    addMessage(message) {
      this.addMessages([message])
    },
    addMessages(messages) {
      this.enqueueMessages(messages)
    },
    mergeSimilarText(content) {
      let res = false
      this.forEachRecentMessage(5, message => {
        if (message.type !== constants.MESSAGE_TYPE_TEXT) {
          return true
        }
        let longer, shorter
        if (message.content.length > content.length) {
          longer = message.content
          shorter = content
        } else {
          longer = content
          shorter = message.content
        }
        if (longer.indexOf(shorter) !== -1 // 长的包含短的
            && longer.length - shorter.length < shorter.length // 长度差较小
        ) {
          message.repeated++
          res = true
          return false
        }
        return true
      })
      return res
    },
    mergeSimilarGift(authorName, price) {
      let res = false
      this.forEachRecentMessage(5, message => {
        if (message.type === constants.MESSAGE_TYPE_SUPER_CHAT
            && message.content === ''
            && message.authorName === authorName
        ) {
          message.price += price
          res = true
          return false
        }
        return true
      })
      return res
    },
    forEachRecentMessage(num, callback) {
      // 从新到老遍历num条消息
      for (let i = this.smoothedMessageQueue.length - 1; i >= 0 && num > 0; i--) {
        let messageGroup = this.smoothedMessageQueue[i]
        for (let j = messageGroup.length - 1; j >= 0 && num-- > 0; j--) {
          if (!callback(messageGroup[j])) {
            return
          }
        }
      }
      for (let arr of [this.messagesBuffer, this.messages]) {
        for (let i = arr.length - 1; i >= 0 && num-- > 0; i--) {
          if (!callback(arr[i])) {
            return
          }
        }
      }
    },
    delMessage(id) {
      this.delMessages([id])
    },
    delMessages(ids) {
      this.enqueueMessages(ids.map(id => {
        return {
          id: id,
          type: constants.MESSAGE_TYPE_DEL
        }
      }))
    },
    clearMessages() {
      this.messages = []
      this.paidMessages = []
      this.smoothedMessageQueue = []
      this.messagesBuffer = []
      this.isSmoothed = true
      this.lastSmoothChatMessageAddMs = null
      this.chatRateMs = 1000
      this.lastSmoothScrollUpdate = null
      this.scrollTimeRemainingMs = this.scrollPixelsRemaining = 0
      this.smoothScrollRafHandle = null
      this.preinsertHeight = 0
      this.maybeResizeScrollContainer()
      if (!this.atBottom) {
        this.scrollToBottom()
      }
    },

    enqueueMessages(messages) {
      if (this.lastEnqueueTime) {
        let interval = new Date() - this.lastEnqueueTime
        // 理论上B站发包间隔1S，如果不过滤间隔太短的会导致消息平滑失效
        if (interval > 100) {
          this.enqueueIntervals.push(interval)
          if (this.enqueueIntervals.length > 5) {
            this.enqueueIntervals.splice(0, this.enqueueIntervals.length - 5)
          }
          this.estimatedEnqueueInterval = Math.max(...this.enqueueIntervals)
        }
      }
      this.lastEnqueueTime = new Date()

      // 只有要显示的消息需要平滑
      let messageGroup = []
      for (let message of messages) {
        messageGroup.push(message)
        if (message.type !== constants.MESSAGE_TYPE_DEL) {
          this.smoothedMessageQueue.push(messageGroup)
          messageGroup = []
        }
      }
      if (messageGroup.length > 0) {
          this.smoothedMessageQueue.push(messageGroup)
      }

      if (!this.emitSmoothedMessageTimerId) {
        this.emitSmoothedMessageTimerId = window.setTimeout(this.emitSmoothedMessages)
      }
    },
    emitSmoothedMessages() {
      this.emitSmoothedMessageTimerId = null
      if (this.smoothedMessageQueue.length <= 0) {
        return
      }

      // 估计的下次进队列剩余时间
      let estimatedNextEnqueueRemainTime = 10 * 1000
      if (this.estimatedEnqueueInterval) {
        estimatedNextEnqueueRemainTime = Math.max(this.lastEnqueueTime - new Date() + this.estimatedEnqueueInterval, 1)
      }
      // 最快80ms/条，计算发送的消息数，保证在下次进队列之前消费完队列
      let groupNumToEmit
      if (this.smoothedMessageQueue.length < estimatedNextEnqueueRemainTime / 80) {
        // 队列中消息数很少，每次发1条也能发完
        groupNumToEmit = 1
      } else {
        // 每次发1条以上，保证按最快速度能发完
        groupNumToEmit = Math.ceil(this.smoothedMessageQueue.length / (estimatedNextEnqueueRemainTime / 80))
      }

      let messageGroups = this.smoothedMessageQueue.splice(0, groupNumToEmit)
      let mergedGroup = []
      for (let messageGroup of messageGroups) {
        for (let message of messageGroup) {
          mergedGroup.push(message)
        }
      }
      this.handleMessageGroup(mergedGroup)

      if (this.smoothedMessageQueue.length <= 0) {
        return
      }
      let sleepTime
      if (groupNumToEmit == 1) {
        // 队列中消息数很少，随便定个80-1000ms的时间
        sleepTime = estimatedNextEnqueueRemainTime / this.smoothedMessageQueue.length
        sleepTime *= 0.5 + Math.random()
        if (sleepTime > 1000) {
          sleepTime = 1000
        } else if (sleepTime < 80) {
          sleepTime = 80
        }
      } else {
        // 按最快速度发
        sleepTime = 80
      }
      this.emitSmoothedMessageTimerId = window.setTimeout(this.emitSmoothedMessages, sleepTime)
    },

    handleMessageGroup(messageGroup) {
      if (messageGroup.length <= 0) {
        return
      }

      for (let message of messageGroup) {
        switch (message.type) {
          case constants.MESSAGE_TYPE_TEXT:
          case constants.MESSAGE_TYPE_MEMBER:
          case constants.MESSAGE_TYPE_SUPER_CHAT:
            this.handleAddMessage(message)
            break
          case constants.MESSAGE_TYPE_DEL:
            this.handleDelMessage(message.id)
            break
        }
      }

      this.maybeResizeScrollContainer(),
      this.flushMessagesBuffer()
      this.$nextTick(this.maybeScrollToBottom)
    },
    handleAddMessage(message) {
      message = {
        ...message,
        addTime: new Date() // 添加一个本地时间给Ticker用，防止本地时间和服务器时间相差很大的情况
      }
      this.messagesBuffer.push(message)
      if (message.type !== constants.MESSAGE_TYPE_TEXT) {
        this.paidMessages.unshift(message)
      }
    },
    handleDelMessage(message) {
      let id = message.id
      for (let arr of [this.messages, this.paidMessages, this.messagesBuffer]) {
        for (let i = 0; i < arr.length; i++) {
          if (arr[i].id === id) {
            arr.splice(i, 1)
            break
          }
        }
      }
    },

    async flushMessagesBuffer() {
      if (this.messagesBuffer.length <= 0) {
        return
      }
      if (!this.canScrollToBottom) {
        if (this.messagesBuffer.length > this.maxNumber) {
          // 未显示消息数 > 最大可显示数，丢弃
          this.messagesBuffer.splice(0, this.messagesBuffer.length - this.maxNumber)
        }
        return
      }

      let removeNum = Math.max(this.messages.length + this.messagesBuffer.length - this.maxNumber, 0)
      if (removeNum > 0) {
        this.messages.splice(0, removeNum)
        // 防止同时添加和删除项目时所有的项目重新渲染 https://github.com/vuejs/vue/issues/6857
        await this.$nextTick()
      }

      this.preinsertHeight = this.$refs.items.clientHeight
      for (let message of this.messagesBuffer) {
        this.messages.push(message)
      }
      this.messagesBuffer = []
      // 等items高度变化
      this.$nextTick(this.showNewMessages)
    },
    showNewMessages() {
      let hasScrollBar = this.$refs.items.clientHeight > this.$refs.scroller.clientHeight
      this.$refs.itemOffset.style.height = `${this.$refs.items.clientHeight}px`
      if (!this.canScrollToBottom || !hasScrollBar) {
        return
      }

      // 计算剩余像素
      this.scrollPixelsRemaining += this.$refs.items.clientHeight - this.preinsertHeight
      this.scrollToBottom()

      // 计算是否平滑滚动、剩余时间
      if (!this.lastSmoothChatMessageAddMs) {
        this.lastSmoothChatMessageAddMs = performance.now()
      }
      let interval = performance.now() - this.lastSmoothChatMessageAddMs
      this.chatRateMs = 0.9 * this.chatRateMs + 0.1 * interval
      if (this.isSmoothed) {
        if (this.chatRateMs < 400) {
          this.isSmoothed = false
        }
      } else {
        if (this.chatRateMs > 450) {
          this.isSmoothed = true
        }
      }
      this.scrollTimeRemainingMs += this.isSmoothed ? CHAT_SMOOTH_ANIMATION_TIME_MS : 0

      if (!this.smoothScrollRafHandle) {
        this.smoothScrollRafHandle = window.requestAnimationFrame(this.smoothScroll)
      }
      this.lastSmoothChatMessageAddMs = performance.now()
    },
    smoothScroll(time) {
      if (!this.lastSmoothScrollUpdate) {
        // 第一帧
        this.lastSmoothScrollUpdate = time
        this.smoothScrollRafHandle = window.requestAnimationFrame(this.smoothScroll)
        return
      }

      let interval = time - this.lastSmoothScrollUpdate
      if (
        this.scrollPixelsRemaining <= 0 || this.scrollPixelsRemaining >= 400  // 已经滚动到底部或者离底部太远则结束
        || interval >= 1000 // 离上一帧时间太久，可能用户切换到其他网页
        || this.scrollTimeRemainingMs <= 0 // 时间已结束
      ) {
        this.resetSmoothScroll()
        return
      }

      let pixelsToScroll = interval / this.scrollTimeRemainingMs * this.scrollPixelsRemaining
      this.scrollPixelsRemaining -= pixelsToScroll
      if (this.scrollPixelsRemaining < 0) {
        this.scrollPixelsRemaining = 0
      }
      this.scrollTimeRemainingMs -= interval
      if (this.scrollTimeRemainingMs < 0) {
        this.scrollTimeRemainingMs = 0
      }
      this.lastSmoothScrollUpdate = time
      this.smoothScrollRafHandle = window.requestAnimationFrame(this.smoothScroll)
    },
    resetSmoothScroll() {
      this.scrollTimeRemainingMs = this.scrollPixelsRemaining = 0
      this.lastSmoothScrollUpdate = null
      if (this.smoothScrollRafHandle) {
        window.cancelAnimationFrame(this.smoothScrollRafHandle)
        this.smoothScrollRafHandle = null
      }
    },

    maybeResizeScrollContainer() {
      this.$refs.itemOffset.style.height = `${this.$refs.items.clientHeight}px`
      this.maybeScrollToBottom()
    },
    maybeScrollToBottom() {
      if (this.canScrollToBottom) {
        this.scrollToBottom()
      }
    },
    scrollToBottom() {
      this.$refs.scroller.scrollTop = Math.pow(2, 24)
      this.atBottom = true
    },
    onScroll() {
      let scroller = this.$refs.scroller
      this.atBottom = scroller.scrollHeight - scroller.scrollTop - scroller.clientHeight < SCROLLED_TO_BOTTOM_EPSILON
      this.flushMessagesBuffer()
    }
  }
}
</script>

<style>
yt-live-chat-renderer, yt-live-chat-item-list-renderer #item-scroller {
  height: 100%;
}

yt-live-chat-renderer ::-webkit-scrollbar {
  content: '';
}

yt-live-chat-renderer ::-webkit-scrollbar-thumb {
  background-color: hsla(0, 0%, 53.3%, .2);
  border: 2px solid #fcfcfc;
  min-height: 30px;
}

yt-live-chat-renderer ::-webkit-scrollbar-track {
  background-color: #fcfcfc;
}
</style>

<!-- html -->
<style>
html:not(.style-scope) {
  --yt-live-chat-background-color: hsl(0, 0%, 100%);
  --yt-live-chat-action-panel-background-color: hsla(0, 0%, 93.3%, .4);
  --yt-live-chat-action-panel-background-color-transparent: hsla(0, 0%, 97%, .8);
  --yt-live-chat-mode-change-background-color: hsla(0, 0%, 93.3%, .4);
  --yt-live-chat-primary-text-color: hsl(0, 0%, 6.7%);
  --yt-live-chat-secondary-text-color: hsla(0, 0%, 6.7%, .6);
  --yt-live-chat-tertiary-text-color: hsla(0, 0%, 6.7%, .4);
  --yt-live-chat-text-input-field-inactive-underline-color: #b8b8b8;
  --yt-live-chat-text-input-field-placeholder-color: hsla(0, 0%, 6.7%, .6);
  --yt-live-chat-icon-button-color: hsla(0, 0%, 6.7%, .4);
  --yt-live-chat-enabled-send-button-color: #4285f4;
  --yt-live-chat-disabled-icon-button-color: hsla(0, 0%, 6.7%, .2);
  --yt-live-chat-picker-button-color: hsla(0, 0%, 6.7%, .4);
  --yt-live-chat-picker-button-active-color: hsla(0, 0%, 6.7%, .8);
  --yt-live-chat-picker-button-disabled-color: var(--yt-live-chat-disabled-icon-button-color);
  --yt-live-chat-picker-button-hover-color: hsla(0, 0%, 6.7%, .6);
  --yt-live-chat-mention-background-color: #ff5722;
  --yt-live-chat-mention-text-color: hsl(0, 0%, 100%);
  --yt-live-chat-deleted-message-color: rgba(0, 0, 0, .5);
  --yt-live-chat-deleted-message-bar-color: rgba(11, 11, 11, .2);
  --yt-live-chat-disabled-button-background-color: hsl(0, 0%, 93.3%);
  --yt-live-chat-disabled-button-text-color: hsla(0, 0%, 6.7%, .4);
  --yt-live-chat-sub-panel-background-color: hsl(0, 0%, 93.3%);
  --yt-live-chat-sub-panel-background-color-transparent: hsla(0, 0%, 93%, .7);
  --yt-live-chat-header-background-color: hsla(0, 0%, 93.3%, .4);
  --yt-live-chat-header-button-color: hsl(0, 0%, 6.7%);
  --yt-live-chat-error-message-color: hsl(10, 51%, 49%);
  --yt-live-chat-reconnect-message-color: hsla(0, 0%, 7%, 0.2);
  --yt-live-chat-moderator-color: hsl(225, 84%, 66%);
  --yt-live-chat-owner-color: hsl(40, 76%, 55%);
  --yt-live-chat-author-chip-owner-text-color: rgba(0,0,0,0.87);
  --yt-live-chat-author-chip-verified-background-color: #CCCCCC;
  --yt-live-chat-author-chip-verified-text-color: #606060;
  --yt-live-chat-message-highlight-background-color: #f8f8f8;
  --yt-live-chat-sponsor-color: #107516;
  --yt-live-chat-overlay-color: hsla(0, 0%, 0%, 0.6);
  --yt-live-chat-dialog-background-color: hsl(0, 0%, 100%);
  --yt-live-chat-dialog-text-color: hsla(0, 0%, 6.7%, .6);
  --yt-live-chat-poll-choice-text-color: var(--yt-spec-text-secondary);
  --yt-live-chat-poll-choice-border-color: var(--yt-spec-10-percent-layer);
  --yt-live-chat-poll-choice-vote-bar-background-color: hsla(0, 0%, 93.3%, .8);
  --yt-live-chat-poll-choice-vote-bar-background-color-selected: #F2F8FF;
  --yt-live-chat-poll-choice-color-selected: #065FD4;
  --yt-live-chat-moderation-mode-hover-background-color: hsla(0, 0%, 6.7%, .2);
  --yt-live-chat-additional-inline-action-button-color: hsl(0, 0%, 100%);
  --yt-live-chat-additional-inline-action-button-background-color: hsla(0, 0%, 26%, 0.8);
  --yt-live-chat-additional-inline-action-button-background-color-hover: hsla(0, 0%, 26%, 1.0);
  --yt-formatted-string-emoji-size: 24px;
  --yt-live-chat-emoji-size: 24px;
  --yt-live-chat-text-input-field-suggestion-background-color: hsl(0, 0%, 100%);
  --yt-live-chat-text-input-field-suggestion-background-color-hover: #eee;
  --yt-live-chat-text-input-field-suggestion-text-color: #666;
  --yt-live-chat-text-input-field-suggestion-text-color-hover: #333;
  --yt-live-chat-ticker-arrow-background: hsl(0, 0%, 97.3%);
  --yt-emoji-picker-category-background-color: var(--yt-live-chat-action-panel-background-color-transparent);
  --yt-emoji-picker-category-color: var(--yt-live-chat-secondary-text-color);
  --yt-emoji-picker-category-button-color: var(--yt-live-chat-picker-button-color);
  --yt-emoji-picker-search-background-color: hsla(0, 0%, 100%, .6);
  --yt-emoji-picker-search-color: hsla(0, 0%, 6.7%, .8);
  --yt-emoji-picker-search-placeholder-color: hsla(0, 0%, 6.7%, .6);
  --yt-live-chat-slider-active-color: #2196f3;
  --yt-live-chat-slider-container-color: #c8c8c8;
  --yt-live-chat-slider-markers-color: #505050;
  --yt-live-chat-toast-background-color: hsl(0, 0%, 20%);
  --yt-live-chat-toast-text-color: hsl(0, 0%, 100%);
  --yt-live-chat-automod-button-background-color: hsl(0, 0%, 93.3%);
  --yt-live-chat-automod-button-background-color-hover: hsla(0, 0%, 6.7%, .2);
  --yt-live-chat-countdown-opacity: 0.3;
  --yt-live-chat-shimmer-background-color: rgba(136, 136, 136, 0.2);
  --yt-live-chat-shimmer-linear-gradient: linear-gradient(0deg, rgba(255, 255, 255, 0) 40%, rgba(255, 255, 255, 0.5) 50%, rgba(255, 255, 255, 0) 65%);
  --yt-live-chat-vem-background-color: hsl(0, 0%, 93.3%);
  --yt-live-chat-upsell-dialog-renderer-button-padding: 10px 16px;
  --yt-live-chat-product-picker-icon-color: rgba(17, 17, 17, 0.6);
  --yt-live-chat-product-picker-hover-color: rgba(17, 17, 16, 0.1);
  --yt-live-chat-product-picker-disabled-icon-color: rgba(17, 17, 17, 0.4);
  --yt-pdg-paid-stickers-tab-selection-bar-color: #065FD4;
  --yt-pdg-paid-stickers-author-name-font-size: 13px;
  --yt-pdg-paid-stickers-margin-left: 38px;
}
</style>

<!-- yt-live-chat-app -->
<style>
canvas.yt-live-chat-app, caption.yt-live-chat-app, center.yt-live-chat-app, cite.yt-live-chat-app, code.yt-live-chat-app, dd.yt-live-chat-app, del.yt-live-chat-app, dfn.yt-live-chat-app, div.yt-live-chat-app, dl.yt-live-chat-app, dt.yt-live-chat-app, em.yt-live-chat-app, embed.yt-live-chat-app, fieldset.yt-live-chat-app, font.yt-live-chat-app, form.yt-live-chat-app, h1.yt-live-chat-app, h2.yt-live-chat-app, h3.yt-live-chat-app, h4.yt-live-chat-app, h5.yt-live-chat-app, h6.yt-live-chat-app, hr.yt-live-chat-app, i.yt-live-chat-app, iframe.yt-live-chat-app, img.yt-live-chat-app, ins.yt-live-chat-app, kbd.yt-live-chat-app, label.yt-live-chat-app, legend.yt-live-chat-app, li.yt-live-chat-app, menu.yt-live-chat-app, object.yt-live-chat-app, ol.yt-live-chat-app, p.yt-live-chat-app, pre.yt-live-chat-app, q.yt-live-chat-app, s.yt-live-chat-app, samp.yt-live-chat-app, small.yt-live-chat-app, span.yt-live-chat-app, strike.yt-live-chat-app, strong.yt-live-chat-app, sub.yt-live-chat-app, sup.yt-live-chat-app, table.yt-live-chat-app, tbody.yt-live-chat-app, td.yt-live-chat-app, tfoot.yt-live-chat-app, th.yt-live-chat-app, thead.yt-live-chat-app, tr.yt-live-chat-app, tt.yt-live-chat-app, u.yt-live-chat-app, ul.yt-live-chat-app, var.yt-live-chat-app {
  margin: 0;
  padding: 0;
  border: 0;
  background: transparent;
}

.yt-live-chat-app[hidden] {
  display: none !important;
}

yt-live-chat-app {
  display: block;
  width: 100vw;
  height: 100vh;
  --yt-report-form-modal-renderer-min-width: 0;
  display: flex;
  -ms-flex-direction: column;
  -webkit-flex-direction: column;
  flex-direction: column;
}

#contents.yt-live-chat-app {
/* yt-live-chat-renderer.yt-live-chat-app { */
  display: flex;
  -ms-flex-direction: column;
  -webkit-flex-direction: column;
  flex-direction: column;
  -ms-flex: 1 1 0.000000001px;
  -webkit-flex: 1;
  flex: 1;
  -webkit-flex-basis: 0.000000001px;
  flex-basis: 0.000000001px;
}

#contents.yt-live-chat-app>*.yt-live-chat-app {
/* yt-live-chat-renderer.yt-live-chat-app { */
  -ms-flex: 1 1 0.000000001px;
  -webkit-flex: 1;
  flex: 1;
  -webkit-flex-basis: 0.000000001px;
  flex-basis: 0.000000001px;
}

yt-live-chat-app[dashboard-money-feed] #contents.yt-live-chat-app>yt-live-chat-message-renderer.yt-live-chat-app {
  font-size: 18px;
}
</style>

<!-- yt-live-chat-renderer -->
<style>
canvas.yt-live-chat-renderer, caption.yt-live-chat-renderer, center.yt-live-chat-renderer, cite.yt-live-chat-renderer, code.yt-live-chat-renderer, dd.yt-live-chat-renderer, del.yt-live-chat-renderer, dfn.yt-live-chat-renderer, div.yt-live-chat-renderer, dl.yt-live-chat-renderer, dt.yt-live-chat-renderer, em.yt-live-chat-renderer, embed.yt-live-chat-renderer, fieldset.yt-live-chat-renderer, font.yt-live-chat-renderer, form.yt-live-chat-renderer, h1.yt-live-chat-renderer, h2.yt-live-chat-renderer, h3.yt-live-chat-renderer, h4.yt-live-chat-renderer, h5.yt-live-chat-renderer, h6.yt-live-chat-renderer, hr.yt-live-chat-renderer, i.yt-live-chat-renderer, iframe.yt-live-chat-renderer, img.yt-live-chat-renderer, ins.yt-live-chat-renderer, kbd.yt-live-chat-renderer, label.yt-live-chat-renderer, legend.yt-live-chat-renderer, li.yt-live-chat-renderer, menu.yt-live-chat-renderer, object.yt-live-chat-renderer, ol.yt-live-chat-renderer, p.yt-live-chat-renderer, pre.yt-live-chat-renderer, q.yt-live-chat-renderer, s.yt-live-chat-renderer, samp.yt-live-chat-renderer, small.yt-live-chat-renderer, span.yt-live-chat-renderer, strike.yt-live-chat-renderer, strong.yt-live-chat-renderer, sub.yt-live-chat-renderer, sup.yt-live-chat-renderer, table.yt-live-chat-renderer, tbody.yt-live-chat-renderer, td.yt-live-chat-renderer, tfoot.yt-live-chat-renderer, th.yt-live-chat-renderer, thead.yt-live-chat-renderer, tr.yt-live-chat-renderer, tt.yt-live-chat-renderer, u.yt-live-chat-renderer, ul.yt-live-chat-renderer, var.yt-live-chat-renderer {
  margin: 0;
  padding: 0;
  border: 0;
  background: transparent;
}

.yt-live-chat-renderer[hidden] {
  display: none !important;
}

yt-live-chat-renderer {
  font-size: 13px;
  --yt-emoji-picker-renderer-height: 180px;
  --yt-button-default-text-color: var(--yt-live-chat-button-default-text-color);
  --yt-button-default-background-color: var(--yt-live-chat-button-default-background-color);
  --yt-button-dark-text-color: var(--yt-live-chat-button-dark-text-color);
  --yt-button-dark-background-color: var(--yt-live-chat-button-dark-background-color);
  --yt-button-payment-background-color: var(--yt-live-chat-sponsor-color);
}

yt-live-chat-renderer {
  position: relative;
  background: var(--yt-live-chat-background-color);
  color: var(--yt-live-chat-primary-text-color);
  overflow: hidden;
  z-index: 0;
  display: flex;
  -ms-flex-direction: column;
  -webkit-flex-direction: column;
  flex-direction: column;
}

yt-live-chat-renderer[hide-timestamps] {
  --yt-live-chat-item-timestamp-display: none;
}

#separator.yt-live-chat-renderer {
  border-bottom: var(--yt-live-chat-header-bottom-border, none);
}

#content-pages.yt-live-chat-renderer {
  display: flex;
  -ms-flex-direction: column;
  -webkit-flex-direction: column;
  flex-direction: column;
  -ms-flex: 1 1 0.000000001px;
  -webkit-flex: 1;
  flex: 1;
  -webkit-flex-basis: 0.000000001px;
  flex-basis: 0.000000001px;
}

#panel-pages.yt-live-chat-renderer {
  max-height: 100%;
  overflow-x: hidden;
  overflow-y: auto;
}

#contents.yt-live-chat-renderer {
  overflow: hidden;
  position: relative;
  z-index: 0;
}

#chat-messages.yt-live-chat-renderer, #contents.yt-live-chat-renderer, #item-list.yt-live-chat-renderer {
  display: flex;
  -ms-flex-direction: column;
  -webkit-flex-direction: column;
  flex-direction: column;
  -ms-flex: 1 1 0.000000001px;
  -webkit-flex: 1;
  flex: 1;
  -webkit-flex-basis: 0.000000001px;
  flex-basis: 0.000000001px;
}

#ticker.yt-live-chat-renderer {
  z-index: 1;
}

#chat.yt-live-chat-renderer {
  position: relative;
  display: flex;
  -ms-flex-direction: column;
  -webkit-flex-direction: column;
  flex-direction: column;
  -ms-flex: 1 1 0.000000001px;
  -webkit-flex: 1;
  flex: 1;
  -webkit-flex-basis: 0.000000001px;
  flex-basis: 0.000000001px;
}

#chat.yt-live-chat-renderer::after {
  content: '';
  display: none;
  animation: gradient-slide 1.2s ease infinite;
  animation-name: gradient-slide;
  background-color: var(--yt-live-chat-shimmer-background-color);
  background-image: var(--yt-live-chat-shimmer-linear-gradient);
  background-size: 300% 300%;
  transform: rotateX(180deg);
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
}

yt-live-chat-renderer[loading] #chat.yt-live-chat-renderer::after {
  display: block;
}

yt-live-chat-pinned-message-renderer.yt-live-chat-renderer {
  bottom: 0;
  left: 0;
  position: absolute;
  right: 0;
  top: 0;
}

yt-live-chat-item-list-renderer.yt-live-chat-renderer, yt-live-chat-ninja-message-renderer.yt-live-chat-renderer {
  -ms-flex: 1 1 0.000000001px;
  -webkit-flex: 1;
  flex: 1;
  -webkit-flex-basis: 0.000000001px;
  flex-basis: 0.000000001px;
}

#action-panel.yt-live-chat-renderer {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  overflow: hidden;
}

yt-live-chat-renderer[has-action-panel-renderer] yt-live-chat-action-panel-renderer.yt-live-chat-renderer {
  animation: slideUp cubic-bezier(0.05, 0.00, 0.00, 1.00) forwards;
  animation-duration: 0.5s;
}

#action-panel-backdrop.yt-live-chat-renderer {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  visibility: hidden;
}

yt-live-chat-renderer[has-action-panel-renderer] #action-panel-backdrop.yt-live-chat-renderer {
  visibility: visible;
  animation: fadeIn cubic-bezier(0.05, 0.00, 0.00, 1.00) forwards;
  animation-duration: 0.5s;
}

#input-panel.yt-live-chat-renderer {
  -ms-flex: none;
  -webkit-flex: none;
  flex: none;
}

#input-panel.yt-live-chat-renderer:not(:empty) {
  border-top: var(--yt-live-chat-action-panel-top-border, none);
}

.hide-on-collapse.yt-live-chat-renderer {
  transition: opacity 0.3s;
}

yt-live-chat-renderer[collapsed] .hide-on-collapse.yt-live-chat-renderer {
  opacity: 0;
}

#loading.yt-live-chat-renderer {
  height: 387px;
  background-color: var(--yt-live-chat-action-panel-background-color);
  display: flex;
  -ms-flex-direction: column;
  -webkit-flex-direction: column;
  flex-direction: column;
  -ms-flex-align: center;
  -webkit-align-items: center;
  align-items: center;
  -ms-flex-pack: center;
  -webkit-justify-content: center;
  justify-content: center;
}

#loading.yt-live-chat-renderer>paper-spinner-lite.yt-live-chat-renderer {
  --paper-spinner-color: var(--yt-live-chat-primary-text-color);
}

#nitrate-promo.yt-live-chat-renderer>*.yt-live-chat-renderer {
  background: var(--yt-live-chat-overlay-color);
  z-index: 3;
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
}

@keyframes gradient-slide {
  0% {
    background-position: 100% 100%;
  }
  to {
    background-position: 0% 0%;
  }
}

@keyframes slideUp {
  0% {
    transform: translateY(15%);
    opacity: 0;
  }
  100% {
    transform: translateY(0);
    opacity: 1;
  }
}

@keyframes fadeIn {
  0% {
    background-color: transparent;
  }
  100% {
    background-color: rgba(0, 0, 0, 0.60);
  }
}
</style>

<!-- yt-live-chat-item-list-renderer -->
<style>
canvas.yt-live-chat-item-list-renderer, caption.yt-live-chat-item-list-renderer, center.yt-live-chat-item-list-renderer, cite.yt-live-chat-item-list-renderer, code.yt-live-chat-item-list-renderer, dd.yt-live-chat-item-list-renderer, del.yt-live-chat-item-list-renderer, dfn.yt-live-chat-item-list-renderer, div.yt-live-chat-item-list-renderer, dl.yt-live-chat-item-list-renderer, dt.yt-live-chat-item-list-renderer, em.yt-live-chat-item-list-renderer, embed.yt-live-chat-item-list-renderer, fieldset.yt-live-chat-item-list-renderer, font.yt-live-chat-item-list-renderer, form.yt-live-chat-item-list-renderer, h1.yt-live-chat-item-list-renderer, h2.yt-live-chat-item-list-renderer, h3.yt-live-chat-item-list-renderer, h4.yt-live-chat-item-list-renderer, h5.yt-live-chat-item-list-renderer, h6.yt-live-chat-item-list-renderer, hr.yt-live-chat-item-list-renderer, i.yt-live-chat-item-list-renderer, iframe.yt-live-chat-item-list-renderer, img.yt-live-chat-item-list-renderer, ins.yt-live-chat-item-list-renderer, kbd.yt-live-chat-item-list-renderer, label.yt-live-chat-item-list-renderer, legend.yt-live-chat-item-list-renderer, li.yt-live-chat-item-list-renderer, menu.yt-live-chat-item-list-renderer, object.yt-live-chat-item-list-renderer, ol.yt-live-chat-item-list-renderer, p.yt-live-chat-item-list-renderer, pre.yt-live-chat-item-list-renderer, q.yt-live-chat-item-list-renderer, s.yt-live-chat-item-list-renderer, samp.yt-live-chat-item-list-renderer, small.yt-live-chat-item-list-renderer, span.yt-live-chat-item-list-renderer, strike.yt-live-chat-item-list-renderer, strong.yt-live-chat-item-list-renderer, sub.yt-live-chat-item-list-renderer, sup.yt-live-chat-item-list-renderer, table.yt-live-chat-item-list-renderer, tbody.yt-live-chat-item-list-renderer, td.yt-live-chat-item-list-renderer, tfoot.yt-live-chat-item-list-renderer, th.yt-live-chat-item-list-renderer, thead.yt-live-chat-item-list-renderer, tr.yt-live-chat-item-list-renderer, tt.yt-live-chat-item-list-renderer, u.yt-live-chat-item-list-renderer, ul.yt-live-chat-item-list-renderer, var.yt-live-chat-item-list-renderer {
  margin: 0;
  padding: 0;
  border: 0;
  background: transparent;
}

.yt-live-chat-item-list-renderer[hidden] {
  display: none !important;
}

yt-live-chat-item-list-renderer {
  position: relative;
  display: block;
  overflow: hidden;
  z-index: 0;
}

yt-live-chat-item-list-renderer[moderation-mode-enabled] {
  --yt-live-chat-item-with-inline-actions-context-menu-display: none;
  --yt-live-chat-inline-action-button-container-display: flex;
}

#contents.yt-live-chat-item-list-renderer {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  display: flex;
  -ms-flex-direction: column;
  -webkit-flex-direction: column;
  flex-direction: column;
}

#empty-state-message.yt-live-chat-item-list-renderer {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  display: flex;
  -ms-flex-direction: column;
  -webkit-flex-direction: column;
  flex-direction: column;
  -ms-flex-pack: center;
  -webkit-justify-content: center;
  justify-content: center;
}

#empty-state-message.yt-live-chat-item-list-renderer>yt-live-chat-message-renderer.yt-live-chat-item-list-renderer {
  color: var(--yt-live-chat-tertiary-text-color);
  background: transparent;
  font-size: 18px;
  --yt-live-chat-message-renderer-text-align: center;
}

yt-icon-button.yt-live-chat-item-list-renderer {
  background-color: #2196f3;
  border-radius: 999px;
  bottom: 0;
  color: #fff;
  cursor: pointer;
  width: 32px;
  height: 32px;
  margin: 0 calc(50% - 16px) 8px calc(50% - 16px);
  padding: 4px;
  position: absolute;
  transition-property: bottom;
  transition-timing-function: cubic-bezier(0.0, 0.0, 0.2, 1);
  transition-duration: 0.15s;
  box-shadow: 0 2px 2px 0 rgba(0, 0, 0, 0.14), 0 1px 5px 0 rgba(0, 0, 0, 0.12), 0 3px 1px -2px rgba(0, 0, 0, 0.2);
}

yt-icon-button.yt-live-chat-item-list-renderer[disabled] {
  bottom: -42px;
  color: #fff;
  transition-timing-function: cubic-bezier(0.4, 0.0, 1, 1);
}

#item-scroller.yt-live-chat-item-list-renderer {
  -ms-flex: 1 1 0.000000001px;
  -webkit-flex: 1;
  flex: 1;
  -webkit-flex-basis: 0.000000001px;
  flex-basis: 0.000000001px;
  overflow-x: hidden;
  overflow-y: hidden;
  padding-right: var(--scrollbar-width);
}

yt-live-chat-item-list-renderer[allow-scroll] #item-scroller.yt-live-chat-item-list-renderer {
  overflow-y: scroll;
  padding-right: 0;
}

#item-offset.yt-live-chat-item-list-renderer {
  position: relative;
}

#item-scroller.animated.yt-live-chat-item-list-renderer #item-offset.yt-live-chat-item-list-renderer {
  overflow: hidden;
}

#items.yt-live-chat-item-list-renderer {
  -ms-flex: 1 1 0.000000001px;
  -webkit-flex: 1;
  flex: 1;
  -webkit-flex-basis: 0.000000001px;
  flex-basis: 0.000000001px;
  padding: var(--yt-live-chat-item-list-renderer-padding, 4px 0);
}

#items.yt-live-chat-item-list-renderer>*.yt-live-chat-item-list-renderer:not(:first-child) {
  border-top: var(--yt-live-chat-item-list-item-border, none);
}

#item-scroller.animated.yt-live-chat-item-list-renderer #items.yt-live-chat-item-list-renderer {
  bottom: 0;
  left: 0;
  position: absolute;
  right: 0;
  transform: translateY(0);
}

#docked-messages.yt-live-chat-item-list-renderer {
  z-index: 1;
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
}

yt-live-chat-paid-sticker-renderer.yt-live-chat-item-list-renderer {
  padding: 4px 24px;
}

yt-live-chat-paid-sticker-renderer.yt-live-chat-item-list-renderer[dashboard-money-feed] {
  padding: 8px 16px;
}
</style>
