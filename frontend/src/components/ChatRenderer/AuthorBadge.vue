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

<!-- yt-live-chat-author-badge-renderer -->
<style>
canvas.yt-live-chat-author-badge-renderer, caption.yt-live-chat-author-badge-renderer, center.yt-live-chat-author-badge-renderer, cite.yt-live-chat-author-badge-renderer, code.yt-live-chat-author-badge-renderer, dd.yt-live-chat-author-badge-renderer, del.yt-live-chat-author-badge-renderer, dfn.yt-live-chat-author-badge-renderer, div.yt-live-chat-author-badge-renderer, dl.yt-live-chat-author-badge-renderer, dt.yt-live-chat-author-badge-renderer, em.yt-live-chat-author-badge-renderer, embed.yt-live-chat-author-badge-renderer, fieldset.yt-live-chat-author-badge-renderer, font.yt-live-chat-author-badge-renderer, form.yt-live-chat-author-badge-renderer, h1.yt-live-chat-author-badge-renderer, h2.yt-live-chat-author-badge-renderer, h3.yt-live-chat-author-badge-renderer, h4.yt-live-chat-author-badge-renderer, h5.yt-live-chat-author-badge-renderer, h6.yt-live-chat-author-badge-renderer, hr.yt-live-chat-author-badge-renderer, i.yt-live-chat-author-badge-renderer, iframe.yt-live-chat-author-badge-renderer, img.yt-live-chat-author-badge-renderer, ins.yt-live-chat-author-badge-renderer, kbd.yt-live-chat-author-badge-renderer, label.yt-live-chat-author-badge-renderer, legend.yt-live-chat-author-badge-renderer, li.yt-live-chat-author-badge-renderer, menu.yt-live-chat-author-badge-renderer, object.yt-live-chat-author-badge-renderer, ol.yt-live-chat-author-badge-renderer, p.yt-live-chat-author-badge-renderer, pre.yt-live-chat-author-badge-renderer, q.yt-live-chat-author-badge-renderer, s.yt-live-chat-author-badge-renderer, samp.yt-live-chat-author-badge-renderer, small.yt-live-chat-author-badge-renderer, span.yt-live-chat-author-badge-renderer, strike.yt-live-chat-author-badge-renderer, strong.yt-live-chat-author-badge-renderer, sub.yt-live-chat-author-badge-renderer, sup.yt-live-chat-author-badge-renderer, table.yt-live-chat-author-badge-renderer, tbody.yt-live-chat-author-badge-renderer, td.yt-live-chat-author-badge-renderer, tfoot.yt-live-chat-author-badge-renderer, th.yt-live-chat-author-badge-renderer, thead.yt-live-chat-author-badge-renderer, tr.yt-live-chat-author-badge-renderer, tt.yt-live-chat-author-badge-renderer, u.yt-live-chat-author-badge-renderer, ul.yt-live-chat-author-badge-renderer, var.yt-live-chat-author-badge-renderer {
  margin: 0;
  padding: 0;
  border: 0;
  background: transparent;
}

.yt-live-chat-author-badge-renderer[hidden] {
  display: none !important;
}

yt-live-chat-author-badge-renderer {
  display: inline-block;
}

yt-live-chat-author-badge-renderer[type='moderator'] {
  color: var(--yt-live-chat-moderator-color, #5e84f1);
}

yt-live-chat-author-badge-renderer[type='owner'] {
  color: var(--yt-live-chat-owner-color, #ffd600);
}

yt-live-chat-author-badge-renderer[type='member'] {
  color: var(--yt-live-chat-sponsor-color, #107516);
}

yt-live-chat-author-badge-renderer[type='verified'] {
  color: #999;
}

img.yt-live-chat-author-badge-renderer, yt-icon.yt-live-chat-author-badge-renderer {
  display: block;
  width: 16px;
  height: 16px;
}
</style>

<!-- yt-icon -->
<style>
canvas.yt-icon, caption.yt-icon, center.yt-icon, cite.yt-icon, code.yt-icon, dd.yt-icon, del.yt-icon, dfn.yt-icon, div.yt-icon, dl.yt-icon, dt.yt-icon, em.yt-icon, embed.yt-icon, fieldset.yt-icon, font.yt-icon, form.yt-icon, h1.yt-icon, h2.yt-icon, h3.yt-icon, h4.yt-icon, h5.yt-icon, h6.yt-icon, hr.yt-icon, i.yt-icon, iframe.yt-icon, img.yt-icon, ins.yt-icon, kbd.yt-icon, label.yt-icon, legend.yt-icon, li.yt-icon, menu.yt-icon, object.yt-icon, ol.yt-icon, p.yt-icon, pre.yt-icon, q.yt-icon, s.yt-icon, samp.yt-icon, small.yt-icon, span.yt-icon, strike.yt-icon, strong.yt-icon, sub.yt-icon, sup.yt-icon, table.yt-icon, tbody.yt-icon, td.yt-icon, tfoot.yt-icon, th.yt-icon, thead.yt-icon, tr.yt-icon, tt.yt-icon, u.yt-icon, ul.yt-icon, var.yt-icon {
  margin: 0;
  padding: 0;
  border: 0;
  background: transparent;
}

.yt-icon[hidden] {
  display: none !important;
}

yt-icon, .yt-icon-container.yt-icon {
  display: inline-flex;
  -ms-flex-align: center;
  -webkit-align-items: center;
  align-items: center;
  -ms-flex-pack: center;
  -webkit-justify-content: center;
  justify-content: center;
  position: relative;
  vertical-align: middle;
  fill: currentcolor;
  stroke: none;
  width: var(--iron-icon-width, 24px);
  height: var(--iron-icon-height, 24px);
}

yt-icon.external-container {
  display: none !important;
}
</style>
