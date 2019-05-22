<template>
  <yt-live-chat-legacy-paid-message-renderer>
    <div id="author-photo" :style="`background-image: url(${avatarUrl})`"></div>
    <div id="content">
      <div id="event-text">{{title}}</div>
      <div id="detail-text">{{content}}</div>
    </div>
  </yt-live-chat-legacy-paid-message-renderer>
</template>

<script>
export default {
  name: 'LegacyPaidMessage',
  props: {
    avatarUrl: String,
    title: String,
    content: String
  }
}
</script>
