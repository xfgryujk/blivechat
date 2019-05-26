<template>
  <yt-live-chat-text-message-renderer :author-type="authorTypeText">
    <div id="author-photo" :style="`background-image: url(${avatarUrl})`"></div>
    <div id="content">
      <span id="timestamp">{{time}}</span>
      <span id="author-name" :type="authorTypeText">{{authorName}}</span>
      <span id="message">{{content}}</span>
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

export default {
  name: 'TextMessage',
  props: {
    avatarUrl: String,
    time: String,
    authorName: String,
    authorType: Number,
    content: String
  },
  computed: {
    authorTypeText() {
      return AUTHOR_TYPE_TO_TEXT[this.authorType]
    }
  }
}
</script>
