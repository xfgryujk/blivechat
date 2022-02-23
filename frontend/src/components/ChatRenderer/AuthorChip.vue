<template>
  <yt-live-chat-author-chip>
    <span id="author-name" dir="auto" class="style-scope yt-live-chat-author-chip" :class="{ member: isInMemberMessage }"
      :type="authorTypeText"
    >
      <template>{{ authorName }}</template>
      <!-- 这里是已验证勋章 -->
      <span id="chip-badges" class="style-scope yt-live-chat-author-chip"></span>
    </span>
    <span id="chat-badges" class="style-scope yt-live-chat-author-chip">
      <author-badge v-if="isInMemberMessage" class="style-scope yt-live-chat-author-chip"
        :isAdmin="false" :privilegeType="privilegeType"
      ></author-badge>
      <template v-else>
        <author-badge v-if="authorType === AUTHRO_TYPE_ADMIN" class="style-scope yt-live-chat-author-chip"
          isAdmin :privilegeType="0"
        ></author-badge>
        <author-badge v-if="privilegeType > 0" class="style-scope yt-live-chat-author-chip"
          :isAdmin="false" :privilegeType="privilegeType"
        ></author-badge>
      </template>
    </span>
  </yt-live-chat-author-chip>
</template>

<script>
import AuthorBadge from './AuthorBadge'
import * as constants from './constants'

export default {
  name: 'AuthorChip',
  components: {
    AuthorBadge
  },
  props: {
    isInMemberMessage: Boolean,
    authorName: String,
    authorType: Number,
    privilegeType: Number
  },
  data() {
    return {
      AUTHRO_TYPE_ADMIN: constants.AUTHRO_TYPE_ADMIN
    }
  },
  computed: {
    authorTypeText() {
      return constants.AUTHOR_TYPE_TO_TEXT[this.authorType]
    }
  }
}
</script>

<style src="@/assets/css/youtube/yt-live-chat-author-chip.css"></style>
