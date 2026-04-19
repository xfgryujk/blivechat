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
  if (!config.showAvatars) {
    return `/* 头像 Avatars */
yt-live-chat-item-list-renderer #author-photo {
    display: none;
}`
  }
  return `/* 头像 Avatars */
yt-live-chat-item-list-renderer :is(#author-photo, #author-photo img) {
  width: var(--avatar-size);
  height: var(--avatar-size);
  margin-right: 10px;
}`
}

export function getTimeStyle(config) {
  if (!config.showTime) {
    return `/* 时间 Timestamps */
yt-live-chat-text-message-renderer #timestamp {
  display: none;
}`
  }
  return `/* 时间 Timestamps */
yt-live-chat-text-message-renderer #timestamp {
  display: inline;
  color: var(--time-color);
  font-family: ${fontsStrToCss(config.timeFont)};
  font-size: var(--time-size);
  line-height: calc(${config.timeLineHeight || (config.timeFontSize * 1.2)} * var(--font-base-size));
}`
}

export function getUserNameStyle(config) {
  return `/* 用户名 Channel names */
yt-live-chat-text-message-renderer #author-name {
  ${config.showUserNames ? '' : 'display: none;'}
  color: var(--username-color);
  font-family: ${fontsStrToCss(config.userNameFont)};
  font-size: var(--username-size);
  line-height: calc(${config.userNameLineHeight || (config.userNameFontSize * 1.2)} * var(--font-base-size));
}

yt-live-chat-text-message-renderer :is(#author-name, yt-live-chat-author-badge-renderer)[type="owner"] {
  color: var(--username-color-owner);
}

yt-live-chat-text-message-renderer :is(#author-name, yt-live-chat-author-badge-renderer)[type="moderator"] {
  color: var(--username-color-moderator);
}

yt-live-chat-text-message-renderer :is(#author-name, yt-live-chat-author-badge-renderer)[type="member"] {
  color: var(--username-color-member);
}

${config.showBadges ? `yt-live-chat-text-message-renderer yt-live-chat-author-badge-renderer :is(img, yt-icon) {
  width: calc(${config.userNameLineHeight || (config.userNameFontSize * 1.2)} * var(--font-base-size));
  height: calc(${config.userNameLineHeight || (config.userNameFontSize * 1.2)} * var(--font-base-size));
}` : `/* 隐藏勋章 Hide badges */
yt-live-chat-text-message-renderer #chat-badges {
  display: none;
}`}`
}

export function getMessageStyle(config) {
  return `/* 文本消息 Text messages */
yt-live-chat-text-message-renderer :is(#message, #message *) {
  color: var(--text-content-color);
  font-family: ${fontsStrToCss(config.messageFont)};
  font-size: var(--text-content-size);
  line-height: calc(${config.messageLineHeight || (config.messageFontSize * 1.2)} * var(--font-base-size));
}

${EMOTICON_STYLE}

${getReverseScrollStyle(config)}`
}

const EMOTICON_STYLE = `yt-live-chat-text-message-renderer #message .emoji {
  width: auto;
  height: var(--emote-size);
}

yt-live-chat-text-message-renderer #message .emoji.blc-large-emoji {
  height: var(--large-emote-size);
}`

function getReverseScrollStyle(config) {
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

export function getScAndNewMemberStyle(config) {
  return `/* 付费、上舰消息 Super Chats / Membership messages */
yt-live-chat-paid-message-renderer {
  margin: 4px 0;
}

${getScAndNewMemberFontStyle(config)}

yt-live-chat-membership-item-renderer :is(#card, #header) {
  background-color: var(--membership-msg-bg-color);
  margin: 4px 0;
}

${getScTickerStyle(config)}

${config.showOtherThings ? '' : `yt-live-chat-item-list-renderer {
  display: none;
}`}`
}

function getScAndNewMemberFontStyle(config) {
  let firstLineLineHeight = config.firstLineLineHeight || (config.firstLineFontSize * 1.2)
  return `yt-live-chat-paid-message-renderer :is(#author-name, #author-name *),
yt-live-chat-membership-item-renderer :is(#header-content-inner-column, #header-content-inner-column *) {
  font-family: ${fontsStrToCss(config.firstLineFont)};
  font-size: var(--paid-msg-line-1-size);
  line-height: calc(${firstLineLineHeight} * var(--font-base-size));
}

yt-live-chat-membership-item-renderer yt-live-chat-author-badge-renderer :is(img, yt-icon) {
  width: calc(${firstLineLineHeight} * var(--font-base-size));
  height: calc(${firstLineLineHeight} * var(--font-base-size));
}

yt-live-chat-paid-message-renderer :is(#purchase-amount, #purchase-amount *),
yt-live-chat-membership-item-renderer :is(#header-subtext, #header-subtext *) {
  font-family: ${fontsStrToCss(config.secondLineFont)};
  font-size: var(--paid-msg-line-2-size);
  line-height: calc(${config.secondLineLineHeight || (config.secondLineFontSize * 1.2)} * var(--font-base-size));
}

yt-live-chat-paid-message-renderer :is(#content, #content *) {
  font-family: ${fontsStrToCss(config.scContentFont)};
  font-size: var(--paid-msg-content-size);
  line-height: calc(${config.scContentLineHeight || (config.scContentFontSize * 1.2)} * var(--font-base-size));
}`
}

function getScTickerStyle(config) {
  if (!config.showScTicker) {
    return `yt-live-chat-ticker-renderer {
  display: none;
}`
  }
  let secondLineLineHeight = config.secondLineLineHeight || (config.secondLineFontSize * 1.2)
  return `/* SC固定栏 Super Chat ticker */
yt-live-chat-ticker-renderer #items {
  height: unset;
}

yt-live-chat-ticker-paid-message-item-renderer #author-photo img {
  width: calc(${secondLineLineHeight} * var(--font-base-size));
  height: calc(${secondLineLineHeight} * var(--font-base-size));
}

yt-live-chat-ticker-paid-message-item-renderer #content {
  height: unset;
  font-family: ${fontsStrToCss(config.secondLineFont)};
  font-size: var(--paid-msg-line-2-size);
  line-height: calc(${secondLineLineHeight} * var(--font-base-size));
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
      : ` translate: calc(${config.reverseSlide ? 16 : -16} * var(--base-size));`
    } }`)
    curTime += config.fadeInTime
    keyframes.push(`  ${curTime / totalTime * 100}% { opacity: 1; translate: none; }`)
  }
  if (config.animateOut) {
    curTime += config.animateOutWaitTime * 1000
    keyframes.push(`  ${curTime / totalTime * 100}% { opacity: 1; translate: none; }`)
    curTime += config.fadeOutTime
    keyframes.push(`  ${curTime / totalTime * 100}% { opacity: 0;${!config.slide ? ''
      : ` translate: calc(${config.reverseSlide ? -16 : 16} * var(--base-size);`
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
