<template>
  <yt-live-chat-text-message-renderer :author-type="authorTypeText">
    <div id="author-photo" :style="`background-image: url(${avatarUrl})`"></div>
    <div id="content">
      <span id="timestamp">{{time}}</span>
      <span id="author-name" :type="authorTypeText">{{authorName}}</span>
      <span id="message">{{content}}</span>
      <el-badge :value="repeated" :max="99" v-show="repeated > 1"
        :style="`--repeated-mark-color: ${repeatedMarkColor}`"
      ></el-badge>
    </div>
  </yt-live-chat-text-message-renderer>
</template>

<script>
const AUTHOR_TYPE_TO_TEXT = [
  '',
  'member', // 舰队
  'moderator', // 房管
  'owner' // 主播
]
const REPEATED_MARK_COLOR_START = [0x21, 0x96, 0xF3]
const REPEATED_MARK_COLOR_END = [0xFF, 0x57, 0x22]

export default {
  name: 'TextMessage',
  props: {
    avatarUrl: String,
    time: String,
    authorName: String,
    authorType: Number,
    content: String,
    repeated: Number
  },
  computed: {
    authorTypeText() {
      return AUTHOR_TYPE_TO_TEXT[this.authorType]
    },
    repeatedMarkColor() {
      let color
      if (this.repeated <= 2) {
        color = REPEATED_MARK_COLOR_START
      } else if (this.repeated >= 10) {
        color = REPEATED_MARK_COLOR_END
      } else {
        color = [0, 0, 0]
        let t = (this.repeated - 2) / (10 - 2)
        for (let i = 0; i < 3; i++) {
          color[i] = REPEATED_MARK_COLOR_START[i] + (REPEATED_MARK_COLOR_END[i] - REPEATED_MARK_COLOR_START[i]) * t
        }
      }
      return `rgb(${color.join(', ')})`
    }
  }
}
</script>

<style>
yt-live-chat-text-message-renderer #content .el-badge {
  margin-left: 0.5em;
}

yt-live-chat-text-message-renderer #content .el-badge * {
  text-shadow: none !important;
  font-family: sans-serif !important;
  background-color: var(--repeated-mark-color) !important;
}
</style>
