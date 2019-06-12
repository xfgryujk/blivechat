import axios from 'axios'

const DEFAULT_CSS = `@import url("https://fonts.googleapis.com/css?family=Changa%20One");
@import url("https://fonts.googleapis.com/css?family=Imprima");
/* @import url("https://fonts.lug.ustc.edu.cn/css?family=Changa%20One"); */
/* @import url("https://fonts.lug.ustc.edu.cn/css?family=Imprima"); */

/* Background colors*/
body {
  overflow: hidden;
  background-color: rgba(0,0,0,0);
}
/* Transparent background. */
yt-live-chat-renderer {
  background-color: transparent !important;
}
yt-live-chat-text-message-renderer,
yt-live-chat-text-message-renderer[is-highlighted] {
  background-color: transparent !important;
}

yt-live-chat-text-message-renderer[author-type="owner"],
yt-live-chat-text-message-renderer[author-type="owner"][is-highlighted] {
  background-color: transparent !important;
}

yt-live-chat-text-message-renderer[author-type="moderator"],
yt-live-chat-text-message-renderer[author-type="moderator"][is-highlighted] {
  background-color: transparent !important;
}

yt-live-chat-text-message-renderer[author-type="member"],
yt-live-chat-text-message-renderer[author-type="member"][is-highlighted] {
  background-color: transparent !important;
}


yt-live-chat-author-chip #author-name {
  background-color: transparent !important;
}
/* Outlines */
yt-live-chat-renderer * {
  text-shadow: -2px -2px #000000,-2px -1px #000000,-2px 0px #000000,-2px 1px #000000,-2px 2px #000000,-1px -2px #000000,-1px -1px #000000,-1px 0px #000000,-1px 1px #000000,-1px 2px #000000,0px -2px #000000,0px -1px #000000,0px 0px #000000,0px 1px #000000,0px 2px #000000,1px -2px #000000,1px -1px #000000,1px 0px #000000,1px 1px #000000,1px 2px #000000,2px -2px #000000,2px -1px #000000,2px 0px #000000,2px 1px #000000,2px 2px #000000;
  font-family: "Imprima";
  font-size: 18px !important;
  line-height: 18px !important;
}

yt-live-chat-text-message-renderer #content,
yt-live-chat-legacy-paid-message-renderer #content {
  overflow: initial !important;
}

/* Hide scrollbar. */
yt-live-chat-item-list-renderer #items{
  overflow: hidden !important;
}

yt-live-chat-item-list-renderer #item-scroller{
  overflow: hidden !important;
}

/* Hide header and input. */
yt-live-chat-header-renderer,
yt-live-chat-message-input-renderer {
  display: none !important;
}

/* Reduce side padding. */
yt-live-chat-text-message-renderer,
yt-live-chat-legacy-paid-message-renderer {
    padding-left: 4px !important;
  padding-right: 4px !important;
}

yt-live-chat-paid-message-renderer #header {
    padding-left: 4px !important;
  padding-right: 4px !important;
}

/* Avatars. */
yt-live-chat-text-message-renderer #author-photo,
yt-live-chat-paid-message-renderer #author-photo,
yt-live-chat-legacy-paid-message-renderer #author-photo {
  
  width: 24px !important;
  height: 24px !important;
  border-radius: 24px !important;
  margin-right: 6px !important;
  background-size: cover;
}

/* Hide badges. */
yt-live-chat-text-message-renderer #author-badges {
  display: none !important;
  vertical-align: text-top !important;
}

/* Timestamps. */
yt-live-chat-text-message-renderer #timestamp {
  
  color: #999999 !important;
  font-family: "Imprima";
  font-size: 16px !important;
  line-height: 16px !important;
}

/* Badges. */
yt-live-chat-text-message-renderer #author-name[type="owner"],
yt-live-chat-text-message-renderer yt-live-chat-author-badge-renderer[type="owner"] {
  color: #ffd600 !important;
}

yt-live-chat-text-message-renderer #author-name[type="moderator"],
yt-live-chat-text-message-renderer yt-live-chat-author-badge-renderer[type="moderator"] {
  color: #5e84f1 !important;
}

yt-live-chat-text-message-renderer #author-name[type="member"],
yt-live-chat-text-message-renderer yt-live-chat-author-badge-renderer[type="member"] {
  color: #0f9d58 !important;
}

/* Channel names. */
yt-live-chat-text-message-renderer #author-name {
  color: #cccccc !important;
  font-family: "Changa One";
  font-size: 20px !important;
  line-height: 20px !important;
}

yt-live-chat-text-message-renderer #author-name::after {
  content: ":";
  margin-left: 2px;
}

/* Messages. */
yt-live-chat-text-message-renderer #message,
yt-live-chat-text-message-renderer #message * {
  color: #ffffff !important;
  font-family: "Imprima";
  font-size: 18px !important;
  line-height: 18px !important;
}


/* SuperChat/Fan Funding Messages. */
yt-live-chat-paid-message-renderer #author-name,
yt-live-chat-paid-message-renderer #author-name *,
yt-live-chat-legacy-paid-message-renderer #event-text,
yt-live-chat-legacy-paid-message-renderer #event-text * {
  color: #ffffff !important;
  font-family: "Changa One";
  font-size: 20px !important;
  line-height: 20px !important;
}

yt-live-chat-paid-message-renderer #purchase-amount,
yt-live-chat-paid-message-renderer #purchase-amount *,
yt-live-chat-legacy-paid-message-renderer #detail-text,
yt-live-chat-legacy-paid-message-renderer #detail-text * {
  color: #ffffff !important;
  font-family: "Imprima";
  font-size: 18px !important;
  line-height: 18px !important;
}

yt-live-chat-paid-message-renderer #content,
yt-live-chat-paid-message-renderer #content * {
  color: #ffffff !important;
  font-family: "Imprima";
  font-size: 18px !important;
  line-height: 18px !important;
}

yt-live-chat-paid-message-renderer {
  margin: 4px 0 !important;
}

yt-live-chat-legacy-paid-message-renderer {
  background-color: #0f9d58 !important;
  margin: 4px 0 !important;
}

yt-live-chat-text-message-renderer a,
yt-live-chat-legacy-paid-message-renderer a {
  text-decoration: none !important;
}

yt-live-chat-text-message-renderer[is-deleted],
yt-live-chat-legacy-paid-message-renderer[is-deleted] {
  display: none !important;
}

yt-live-chat-ticker-renderer {
  background-color: transparent !important;
  box-shadow: none !important;
}
yt-live-chat-ticker-renderer {
  display: none !important;
}


yt-live-chat-ticker-paid-message-item-renderer,
yt-live-chat-ticker-paid-message-item-renderer *,
yt-live-chat-ticker-sponsor-item-renderer,
yt-live-chat-ticker-sponsor-item-renderer * {
  color: #ffffff !important;
  font-family: "Imprima";
}

yt-live-chat-mode-change-message-renderer, 
yt-live-chat-viewer-engagement-message-renderer, 
yt-live-chat-restricted-participation-renderer {
  display: none !important;
}  
`

export const DEFAULT_CONFIG = {
  minGiftPrice: 6.911, // $1
  mergeSimilarDanmaku: true,

  blockGiftDanmaku: true,
  blockLevel: 0,
  blockNewbie: true,
  blockNotMobileVerified: true,
  blockKeywords: '',
  blockUsers: '',

  css: DEFAULT_CSS
}

function mergeConfig (config) {
  let res = {}
  for (let i in DEFAULT_CONFIG) {
    res[i] = i in config ? config[i] : DEFAULT_CONFIG[i]
  }
  return res
}

export function setLocalConfig (config) {
  config = mergeConfig(config)
  window.localStorage.config = JSON.stringify(config)
}

export function getLocalConfig () {
  if (!window.localStorage.config) {
    return DEFAULT_CONFIG
  }
  return mergeConfig(JSON.parse(window.localStorage.config))
}

export async function createRemoteConfig (config) {
  config = mergeConfig(config)
  return (await axios.post('/config', config)).data
}

export async function setRemoteConfig (id, config) {
  config = mergeConfig(config)
  return (await axios.put(`/config/${id}`, config)).data
}

export async function getRemoteConfig (id) {
  let config = (await axios.get(`/config/${id}`)).data
  return mergeConfig(config)
}

export default {
  DEFAULT_CONFIG,
  setLocalConfig,
  getLocalConfig,
  createRemoteConfig,
  setRemoteConfig,
  getRemoteConfig
}
