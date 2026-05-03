---
name: blivechat-css-ref
description: blivechat 自定义 CSS 参考。使用场景：用户提到 写/设计/生成/修改 一个 弹幕样式/CSS；排查弹幕样式不生效等问题。
license: MIT
metadata:
  author: xfgryujk
---

# blivechat 自定义 CSS 参考

blivechat 软件获取 bilibili 直播弹幕并以 HTML 形式在 OBS 中嵌入显示。默认样式模仿 YouTube，但可通过自定义 CSS 修改。

## 输出

输出为一个 CSS 文件。

如果用户未指定输出路径，则询问保存位置。推荐 `data/custom_public/preset.css`，因为在 blivechat 设置中启用 *导入服务器预设 CSS* 即可自动导入该文件。

**输出必须包含以下内容：**
```css
/* （必需）透明背景 */
body,
yt-live-chat-renderer,
yt-live-chat-ticker-renderer,
yt-live-chat-author-chip #author-name {
  background-color: transparent;
}

/* （必需）隐藏滚动条 */
body,
yt-live-chat-item-list-renderer #item-scroller {
  overflow: hidden;
}
```

## 参考文件

- DOM 结构源码：`frontend/src/components/ChatRenderer/index.vue`
- 内置 YouTube 样式：`frontend/src/assets/css/youtube/`——默认样式未被覆盖时可以参考
- [聊天气泡风格 CSS 示例](references/bubble.css)
- [纯文字无消息背景 CSS 示例](references/text.css)——添加文字描边以提高对比度

## 常用模式

### 修复含有大表情的文本消息中头像和用户名没有垂直对齐的问题

大表情会把文本消息的高度撑大，导致头像和用户名没有垂直对齐。

修复方式1，指定顶端对齐：
```css
yt-live-chat-text-message-renderer #content:has(.emoji.blc-large-emoji) > * {
  vertical-align: top;
}
```

修复方式2，大表情换行显示：
```css
yt-live-chat-text-message-renderer #message:has(.emoji.blc-large-emoji) {
  display: block;
}
```

### 区分舰队等级

文本消息 `yt-live-chat-text-message-renderer` 和上舰消息 `yt-live-chat-membership-item-renderer` 带有 `blc-guard-level` 属性区分舰队等级。

**blc-guard-level 取值：**
- `0`：非舰队成员
- `1`：总督
- `2`：提督
- `3`：舰长

### 区分付费消息金额档位

付费消息 `yt-live-chat-paid-message-renderer` 带有 `blc-price-level` 属性区分金额档位。其值从低到高为 `0`-`7`，`0` 代表免费礼物。

### 引用本地资源文件

如需引用本地资源，将文件放入 `data/custom_public/` 目录，通过绝对 URL `/custom_public/` 引用。例如 `data/custom_public/img/bg.png` 可通过 `/custom_public/img/bg.png` 引用。

禁止使用 `file:` 协议引用本地文件，这种方式不可移植到其他主机。
