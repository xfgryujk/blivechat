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
