<template>
  <yt-live-chat-paid-message-renderer>
    <div id="header" :style="'background-color: ' + headerColor">
      <div id="author-photo" :style="`background-image: url(${avatarUrl})`"></div>
      <div id="header-content">
        <div id="author-name">{{authorName}}</div>
        <div id="purchase-amount">{{title}}</div>
      </div>
    </div>
    <div id="content" :style="'background-color: ' + contentColor">
      <div id="message" dir="auto">{{content}}</div>
    </div>
  </yt-live-chat-paid-message-renderer>
</template>

<script>
let LEVEL_TO_HEADER_COLOR = [
  'rgba(0,184,212,1)', // $2浅蓝
  'rgba(255,176,0,1)', // $10黄
  'rgba(245,91,0,1)', // $20橙
  'rgba(208,0,0,1)' // $100红
]
let LEVEL_TO_CONTENT_COLOR = [
  'rgba(0,229,255,1)', // $2浅蓝
  'rgba(236,182,29,1)', // $10黄
  'rgba(255,127,0,1)', // $20橙
  'rgba(230,33,23,1)' // $100红
]

export default {
  name: 'PaidMessage',
  props: {
    level: Number, // 高亮等级，决定颜色
    avatarUrl: String,
    authorName: String,
    title: String,
    content: String
  },
  computed: {
    headerColor() {
      if (this.level < 0)
        return LEVEL_TO_HEADER_COLOR[0]
      if (this.level >= LEVEL_TO_HEADER_COLOR.length)
        return LEVEL_TO_HEADER_COLOR[LEVEL_TO_HEADER_COLOR.length - 1]
      return LEVEL_TO_HEADER_COLOR[this.level]
    },
    contentColor() {
      if (this.level < 0)
        return LEVEL_TO_CONTENT_COLOR[0]
      if (this.level >= LEVEL_TO_CONTENT_COLOR.length)
        return LEVEL_TO_CONTENT_COLOR[LEVEL_TO_CONTENT_COLOR.length - 1]
      return LEVEL_TO_CONTENT_COLOR[this.level]
    }
  }
}
</script>
