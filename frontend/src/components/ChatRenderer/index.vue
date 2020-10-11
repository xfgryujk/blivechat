<template>
  <yt-live-chat-renderer class="style-scope yt-live-chat-app" style="--scrollbar-width:11px;" hide-timestamps
    @mousemove="refreshCantScrollStartTime"
  >
    <ticker class="style-scope yt-live-chat-renderer" :messages="paidMessages" :showGiftName="showGiftName"></ticker>
    <yt-live-chat-item-list-renderer class="style-scope yt-live-chat-renderer" allow-scroll>
      <div ref="scroller" id="item-scroller" class="style-scope yt-live-chat-item-list-renderer animated" @scroll="onScroll">
        <div ref="itemOffset" id="item-offset" class="style-scope yt-live-chat-item-list-renderer" style="height: 0px;">
          <div ref="items" id="items" class="style-scope yt-live-chat-item-list-renderer" style="overflow: hidden"
            :style="{transform: `translateY(${Math.floor(scrollPixelsRemaining)}px)`}"
          >
            <template v-for="message in messages">
              <text-message :key="message.id" v-if="message.type === MESSAGE_TYPE_TEXT"
                class="style-scope yt-live-chat-item-list-renderer"
                :avatarUrl="message.avatarUrl" :time="message.time" :authorName="message.authorName"
                :authorType="message.authorType" :content="getShowContent(message)" :privilegeType="message.privilegeType"
                :repeated="message.repeated"
              ></text-message>
              <paid-message :key="message.id" v-else-if="message.type === MESSAGE_TYPE_GIFT"
                class="style-scope yt-live-chat-item-list-renderer"
                :price="message.price" :avatarUrl="message.avatarUrl" :authorName="message.authorName"
                :time="message.time" :content="getGiftShowContent(message)"
              ></paid-message>
              <membership-item :key="message.id" v-else-if="message.type === MESSAGE_TYPE_MEMBER"
                class="style-scope yt-live-chat-item-list-renderer"
                :avatarUrl="message.avatarUrl" :authorName="message.authorName" :privilegeType="message.privilegeType"
                :title="message.title" :time="message.time"
              ></membership-item>
              <paid-message :key="message.id" v-else-if="message.type === MESSAGE_TYPE_SUPER_CHAT"
                class="style-scope yt-live-chat-item-list-renderer"
                :price="message.price" :avatarUrl="message.avatarUrl" :authorName="message.authorName"
                :time="message.time" :content="getShowContent(message)"
              ></paid-message>
            </template>
          </div>
        </div>
      </div>
    </yt-live-chat-item-list-renderer>
  </yt-live-chat-renderer>
</template>

<script>
import * as chatConfig from '@/api/chatConfig'
import Ticker from './Ticker.vue'
import TextMessage from './TextMessage.vue'
import MembershipItem from './MembershipItem.vue'
import PaidMessage from './PaidMessage.vue'
import * as constants from './constants'

const CHAT_SMOOTH_ANIMATION_TIME_MS = 84
const SCROLLED_TO_BOTTOM_EPSILON = 15

export default {
  name: 'ChatRenderer',
  components: {
    Ticker,
    TextMessage,
    MembershipItem,
    PaidMessage
  },
  props: {
    css: String,
    maxNumber: {
      type: Number,
      default: chatConfig.DEFAULT_CONFIG.maxNumber
    },
    showGiftName: {
      type: Boolean,
      default: chatConfig.DEFAULT_CONFIG.showGiftName
    }
  },
  data() {
    let styleElement = document.createElement('style')
    document.head.appendChild(styleElement)
    return {
      MESSAGE_TYPE_TEXT: constants.MESSAGE_TYPE_TEXT,
      MESSAGE_TYPE_GIFT: constants.MESSAGE_TYPE_GIFT,
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

      atBottom: true,                      // 滚动到底部，用来判断能否自动滚动
      cantScrollStartTime: null            // 开始不能自动滚动的时间，用来防止卡住
    }
  },
  computed: {
    canScrollToBottom() {
      return this.atBottom/* || this.allowScroll*/
    }
  },
  watch: {
    css(val) {
      this.styleElement.innerText = val
    },
    canScrollToBottom(val) {
      this.cantScrollStartTime = val ? null : new Date()
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
  methods: {
    getGiftShowContent(message) {
      return constants.getGiftShowContent(message, this.showGiftName)
    },
    getShowContent: constants.getShowContent,

    addMessage(message) {
      this.addMessages([message])
    },
    addMessages(messages) {
      this.enqueueMessages(messages)
    },
    mergeSimilarText(content) {
      content = content.trim().toLowerCase()
      let res = false
      this.forEachRecentMessage(5, message => {
        if (message.type !== constants.MESSAGE_TYPE_TEXT) {
          return true
        }
        let messageContent = message.content.trim().toLowerCase()
        let longer, shorter
        if (messageContent.length > content.length) {
          longer = messageContent
          shorter = content
        } else {
          longer = content
          shorter = messageContent
        }
        if (longer.indexOf(shorter) !== -1 // 长的包含短的
            && longer.length - shorter.length < shorter.length // 长度差较小
        ) {
          // 其实有小概率导致弹幕卡住
          message.repeated++
          res = true
          return false
        }
        return true
      })
      return res
    },
    mergeSimilarGift(authorName, price, giftName, num) {
      let res = false
      this.forEachRecentMessage(5, message => {
        if (message.type === constants.MESSAGE_TYPE_GIFT
            && message.authorName === authorName
            && message.giftName === giftName
        ) {
          message.price += price
          message.num += num
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
          type: constants.MESSAGE_TYPE_DEL,
          id
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
    updateMessage(id, newValuesObj) {
      this.enqueueMessages([{
        type: constants.MESSAGE_TYPE_UPDATE,
        id,
        newValuesObj
      }])
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
        if (message.type !== constants.MESSAGE_TYPE_DEL && message.type !== constants.MESSAGE_TYPE_UPDATE) {
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
      // 最快80ms/条，计算发送的消息数，保证在下次进队列之前消费队列到最多剩3条消息，不消费完是为了防止消息速度变慢时突然停顿
      const MIN_SLEEP_TIME = 80
      const MAX_SLEEP_TIME = 1000
      const MAX_REMAIN_GROUP_NUM = 3
      // 下次进队列之前应该发多少条消息
      let shouldEmitGroupNum = Math.max(this.smoothedMessageQueue.length - MAX_REMAIN_GROUP_NUM, 0)
      // 下次进队列之前最多能发多少次
      let maxCanEmitCount = estimatedNextEnqueueRemainTime / MIN_SLEEP_TIME
      // 这次发多少条消息
      let groupNumToEmit
      if (shouldEmitGroupNum < maxCanEmitCount) {
        // 队列中消息数很少，每次发1条也能发到最多剩3条
        groupNumToEmit = 1
      } else {
        // 每次发1条以上，保证按最快速度能发到最多剩3条
        groupNumToEmit = Math.ceil(shouldEmitGroupNum / maxCanEmitCount)
      }

      // 发消息
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
      // 消息没发完，计算下次发消息时间
      let sleepTime
      if (groupNumToEmit === 1) {
        // 队列中消息数很少，随便定个[MIN_SLEEP_TIME, MAX_SLEEP_TIME]的时间
        sleepTime = estimatedNextEnqueueRemainTime / this.smoothedMessageQueue.length
        sleepTime *= 0.5 + Math.random()
        if (sleepTime > MAX_SLEEP_TIME) {
          sleepTime = MAX_SLEEP_TIME
        } else if (sleepTime < MIN_SLEEP_TIME) {
          sleepTime = MIN_SLEEP_TIME
        }
      } else {
        // 按最快速度发
        sleepTime = MIN_SLEEP_TIME
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
          case constants.MESSAGE_TYPE_GIFT:
          case constants.MESSAGE_TYPE_MEMBER:
          case constants.MESSAGE_TYPE_SUPER_CHAT:
            this.handleAddMessage(message)
            break
          case constants.MESSAGE_TYPE_DEL:
            this.handleDelMessage(message)
            break
          case constants.MESSAGE_TYPE_UPDATE:
            this.handleUpdateMessage(message)
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
    handleDelMessage({id}) {
      for (let arr of [this.messages, this.paidMessages, this.messagesBuffer]) {
        for (let i = 0; i < arr.length; i++) {
          if (arr[i].id === id) {
            arr.splice(i, 1)
            this.resetSmoothScroll()
            break
          }
        }
      }
    },
    handleUpdateMessage({id, newValuesObj}) {
      // 遍历滚动的消息
      this.forEachRecentMessage(999999999, message => {
        if (message.id !== id) {
          return true
        }
        for (let name in newValuesObj) {
          message[name] = newValuesObj[name]
        }
        return false
      })
      // 遍历固定的消息
      for (let message of this.paidMessages) {
        if (message.id !== id) {
          continue
        }
        for (let name in newValuesObj) {
          message[name] = newValuesObj[name]
        }
        break
      }
      this.resetSmoothScroll()
    },

    async flushMessagesBuffer() {
      if (this.messagesBuffer.length <= 0) {
        return
      }
      if (!this.canScrollToBottomOrTimedOut()) {
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
      if (!this.canScrollToBottomOrTimedOut() || !hasScrollBar) {
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
      if (this.canScrollToBottomOrTimedOut()) {
        this.scrollToBottom()
      }
    },
    scrollToBottom() {
      this.$refs.scroller.scrollTop = Math.pow(2, 24)
      this.atBottom = true
    },
    onScroll() {
      this.refreshCantScrollStartTime()
      let scroller = this.$refs.scroller
      this.atBottom = scroller.scrollHeight - scroller.scrollTop - scroller.clientHeight < SCROLLED_TO_BOTTOM_EPSILON
      this.flushMessagesBuffer()
    },
    canScrollToBottomOrTimedOut() {
      if (this.canScrollToBottom) {
        return true
      }
      // 防止在OBS中卡住，超过一定时间也可以自动滚动
      return new Date() - this.cantScrollStartTime >= 5 * 1000
    },
    refreshCantScrollStartTime() {
      // 有鼠标事件时刷新，防止用户看弹幕时自动滚动
      if (this.cantScrollStartTime) {
        this.cantScrollStartTime = new Date()
      }
    }
  }
}
</script>

<style src="@/assets/css/youtube/yt-html.css"></style>
<style src="@/assets/css/youtube/yt-live-chat-renderer.css"></style>
<style src="@/assets/css/youtube/yt-live-chat-item-list-renderer.css"></style>
