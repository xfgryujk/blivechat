export default {
  sidebar: {
    home: '首页',
    stylegen: '样式生成器',
    help: '帮助',
    plugins: '插件',
    links: '常用链接',
    projectAddress: '项目地址',
    discussion: '反馈 / 交流',
    documentation: '文档',
    mall: 'B站商店',
    giftRecordOfficial: '打赏记录',
  },
  home: {
    roomIdEmpty: '房间ID不能为空',
    roomIdInteger: '房间ID必须为正整数',
    authCodeEmpty: '身份码不能为空',
    authCodeFormatError: '身份码格式错误',

    unavailableWhenUsingAuthCode: '已过时，使用身份码时不可用',
    disabledByServer: '已被服务器禁用',

    general: '常规',
    useAuthCodeWarning: '请优先使用身份码，否则无法显示头像和昵称',
    room: '房间',
    roomId: '房间ID（不推荐）',
    authCode: '身份码',
    howToGetAuthCode: '如何获取身份码',
    showDanmaku: '显示弹幕',
    showGift: '显示打赏和新舰长',
    showGiftName: '显示礼物名',
    mergeSimilarDanmaku: '合并相似弹幕',
    mergeGift: '合并礼物',
    minGiftPrice: '最低显示打赏价格（元）',
    maxNumber: '最大弹幕数',

    block: '屏蔽',
    giftDanmaku: '屏蔽礼物弹幕',
    blockLevel: '屏蔽用户等级低于',
    informalUser: '屏蔽非正式会员',
    unverifiedUser: '屏蔽未绑定手机用户',
    blockKeywords: '屏蔽关键词',
    onePerLine: '一行一个',
    blockUsers: '屏蔽用户',
    blockMedalLevel: '屏蔽当前直播间勋章等级低于',

    advanced: '高级',
    showDebugMessages: '显示调试消息',
    showDebugMessagesTip: '如果消息不能显示，可以开启这个用来调试，否则没必要开启',
    relayMessagesByServer: '通过服务器转发消息',
    relayMessagesByServerTip: '开启时的消息路径：B站服务器 -> blivechat服务器 -> 你的浏览器。部分高级功能需要开启这个。推荐只在本地使用blivechat时开启，而通过远程服务器使用时不开启',
    autoTranslate: '自动翻译弹幕到日语',
    requiresRelayMessagesByServer: '需要通过服务器转发消息',
    giftUsernamePronunciation: '标注打赏用户名读音',
    dontShow: '不显示',
    pinyin: '拼音',
    kana: '日文假名',
    importPresetCss: '导入服务器预设CSS',
    importPresetCssTip: '自动导入服务器的CSS文件：data/custom_public/preset.css',

    emoticon: '自定义表情',
    emoticonKeyword: '替换关键词',
    emoticonUrl: 'URL',
    operation: '操作',
    addEmoticon: '添加表情',
    emoticonFileTooLarge: '文件尺寸太大，最大1MB',

    template: '自定义HTML模板',
    templateHelp: '帮助',
    templateHelpContent: `\
<p>自定义HTML模板可以完全自定义房间页面，包括DOM结构、CSS样式。模板可能由第三方作者开发，其安全性和质量由模板作者负责。
  你可以在<a target="_blank" href="https://github.com/xfgryujk/blivechat/discussions/categories/%E8%87%AA%E5%AE%9A%E4%B9%89html%E6%A8%A1%E6%9D%BF"
  >GitHub Discussions</a>获取一些已发布的模板</p>
<p>模板安装方法：把解压后的模板目录放到“data/custom_public/templates”目录，然后等待约10秒后刷新网页。
  另外你也可以直接输入模板URL来使用在线模板</p>
<p>注意：修改自定义模板设置后，OBS中的自定义CSS将不会生效</p>
<p><a target="_blank" href="https://github.com/xfgryujk/blivechat/wiki/%E8%87%AA%E5%AE%9A%E4%B9%89HTML%E6%A8%A1%E6%9D%BF">模板开发文档</a></p>
`,
    templateDefaultTitle: '默认',
    templateDefaultDescription: '仿YouTube风格的模板，可以用自定义CSS修改样式。如果你不了解自定义HTML模板的功能，就选择这个，否则OBS中的自定义CSS不会生效',
    templateCustomUrlTitle: '输入模板URL',
    templateCustomUrlDescription: '没有列出的模板，也可以在这里手动输入作者提供的URL',
    author: '作者：',

    urlTooLong: '房间URL太长了，会被直播姬截断（OBS不会）',
    roomUrlUpdated: '房间URL已更新，记得重新复制',
    roomUrl: '房间URL',
    enterRoom: '进入房间',
    copyTestRoomUrl: '复制测试房间URL',
    exportConfig: '导出配置',
    importConfig: '导入配置',

    failedToParseConfig: '配置解析失败：'
  },
  stylegen: {
    legacy: '经典',
    lineLike: '仿微信',

    light: '亮色',
    dark: '暗色',

    outlines: '描边',
    showOutlines: '显示描边',
    outlineSize: '描边尺寸',
    outlineColor: '描边颜色',

    avatars: '头像',
    showAvatars: '显示头像',
    avatarSize: '头像尺寸',

    userNames: '用户名',
    showUserNames: '显示用户名',
    font: '字体',
    fontSelectTip: '你也可以输入本地字体名。前面的字体会被优先使用',
    recentFonts: '最近使用的字体',
    presetFonts: '预设字体',
    networkFonts: '网络字体',
    localFonts: '本地字体',
    fontSize: '字体尺寸',
    lineHeight: '行高（0为默认）',
    normalColor: '普通颜色',
    ownerColor: '主播颜色',
    moderatorColor: '房管颜色',
    memberColor: '舰长颜色',
    showBadges: '显示勋章',
    showColon: '用户名后显示冒号',
    emoticonSize: '表情大小',
    largeEmoticonSize: '大表情大小',

    messages: '消息',
    color: '颜色',
    onNewLine: '在新行显示',

    time: '时间',
    showTime: '显示时间',

    backgrounds: '背景',
    bgColor: '背景色',
    useBarsInsteadOfBg: '用条代替消息背景',
    showLargeEmoticonBg: '显示大表情背景',
    messageBgColor: '消息背景色',
    ownerMessageBgColor: '主播消息背景色',
    moderatorMessageBgColor: '房管消息背景色',
    memberMessageBgColor: '舰长消息背景色',

    scAndNewMember: '打赏、舰长',
    firstLineFont: '第一行字体',
    firstLineFontSize: '第一行字体尺寸',
    firstLineLineHeight: '第一行行高（0为默认）',
    firstLineColor: '第一行颜色',
    secondLineFont: '第二行字体',
    secondLineFontSize: '第二行字体尺寸',
    secondLineLineHeight: '第二行行高（0为默认）',
    secondLineColor: '第二行颜色',
    scContentLineFont: 'Super Chat内容字体',
    scContentLineFontSize: 'Super Chat内容字体尺寸',
    scContentLineLineHeight: 'Super Chat内容行高（0为默认）',
    scContentLineColor: 'Super Chat内容颜色',
    showNewMemberBg: '显示新舰长背景',
    showScTicker: '显示Super Chat固定栏',
    showOtherThings: '显示Super Chat固定栏之外的内容',

    animation: '动画',
    animateIn: '进入动画',
    fadeInTime: '淡入时间（毫秒）',
    animateOut: '移除旧消息',
    animateOutWaitTime: '移除前等待时间（秒）',
    fadeOutTime: '淡出时间（毫秒）',
    slide: '滑动',
    reverseSlide: '反向滑动',
    playAnimation: '生成消息',

    result: '结果',
    copy: '复制',
    editor: '编辑器',
    resetConfig: '恢复默认设置'
  },
  help: {
    help: '帮助',
    p1_1: '1. 从这个页面复制身份码：',
    p1_2: '。注意：不要刷新身份码，除非你的身份码泄露了，因为刷新身份码会使旧的身份码失效',
    p2: '2. 把身份码输入到首页的房间配置，复制房间URL',
    p3: '3. 使用样式生成器生成样式，复制CSS',
    p4: '4. 在OBS中添加浏览器源',
    p5: '5. URL处输入之前复制的房间URL，自定义CSS处输入之前复制的CSS'
  },
  room: {
    fatalErrorOccurred: '发生了一个致命错误，请手动刷新页面以重新连接'
  },
  chat: {
    moderator: '管理员',
    guardLevel1: '总督',
    guardLevel2: '提督',
    guardLevel3: '舰长',
    sendGift: '赠送 {giftName}x{num}',
    membershipTitle: '新会员',
    tickerMembership: '会员'
  },
  plugins: {
    plugins: '插件',
    help: '帮助',
    helpContent: `\
<p>插件可以给blivechat添加更多功能，比如消息日志、语音播报、点歌等。插件可能由第三方作者开发，其安全性和质量由插件作者负责。
  你可以在<a target="_blank" href="https://github.com/xfgryujk/blivechat/discussions/categories/%E6%8F%92%E4%BB%B6"
  >GitHub Discussions</a>获取一些已发布的插件</p>
<p>插件安装方法：把解压后的插件目录放到“data/plugins”目录，然后重启blivechat</p>
<p>注意：大部分插件需要开启“通过服务器转发消息”，并且连接到房间，才能接收消息</p>
<p><a target="_blank" href="https://www.bilibili.com/video/BV1nZ42187TX/">介绍视频</a></p>
<p><a target="_blank" href="https://github.com/xfgryujk/blivechat/wiki/%E6%8F%92%E4%BB%B6%E7%B3%BB%E7%BB%9F">插件开发文档</a></p>
`,
    author: '作者：',
    disabledByServer: '已被服务器禁用',
    admin: '管理',
    connected: '已连接',
    unconnected: '未连接',
  },
}
