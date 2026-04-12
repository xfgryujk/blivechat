import * as fonts from './fonts'

const FALLBACK_FONTS_CSS = '"Helvetica Neue", Helvetica, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", \
"\\5FAE \\8F6F \\96C5 \\9ED1 ", SimHei, Arial, sans-serif'

export const COMMON_STYLE = `/* （必需）透明背景 (Required) Transparent background */
yt-live-chat-renderer,
yt-live-chat-ticker-renderer,
yt-live-chat-author-chip #author-name {
  background-color: transparent;
}

/* （必需）隐藏滚动条 (Required) Hide scrollbar */
body,
yt-live-chat-item-list-renderer #item-scroller {
  overflow: hidden;
}`

export function getImportStyle(allFontsStrs) {
  let allFonts = new Set()
  for (let fontsStr of allFontsStrs) {
    for (let font of fontsStrToArr(fontsStr)) {
      allFonts.add(font)
    }
  }

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

export function getVariableStyle(config) {
  return `/* 基准尺寸，用于整体缩放 Base size for scaling */
  --base-size: 1px;
  --font-base-size: calc(1 * var(--base-size));

  /* 没有首选字体时的备用字体 Fallback font families */
  --fallback-fonts: ${FALLBACK_FONTS_CSS};

  /* 头像 Avatars */
  --avatar-size: calc(${config.avatarSize} * var(--base-size));

  /* 时间 Timestamps */
  --time-color: ${config.timeColor ?? '#999999'};
  --time-size: calc(${config.timeFontSize} * var(--font-base-size));

  /* 用户名 Channel names
    普通、舰长、房管、主播 */
  --username-color: ${config.userNameColor ?? '#111111'};
  --username-color-member: ${config.memberUserNameColor ?? 'var(--username-color)'};
  --username-color-moderator: ${config.moderatorUserNameColor ?? 'var(--username-color)'};
  --username-color-owner: ${config.ownerUserNameColor ?? 'var(--username-color)'};
  --username-size: calc(${config.userNameFontSize} * var(--font-base-size));

  /* 文本消息 Text messages */
  --text-content-color: ${config.messageColor ?? '#111111'};
  --text-content-size: calc(${config.messageFontSize} * var(--font-base-size));

  /* 表情 Emotes */
  --emote-size: calc(${config.emoticonSize} * var(--font-base-size));
  --large-emote-size: calc(${config.largeEmoticonSize} * var(--font-base-size));`
}

export function getAvatarStyle(config) {
  return `/* 头像 Avatars */
yt-live-chat-item-list-renderer :is(#author-photo, #author-photo img) {
  ${config.showAvatars ? '' : 'display: none;'}
  width: var(--avatar-size);
  height: var(--avatar-size);
  border-radius: var(--avatar-size);
  margin-right: calc(var(--avatar-size) / 4);
}`
}

export function getTimeStyle(config) {
  return `/* 时间 Timestamps */
yt-live-chat-text-message-renderer #timestamp {
  display: ${config.showTime ? 'inline' : 'none'};
  color: var(--time-color);
  font-family: ${fontsStrToCss(config.timeFont)};
  font-size: var(--time-size);
  line-height: ${config.timeLineHeight || config.timeFontSize}px;
}`
}

export function getUserNameStyle(config) {
  return `yt-live-chat-text-message-renderer :is(#author-name, yt-live-chat-author-badge-renderer)[type="owner"] {
  color: var(--username-color-owner);
}

yt-live-chat-text-message-renderer :is(#author-name, yt-live-chat-author-badge-renderer)[type="moderator"] {
  color: var(--username-color-moderator);
}

yt-live-chat-text-message-renderer :is(#author-name, yt-live-chat-author-badge-renderer)[type="member"] {
  color: var(--username-color-member);
}

${config.showBadges ? '' : `/* 隐藏勋章 Hide badges */
yt-live-chat-text-message-renderer #chat-badges {
  display: none;
}`}`
}

export const EMOTICON_STYLE = `yt-live-chat-text-message-renderer #message .emoji {
  width: auto;
  height: var(--emote-size);
}

yt-live-chat-text-message-renderer #message .emoji.blc-large-emoji {
  height: var(--large-emote-size);
}`

export function getReverseScrollStyle(config) {
  if (!config.messageReverseScroll) {
    return ''
  }
  return `/* 反向滚动 Reverse scrolling */
yt-live-chat-item-list-renderer,
yt-live-chat-item-list-renderer #items > * {
  rotate: 180deg;
  backface-visibility: hidden;
}`
}

export function getAnimationStyle(config) {
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
      : ` translate: ${config.reverseSlide ? 16 : -16}px;`
    } }`)
    curTime += config.fadeInTime
    keyframes.push(`  ${curTime / totalTime * 100}% { opacity: 1; translate: none; }`)
  }
  if (config.animateOut) {
    curTime += config.animateOutWaitTime * 1000
    keyframes.push(`  ${curTime / totalTime * 100}% { opacity: 1; translate: none; }`)
    curTime += config.fadeOutTime
    keyframes.push(`  ${curTime / totalTime * 100}% { opacity: 0;${!config.slide ? ''
      : ` translate: ${config.reverseSlide ? -16 : 16}px;`
    } }`)
  }
  return `/* 动画 Animation */
@keyframes anim {
${keyframes.join('\n')}
}

yt-live-chat-item-list-renderer #items > * {
  animation: anim ${totalTime}ms;
  animation-fill-mode: both;
}`
}

export function fontsStrToArr(fontsStr) {
  return fontsStr ? fontsStr.split(',') : []
}

export function fontsArrToStr(fontsArr) {
  return fontsArr.join(',')
}

export function fontsStrToCss(fontsStr) {
  let fontsArr = fontsStrToArr(fontsStr)
  fontsArr = fontsArr.map(cssEscapeStr)
  fontsArr.push('var(--fallback-fonts)')
  return fontsArr.join(', ')
}

function cssEscapeStr(str) {
  let res = []
  for (let char of str) {
    res.push(cssEscapeChar(char))
  }
  return `"${res.join('')}"`
}

function cssEscapeChar(char) {
  if (!needEscapeChar(char)) {
    return char
  }
  let hexCode = char.codePointAt(0).toString(16)
  // https://drafts.csswg.org/cssom/#escape-a-character-as-code-point
  return `\\${hexCode} `
}

function needEscapeChar(char) {
  let code = char.codePointAt(0)
  if (0x20 <= code && code <= 0x7E) {
    return char === '"' || char === '\\'
  }
  return true
}
