<template>
  <yt-live-chat-text-message-renderer :author-type="authorTypeText">
    <yt-img-shadow id="author-photo" class="no-transition style-scope yt-live-chat-text-message-renderer" height="24"
      width="24" style="background-color: transparent;" loaded
    >
      <img id="img" class="style-scope yt-img-shadow" alt="" height="24" width="24" :src="avatarUrl">
    </yt-img-shadow>
    <div id="content" class="style-scope yt-live-chat-text-message-renderer">
      <span id="timestamp" class="style-scope yt-live-chat-text-message-renderer">{{time}}</span>
      <yt-live-chat-author-chip class="style-scope yt-live-chat-text-message-renderer">
        <span id="author-name" dir="auto" class="style-scope yt-live-chat-author-chip" :type="authorTypeText">
          {{authorName}}
          <span id="chip-badges" class="style-scope yt-live-chat-author-chip"></span>
        </span>
        <span id="chat-badges" class="style-scope yt-live-chat-author-chip"></span>
      </yt-live-chat-author-chip>
      <span id="message" class="style-scope yt-live-chat-text-message-renderer">{{content}}</span>
      <el-badge :value="repeated" :max="99" v-show="repeated > 1" class="style-scope yt-live-chat-text-message-renderer"
        :style="{'--repeated-mark-color': repeatedMarkColor}"
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
const REPEATED_MARK_COLOR_START = [64, 158, 255]
const REPEATED_MARK_COLOR_END = [245, 108, 108]

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
yt-live-chat-text-message-renderer>#content>.el-badge {
  margin-left: 10px;
}

yt-live-chat-text-message-renderer>#content>.el-badge .el-badge__content {
  font-size: 12px !important;
  line-height: 18px !important;
  text-shadow: none !important;
  font-family: sans-serif !important;
  background-color: var(--repeated-mark-color) !important;
}
</style>

<!-- yt-live-chat-text-message-renderer -->
<style>
canvas.yt-live-chat-text-message-renderer, caption.yt-live-chat-text-message-renderer, center.yt-live-chat-text-message-renderer, cite.yt-live-chat-text-message-renderer, code.yt-live-chat-text-message-renderer, dd.yt-live-chat-text-message-renderer, del.yt-live-chat-text-message-renderer, dfn.yt-live-chat-text-message-renderer, div.yt-live-chat-text-message-renderer, dl.yt-live-chat-text-message-renderer, dt.yt-live-chat-text-message-renderer, em.yt-live-chat-text-message-renderer, embed.yt-live-chat-text-message-renderer, fieldset.yt-live-chat-text-message-renderer, font.yt-live-chat-text-message-renderer, form.yt-live-chat-text-message-renderer, h1.yt-live-chat-text-message-renderer, h2.yt-live-chat-text-message-renderer, h3.yt-live-chat-text-message-renderer, h4.yt-live-chat-text-message-renderer, h5.yt-live-chat-text-message-renderer, h6.yt-live-chat-text-message-renderer, hr.yt-live-chat-text-message-renderer, i.yt-live-chat-text-message-renderer, iframe.yt-live-chat-text-message-renderer, img.yt-live-chat-text-message-renderer, ins.yt-live-chat-text-message-renderer, kbd.yt-live-chat-text-message-renderer, label.yt-live-chat-text-message-renderer, legend.yt-live-chat-text-message-renderer, li.yt-live-chat-text-message-renderer, menu.yt-live-chat-text-message-renderer, object.yt-live-chat-text-message-renderer, ol.yt-live-chat-text-message-renderer, p.yt-live-chat-text-message-renderer, pre.yt-live-chat-text-message-renderer, q.yt-live-chat-text-message-renderer, s.yt-live-chat-text-message-renderer, samp.yt-live-chat-text-message-renderer, small.yt-live-chat-text-message-renderer, span.yt-live-chat-text-message-renderer, strike.yt-live-chat-text-message-renderer, strong.yt-live-chat-text-message-renderer, sub.yt-live-chat-text-message-renderer, sup.yt-live-chat-text-message-renderer, table.yt-live-chat-text-message-renderer, tbody.yt-live-chat-text-message-renderer, td.yt-live-chat-text-message-renderer, tfoot.yt-live-chat-text-message-renderer, th.yt-live-chat-text-message-renderer, thead.yt-live-chat-text-message-renderer, tr.yt-live-chat-text-message-renderer, tt.yt-live-chat-text-message-renderer, u.yt-live-chat-text-message-renderer, ul.yt-live-chat-text-message-renderer, var.yt-live-chat-text-message-renderer {
  margin: 0;
  padding: 0;
  border: 0;
  background: transparent;
}

.yt-live-chat-text-message-renderer[hidden] {
  display: none !important;
}

#timestamp.yt-live-chat-text-message-renderer {
  display: var(--yt-live-chat-item-timestamp-display, inline);
  margin: var(--yt-live-chat-item-timestamp-margin, 0 8px 0 0);
  color: var(--yt-live-chat-tertiary-text-color);
  font-size: 11px;
}

#author-photo.yt-live-chat-text-message-renderer {
  display: block;
  margin-right: 16px;
  overflow: hidden;
  border-radius: 50%;
  -ms-flex: none;
  -webkit-flex: none;
  flex: none;
}

#menu-button.yt-live-chat-text-message-renderer {
  width: 40px;
  height: 40px;
  padding: 8px;
}

#menu.yt-live-chat-text-message-renderer {
  position: absolute;
  top: 0;
  bottom: 0;
  right: 0;
  transform: translateX(100px);
}

yt-live-chat-text-message-renderer:hover #menu.yt-live-chat-text-message-renderer, yt-live-chat-text-message-renderer[menu-visible] #menu.yt-live-chat-text-message-renderer {
  transform: none;
}

yt-live-chat-text-message-renderer:focus-within #menu.yt-live-chat-text-message-renderer {
  transform: none;
}

#inline-action-button-container.yt-live-chat-text-message-renderer {
  position: absolute;
  top: -4px;
  right: 0;
  bottom: -4px;
  left: 0;
  background-color: var(--yt-live-chat-moderation-mode-hover-background-color);
  display: none;
  -ms-flex-align: center;
  -webkit-align-items: center;
  align-items: center;
  -ms-flex-pack: center;
  -webkit-justify-content: center;
  justify-content: center;
}

yt-live-chat-text-message-renderer[has-inline-action-buttons]:hover #inline-action-button-container.yt-live-chat-text-message-renderer {
  display: flex;
  -ms-flex-direction: row;
  -webkit-flex-direction: row;
  flex-direction: row;
  display: var(--yt-live-chat-inline-action-button-container-display, none);
}

yt-live-chat-text-message-renderer[has-inline-action-buttons][hide-inline-action-buttons]:hover #inline-action-button-container.yt-live-chat-text-message-renderer {
  display: none;
}

yt-live-chat-text-message-renderer[has-inline-action-buttons]:hover #menu.yt-live-chat-text-message-renderer {
  display: var(--yt-live-chat-item-with-inline-actions-context-menu-display, block);
}

#inline-action-buttons.yt-live-chat-text-message-renderer>*.yt-live-chat-text-message-renderer, #additional-inline-action-buttons.yt-live-chat-text-message-renderer>*.yt-live-chat-text-message-renderer {
  --yt-button-icon-size: 36px;
  --yt-button-icon-padding: 6px;
  color: hsl(0, 0%, 100%);
  border-radius: 2px;
}

#inline-action-buttons.yt-live-chat-text-message-renderer>*.yt-live-chat-text-message-renderer {
  background: hsla(0, 0%, 6.7%, .8);
}

#inline-action-buttons.yt-live-chat-text-message-renderer>.yt-live-chat-text-message-renderer:hover {
  background: hsl(0, 0%, 6.7%);
}

#additional-inline-action-buttons.yt-live-chat-text-message-renderer>*.yt-live-chat-text-message-renderer {
  color: var(--yt-live-chat-additional-inline-action-button-color);
  background: var(--yt-live-chat-additional-inline-action-button-background-color);
}

#additional-inline-action-buttons.yt-live-chat-text-message-renderer>.yt-live-chat-text-message-renderer:hover {
  background: var(--yt-live-chat-additional-inline-action-button-background-color-hover);
}

#additional-inline-action-buttons.yt-live-chat-text-message-renderer:not(:empty) {
  margin-left: 32px;
}

#inline-action-buttons.yt-live-chat-text-message-renderer>*.yt-live-chat-text-message-renderer:not(:first-child), #additional-inline-action-buttons.yt-live-chat-text-message-renderer>*.yt-live-chat-text-message-renderer:not(:first-child) {
  margin-left: 8px;
}

yt-live-chat-text-message-renderer {
  position: relative;
  font-size: 13px;
  padding: 4px 24px;
  overflow: hidden;
  --yt-endpoint-color: var(--yt-live-chat-primary-text-color, hsl(0, 0%, 6.7%));
  --yt-endpoint-hover-color: var(--yt-live-chat-primary-text-color, var(--yt-endpoint-color));
  display: flex;
  -ms-flex-direction: row;
  -webkit-flex-direction: row;
  flex-direction: row;
  -ms-flex-align: start;
  -webkit-align-items: flex-start;
  align-items: flex-start;
}

yt-live-chat-text-message-renderer:hover {
  overflow: initial;
}

yt-live-chat-text-message-renderer[author-is-owner] {
  background-color: var(--yt-live-chat-message-highlight-background-color);
}

#content.yt-live-chat-text-message-renderer {
  -ms-align-self: center;
  -webkit-align-self: center;
  align-self: center;
  min-width: 0;
}

yt-live-chat-author-chip.yt-live-chat-text-message-renderer {
  margin-right: 8px;
}

#message.yt-live-chat-text-message-renderer {
  color: var(--yt-live-chat-primary-text-color, var(--yt-primary-text-color));
  line-height: 16px;
  overflow: hidden;
  overflow-wrap: break-word;
  word-wrap: break-word;
  word-break: break-word;
  font-style: var(--yt-live-chat-text-message-renderer-message-message-style_-_font-style);
  opacity: var(--yt-live-chat-text-message-renderer-message-message-style_-_opacity);
}

#message.yt-live-chat-text-message-renderer .emoji.yt-live-chat-text-message-renderer {
  width: var(--yt-live-chat-emoji-size);
  height: var(--yt-live-chat-emoji-size);
  margin: -1px 2px 1px 2px;
  vertical-align: middle;
}

a.yt-live-chat-text-message-renderer {
  display: inline;
  text-decoration: underline;
}

#message.yt-live-chat-text-message-renderer a.yt-live-chat-text-message-renderer {
  display: inline;
  text-decoration: underline;
  word-break: break-all;
}

#message.yt-live-chat-text-message-renderer a.yt-live-chat-text-message-renderer .mention.yt-live-chat-text-message-renderer {
  text-decoration: underline;
}

#show-original.yt-live-chat-text-message-renderer {
  margin-left: 2px;
}

#message.yt-live-chat-text-message-renderer:empty, #deleted-state.yt-live-chat-text-message-renderer:empty, #show-original.yt-live-chat-text-message-renderer:empty, yt-live-chat-text-message-renderer[show-original] #deleted-state.yt-live-chat-text-message-renderer, yt-live-chat-text-message-renderer[show-original] #show-original.yt-live-chat-text-message-renderer, yt-live-chat-text-message-renderer[is-deleted]:not([show-original]) #message.yt-live-chat-text-message-renderer {
  display: none;
}

#menu.yt-live-chat-text-message-renderer {
  color: var(--yt-live-chat-secondary-text-color);
  background: linear-gradient(to right, transparent, var(--yt-live-chat-background-color, hsl(0, 0%, 100%)) 100%);
}

.mention.yt-live-chat-text-message-renderer {
  background: var(--yt-live-chat-mention-background-color);
  color: var(--yt-live-chat-mention-text-color);
  padding: 2px 4px;
  border-radius: 2px;
}

#deleted-state.yt-live-chat-text-message-renderer, #show-original.yt-live-chat-text-message-renderer, yt-live-chat-text-message-renderer[is-deleted] #message.yt-live-chat-text-message-renderer {
  font-style: italic;
  color: var(--yt-live-chat-deleted-message-color, rgba(0, 0, 0, 0.5));
}

yt-live-chat-text-message-renderer[show-bar]::before {
  content: '';
  position: absolute;
  display: block;
  left: 8px;
  top: 4px;
  bottom: 4px;
  width: 4px;
  box-sizing: border-box;
  border-radius: 2px;
}

yt-live-chat-text-message-renderer[is-deleted]::before {
  background: var(--yt-live-chat-deleted-message-bar-color, rgba(0, 0, 0, 0.5));
}

yt-live-chat-text-message-renderer[is-dimmed] #message.yt-live-chat-text-message-renderer {
  opacity: 0.25;
}

yt-live-chat-text-message-renderer[is-dimmed]::before {
  background: var(--yt-live-chat-error-message-color, #f44336);
}
</style>

<!-- yt-img-shadow -->
<style>
canvas.yt-img-shadow, caption.yt-img-shadow, center.yt-img-shadow, cite.yt-img-shadow, code.yt-img-shadow, dd.yt-img-shadow, del.yt-img-shadow, dfn.yt-img-shadow, div.yt-img-shadow, dl.yt-img-shadow, dt.yt-img-shadow, em.yt-img-shadow, embed.yt-img-shadow, fieldset.yt-img-shadow, font.yt-img-shadow, form.yt-img-shadow, h1.yt-img-shadow, h2.yt-img-shadow, h3.yt-img-shadow, h4.yt-img-shadow, h5.yt-img-shadow, h6.yt-img-shadow, hr.yt-img-shadow, i.yt-img-shadow, iframe.yt-img-shadow, img.yt-img-shadow, ins.yt-img-shadow, kbd.yt-img-shadow, label.yt-img-shadow, legend.yt-img-shadow, li.yt-img-shadow, menu.yt-img-shadow, object.yt-img-shadow, ol.yt-img-shadow, p.yt-img-shadow, pre.yt-img-shadow, q.yt-img-shadow, s.yt-img-shadow, samp.yt-img-shadow, small.yt-img-shadow, span.yt-img-shadow, strike.yt-img-shadow, strong.yt-img-shadow, sub.yt-img-shadow, sup.yt-img-shadow, table.yt-img-shadow, tbody.yt-img-shadow, td.yt-img-shadow, tfoot.yt-img-shadow, th.yt-img-shadow, thead.yt-img-shadow, tr.yt-img-shadow, tt.yt-img-shadow, u.yt-img-shadow, ul.yt-img-shadow, var.yt-img-shadow {
  margin: 0;
  padding: 0;
  border: 0;
  background: transparent;
}

.yt-img-shadow[hidden] {
  display: none !important;
}

yt-img-shadow {
  display: inline-block;
  opacity: 0;
  transition: opacity 0.2s;
  -ms-flex: none;
  -webkit-flex: none;
  flex: none;
}

yt-img-shadow.no-transition {
  opacity: 1;
  transition: none;
}

yt-img-shadow.with-placeholder {
  background-color: transparent;
  min-height: unset;
  min-width: unset;
}

yt-img-shadow[loaded] {
  opacity: 1;
}

yt-img-shadow.empty img.yt-img-shadow {
  visibility: hidden;
}

yt-img-shadow[object-fit="FILL"] img.yt-img-shadow, yt-img-shadow[fit] img.yt-img-shadow {
  width: 100%;
  height: 100%;
}

yt-img-shadow[object-fit="COVER"] img.yt-img-shadow {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

yt-img-shadow[object-fit="CONTAIN"] img.yt-img-shadow {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

yt-img-shadow[object-position="LEFT"] img.yt-img-shadow {
  object-position: left;
}

img.yt-img-shadow {
  display: block;
  margin-left: auto;
  margin-right: auto;
  max-height: none;
  max-width: 100%;
  border-radius: none;
}
</style>

<!-- yt-live-chat-author-chip -->
<style>
canvas.yt-live-chat-author-chip, caption.yt-live-chat-author-chip, center.yt-live-chat-author-chip, cite.yt-live-chat-author-chip, code.yt-live-chat-author-chip, dd.yt-live-chat-author-chip, del.yt-live-chat-author-chip, dfn.yt-live-chat-author-chip, div.yt-live-chat-author-chip, dl.yt-live-chat-author-chip, dt.yt-live-chat-author-chip, em.yt-live-chat-author-chip, embed.yt-live-chat-author-chip, fieldset.yt-live-chat-author-chip, font.yt-live-chat-author-chip, form.yt-live-chat-author-chip, h1.yt-live-chat-author-chip, h2.yt-live-chat-author-chip, h3.yt-live-chat-author-chip, h4.yt-live-chat-author-chip, h5.yt-live-chat-author-chip, h6.yt-live-chat-author-chip, hr.yt-live-chat-author-chip, i.yt-live-chat-author-chip, iframe.yt-live-chat-author-chip, img.yt-live-chat-author-chip, ins.yt-live-chat-author-chip, kbd.yt-live-chat-author-chip, label.yt-live-chat-author-chip, legend.yt-live-chat-author-chip, li.yt-live-chat-author-chip, menu.yt-live-chat-author-chip, object.yt-live-chat-author-chip, ol.yt-live-chat-author-chip, p.yt-live-chat-author-chip, pre.yt-live-chat-author-chip, q.yt-live-chat-author-chip, s.yt-live-chat-author-chip, samp.yt-live-chat-author-chip, small.yt-live-chat-author-chip, span.yt-live-chat-author-chip, strike.yt-live-chat-author-chip, strong.yt-live-chat-author-chip, sub.yt-live-chat-author-chip, sup.yt-live-chat-author-chip, table.yt-live-chat-author-chip, tbody.yt-live-chat-author-chip, td.yt-live-chat-author-chip, tfoot.yt-live-chat-author-chip, th.yt-live-chat-author-chip, thead.yt-live-chat-author-chip, tr.yt-live-chat-author-chip, tt.yt-live-chat-author-chip, u.yt-live-chat-author-chip, ul.yt-live-chat-author-chip, var.yt-live-chat-author-chip {
  margin: 0;
  padding: 0;
  border: 0;
  background: transparent;
}

.yt-live-chat-author-chip[hidden] {
  display: none !important;
}

yt-live-chat-author-chip {
  display: inline-flex;
  -ms-flex-align: baseline;
  -webkit-align-items: baseline;
  align-items: baseline;
}

#author-name.yt-live-chat-author-chip {
  box-sizing: border-box;
  border-radius: 2px;
  color: var(--yt-live-chat-secondary-text-color);
  font-weight: 500;
}

yt-live-chat-author-chip[is-highlighted] #author-name.yt-live-chat-author-chip {
  padding: 2px 4px;
  color: var(--yt-live-chat-author-chip-verified-text-color);
  background-color: var(--yt-live-chat-author-chip-verified-background-color);
}

#author-name.yt-live-chat-author-chip[type='moderator'] {
  color: var(--yt-live-chat-moderator-color);
}

yt-live-chat-author-chip[is-highlighted] #author-name.yt-live-chat-author-chip[type='owner'], #author-name.yt-live-chat-author-chip[type='owner'] {
  background-color: #ffd600;
  color: var(--yt-live-chat-author-chip-owner-text-color);
}

#author-name.yt-live-chat-author-chip[type='member'] {
  color: var(--yt-live-chat-sponsor-color);
}

#chip-badges.yt-live-chat-author-chip:empty {
  display: none;
}

yt-live-chat-author-chip[is-highlighted] #chat-badges.yt-live-chat-author-chip:not(:empty) {
  margin-left: 1px;
}

yt-live-chat-author-badge-renderer.yt-live-chat-author-chip {
  margin: 0 0 0 2px;
  vertical-align: sub;
}

yt-live-chat-author-chip[is-highlighted] #chip-badges.yt-live-chat-author-chip yt-live-chat-author-badge-renderer.yt-live-chat-author-chip {
  color: inherit;
}

#chip-badges.yt-live-chat-author-chip yt-live-chat-author-badge-renderer.yt-live-chat-author-chip:last-of-type {
  margin-right: -2px;
}
</style>
