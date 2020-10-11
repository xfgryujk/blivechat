<template>
  <yt-live-chat-author-badge-renderer :type="authorTypeText" v-if="isAdmin || privilegeType > 0">
    <el-tooltip :content="readableAuthorTypeText" placement="top">
      <div id="image" class="style-scope yt-live-chat-author-badge-renderer">
        <yt-icon v-if="isAdmin" class="style-scope yt-live-chat-author-badge-renderer">
          <svg viewBox="0 0 16 16" class="style-scope yt-icon" preserveAspectRatio="xMidYMid meet" focusable="false"
            style="pointer-events: none; display: block; width: 100%; height: 100%;"
          >
            <g class="style-scope yt-icon">
              <path class="style-scope yt-icon"
                d="M9.64589146,7.05569719 C9.83346524,6.562372 9.93617022,6.02722257 9.93617022,5.46808511 C9.93617022,3.00042984 7.93574038,1 5.46808511,1 C4.90894765,1 4.37379823,1.10270499 3.88047304,1.29027875 L6.95744681,4.36725249 L4.36725255,6.95744681 L1.29027875,3.88047305 C1.10270498,4.37379824 1,4.90894766 1,5.46808511 C1,7.93574038 3.00042984,9.93617022 5.46808511,9.93617022 C6.02722256,9.93617022 6.56237198,9.83346524 7.05569716,9.64589147 L12.4098057,15 L15,12.4098057 L9.64589146,7.05569719 Z"
              ></path>
            </g>
          </svg>
        </yt-icon>
        <img v-else :src="`/static/img/icons/guard-level-${privilegeType}.png`"
          class="style-scope yt-live-chat-author-badge-renderer" :alt="readableAuthorTypeText">
      </div>
    </el-tooltip>
  </yt-live-chat-author-badge-renderer>
</template>

<script>
import * as constants from './constants'

export default {
  name: 'AuthorBadge',
  props: {
    isAdmin: Boolean,
    privilegeType: Number
  },
  computed: {
    authorTypeText() {
      if (this.isAdmin) {
        return 'moderator'
      }
      return this.privilegeType > 0 ? 'member' : ''
    },
    readableAuthorTypeText() {
      if (this.isAdmin) {
        return '管理员'
      }
      return constants.GUARD_LEVEL_TO_TEXT[this.privilegeType]
    }
  }
}
</script>

<style src="@/assets/css/youtube/yt-live-chat-author-badge-renderer.css"></style>
<style src="@/assets/css/youtube/yt-icon.css"></style>
