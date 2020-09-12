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
              <yt-live-chat-author-chip class="style-scope yt-live-chat-membership-item-renderer">
                <span id="author-name" dir="auto" class="member style-scope yt-live-chat-author-chip">{{
                  authorName
                  }}<!-- 这里是已验证勋章 -->
                  <span id="chip-badges" class="style-scope yt-live-chat-author-chip"></span>
                </span>
                <span id="chat-badges" class="style-scope yt-live-chat-author-chip">
                  <author-badge class="style-scope yt-live-chat-author-chip"
                    :isAdmin="false" :privilegeType="privilegeType"
                  ></author-badge>
                </span>
              </yt-live-chat-author-chip>
            </div>
            <div id="header-subtext" class="style-scope yt-live-chat-membership-item-renderer">{{title}}</div>
          </div>
          <div id="timestamp" class="style-scope yt-live-chat-membership-item-renderer">{{timeText}}</div>
        </div>
      </div>
    </div>
  </yt-live-chat-membership-item-renderer>
</template>

<script>
import ImgShadow from './ImgShadow.vue'
import AuthorBadge from './AuthorBadge.vue'
import * as utils from '@/utils'

export default {
  name: 'MembershipItem',
  components: {
    ImgShadow,
    AuthorBadge
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
