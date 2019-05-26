<template>
  <yt-live-chat-paid-message-renderer>
    <div id="header" :style="'background-color: ' + headerColor">
      <div id="author-photo" :style="`background-image: url(${avatarUrl})`"></div>
      <div id="header-content">
        <div id="author-name">{{authorName}}</div>
        <div id="purchase-amount">CN¥{{price}}</div>
      </div>
    </div>
    <div id="content" :style="'background-color: ' + contentColor">
      <div id="message" dir="auto">{{content}}</div>
    </div>
  </yt-live-chat-paid-message-renderer>
</template>

<script>
const LEVEL_TO_HEADER_COLOR = [
  'rgba(21,101,192,1)', //$1蓝
  'rgba(0,184,212,1)', // $2浅蓝
  'rgba(0,191,165,1)', // $5绿
  'rgba(255,179,0,1)', // $10黄
  'rgba(230,81,0,1)', // $20橙
  'rgba(194,24,91,1)', // $50品红
  'rgba(208,0,0,1)' // $100红
]
const LEVEL_TO_CONTENT_COLOR = [
  'rgba(30,136,229,1)', //$1蓝
  'rgba(0,229,255,1)', // $2浅蓝
  'rgba(29,233,182,1)', // $5绿
  'rgba(255,202,40,1)', // $10黄
  'rgba(245,124,0,1)', // $20橙
  'rgba(233,30,99,1)', // $50品红
  'rgba(230,33,23,1)' // $100红
]

export default {
  name: 'PaidMessage',
  props: {
    price: Number, // 价格，人民币
    avatarUrl: String,
    authorName: String,
    content: String
  },
  computed: {
    level() {
      if (this.price < 9.9) // 0~9.9，丢人
        return 0
      else if (this.price < 28) // 9.9~28，B坷垃
        return 1
      else if (this.price < 52) // 28~52，礼花
        return 2
      else if (this.price < 100) // 52~100，疯狂打call
        return 3
      else if (this.price < 450) // 100~450，节奏风暴、天空之翼
        return 4
      else if (this.price < 1245) // 450~1245，摩天大楼
        return 5
      else // 1245，小电视飞船
        return 6
    },
    headerColor() {
      return LEVEL_TO_HEADER_COLOR[this.level]
    },
    contentColor() {
      return LEVEL_TO_CONTENT_COLOR[this.level]
    }
  }
}
</script>
