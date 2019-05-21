<template>
  <yt-live-chat-text-message-renderer>
    <div id="author-photo">
      <img id="img" height="24" width="24" :src="avatarUrl" />
    </div>
    <div id="content">
      <span id="timestamp">{{time}}</span>
      <span id="author-name">{{authorName}}</span>
      <span id="message">{{content}}</span>
    </div>
  </yt-live-chat-text-message-renderer>
</template>

<script>
export default {
  name: 'TextMessage',
  props: {
    avatarUrl: String,
    time: String,
    authorName: String,
    content: String
  }
}
</script>
