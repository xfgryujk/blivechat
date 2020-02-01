import {mergeConfig} from '@/utils'
import * as fonts from './fonts'

export const DEFAULT_CONFIG = {
  showOutlines: true,
  outlineSize: 2,
  outlineColor: '#000000',

  showAvatars: true,
  avatarSize: 24,

  userNameFont: 'Changa One',
  userNameFontSize: 20,
  userNameLineHeight: 0,
  userNameColor: '#cccccc',
  ownerUserNameColor: '#ffd600',
  moderatorUserNameColor: '#5e84f1',
  memberUserNameColor: '#0f9d58',
  showBadges: false,
  showColon: true,

  messageFont: 'Imprima',
  messageFontSize: 18,
  messageLineHeight: 0,
  messageColor: '#ffffff',
  messageOnNewLine: false,

  showTime: false,
  timeFont: 'Imprima',
  timeFontSize: 16,
  timeLineHeight: 0,
  timeColor: '#999999',

  bgColor: 'rgba(0, 0, 0, 0)',
  useBarsInsteadOfBg: false,
  messageBgColor: 'rgba(204, 204, 204, 0)',
  ownerMessageBgColor: 'rgba(255, 214, 0, 0)',
  moderatorMessageBgColor: 'rgba(94, 132, 241, 0)',
  memberMessageBgColor: 'rgba(15, 157, 88, 0)',

  firstLineFont: 'Changa One',
  firstLineFontSize: 20,
  firstLineLineHeight: 0,
  firstLineColor: '#ffffff',
  secondLineFont: 'Imprima',
  secondLineFontSize: 18,
  secondLineLineHeight: 0,
  secondLineColor: '#ffffff',
  scContentFont: 'Imprima',
  scContentFontSize: 18,
  scContentLineHeight: 0,
  scContentColor: '#ffffff',
  showNewMemberBg: true,
  showScTicker: false,
  showOtherThings: true,

  animateIn: false,
  fadeInTime: 200, // ms
  animateOut: false,
  animateOutWaitTime: 30, // s
  fadeOutTime: 200, // ms
  slide: false,
  reverseSlide: false
}

const FALLBACK_FONTS = ', "Helvetica Neue", Helvetica, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "\\5FAE\\8F6F\\96C5\\9ED1", SimHei, Arial, sans-serif'

export function setLocalConfig (config) {
  config = mergeConfig(config, DEFAULT_CONFIG)
  window.localStorage.stylegenConfig = JSON.stringify(config)
}

export function getLocalConfig () {
  if (!window.localStorage.stylegenConfig) {
    return DEFAULT_CONFIG
  }
  return mergeConfig(JSON.parse(window.localStorage.stylegenConfig), DEFAULT_CONFIG)
}

export function getStyle (config) {
  config = mergeConfig(config, DEFAULT_CONFIG)
  return `${getImports(config)}

/* Background colors */
body {
  overflow: hidden;
  ${config.bgColor ? `background-color: ${config.bgColor};` : ''}
}

/* Transparent background. */
yt-live-chat-renderer {
  background-color: transparent !important;
}

${getMessageColorStyle('', config.messageBgColor, config.useBarsInsteadOfBg)}

${getMessageColorStyle('owner', config.ownerMessageBgColor, config.useBarsInsteadOfBg)}

${getMessageColorStyle('moderator', config.moderatorMessageBgColor, config.useBarsInsteadOfBg)}

${getMessageColorStyle('member', config.memberMessageBgColor, config.useBarsInsteadOfBg)}

yt-live-chat-author-chip #author-name {
  background-color: transparent !important;
}

/* Outlines */
yt-live-chat-renderer * {
  ${getShowOutlinesStyle(config)}
  font-family: "${config.messageFont}"${FALLBACK_FONTS};
  font-size: ${config.messageFontSize}px !important;
  line-height: ${config.messageLineHeight}px !important;
}

yt-live-chat-text-message-renderer #content,
yt-live-chat-legacy-paid-message-renderer #content {
  overflow: initial !important;
}

/* Hide scrollbar. */
yt-live-chat-item-list-renderer #items {
  overflow: hidden !important;
}

yt-live-chat-item-list-renderer #item-scroller {
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
  ${getPaddingStyle(config)}
}

yt-live-chat-paid-message-renderer #header {
  ${getPaddingStyle(config)}
}

/* Avatars. */
yt-live-chat-text-message-renderer #author-photo,
yt-live-chat-text-message-renderer #author-photo img,
yt-live-chat-paid-message-renderer #author-photo,
yt-live-chat-paid-message-renderer #author-photo img,
yt-live-chat-legacy-paid-message-renderer #author-photo,
yt-live-chat-legacy-paid-message-renderer #author-photo img {
  ${config.showAvatars ? '' : 'display: none !important;'}
  width: ${config.avatarSize}px !important;
  height: ${config.avatarSize}px !important;
  border-radius: ${config.avatarSize}px !important;
  margin-right: ${config.avatarSize / 4}px !important;
}

/* Hide badges. */
yt-live-chat-text-message-renderer #chat-badges {
  ${config.showBadges ? '' : 'display: none !important;'}
  vertical-align: text-top !important;
}

/* Timestamps. */
yt-live-chat-text-message-renderer #timestamp {
  display: ${config.showTime ? 'inline' : 'none'} !important;
  ${config.timeColor ? `color: ${config.timeColor} !important;` : ''}
  font-family: "${config.timeFont}"${FALLBACK_FONTS};
  font-size: ${config.timeFontSize}px !important;
  line-height: ${config.timeLineHeight || config.timeFontSize}px !important;
}

/* Badges. */
yt-live-chat-text-message-renderer #author-name[type="owner"],
yt-live-chat-text-message-renderer yt-live-chat-author-badge-renderer[type="owner"] {
  ${config.ownerUserNameColor ? `color: ${config.ownerUserNameColor} !important;` : ''}
}

yt-live-chat-text-message-renderer #author-name[type="moderator"],
yt-live-chat-text-message-renderer yt-live-chat-author-badge-renderer[type="moderator"] {
  ${config.moderatorUserNameColor ? `color: ${config.moderatorUserNameColor} !important;` : ''}
}

yt-live-chat-text-message-renderer #author-name[type="member"],
yt-live-chat-text-message-renderer yt-live-chat-author-badge-renderer[type="member"] {
  ${config.memberUserNameColor ? `color: ${config.memberUserNameColor} !important;` : ''}
}

/* Channel names. */
yt-live-chat-text-message-renderer #author-name {
  ${config.userNameColor ? `color: ${config.userNameColor} !important;` : ''}
  font-family: "${config.userNameFont}"${FALLBACK_FONTS};
  font-size: ${config.userNameFontSize}px !important;
  line-height: ${config.userNameLineHeight || config.userNameFontSize}px !important;
}

${getShowColonStyle(config)}

/* Messages. */
yt-live-chat-text-message-renderer #message,
yt-live-chat-text-message-renderer #message * {
  ${config.messageColor ? `color: ${config.messageColor} !important;` : ''}
  font-family: "${config.messageFont}"${FALLBACK_FONTS};
  font-size: ${config.messageFontSize}px !important;
  line-height: ${config.messageLineHeight || config.messageFontSize}px !important;
}

${!config.messageOnNewLine ? '' : `yt-live-chat-text-message-renderer #message {
  display: block !important;
}`}

/* SuperChat/Fan Funding Messages. */
yt-live-chat-paid-message-renderer #author-name,
yt-live-chat-paid-message-renderer #author-name *,
yt-live-chat-legacy-paid-message-renderer #event-text,
yt-live-chat-legacy-paid-message-renderer #event-text * {
  ${config.firstLineColor ? `color: ${config.firstLineColor} !important;` : ''}
  font-family: "${config.firstLineFont}"${FALLBACK_FONTS};
  font-size: ${config.firstLineFontSize}px !important;
  line-height: ${config.firstLineLineHeight || config.firstLineFontSize}px !important;
}

yt-live-chat-paid-message-renderer #purchase-amount,
yt-live-chat-paid-message-renderer #purchase-amount *,
yt-live-chat-legacy-paid-message-renderer #detail-text,
yt-live-chat-legacy-paid-message-renderer #detail-text * {
  ${config.secondLineColor ? `color: ${config.secondLineColor} !important;` : ''}
  font-family: "${config.secondLineFont}"${FALLBACK_FONTS};
  font-size: ${config.secondLineFontSize}px !important;
  line-height: ${config.secondLineLineHeight || config.secondLineFontSize}px !important;
}

yt-live-chat-paid-message-renderer #content,
yt-live-chat-paid-message-renderer #content * {
  ${config.scContentColor ? `color: ${config.scContentColor} !important;` : ''}
  font-family: "${config.scContentFont}"${FALLBACK_FONTS};
  font-size: ${config.scContentFontSize}px !important;
  line-height: ${config.scContentLineHeight || config.scContentFontSize}px !important;
}

yt-live-chat-paid-message-renderer {
  margin: 4px 0 !important;
}

yt-live-chat-legacy-paid-message-renderer #card {
  ${getShowNewMemberBgStyle(config)}
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

${config.showScTicker ? '' : `yt-live-chat-ticker-renderer {
  display: none !important;
}`}

${config.showOtherThings ? '' : `yt-live-chat-item-list-renderer {
  display: none !important;
}`}

yt-live-chat-ticker-paid-message-item-renderer,
yt-live-chat-ticker-paid-message-item-renderer *,
yt-live-chat-ticker-sponsor-item-renderer,
yt-live-chat-ticker-sponsor-item-renderer * {
  ${config.secondLineColor ? `color: ${config.secondLineColor} !important;` : ''}
  font-family: "${config.secondLineFont}"${FALLBACK_FONTS};
}

yt-live-chat-mode-change-message-renderer, 
yt-live-chat-viewer-engagement-message-renderer, 
yt-live-chat-restricted-participation-renderer {
  display: none !important;
}

${getAnimationStyle(config)}
`
}

function getImports (config) {
  let fontsNeedToImport = new Set()
  for (let name of ['userNameFont', 'messageFont', 'timeFont', 'firstLineFont', 'secondLineFont', 'scContentFont']) {
    let font = config[name]
    if (fonts.NETWORK_FONTS.indexOf(font) !== -1) {
      fontsNeedToImport.add(font)
    }
  }
  let res = []
  for (let font of fontsNeedToImport) {
    res.push(`@import url("https://fonts.googleapis.com/css?family=${encodeURIComponent(font)}");`)
  }
  return res.join('\n')
}

function getMessageColorStyle (authorType, color, useBarsInsteadOfBg) {
  let typeSelector = authorType ? `[author-type="${authorType}"]` : ''
  if (!useBarsInsteadOfBg) {
    return `yt-live-chat-text-message-renderer${typeSelector},
yt-live-chat-text-message-renderer${typeSelector}[is-highlighted] {
  ${color ? `background-color: ${color} !important;` : ''}
}`
  } else {
    return `yt-live-chat-text-message-renderer${typeSelector}::after {
  ${color ? `border: 2px solid ${color};` : ''}
  content: "";
  position: absolute;
  display: block;
  left: 8px;
  top: 4px;
  bottom: 4px;
  width: 1px;
  box-sizing: border-box;
  border-radius: 2px;
}`
  }
}

function getShowOutlinesStyle (config) {
  if (!config.showOutlines || !config.outlineSize) {
    return ''
  }
  let shadow = []
  for (var x = -config.outlineSize; x <= config.outlineSize; x += Math.ceil(config.outlineSize / 4)) {
    for (var y = -config.outlineSize; y <= config.outlineSize; y += Math.ceil(config.outlineSize / 4)) {
      shadow.push(`${x}px ${y}px ${config.outlineColor}`)
    }
  }
  return `text-shadow: ${shadow.join(', ')};`
}

function getPaddingStyle (config) {
  return `padding-left: ${config.useBarsInsteadOfBg ? 20 : 4}px !important;
  padding-right: 4px !important;`
}

function getShowColonStyle (config) {
  if (!config.showColon) {
    return ''
  }
  return `yt-live-chat-text-message-renderer #author-name::after {
  content: ":";
  margin-left: ${config.outlineSize}px;
}`
}

function getShowNewMemberBgStyle (config) {
  if (config.showNewMemberBg) {
    return `background-color: ${config.memberUserNameColor} !important;
  margin: 4px 0 !important;`
  } else {
    return `background-color: transparent !important;
  box-shadow: none !important;
  margin: 0 !important;`
  }
}

function getAnimationStyle (config) {
  if (!config.animateIn && !config.animateOut) {
    return ''
  }
  let totalTime = 0
  if (config.animateIn) {
    totalTime += config.fadeInTime
  }
  if (config.animateOut) {
    totalTime += config.animateOutWaitTime * 1000
    totalTime += config.fadeOutTime
  }
  let keyframes = []
  let curTime = 0
  if (config.animateIn) {
    keyframes.push(`  0% { opacity: 0;${!config.slide ? ''
      : ` transform: translateX(${config.reverseSlide ? 16 : -16}px);`
    } }`)
    curTime += config.fadeInTime
    keyframes.push(`  ${(curTime / totalTime) * 100}% { opacity: 1; transform: none; }`)
  }
  if (config.animateOut) {
    curTime += config.animateOutWaitTime * 1000
    keyframes.push(`  ${(curTime / totalTime) * 100}% { opacity: 1; transform: none; }`)
    curTime += config.fadeOutTime
    keyframes.push(`  ${(curTime / totalTime) * 100}% { opacity: 0;${!config.slide ? ''
      : ` transform: translateX(${config.reverseSlide ? -16 : 16}px);`
    } }`)
  }
  return `@keyframes anim {
${keyframes.join('\n')}
}

yt-live-chat-text-message-renderer,
yt-live-chat-legacy-paid-message-renderer {
  animation: anim ${totalTime}ms;
  animation-fill-mode: both;
}`
}
