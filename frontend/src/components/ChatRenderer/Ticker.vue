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
      <legacy-paid-message :key="pinnedMessage.id" v-if="pinnedMessage.type === MESSAGE_TYPE_MEMBER"
        class="style-scope yt-live-chat-ticker-renderer"
        :avatarUrl="pinnedMessage.avatarUrl" :title="pinnedMessage.title" :content="pinnedMessage.content"
        :time="pinnedMessage.time"
      ></legacy-paid-message>
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
import LegacyPaidMessage from './LegacyPaidMessage.vue'
import PaidMessage from './PaidMessage.vue'
import * as constants from './constants'

export default {
  name: 'Ticker',
  components: {
    ImgShadow,
    LegacyPaidMessage,
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

<!-- yt-live-chat-ticker-renderer -->
<style>
canvas.yt-live-chat-ticker-renderer, caption.yt-live-chat-ticker-renderer, center.yt-live-chat-ticker-renderer, cite.yt-live-chat-ticker-renderer, code.yt-live-chat-ticker-renderer, dd.yt-live-chat-ticker-renderer, del.yt-live-chat-ticker-renderer, dfn.yt-live-chat-ticker-renderer, div.yt-live-chat-ticker-renderer, dl.yt-live-chat-ticker-renderer, dt.yt-live-chat-ticker-renderer, em.yt-live-chat-ticker-renderer, embed.yt-live-chat-ticker-renderer, fieldset.yt-live-chat-ticker-renderer, font.yt-live-chat-ticker-renderer, form.yt-live-chat-ticker-renderer, h1.yt-live-chat-ticker-renderer, h2.yt-live-chat-ticker-renderer, h3.yt-live-chat-ticker-renderer, h4.yt-live-chat-ticker-renderer, h5.yt-live-chat-ticker-renderer, h6.yt-live-chat-ticker-renderer, hr.yt-live-chat-ticker-renderer, i.yt-live-chat-ticker-renderer, iframe.yt-live-chat-ticker-renderer, img.yt-live-chat-ticker-renderer, ins.yt-live-chat-ticker-renderer, kbd.yt-live-chat-ticker-renderer, label.yt-live-chat-ticker-renderer, legend.yt-live-chat-ticker-renderer, li.yt-live-chat-ticker-renderer, menu.yt-live-chat-ticker-renderer, object.yt-live-chat-ticker-renderer, ol.yt-live-chat-ticker-renderer, p.yt-live-chat-ticker-renderer, pre.yt-live-chat-ticker-renderer, q.yt-live-chat-ticker-renderer, s.yt-live-chat-ticker-renderer, samp.yt-live-chat-ticker-renderer, small.yt-live-chat-ticker-renderer, span.yt-live-chat-ticker-renderer, strike.yt-live-chat-ticker-renderer, strong.yt-live-chat-ticker-renderer, sub.yt-live-chat-ticker-renderer, sup.yt-live-chat-ticker-renderer, table.yt-live-chat-ticker-renderer, tbody.yt-live-chat-ticker-renderer, td.yt-live-chat-ticker-renderer, tfoot.yt-live-chat-ticker-renderer, th.yt-live-chat-ticker-renderer, thead.yt-live-chat-ticker-renderer, tr.yt-live-chat-ticker-renderer, tt.yt-live-chat-ticker-renderer, u.yt-live-chat-ticker-renderer, ul.yt-live-chat-ticker-renderer, var.yt-live-chat-ticker-renderer {
  margin: 0;
  padding: 0;
  border: 0;
  background: transparent;
}

.yt-live-chat-ticker-renderer[hidden] {
  display: none !important;
}

yt-live-chat-ticker-renderer {
  display: block;
  background-color: var(--yt-live-chat-header-background-color);
}

#container.yt-live-chat-ticker-renderer {
  position: relative;
}

#items.yt-live-chat-ticker-renderer {
  height: 32px;
  overflow: hidden;
  white-space: nowrap;
  padding: 0 24px 8px 24px;
}

#items.yt-live-chat-ticker-renderer>*.yt-live-chat-ticker-renderer {
  margin-right: 8px;
}

#left-arrow-container.yt-live-chat-ticker-renderer {
  background: linear-gradient(to right, var(--yt-live-chat-ticker-arrow-background) 0, var(--yt-live-chat-ticker-arrow-background) 52px, transparent 60px);
  left: 0;
  padding: 0 16px 0 12px;
}

#right-arrow-container.yt-live-chat-ticker-renderer {
  background: linear-gradient(to left, var(--yt-live-chat-ticker-arrow-background) 0, var(--yt-live-chat-ticker-arrow-background) 52px, transparent 60px);
  right: 0;
  padding: 0 12px 0 16px;
}

#container.yt-live-chat-ticker-renderer:hover #left-arrow-container.yt-live-chat-ticker-renderer, #container.yt-live-chat-ticker-renderer:hover #right-arrow-container.yt-live-chat-ticker-renderer {
  opacity: 1;
}

#left-arrow-container.yt-live-chat-ticker-renderer, #right-arrow-container.yt-live-chat-ticker-renderer {
  height: 32px;
  opacity: 0;
  position: absolute;
  text-align: center;
  top: 0;
  transition: opacity 0.3s 0.1s;
}

yt-icon.yt-live-chat-ticker-renderer {
  background-color: #2196f3;
  border-radius: 999px;
  color: #fff;
  cursor: pointer;
  height: 24px;
  padding: 4px;
  width: 24px;
}
</style>

<!-- yt-live-chat-ticker-paid-message-item-renderer -->
<style>
canvas.yt-live-chat-ticker-paid-message-item-renderer, caption.yt-live-chat-ticker-paid-message-item-renderer, center.yt-live-chat-ticker-paid-message-item-renderer, cite.yt-live-chat-ticker-paid-message-item-renderer, code.yt-live-chat-ticker-paid-message-item-renderer, dd.yt-live-chat-ticker-paid-message-item-renderer, del.yt-live-chat-ticker-paid-message-item-renderer, dfn.yt-live-chat-ticker-paid-message-item-renderer, div.yt-live-chat-ticker-paid-message-item-renderer, dl.yt-live-chat-ticker-paid-message-item-renderer, dt.yt-live-chat-ticker-paid-message-item-renderer, em.yt-live-chat-ticker-paid-message-item-renderer, embed.yt-live-chat-ticker-paid-message-item-renderer, fieldset.yt-live-chat-ticker-paid-message-item-renderer, font.yt-live-chat-ticker-paid-message-item-renderer, form.yt-live-chat-ticker-paid-message-item-renderer, h1.yt-live-chat-ticker-paid-message-item-renderer, h2.yt-live-chat-ticker-paid-message-item-renderer, h3.yt-live-chat-ticker-paid-message-item-renderer, h4.yt-live-chat-ticker-paid-message-item-renderer, h5.yt-live-chat-ticker-paid-message-item-renderer, h6.yt-live-chat-ticker-paid-message-item-renderer, hr.yt-live-chat-ticker-paid-message-item-renderer, i.yt-live-chat-ticker-paid-message-item-renderer, iframe.yt-live-chat-ticker-paid-message-item-renderer, img.yt-live-chat-ticker-paid-message-item-renderer, ins.yt-live-chat-ticker-paid-message-item-renderer, kbd.yt-live-chat-ticker-paid-message-item-renderer, label.yt-live-chat-ticker-paid-message-item-renderer, legend.yt-live-chat-ticker-paid-message-item-renderer, li.yt-live-chat-ticker-paid-message-item-renderer, menu.yt-live-chat-ticker-paid-message-item-renderer, object.yt-live-chat-ticker-paid-message-item-renderer, ol.yt-live-chat-ticker-paid-message-item-renderer, p.yt-live-chat-ticker-paid-message-item-renderer, pre.yt-live-chat-ticker-paid-message-item-renderer, q.yt-live-chat-ticker-paid-message-item-renderer, s.yt-live-chat-ticker-paid-message-item-renderer, samp.yt-live-chat-ticker-paid-message-item-renderer, small.yt-live-chat-ticker-paid-message-item-renderer, span.yt-live-chat-ticker-paid-message-item-renderer, strike.yt-live-chat-ticker-paid-message-item-renderer, strong.yt-live-chat-ticker-paid-message-item-renderer, sub.yt-live-chat-ticker-paid-message-item-renderer, sup.yt-live-chat-ticker-paid-message-item-renderer, table.yt-live-chat-ticker-paid-message-item-renderer, tbody.yt-live-chat-ticker-paid-message-item-renderer, td.yt-live-chat-ticker-paid-message-item-renderer, tfoot.yt-live-chat-ticker-paid-message-item-renderer, th.yt-live-chat-ticker-paid-message-item-renderer, thead.yt-live-chat-ticker-paid-message-item-renderer, tr.yt-live-chat-ticker-paid-message-item-renderer, tt.yt-live-chat-ticker-paid-message-item-renderer, u.yt-live-chat-ticker-paid-message-item-renderer, ul.yt-live-chat-ticker-paid-message-item-renderer, var.yt-live-chat-ticker-paid-message-item-renderer {
  margin: 0;
  padding: 0;
  border: 0;
  background: transparent;
}

.yt-live-chat-ticker-paid-message-item-renderer[hidden] {
  display: none !important;
}

canvas.yt-live-chat-ticker-paid-message-item-renderer, caption.yt-live-chat-ticker-paid-message-item-renderer, center.yt-live-chat-ticker-paid-message-item-renderer, cite.yt-live-chat-ticker-paid-message-item-renderer, code.yt-live-chat-ticker-paid-message-item-renderer, dd.yt-live-chat-ticker-paid-message-item-renderer, del.yt-live-chat-ticker-paid-message-item-renderer, dfn.yt-live-chat-ticker-paid-message-item-renderer, div.yt-live-chat-ticker-paid-message-item-renderer, dl.yt-live-chat-ticker-paid-message-item-renderer, dt.yt-live-chat-ticker-paid-message-item-renderer, em.yt-live-chat-ticker-paid-message-item-renderer, embed.yt-live-chat-ticker-paid-message-item-renderer, fieldset.yt-live-chat-ticker-paid-message-item-renderer, font.yt-live-chat-ticker-paid-message-item-renderer, form.yt-live-chat-ticker-paid-message-item-renderer, h1.yt-live-chat-ticker-paid-message-item-renderer, h2.yt-live-chat-ticker-paid-message-item-renderer, h3.yt-live-chat-ticker-paid-message-item-renderer, h4.yt-live-chat-ticker-paid-message-item-renderer, h5.yt-live-chat-ticker-paid-message-item-renderer, h6.yt-live-chat-ticker-paid-message-item-renderer, hr.yt-live-chat-ticker-paid-message-item-renderer, i.yt-live-chat-ticker-paid-message-item-renderer, iframe.yt-live-chat-ticker-paid-message-item-renderer, img.yt-live-chat-ticker-paid-message-item-renderer, ins.yt-live-chat-ticker-paid-message-item-renderer, kbd.yt-live-chat-ticker-paid-message-item-renderer, label.yt-live-chat-ticker-paid-message-item-renderer, legend.yt-live-chat-ticker-paid-message-item-renderer, li.yt-live-chat-ticker-paid-message-item-renderer, menu.yt-live-chat-ticker-paid-message-item-renderer, object.yt-live-chat-ticker-paid-message-item-renderer, ol.yt-live-chat-ticker-paid-message-item-renderer, p.yt-live-chat-ticker-paid-message-item-renderer, pre.yt-live-chat-ticker-paid-message-item-renderer, q.yt-live-chat-ticker-paid-message-item-renderer, s.yt-live-chat-ticker-paid-message-item-renderer, samp.yt-live-chat-ticker-paid-message-item-renderer, small.yt-live-chat-ticker-paid-message-item-renderer, span.yt-live-chat-ticker-paid-message-item-renderer, strike.yt-live-chat-ticker-paid-message-item-renderer, strong.yt-live-chat-ticker-paid-message-item-renderer, sub.yt-live-chat-ticker-paid-message-item-renderer, sup.yt-live-chat-ticker-paid-message-item-renderer, table.yt-live-chat-ticker-paid-message-item-renderer, tbody.yt-live-chat-ticker-paid-message-item-renderer, td.yt-live-chat-ticker-paid-message-item-renderer, tfoot.yt-live-chat-ticker-paid-message-item-renderer, th.yt-live-chat-ticker-paid-message-item-renderer, thead.yt-live-chat-ticker-paid-message-item-renderer, tr.yt-live-chat-ticker-paid-message-item-renderer, tt.yt-live-chat-ticker-paid-message-item-renderer, u.yt-live-chat-ticker-paid-message-item-renderer, ul.yt-live-chat-ticker-paid-message-item-renderer, var.yt-live-chat-ticker-paid-message-item-renderer {
  margin: 0;
  padding: 0;
  border: 0;
  background: transparent;
}

.yt-live-chat-ticker-paid-message-item-renderer[hidden] {
  display: none !important;
}

yt-live-chat-ticker-paid-message-item-renderer {
  display: inline-block;
  font-size: 14px;
  outline: none;
  transition: width 0.2s;
  vertical-align: top;
  cursor: pointer;
  -moz-user-select: none;
  -ms-user-select: none;
  -webkit-user-select: none;
  user-select: none;
}

#container.yt-live-chat-ticker-paid-message-item-renderer {
  border-radius: 999px;
  padding: 4px;
}

yt-live-chat-ticker-paid-message-item-renderer.sliding-down #container.yt-live-chat-ticker-paid-message-item-renderer {
  opacity: 0.5;
  transform: translateY(44px);
  transition: opacity 0.2s, transform 0.2s cubic-bezier(0.4, 0.0, 1, 1);
}

yt-live-chat-ticker-paid-message-item-renderer.collapsing {
  margin-right: 0;
  transition: margin-right 0.2s cubic-bezier(0.4, 0.0, 0.2, 1), width 0.2s cubic-bezier(0.4, 0.0, 0.2, 1);
}

yt-live-chat-ticker-paid-message-item-renderer[dimmed] {
  opacity: 0.5;
}

yt-img-shadow.yt-live-chat-ticker-paid-message-item-renderer {
  margin-right: -4px;
  overflow: hidden;
  border-radius: 50%;
}

#content.yt-live-chat-ticker-paid-message-item-renderer {
  height: 24px;
  display: flex;
  -ms-flex-direction: row;
  -webkit-flex-direction: row;
  flex-direction: row;
  -ms-flex-align: center;
  -webkit-align-items: center;
  align-items: center;
}

#text.yt-live-chat-ticker-paid-message-item-renderer {
  margin: 0 8px;
  font-weight: 500;
}

yt-live-chat-ticker-paid-message-item-renderer[is-deleted] #author-photo.yt-live-chat-ticker-paid-message-item-renderer {
  display: none;
}
</style>
