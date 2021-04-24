import * as fonts from './fonts'

export const FALLBACK_FONTS = ', "Helvetica Neue", Helvetica, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "\\5FAE \\8F6F \\96C5 \\9ED1 ", SimHei, Arial, sans-serif'

export const COMMON_STYLE = `/* Transparent background */
yt-live-chat-renderer {
  background-color: transparent !important;
}

yt-live-chat-ticker-renderer {
  background-color: transparent !important;
  box-shadow: none !important;
}

yt-live-chat-author-chip #author-name {
  background-color: transparent !important;
}

/* Hide scrollbar */
yt-live-chat-item-list-renderer #items {
  overflow: hidden !important;
}

yt-live-chat-item-list-renderer #item-scroller {
  overflow: hidden !important;
}

yt-live-chat-text-message-renderer #content,
yt-live-chat-membership-item-renderer #content {
  overflow: visible !important;
}

/* Hide header and input */
yt-live-chat-header-renderer,
yt-live-chat-message-input-renderer {
  display: none !important;
}

/* Hide unimportant messages */
yt-live-chat-text-message-renderer[is-deleted],
yt-live-chat-membership-item-renderer[is-deleted] {
  display: none !important;
}

yt-live-chat-mode-change-message-renderer, 
yt-live-chat-viewer-engagement-message-renderer, 
yt-live-chat-restricted-participation-renderer {
  display: none !important;
}

yt-live-chat-text-message-renderer a,
yt-live-chat-membership-item-renderer a {
  text-decoration: none !important;
}`

export function getImportStyle (allFonts) {
  let fontsNeedToImport = new Set()
  for (let font of allFonts) {
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

export function getAvatarStyle (config) {
  return `/* Avatars */
yt-live-chat-text-message-renderer #author-photo,
yt-live-chat-text-message-renderer #author-photo img,
yt-live-chat-paid-message-renderer #author-photo,
yt-live-chat-paid-message-renderer #author-photo img,
yt-live-chat-membership-item-renderer #author-photo,
yt-live-chat-membership-item-renderer #author-photo img {
  ${config.showAvatars ? '' : 'display: none !important;'}
  width: ${config.avatarSize}px !important;
  height: ${config.avatarSize}px !important;
  border-radius: ${config.avatarSize}px !important;
  margin-right: ${config.avatarSize / 4}px !important;
}`
}

export function getTimeStyle (config) {
  return `/* Timestamps */
yt-live-chat-text-message-renderer #timestamp {
  display: ${config.showTime ? 'inline' : 'none'} !important;
  ${config.timeColor ? `color: ${config.timeColor} !important;` : ''}
  font-family: "${cssEscapeStr(config.timeFont)}"${FALLBACK_FONTS};
  font-size: ${config.timeFontSize}px !important;
  line-height: ${config.timeLineHeight || config.timeFontSize}px !important;
}`
}

export function getAnimationStyle (config) {
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
  return `/* Animation */
@keyframes anim {
${keyframes.join('\n')}
}

yt-live-chat-text-message-renderer,
yt-live-chat-membership-item-renderer,
yt-live-chat-paid-message-renderer {
  animation: anim ${totalTime}ms;
  animation-fill-mode: both;
}`
}

export function cssEscapeStr (str) {
  let res = []
  for (let char of str) {
    res.push(cssEscapeChar(char))
  }
  return res.join('')
}

function cssEscapeChar (char) {
  if (!needEscapeChar(char)) {
    return char
  }
  let hexCode = char.codePointAt(0).toString(16)
  // https://drafts.csswg.org/cssom/#escape-a-character-as-code-point
  return `\\${hexCode} `
}

function needEscapeChar (char) {
  let code = char.codePointAt(0)
  if (0x20 <= code && code <= 0x7E) {
    return char === '"' || char === '\\'
  }
  return true
}
