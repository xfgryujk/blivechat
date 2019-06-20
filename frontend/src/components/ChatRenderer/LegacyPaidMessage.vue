<template>
  <yt-live-chat-legacy-paid-message-renderer class="style-scope yt-live-chat-item-list-renderer">
    <div id="card" class="style-scope yt-live-chat-legacy-paid-message-renderer">
      <img-shadow id="author-photo" height="40" width="40" class="style-scope yt-live-chat-legacy-paid-message-renderer"
        :imgUrl="avatarUrl"
      ></img-shadow>
      <div id="content" class="style-scope yt-live-chat-legacy-paid-message-renderer">
        <div id="content-primary-column" class="style-scope yt-live-chat-legacy-paid-message-renderer">
          <div id="author-name" class="style-scope yt-live-chat-legacy-paid-message-renderer">{{authorName}}</div>
          <div id="event-text" class="style-scope yt-live-chat-legacy-paid-message-renderer">{{title}}</div>
          <div id="detail-text" class="style-scope yt-live-chat-legacy-paid-message-renderer">{{content}}</div>
        </div>
        <div id="timestamp" class="style-scope yt-live-chat-legacy-paid-message-renderer">{{time}}</div>
      </div>
    </div>
    <div id="inline-action-button-container" class="style-scope yt-live-chat-legacy-paid-message-renderer" aria-hidden="true">
      <div id="inline-action-buttons" class="style-scope yt-live-chat-legacy-paid-message-renderer"></div>
    </div>
  </yt-live-chat-legacy-paid-message-renderer>
</template>

<script>
import ImgShadow from './ImgShadow.vue'

export default {
  name: 'LegacyPaidMessage',
  components: {
    ImgShadow
  },
  props: {
    avatarUrl: String,
    authorName: String,
    title: String,
    content: String,
    time: String
  }
}
</script>

<!-- yt-live-chat-legacy-paid-message-renderer -->
<style>
canvas.yt-live-chat-legacy-paid-message-renderer, caption.yt-live-chat-legacy-paid-message-renderer, center.yt-live-chat-legacy-paid-message-renderer, cite.yt-live-chat-legacy-paid-message-renderer, code.yt-live-chat-legacy-paid-message-renderer, dd.yt-live-chat-legacy-paid-message-renderer, del.yt-live-chat-legacy-paid-message-renderer, dfn.yt-live-chat-legacy-paid-message-renderer, div.yt-live-chat-legacy-paid-message-renderer, dl.yt-live-chat-legacy-paid-message-renderer, dt.yt-live-chat-legacy-paid-message-renderer, em.yt-live-chat-legacy-paid-message-renderer, embed.yt-live-chat-legacy-paid-message-renderer, fieldset.yt-live-chat-legacy-paid-message-renderer, font.yt-live-chat-legacy-paid-message-renderer, form.yt-live-chat-legacy-paid-message-renderer, h1.yt-live-chat-legacy-paid-message-renderer, h2.yt-live-chat-legacy-paid-message-renderer, h3.yt-live-chat-legacy-paid-message-renderer, h4.yt-live-chat-legacy-paid-message-renderer, h5.yt-live-chat-legacy-paid-message-renderer, h6.yt-live-chat-legacy-paid-message-renderer, hr.yt-live-chat-legacy-paid-message-renderer, i.yt-live-chat-legacy-paid-message-renderer, iframe.yt-live-chat-legacy-paid-message-renderer, img.yt-live-chat-legacy-paid-message-renderer, ins.yt-live-chat-legacy-paid-message-renderer, kbd.yt-live-chat-legacy-paid-message-renderer, label.yt-live-chat-legacy-paid-message-renderer, legend.yt-live-chat-legacy-paid-message-renderer, li.yt-live-chat-legacy-paid-message-renderer, menu.yt-live-chat-legacy-paid-message-renderer, object.yt-live-chat-legacy-paid-message-renderer, ol.yt-live-chat-legacy-paid-message-renderer, p.yt-live-chat-legacy-paid-message-renderer, pre.yt-live-chat-legacy-paid-message-renderer, q.yt-live-chat-legacy-paid-message-renderer, s.yt-live-chat-legacy-paid-message-renderer, samp.yt-live-chat-legacy-paid-message-renderer, small.yt-live-chat-legacy-paid-message-renderer, span.yt-live-chat-legacy-paid-message-renderer, strike.yt-live-chat-legacy-paid-message-renderer, strong.yt-live-chat-legacy-paid-message-renderer, sub.yt-live-chat-legacy-paid-message-renderer, sup.yt-live-chat-legacy-paid-message-renderer, table.yt-live-chat-legacy-paid-message-renderer, tbody.yt-live-chat-legacy-paid-message-renderer, td.yt-live-chat-legacy-paid-message-renderer, tfoot.yt-live-chat-legacy-paid-message-renderer, th.yt-live-chat-legacy-paid-message-renderer, thead.yt-live-chat-legacy-paid-message-renderer, tr.yt-live-chat-legacy-paid-message-renderer, tt.yt-live-chat-legacy-paid-message-renderer, u.yt-live-chat-legacy-paid-message-renderer, ul.yt-live-chat-legacy-paid-message-renderer, var.yt-live-chat-legacy-paid-message-renderer {
  margin: 0;
  padding: 0;
  border: 0;
  background: transparent;
}

.yt-live-chat-legacy-paid-message-renderer[hidden] {
  display: none !important;
}

#timestamp.yt-live-chat-legacy-paid-message-renderer {
  display: var(--yt-live-chat-item-timestamp-display, inline);
  margin: var(--yt-live-chat-item-timestamp-margin, 0 8px 0 0);
  color: var(--yt-live-chat-tertiary-text-color);
  font-size: 11px;
}

#author-photo.yt-live-chat-legacy-paid-message-renderer {
  display: block;
  margin-right: 16px;
  overflow: hidden;
  border-radius: 50%;
  -ms-flex: none;
  -webkit-flex: none;
  flex: none;
}

#menu-button.yt-live-chat-legacy-paid-message-renderer {
  width: 40px;
  height: 40px;
  padding: 8px;
}

#menu.yt-live-chat-legacy-paid-message-renderer {
  position: absolute;
  top: 0;
  bottom: 0;
  right: 0;
  transform: translateX(100px);
}

yt-live-chat-legacy-paid-message-renderer:hover #menu.yt-live-chat-legacy-paid-message-renderer, yt-live-chat-legacy-paid-message-renderer[menu-visible] #menu.yt-live-chat-legacy-paid-message-renderer {
  transform: none;
}

yt-live-chat-legacy-paid-message-renderer:focus-within #menu.yt-live-chat-legacy-paid-message-renderer {
  transform: none;
}

#inline-action-button-container.yt-live-chat-legacy-paid-message-renderer {
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

yt-live-chat-legacy-paid-message-renderer[has-inline-action-buttons]:hover #inline-action-button-container.yt-live-chat-legacy-paid-message-renderer {
  display: flex;
  -ms-flex-direction: row;
  -webkit-flex-direction: row;
  flex-direction: row;
  display: var(--yt-live-chat-inline-action-button-container-display, none);
}

yt-live-chat-legacy-paid-message-renderer[has-inline-action-buttons][hide-inline-action-buttons]:hover #inline-action-button-container.yt-live-chat-legacy-paid-message-renderer {
  display: none;
}

yt-live-chat-legacy-paid-message-renderer[has-inline-action-buttons]:hover #menu.yt-live-chat-legacy-paid-message-renderer {
  display: var(--yt-live-chat-item-with-inline-actions-context-menu-display, block);
}

#inline-action-buttons.yt-live-chat-legacy-paid-message-renderer>*.yt-live-chat-legacy-paid-message-renderer, #additional-inline-action-buttons.yt-live-chat-legacy-paid-message-renderer>*.yt-live-chat-legacy-paid-message-renderer {
  --yt-button-icon-size: 36px;
  --yt-button-icon-padding: 6px;
  color: hsl(0, 0%, 100%);
  border-radius: 2px;
}

#inline-action-buttons.yt-live-chat-legacy-paid-message-renderer>*.yt-live-chat-legacy-paid-message-renderer {
  background: hsla(0, 0%, 6.7%, .8);
}

#inline-action-buttons.yt-live-chat-legacy-paid-message-renderer>.yt-live-chat-legacy-paid-message-renderer:hover {
  background: hsl(0, 0%, 6.7%);
}

#additional-inline-action-buttons.yt-live-chat-legacy-paid-message-renderer>*.yt-live-chat-legacy-paid-message-renderer {
  color: var(--yt-live-chat-additional-inline-action-button-color);
  background: var(--yt-live-chat-additional-inline-action-button-background-color);
}

#additional-inline-action-buttons.yt-live-chat-legacy-paid-message-renderer>.yt-live-chat-legacy-paid-message-renderer:hover {
  background: var(--yt-live-chat-additional-inline-action-button-background-color-hover);
}

#additional-inline-action-buttons.yt-live-chat-legacy-paid-message-renderer:not(:empty) {
  margin-left: 32px;
}

#inline-action-buttons.yt-live-chat-legacy-paid-message-renderer>*.yt-live-chat-legacy-paid-message-renderer:not(:first-child), #additional-inline-action-buttons.yt-live-chat-legacy-paid-message-renderer>*.yt-live-chat-legacy-paid-message-renderer:not(:first-child) {
  margin-left: 8px;
}

yt-live-chat-legacy-paid-message-renderer {
  position: relative;
  display: block;
  --yt-live-chat-sponsor-color: #0f9d58;
  --yt-live-chat-item-timestamp-display: var(--yt-live-chat-paid-message-timestamp-display, none);
  padding: 4px 24px;
}

yt-live-chat-legacy-paid-message-renderer[dashboard-money-feed] {
  padding: 0;
}

#card.yt-live-chat-legacy-paid-message-renderer {
  position: relative;
  padding: 8px 16px;
  background-color: var(--yt-live-chat-sponsor-color);
  border-radius: 4px;
  color: #fff;
  font-size: 14px;
  min-height: 40px;
  display: flex;
  -ms-flex-direction: row;
  -webkit-flex-direction: row;
  flex-direction: row;
  -ms-flex-align: center;
  -webkit-align-items: center;
  align-items: center;
  box-shadow: 0 2px 2px 0 rgba(0, 0, 0, 0.14), 0 1px 5px 0 rgba(0, 0, 0, 0.12), 0 3px 1px -2px rgba(0, 0, 0, 0.2);
}

yt-live-chat-legacy-paid-message-renderer[dashboard-money-feed] #card.yt-live-chat-legacy-paid-message-renderer {
  border-radius: 0;
  box-shadow: none;
  background-color: var(--yt-live-chat-background-color);
  color: rgba(0, 0, 0, 0.87);
}

#author-photo.yt-live-chat-legacy-paid-message-renderer {
  -ms-align-self: flex-start;
  -webkit-align-self: flex-start;
  align-self: flex-start;
}

#author-name.yt-live-chat-legacy-paid-message-renderer {
  display: none;
}

yt-live-chat-legacy-paid-message-renderer[dashboard-money-feed] #author-name.yt-live-chat-legacy-paid-message-renderer {
  display: block;
  margin-right: 8px;
  color: var(--yt-live-chat-secondary-text-color);
  font-weight: 500;
}

#content.yt-live-chat-legacy-paid-message-renderer {
  -ms-flex: 1 1 0.000000001px;
  -webkit-flex: 1;
  flex: 1;
  -webkit-flex-basis: 0.000000001px;
  flex-basis: 0.000000001px;
}

yt-live-chat-legacy-paid-message-renderer[dashboard-money-feed] #content.yt-live-chat-legacy-paid-message-renderer {
  display: flex;
  -ms-flex-direction: column;
  -webkit-flex-direction: column;
  flex-direction: column;
}

yt-live-chat-legacy-paid-message-renderer[dashboard-money-feed] #content-primary-column.yt-live-chat-legacy-paid-message-renderer {
  display: flex;
  -ms-flex-direction: row;
  -webkit-flex-direction: row;
  flex-direction: row;
  -ms-flex-align: baseline;
  -webkit-align-items: baseline;
  align-items: baseline;
}

#event-text.yt-live-chat-legacy-paid-message-renderer {
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
}

yt-live-chat-legacy-paid-message-renderer[dashboard-money-feed] #event-text.yt-live-chat-legacy-paid-message-renderer {
  display: inline;
  height: 24px;
  min-width: 16px;
  border-radius: 12px;
  margin-right: 8px;
  padding: 0 12px;
  background-color: var(--yt-live-chat-sponsor-color);
  color: hsl(0, 0%, 100%);
  display: inline-flex;
  -ms-flex-align: center;
  -webkit-align-items: center;
  align-items: center;
  -ms-flex-pack: center;
  -webkit-justify-content: center;
  justify-content: center;
  font-size: 1.2rem;
  font-weight: 500;
  line-height: 1.2rem;
}

#detail-text.yt-live-chat-legacy-paid-message-renderer {
  font-size: 15px;
  word-wrap: break-word;
  word-break: break-word;
}

#detail-text.yt-live-chat-legacy-paid-message-renderer .emoji.yt-live-chat-legacy-paid-message-renderer {
  width: var(--yt-live-chat-emoji-size);
  height: var(--yt-live-chat-emoji-size);
  margin: -1px 2px 1px 2px;
  vertical-align: middle;
}

yt-live-chat-legacy-paid-message-renderer[dashboard-money-feed] #detail-text.yt-live-chat-legacy-paid-message-renderer {
  display: none;
}

a.yt-live-chat-legacy-paid-message-renderer {
  display: inline;
  text-decoration: underline;
}

#detail-text.yt-live-chat-legacy-paid-message-renderer a.yt-live-chat-legacy-paid-message-renderer {
  word-break: break-all;
}

#detail-text.yt-live-chat-legacy-paid-message-renderer a.yt-live-chat-legacy-paid-message-renderer .mention.yt-live-chat-legacy-paid-message-renderer {
  text-decoration: underline;
}

#menu.yt-live-chat-legacy-paid-message-renderer {
  background: linear-gradient(to right, transparent, var(--yt-live-chat-sponsor-color) 100%);
  border-radius: 0 4px 4px 0;
}

yt-live-chat-legacy-paid-message-renderer[dashboard-money-feed] #menu.yt-live-chat-legacy-paid-message-renderer {
  margin-top: 8px;
  background: linear-gradient(to right, transparent, var(--yt-live-chat-background-color) 40%);
}
</style>
