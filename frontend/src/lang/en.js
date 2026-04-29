export default {
  sidebar: {
    home: 'Home',
    stylegen: 'Style generator',
    help: 'Help',
    plugins: 'Plugins',
    links: 'Links',
    projectAddress: 'Project address',
    discussion: 'Discussions',
    documentation: 'Documentation',
    mall: 'Bilibili store',
    giftRecordOfficial: 'Payment records',
  },
  home: {
    roomIdEmpty: "Room ID can't be empty",
    roomIdInteger: 'Room ID must be a positive integer',
    authCodeEmpty: "Identity code can't be empty",
    authCodeFormatError: 'Identity code format error',

    unavailableWhenUsingAuthCode: 'Deprecated — unavailable when using identity code',
    disabledByServer: 'Disabled by the server',

    general: 'General',
    useAuthCodeWarning: 'Please use an identity code whenever possible. Without one, usernames will not display and message retrieval may stop working at any time',
    room: 'Room',
    roomId: 'Room ID (NOT recommended)',
    authCode: 'Identity code',
    howToGetAuthCode: 'How to get an identity code',
    showDanmaku: 'Show chat messages',
    showGift: 'Show paid messages',
    showGiftName: 'Show gift names',
    mergeSimilarDanmaku: 'Merge similar chat messages',
    mergeGift: 'Merge gifts',
    minGiftPrice: 'Min paid message price to show (CNY)',
    maxNumber: 'Max number of messages',

    block: 'Block',
    giftDanmaku: 'Block raffle messages',
    mirrorMessage: 'Block cross-room messages',
    blockLevel: 'Block user level below',
    informalUser: 'Block informal users',
    unverifiedUser: 'Block unverified users',
    blockKeywords: 'Block keywords',
    onePerLine: 'One per line',
    blockUsers: 'Block users',
    blockMedalLevel: 'Block medal level below',

    advanced: 'Advanced',
    showDebugMessages: 'Show debug messages',
    showDebugMessagesTip: 'Enable for troubleshooting when messages fail to display. No need to enable during normal use',
    relayMessagesByServer: 'Relay messages through the server',
    relayMessagesByServerTip: 'When enabled, message path: Bilibili server → blivechat server → your browser. Required by some advanced features. Recommended when using locally; leave off when connecting to a remote server',
    autoTranslate: 'Auto-translate messages to Japanese',
    requiresRelayMessagesByServer: 'Requires "Relay messages through the server"',
    giftUsernamePronunciation: 'Pronunciation of gift usernames',
    dontShow: 'None',
    pinyin: 'Pinyin',
    kana: 'Kana',
    importPresetCss: 'Import server preset CSS',
    importPresetCssTip: 'Automatically use the server CSS file "data/custom_public/preset.css" without setting the custom CSS in OBS',

    emoticon: 'Custom emotes',
    emoticonKeyword: 'Emote code',
    emoticonUrl: 'URL',
    operation: 'Actions',
    addEmoticon: 'Add emote',
    emoticonFileTooLarge: 'File too large. Max size: 1 MB',

    template: 'Custom HTML template',
    templateHelp: 'Help',
    templateHelpContent: `\
<p>Custom HTML templates allow full customization of the room page, including DOM structure and CSS styles.
  Templates may be developed by third-party authors, who are responsible for their security and quality.
  You can find published templates on <a target="_blank" href="https://github.com/xfgryujk/blivechat/discussions/categories/%E8%87%AA%E5%AE%9A%E4%B9%89html%E6%A8%A1%E6%9D%BF"
  >GitHub Discussions</a></p>
<p>Installation: extract the template folder into "data/custom_public/templates" folder, wait about 10 seconds, then refresh the page.
  You can also enter a URL directly to use an online template</p>
<p>Note: after changing the template setting, custom CSS in OBS will no longer take effect by default</p>
<p><a target="_blank" href="https://github.com/xfgryujk/blivechat/wiki/%E8%87%AA%E5%AE%9A%E4%B9%89HTML%E6%A8%A1%E6%9D%BF"
  >Template Development Docs</a></p>
`,
    templateDefaultTitle: 'Default',
    templateDefaultDescription: 'A YouTube-style template that can be customized with CSS. Choose this unless you are familiar with HTML templates, otherwise your custom CSS in OBS will not apply',
    templateCustomUrlTitle: 'Enter template URL',
    templateCustomUrlDescription: 'For templates not listed below, paste the URL provided by the author here',
    author: 'Author: ',

    urlTooLong: 'The room URL is too long and may be truncated by Bilibili Livehime (OBS is unaffected)',
    roomUrlUpdated: 'Room URL updated — remember to re-copy it',
    roomUrl: 'Room URL',
    enterRoom: 'Enter room',
    copyTestRoomUrl: 'Copy test room URL',
    exportConfig: 'Export config',
    importConfig: 'Import config',

    failedToParseConfig: 'Failed to parse config: '
  },
  stylegen: {
    legacy: 'Classic',
    lineLike: 'LINE-style',

    playAnimation: 'Generate messages',
    messageSpeed: 'Messages per second',
    messageTypes: 'Message types',
    typeText: 'Text',
    typeEmoticon: 'Emote',
    typeGift: 'Gift',
    typeSuperChat: 'Super Chat',
    typeMember: 'Membership',

    light: 'Light',
    dark: 'Dark',

    global: 'Global',
    scalingNotice: 'If the text looks too small, adjust these ratio first instead of stretching the browser source in OBS',
    globalScale: 'Global scale',
    fontScale: 'Font scale',

    outlines: 'Outlines',
    showOutlines: 'Show outlines',
    outlineSize: 'Outline width',
    outlineColor: 'Outline color',
    blurryOutline: 'Blurry',

    avatars: 'Avatars',
    showAvatars: 'Show avatars',
    avatarSize: 'Avatar size',

    userNames: 'User names',
    showUserNames: 'Show user names',
    font: 'Font',
    fontSelectTip: 'You can also enter a local font name. Fonts listed first are given priority',
    recentFonts: 'Recent fonts',
    presetFonts: 'Preset fonts',
    networkFonts: 'Web fonts',
    localFonts: 'Local fonts',
    fontSize: 'Font size',
    fontWeight: 'Font weight',
    normalColor: 'Normal color',
    ownerColor: 'Streamer color',
    moderatorColor: 'Moderator color',
    memberColor: 'Member color',
    showBadges: 'Show badges',
    showColon: 'Show colon after name',
    emoticonSize: 'Emote size',
    largeEmoticonSize: 'Large emote size',

    messages: 'Messages',
    color: 'Color',
    onNewLine: 'On new line',
    messageReverseScroll: 'Reverse scrolling',

    time: 'Timestamps',
    showTime: 'Show timestamps',

    backgrounds: 'Backgrounds',
    bgColor: 'Background color',
    useBarsInsteadOfBg: 'Use bars instead of backgrounds',
    showLargeEmoticonBg: 'Show large emote background',
    messageBgColor: 'Normal background color',
    ownerMessageBgColor: 'Streamer background color',
    moderatorMessageBgColor: 'Moderator background color',
    memberMessageBgColor: 'Member background color',

    scAndNewMember: 'Paid messages',
    firstLineFont: 'First line font',
    firstLineFontSize: 'First line font size',
    firstLineWeight: 'First line font weight',
    firstLineColor: 'First line color',
    secondLineFont: 'Second line font',
    secondLineFontSize: 'Second line font size',
    secondLineWeight: 'Second line font weight',
    secondLineColor: 'Second line color',
    scContentLineFont: 'Super Chat content font',
    scContentLineFontSize: 'Super Chat content font size',
    scContentWeight: 'Super Chat content font weight',
    scContentLineColor: 'Super Chat content color',
    showScTicker: 'Show Super Chat ticker',
    showOtherThings: 'Show content outside the Super Chat ticker',

    animation: 'Animation',
    animateIn: 'Animate in',
    fadeInTime: 'Fade in time (ms)',
    animateOut: 'Animate out (remove old messages)',
    animateOutWaitTime: 'Wait time before removal (seconds)',
    fadeOutTime: 'Fade out time (ms)',
    slide: 'Slide',
    reverseSlide: 'Reverse slide',

    result: 'Result CSS',
    copy: 'Copy',
    editor: 'Editor',
    resetConfig: 'Reset config to default'
  },
  help: {
    help: 'Help',
    p1_1: '1. Copy the identity code (身份码) from this page:',
    p1_2: '. Note: do NOT refresh the identity code unless it has been leaked. Refreshing it invalidates the old code',
    p2: '2. Enter the identity code in the room settings on the home page, then copy the room URL',
    p3: '3. Use the Style Generator to create your styles, then copy the CSS',
    p4: '4. Add a browser source in OBS',
    p5: '5. Paste the room URL in the URL field and the CSS in the Custom CSS field'
  },
  room: {
    fatalErrorOccurred: 'A fatal error occurred. Please refresh the page to reconnect'
  },
  chat: {
    moderator: 'Moderator',
    guardLevel1: 'Governor',
    guardLevel2: 'Admiral',
    guardLevel3: 'Captain',
    mirrorMsg: '[Cross-room] ',
    sendGift: 'Sent {giftName}x{num}',
    membershipTitle: 'New member',
    tickerMembership: 'Member'
  },
  plugins: {
    plugins: 'Plugins',
    help: 'Help',
    helpContent: `\
<p>Plugins can add extra features to blivechat — message logging, text-to-speech, song requests, and more. Plugins
  may be developed by third-party authors, who are responsible for their security and quality.
  Find published plugins on <a target="_blank" href="https://github.com/xfgryujk/blivechat/discussions/categories/%E6%8F%92%E4%BB%B6"
  >GitHub Discussions</a></p>
<p>Installation: extract the plugin folder into "data/plugins" folder, then restart blivechat</p>
<p>Note: most plugins require "Relay messages through the server" to be enabled and a room connection to receive messages</p>
<p><a target="_blank" href="https://www.bilibili.com/video/BV1nZ42187TX/">Introductory Video</a></p>
<p><a target="_blank" href="https://github.com/xfgryujk/blivechat/wiki/%E6%8F%92%E4%BB%B6%E7%B3%BB%E7%BB%9F"
  >Plugin Development Docs</a></p>
`,
    author: 'Author: ',
    disabledByServer: 'Plugin administration is disabled by the server',
    admin: 'Admin',
    connected: 'Connected',
    unconnected: 'Disconnected',
  },
}
