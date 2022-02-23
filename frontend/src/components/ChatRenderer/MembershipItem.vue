<template>
  <yt-live-chat-membership-item-renderer class="style-scope yt-live-chat-item-list-renderer" show-only-header>
    <div id="card" class="style-scope yt-live-chat-membership-item-renderer">
      <div id="header" class="style-scope yt-live-chat-membership-item-renderer">
        <img-shadow id="author-photo" height="40" width="40" class="style-scope yt-live-chat-membership-item-renderer"
          :imgUrl="avatarUrl"
        ></img-shadow>
        <div id="header-content" class="style-scope yt-live-chat-membership-item-renderer">
          <div id="header-content-primary-column" class="style-scope yt-live-chat-membership-item-renderer">
            <div id="header-content-inner-column" class="style-scope yt-live-chat-membership-item-renderer">
              <author-chip class="style-scope yt-live-chat-membership-item-renderer"
                isInMemberMessage :authorName="authorName" :authorType="0" :privilegeType="privilegeType"
              ></author-chip>
            </div>
            <div id="header-subtext" class="style-scope yt-live-chat-membership-item-renderer">{{ title }}</div>
          </div>
          <div id="timestamp" class="style-scope yt-live-chat-membership-item-renderer">{{ timeText }}</div>
        </div>
      </div>
    </div>
  </yt-live-chat-membership-item-renderer>
</template>

<script>
import ImgShadow from './ImgShadow'
import AuthorChip from './AuthorChip'
import * as utils from '@/utils'

export default {
  name: 'MembershipItem',
  components: {
    ImgShadow,
    AuthorChip
  },
  props: {
    avatarUrl: String,
    authorName: String,
    privilegeType: Number,
    title: String,
    time: Date
  },
  computed: {
    timeText() {
      return utils.getTimeTextHourMin(this.time)
    }
  }
}
</script>

<style src="@/assets/css/youtube/yt-live-chat-membership-item-renderer.css"></style>
