export default {
  sidebar: {
    home: 'Home',
    stylegen: 'Style Generator',
    help: 'Help',
    plugins: 'Plugins',
    links: 'Links',
    projectAddress: 'Project Address',
    discussion: 'Discussions',
    documentation: 'Documentation',
    mall: 'Mall',
    giftRecordOfficial: 'Super Chat Records',
  },
  home: {
    roomIdEmpty: "Room ID can't be empty",
    roomIdInteger: 'Room ID must be positive integer',
    authCodeEmpty: "Identity code can't be empty",
    authCodeFormatError: 'Identity code format error',

    unavailableWhenUsingAuthCode: 'Deprecated. Unavailable when using identity code',
    disabledByServer: 'Disabled by the server',

    general: 'General',
    useAuthCodeWarning: 'Please prioritize the identity code, otherwise the avatars and usernames will not display',
    room: 'Room',
    roomId: 'Room ID (not recommended)',
    authCode: 'Identity code',
    howToGetAuthCode: 'How to get identity code',
    showDanmaku: 'Show messages',
    showGift: 'Show Super Chats',
    showGiftName: 'Show gift name',
    mergeSimilarDanmaku: 'Merge similar messages',
    mergeGift: 'Merge gifts',
    minGiftPrice: 'Min price of Super Chats to show (CNY)',
    maxNumber: 'Max number of messages',

    block: 'Block',
    giftDanmaku: 'Block system messages (gift effect)',
    blockLevel: 'Block user level lower than',
    informalUser: 'Block informal users',
    unverifiedUser: 'Block unverified users',
    blockKeywords: 'Block keywords',
    onePerLine: 'One per line',
    blockUsers: 'Block users',
    blockMedalLevel: 'Block medal level lower than',

    advanced: 'Advanced',
    showDebugMessages: 'Show debug messages',
    showDebugMessagesTip: 'If the messages cannot be displayed, you can enable this for debugging. Otherwise there is no need to enable it',
    relayMessagesByServer: 'Relay messages by the server',
    relayMessagesByServerTip: 'Message path when enabled: Bilibili server -> blivechat server -> your browser. Some advanced features require this to be enabled. It is recommended to enable it only when using blivechat locally, and not when using through a remote server',
    autoTranslate: 'Auto translate messages to Japanese',
    requiresRelayMessagesByServer: 'Requires relay messages by the server',
    giftUsernamePronunciation: 'Pronunciation of gift username',
    dontShow: 'None',
    pinyin: 'Pinyin',
    kana: 'Kana',
    importPresetCss: 'Import the server preset CSS',
    importPresetCssTip: 'Automatically import the server CSS file: data/custom_public/preset.css',

    emoticon: 'Custom Emotes',
    emoticonKeyword: 'Emote Code',
    emoticonUrl: 'URL',
    operation: 'Operation',
    addEmoticon: 'Add emote',
    emoticonFileTooLarge: 'File size is too large. Max size is 1MB',

    template: 'Custom HTML Templates',
    templateHelp: 'Help',
    templateHelpContent: `\
<p>Custom HTML templates allow complete customization of the room page, including DOM structure and CSS styles.
  Templates may be developed by third-party authors, and their security and quality are the responsibility of the template author.
  You can find some published templates on <a target="_blank" href="https://github.com/xfgryujk/blivechat/discussions/categories/%E8%87%AA%E5%AE%9A%E4%B9%89html%E6%A8%A1%E6%9D%BF"
  >GitHub Discussions</a></p>
<p>To install a template: Put the extracted template directory into the "data/custom_public/templates" directory, then wait
  about 10 seconds and refresh the webpage. Alternatively, you can directly enter the template URL to use an online template</p>
<p>Note: After modifying the template setting, the custom CSS in OBS will not take effect</p>
<p><a target="_blank" href="https://github.com/xfgryujk/blivechat/wiki/%E8%87%AA%E5%AE%9A%E4%B9%89HTML%E6%A8%A1%E6%9D%BF"
  >Template Development Documentation</a></p>
`,
    templateDefaultTitle: 'Default',
    templateDefaultDescription: 'A YouTube-style template that can be styled with custom CSS. Choose this if you are unfamiliar with custom HTML templates, otherwise your custom CSS in OBS will not take effect',
    templateCustomUrlTitle: 'Enter template URL',
    templateCustomUrlDescription: 'For templates not listed, you can manually enter the URL provided by the author here',
    author: 'Author: ',

    urlTooLong: 'The room URL is too long, and will be truncated by Livehime (but not by OBS)',
    roomUrlUpdated: 'The room URL is updated. Remember to copy it again',
    roomUrl: 'Room URL',
    enterRoom: 'Enter room',
    copyTestRoomUrl: 'Copy test room URL',
    exportConfig: 'Export config',
    importConfig: 'Import config',

    failedToParseConfig: 'Failed to parse config: '
  },
  stylegen: {
    legacy: 'Classic',
    lineLike: 'LINE-like',

    light: 'light',
    dark: 'dark',

    outlines: 'Outlines',
    showOutlines: 'Show outlines',
    outlineSize: 'Outline size',
    outlineColor: 'Outline color',

    avatars: 'Avatars',
    showAvatars: 'Show avatars',
    avatarSize: 'Avatar size',

    userNames: 'User Names',
    showUserNames: 'Show user names',
    font: 'Font',
    fontSelectTip: 'You can also input local font name. Fonts ranked first will be used first',
    recentFonts: 'Recent fonts',
    presetFonts: 'Preset fonts',
    networkFonts: 'Network fonts',
    localFonts: 'Local fonts',
    fontSize: 'Font size',
    lineHeight: 'Line height (0 for default)',
    normalColor: 'Normal color',
    ownerColor: 'Owner color',
    moderatorColor: 'Moderator color',
    memberColor: 'Member color',
    showBadges: 'Show badges',
    showColon: 'Show colon after name',
    emoticonSize: 'Emoticon size',
    largeEmoticonSize: 'Large emoticon size',

    messages: 'Messages',
    color: 'Color',
    onNewLine: 'On new line',
    messageReverseScroll: 'Reverse scrolling',

    time: 'Timestamps',
    showTime: 'Show timestamps',

    backgrounds: 'Backgrounds',
    bgColor: 'Background color',
    useBarsInsteadOfBg: 'Use bars instead of backgrounds',
    showLargeEmoticonBg: 'Show large emoticon background',
    messageBgColor: 'Message background color',
    ownerMessageBgColor: 'Owner background color',
    moderatorMessageBgColor: 'Moderator background color',
    memberMessageBgColor: 'Member background color',

    scAndNewMember: 'Super Chat / New Member',
    firstLineFont: 'First line font',
    firstLineFontSize: 'First line font size',
    firstLineLineHeight: 'First line line height (0 for default)',
    firstLineColor: 'First line color',
    secondLineFont: 'Second line font',
    secondLineFontSize: 'Second line font size',
    secondLineLineHeight: 'Second line line height (0 for default)',
    secondLineColor: 'Second line color',
    scContentLineFont: 'Super Chat content font',
    scContentLineFontSize: 'Super Chat content font size',
    scContentLineLineHeight: 'Super Chat content line height (0 for default)',
    scContentLineColor: 'Super Chat content color',
    showNewMemberBg: 'Show new member background',
    showScTicker: 'Show Super Chat ticker',
    showOtherThings: 'Show everything other than Super Chat ticker',

    animation: 'Animation',
    animateIn: 'Animate in',
    fadeInTime: 'Fade in time (miliseconds)',
    animateOut: 'Animate out (remove old messages)',
    animateOutWaitTime: 'Wait time (seconds)',
    fadeOutTime: 'Fade out time (miliseconds)',
    slide: 'Slide',
    reverseSlide: 'Reverse slide',
    playAnimation: 'Play animation',

    result: 'Result',
    copy: 'Copy',
    editor: 'Editor',
    resetConfig: 'Reset config'
  },
  help: {
    help: 'Help',
    p1_1: '1. Copy the identity code (身份码) from this webpage:',
    p1_2: '. NOTE: DO NOT refresh the identity code, unless it is leaked. Once you refresh the identity code, the old one will be invalid',
    p2: '2. Enter the identity code into the room configuration on the home page. Copy the room URL',
    p3: '3. Generate styles with the style generator. Copy the CSS',
    p4: '4. Add browser source in OBS',
    p5: '5. Enter the previously copied room URL at URL, and enter the previously copied CSS at custom CSS'
  },
  room: {
    fatalErrorOccurred: 'A fatal error has occurred. Please manually refresh the page to reconnect'
  },
  chat: {
    moderator: 'moderator',
    guardLevel1: 'governor',
    guardLevel2: 'admiral',
    guardLevel3: 'captain',
    sendGift: 'Sent {giftName}x{num}',
    membershipTitle: 'New member',
    tickerMembership: 'Member'
  },
  plugins: {
    plugins: 'Plugins',
    help: 'Help',
    helpContent: `\
<p>Plugins can add more functionality to blivechat, such as message logging, text to speech, song requests, etc. Plugins may
  be developed by third-party authors, and the security and quality are the responsibility of the plugin author. You can
  find some published plugins in <a target="_blank" href="https://github.com/xfgryujk/blivechat/discussions/categories/%E6%8F%92%E4%BB%B6"
  >GitHub Discussions</a></p>
<p>To install a plugin: Put the extracted plugin directory into the "data/plugins" directory, then restart blivechat</p>
<p>Notes: Most plugins require enabling the "Relay messages by the server" option and connecting to the room
  in order to receive messages</p>
<p><a target="_blank" href="https://www.bilibili.com/video/BV1nZ42187TX/">Introducing Video</a></p>
<p><a target="_blank" href="https://github.com/xfgryujk/blivechat/wiki/%E6%8F%92%E4%BB%B6%E7%B3%BB%E7%BB%9F"
  >Plugin Development Documentation</a></p>
`,
    author: 'Author: ',
    disabledByServer: 'Administration for plugins is disabled by the server',
    admin: 'Admin',
    connected: 'Connected',
    unconnected: 'Unconnected',
  },
}
