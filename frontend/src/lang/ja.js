export default {
  sidebar: {
    home: 'ホーム',
    stylegen: 'スタイルジェネレーター',
    help: 'ヘルプ',
    plugins: 'プラグイン',
    links: 'リンク',
    projectAddress: 'プロジェクトアドレス',
    discussion: 'ディスカッション',
    documentation: 'ドキュメント',
    mall: 'Bilibiliストア',
    giftRecordOfficial: '支払い記録',
  },
  home: {
    roomIdEmpty: 'ルームIDを入力してください',
    roomIdInteger: 'ルームIDは正の整数でなければなりません',
    authCodeEmpty: 'アイデンティティコードを入力してください',
    authCodeFormatError: 'アイデンティティコードの形式が正しくありません',

    unavailableWhenUsingAuthCode: '非推奨 — アイデンティティコード使用時は利用不可',
    disabledByServer: 'サーバーによって無効化されています',

    general: '一般',
    useAuthCodeWarning: 'アイデンティティコードの使用を推奨します。使用しない場合、ユーザー名が表示されず、いつコメント取得ができなくなるか分かりません',
    room: 'ルーム',
    roomId: 'ルームID（非推奨）',
    authCode: 'アイデンティティコード',
    howToGetAuthCode: 'アイデンティティコードの取得方法',
    showDanmaku: 'コメントを表示',
    showGift: '有料メッセージを表示',
    showGiftName: 'ギフト名を表示',
    mergeSimilarDanmaku: '類似コメントをまとめる',
    mergeGift: 'ギフトをまとめる',
    minGiftPrice: '表示する最低金額（CNY）',
    maxNumber: '最大メッセージ数',

    block: 'ブロック',
    giftDanmaku: '抽選コメントをブロック',
    mirrorMessage: '他ルームからのメッセージをブロック',
    blockLevel: 'ブロック：ユーザーレベルが以下の場合',
    informalUser: '非正式ユーザーをブロック',
    unverifiedUser: '未認証ユーザーをブロック',
    blockKeywords: 'ブロックキーワード',
    onePerLine: '1行に1つ',
    blockUsers: 'ブロックユーザー',
    blockMedalLevel: 'ブロック：メダルレベルが以下の場合',

    advanced: '詳細設定',
    showDebugMessages: 'デバッグメッセージを表示',
    showDebugMessagesTip: 'メッセージが表示されない場合のトラブルシューティング用です。通常時は有効にする必要はありません',
    relayMessagesByServer: 'サーバー経由でメッセージを転送',
    relayMessagesByServerTip: '有効時のメッセージ経路：Bilibiliサーバー → blivechatサーバー → ブラウザ。一部の高度な機能に必要です。ローカル使用時は有効を推奨、リモートサーバー経由ではオフにしてください',
    autoTranslate: 'メッセージを日本語に自動翻訳',
    requiresRelayMessagesByServer: '「サーバー経由でメッセージを転送」が必須です',
    giftUsernamePronunciation: '有料メッセージ送信者のユーザー名の読み方',
    dontShow: '表示しない',
    pinyin: 'ピンイン',
    kana: 'かな',
    importPresetCss: 'サーバープリセットCSSをインポート',
    importPresetCssTip: 'サーバーのCSSファイル「data/custom_public/preset.css」を自動的に適用し、OBSでカスタムCSSを設定する手間を省きます',

    emoticon: 'カスタムスタンプ',
    emoticonKeyword: '置き換えキーワード',
    emoticonUrl: 'URL',
    operation: '操作',
    addEmoticon: 'スタンプを追加',
    emoticonFileTooLarge: 'ファイルサイズが大きすぎます（最大1MB）',

    template: 'カスタムHTMLテンプレート',
    templateHelp: 'ヘルプ',
    templateHelpContent: `\
<p>カスタムHTMLテンプレートを使用すると、DOM構造やCSSスタイルを含むルームページを完全にカスタマイズできます。
  テンプレートはサードパーティの作者によって開発される場合があり、セキュリティと品質はテンプレート作者の責任となります。
  公開されているテンプレートは<a target="_blank" href="https://github.com/xfgryujk/blivechat/discussions/categories/%E8%87%AA%E5%AE%9A%E4%B9%89html%E6%A8%A1%E6%9D%BF"
  >GitHub Discussions</a>で入手できます</p>
<p>インストール方法：解凍したテンプレートフォルダを「data/custom_public/templates」フォルダに配置し、約10秒待ってからページを更新してください。
  また、URLを直接入力してオンラインテンプレートを使用することもできます</p>
<p>注意：テンプレート設定を変更すると、OBSのカスタムCSSはデフォルトで反映されなくなります</p>
<p><a target="_blank" href="https://github.com/xfgryujk/blivechat/wiki/%E8%87%AA%E5%AE%9A%E4%B9%89HTML%E6%A8%A1%E6%9D%BF"
  >テンプレート開発ドキュメント</a></p>
`,
    templateDefaultTitle: 'デフォルト',
    templateDefaultDescription: 'YouTubeスタイルのテンプレートで、カスタムCSSでスタイルを変更できます。HTMLテンプレートに詳しくない場合はこちらを選択してください。そうでないとOBSのカスタムCSSが反映されません',
    templateCustomUrlTitle: 'テンプレートURLを入力',
    templateCustomUrlDescription: 'リストにないテンプレートは、作者が提供するURLをここに貼り付けてください',
    author: '作者：',

    urlTooLong: 'ルームURLが長すぎるため、Bilibili Livehime（直播姬）で切り詰められる可能性があります（OBSでは問題ありません）',
    roomUrlUpdated: 'ルームURLが更新されました — 再コピーをお忘れなく',
    roomUrl: 'ルームURL',
    enterRoom: 'ルームに入室',
    copyTestRoomUrl: 'テスト用ルームURLをコピー',
    exportConfig: '設定をエクスポート',
    importConfig: '設定をインポート',

    failedToParseConfig: '設定の解析に失敗しました：'
  },
  stylegen: {
    legacy: 'クラシック',
    lineLike: 'LINE風',

    playAnimation: 'メッセージを生成',
    messageSpeed: '毎秒メッセージ数',
    messageTypes: 'メッセージタイプ',
    typeText: 'テキスト',
    typeEmoticon: 'スタンプ',
    typeGift: 'ギフト',
    typeSuperChat: 'Super Chat',
    typeMember: 'メンバーシップ',

    light: 'ライト',
    dark: 'ダーク',

    global: '全体',
    scalingNotice: '文字が小さすぎると感じる場合は、OBSでブラウザソースを引き伸ばすのではなく、まずこちらの比率を調整してください',
    globalScale: '全体の拡大率',
    fontScale: 'フォント拡大率',

    outlines: 'アウトライン',
    showOutlines: 'アウトラインを表示',
    outlineSize: 'アウトラインの太さ',
    outlineColor: 'アウトラインの色',
    blurryOutline: 'ぼかし',

    avatars: 'アイコン',
    showAvatars: 'アイコンを表示',
    avatarSize: 'アイコンのサイズ',

    userNames: 'ユーザー名',
    showUserNames: 'ユーザー名を表示',
    font: 'フォント',
    fontSelectTip: 'ローカルフォント名を入力することもできます。リストの上位にあるフォントが優先されます',
    recentFonts: '最近使用したフォント',
    presetFonts: 'プリセットフォント',
    networkFonts: 'Webフォント',
    localFonts: 'ローカルフォント',
    fontSize: 'フォントサイズ',
    fontWeight: 'フォントの太さ',
    normalColor: '通常の色',
    ownerColor: '配信者の色',
    moderatorColor: 'モデレーターの色',
    memberColor: 'メンバーの色',
    showBadges: 'バッジを表示',
    showColon: 'ユーザー名の後にコロンを表示',
    emoticonSize: 'スタンプサイズ',
    largeEmoticonSize: '大スタンプサイズ',

    messages: 'コメント',
    color: '色',
    onNewLine: '改行して表示',
    messageReverseScroll: '逆方向にスクロール',

    time: 'タイムスタンプ',
    showTime: 'タイムスタンプを表示',

    backgrounds: '背景',
    bgColor: '背景色',
    useBarsInsteadOfBg: '背景の代わりにバーを使用',
    showLargeEmoticonBg: '大スタンプの背景を表示',
    messageBgColor: '通常背景色',
    ownerMessageBgColor: '配信者背景色',
    moderatorMessageBgColor: 'モデレーター背景色',
    memberMessageBgColor: 'メンバー背景色',

    scAndNewMember: '有料メッセージ',
    firstLineFont: '1行目のフォント',
    firstLineFontSize: '1行目のフォントサイズ',
    firstLineWeight: '1行目のフォントの太さ',
    firstLineColor: '1行目の色',
    secondLineFont: '2行目のフォント',
    secondLineFontSize: '2行目のフォントサイズ',
    secondLineWeight: '2行目のフォントの太さ',
    secondLineColor: '2行目の色',
    scContentLineFont: 'Super Chat内容のフォント',
    scContentLineFontSize: 'Super Chat内容のフォントサイズ',
    scContentWeight: 'Super Chat内容のフォントの太さ',
    scContentLineColor: 'Super Chat内容の色',
    showScTicker: 'Super Chatティッカーを表示',
    showOtherThings: 'Super Chatティッカー以外の内容を表示',

    animation: 'アニメーション',
    animateIn: '入場アニメーション',
    fadeInTime: 'フェードイン時間（ミリ秒）',
    animateOut: '退場アニメーション（古いメッセージを削除）',
    animateOutWaitTime: '削除前の待機時間（秒）',
    fadeOutTime: 'フェードアウト時間（ミリ秒）',
    slide: 'スライド',
    reverseSlide: '逆スライド',

    result: '結果CSS',
    copy: 'コピー',
    editor: 'エディタ',
    resetConfig: '設定をデフォルトに戻す'
  },
  help: {
    help: 'ヘルプ',
    p1_1: '1. このページからアイデンティティコード（身份码）をコピーします：',
    p1_2: '。注意：アイデンティティコードは、漏洩した場合を除き更新しないでください。更新すると古いコードは無効になります',
    p2: '2. ホームページのルーム設定にアイデンティティコードを入力し、ルームURLをコピーします',
    p3: '3. スタイルジェネレーターで好みのスタイルを作成し、CSSをコピーします',
    p4: '4. OBSでブラウザソースを追加します',
    p5: '5. URL欄に先ほどコピーしたルームURLを、カスタムCSS欄に先ほどのCSSを貼り付けます'
  },
  room: {
    fatalErrorOccurred: '致命的なエラーが発生しました。ページを更新して再接続してください'
  },
  chat: {
    moderator: 'モデレーター',
    guardLevel1: '総督',
    guardLevel2: '提督',
    guardLevel3: '艦長',
    mirrorMsg: '[他ルーム] ',
    sendGift: '{giftName}x{num} を贈りました',
    membershipTitle: '新規メンバー',
    tickerMembership: 'メンバー'
  },
  plugins: {
    plugins: 'プラグイン',
    help: 'ヘルプ',
    helpContent: `\
<p>プラグインを使用すると、メッセージログ、読み上げ、リクエスト曲など、blivechatに追加機能を組み込めます。
  プラグインはサードパーティの作者によって開発される場合があり、セキュリティと品質はプラグイン作者の責任です。
  公開されているプラグインは<a target="_blank" href="https://github.com/xfgryujk/blivechat/discussions/categories/%E6%8F%92%E4%BB%B6"
  >GitHub Discussions</a>で見つけることができます</p>
<p>インストール方法：解凍したプラグインフォルダを「data/plugins」フォルダに配置し、blivechatを再起動します</p>
<p>注意：ほとんどのプラグインは、「サーバー経由でメッセージを転送」を有効にし、ルームに接続してメッセージを受信する必要があります</p>
<p><a target="_blank" href="https://www.bilibili.com/video/BV1nZ42187TX/">紹介動画</a></p>
<p><a target="_blank" href="https://github.com/xfgryujk/blivechat/wiki/%E6%8F%92%E4%BB%B6%E7%B3%BB%E7%BB%9F"
  >プラグイン開発ドキュメント</a></p>
`,
    author: '作者：',
    disabledByServer: 'プラグイン管理はサーバーによって無効化されています',
    admin: '管理',
    connected: '接続済み',
    unconnected: '未接続',
  },
}
