export default {
  sidebar: {
    home: 'トップページ',
    stylegen: 'スタイルジェネレータ',
    help: 'ヘルプ',
    plugins: 'プラグイン',
    links: 'リンク',
    projectAddress: 'プロジェクトアドレス',
    discussion: '議論',
    documentation: 'ドキュメンテーション',
    mall: 'モール',
    giftRecordOfficial: 'スーパーチャット記録',
  },
  home: {
    roomIdEmpty: 'ルームのIDを空白にすることはできません',
    roomIdInteger: 'ルームは正の整数でなければなりません',
    authCodeEmpty: 'アイデンティティコードを空白にすることはできません',
    authCodeFormatError: 'アイデンティティコードの形式エラー',

    unavailableWhenUsingAuthCode: '非推奨です。アイデンティティコードを使用する際に利用できません',
    disabledByServer: 'サーバーによって無効にされました',

    general: '常規',
    useAuthCodeWarning: 'アイデンティティコードを優先的に使用してください。そうしないと、アイコンやユーザー名が表示されません',
    room: 'ルーム',
    roomId: 'ルームID（推奨されません）',
    authCode: 'アイデンティティコード',
    howToGetAuthCode: 'アイデンティティコードの取得方法',
    showDanmaku: 'コメントを表示する',
    showGift: 'スーパーチャットと新メンバーを表示する',
    showGiftName: 'ギフト名を表示する',
    mergeSimilarDanmaku: '同じコメントを合併する',
    mergeGift: 'ギフトを合併する',
    minGiftPrice: '最低表示スーパーチャット価格（CNY）',
    maxNumber: '最大コメント数',

    block: 'ブロック',
    giftDanmaku: 'ブロックシステムコメント（プレゼント効果）',
    blockLevel: 'ブロックユーザーレベルがx未満',
    informalUser: 'ブロック非公式ユーザー',
    unverifiedUser: 'ブロック認証されていないユーザー',
    blockKeywords: 'ブロックキーワード',
    onePerLine: '1行に1つずつ',
    blockUsers: 'ブロックユーザー',
    blockMedalLevel: 'ブロック勲章等級がx未満',

    advanced: 'アドバンスド',
    showDebugMessages: 'デバッグメッセージを表示する',
    showDebugMessagesTip: 'メッセージが表示されない場合、デバッグのためにこれを有効にすることができます。それ以外の場合は、有効にする必要はありません',
    relayMessagesByServer: 'サーバを介してメッセージを転送する',
    relayMessagesByServerTip: '有効になった場合のメッセージパス：Bilibiliサーバー -> blivechatサーバー -> あなたのブラウザー。一部の高度な機能では、これが有効になっている必要があります。blivechatをローカルで使用する場合にのみ有効にすることを推奨します。リモートサーバーを介して使用する場合には、有効にしないようにしてください',
    autoTranslate: 'コメントを日本語に翻訳する',
    requiresRelayMessagesByServer: 'サーバを介してメッセージを転送する必要',
    giftUsernamePronunciation: 'スーパーチャットのユーザー名の発音',
    dontShow: '非表示',
    pinyin: 'ピンイン',
    kana: '仮名',
    importPresetCss: 'サーバープリセットのCSSをインポートする',
    importPresetCssTip: 'サーバーのCSSファイル「data/custom_public/preset.css」を自動的にインポートする',

    emoticon: 'カスタムスタンプ',
    emoticonKeyword: '置き換えるキーワード',
    emoticonUrl: 'URL',
    operation: '操作',
    addEmoticon: 'スタンプを追加',
    emoticonFileTooLarge: 'ファイルサイズが大きすぎます。最大サイズは1MBです',

    urlTooLong: 'ルームのURLが長すぎて、直播姬によって切り詰められます（ただし、OBSでは切り詰められません）',
    roomUrlUpdated: 'ルームのURLが更新されました。再度コピーすることをお忘れなく',
    roomUrl: 'ルームのURL',
    enterRoom: 'ルームに入る',
    copyTestRoomUrl: 'テストルームのURLをコピーする',
    exportConfig: 'コンフィグの導出',
    importConfig: 'コンフィグの導入',

    failedToParseConfig: 'コンフィグ解析に失敗しました'
  },
  stylegen: {
    legacy: '古典',
    lineLike: 'LINE風',

    light: '明るい',
    dark: '暗い',

    outlines: 'アウトライン',
    showOutlines: 'アウトラインを表示する',
    outlineSize: 'アウトラインのサイズ',
    outlineColor: 'アウトラインの色',

    avatars: 'アイコン',
    showAvatars: 'アイコンを表示する',
    avatarSize: 'アイコンのサイズ',

    userNames: 'ユーザー名',
    showUserNames: 'ユーザー名を表示する',
    font: 'フォント',
    fontSelectTip: 'ローカルフォント名も入力することができます',
    fontSize: 'フォントサイズ',
    lineHeight: '行の高さ（0はデフォルト）',
    normalColor: 'ノーマルの色',
    ownerColor: 'オーナーの色',
    moderatorColor: '管理者の色',
    memberColor: 'メンバーの色',
    showBadges: '勲章を見せる',
    showColon: 'ユーザー名の後にコロンが表示されます',
    emoticonSize: 'スタンプサイズ',
    largeEmoticonSize: '大きなスタンプサイズ',

    messages: 'コメント',
    color: '色',
    onNewLine: '新しい行に表示する',

    time: '時間',
    showTime: '時間を表示する',

    backgrounds: '背景',
    bgColor: '背景色',
    useBarsInsteadOfBg: '背景に代わります',
    showLargeEmoticonBg: '大きなスタンプの背景を表示する',
    messageBgColor: 'コメント背景色',
    ownerMessageBgColor: 'オーナーコメント背景色',
    moderatorMessageBgColor: '管理者コメント背景色',
    memberMessageBgColor: 'メンバーコメント背景色',

    scAndNewMember: 'スーパーチャット、新メンバー',
    firstLineFont: '1行目のフォント',
    firstLineFontSize: '1行目のフォントサイズ',
    firstLineLineHeight: '1行目の高さ（0はデフォルト）',
    firstLineColor: '1行目の色',
    secondLineFont: '2行目のフォント',
    secondLineFontSize: '2行目のフォントサイズ',
    secondLineLineHeight: '2行目の高さ（0はデフォルト）',
    secondLineColor: '2行目の色',
    scContentLineFont: 'スーパーチャットのコンテンツフォント',
    scContentLineFontSize: 'スーパーチャットコンテンツフォントサイズ',
    scContentLineLineHeight: 'スーパーチャットコンテンツライン高さ（0がデフォルト）',
    scContentLineColor: 'スーパーチャットコンテンツライン色',
    showNewMemberBg: '新メンバーの背景を表示する',
    showScTicker: 'スーパーチャットチカーの表示',
    showOtherThings: 'スーパーチャットチカー以外のコンテンツを表示します',

    animation: 'アニメーション',
    animateIn: '入場アニメーション',
    fadeInTime: 'フェードイン時間（ミリ秒）',
    animateOut: '古いコメントを除去する',
    animateOutWaitTime: '待ち時間（秒）',
    fadeOutTime: 'フェードアウト時間（ミリ秒）',
    slide: '滑る',
    reverseSlide: '逆の滑る',
    playAnimation: 'アニメーションを再生する',

    result: '結果',
    copy: 'コピー',
    editor: 'エディタ',
    resetConfig: 'デフォルトに戻す'
  },
  help: {
    help: 'ヘルプ',
    p1_1: '1. このウェブページからアイデンティティコード（身份码）をコピーして：',
    p1_2: '。注意：アイデンティティコードは漏洩していない限り、更新しないでください。アイデンティティコードを更新すると、古いコードは無効になります',
    p2: '2. ホームページに先ほどコピーしたアイデンティティコードを入力して、ルームのURLをこぴーする',
    p3: '3. スタイルジェネレータでお好みのコメント様子を選び、出力したCSSをコピーする',
    p4: '4. OBSでブラウザを新規作成する',
    p5: '5. プロパティでこぴーしたURLを入力し、カスタムCSSでスタイルジェネレータのCSSを入力する'
  },
  room: {
    fatalErrorOccurred: '致命的なエラーが発生しました。ページを手動で更新して再接続してください'
  },
  chat: {
    moderator: 'モデレーター',
    guardLevel1: '総督',
    guardLevel2: '提督',
    guardLevel3: '艦長',
    sendGift: '{giftName}x{num} を贈りました',
    membershipTitle: '新規メンバー',
    tickerMembership: 'メンバー'
  },
  plugins: {
    plugins: 'プラグイン',
    help: 'ヘルプ',
    helpContent: `\
<p>プラグインは、メッセージの記録、テキスト読み上げ、曲リクエストなど、blivechatにさらなる機能を追加できます。
  プラグインはサードパーティの作者によって開発される場合があり、セキュリティと品質はプラグイン作者の責任です。
  いくつかの公開されたプラグインは<a target="_blank" href="https://github.com/xfgryujk/blivechat/discussions/categories/%E6%8F%92%E4%BB%B6"
  >GitHub Discussions</a>で見つけることができます</p>
<p>プラグインのインストール方法：抽出されたプラグインディレクトリを「data/plugins」ディレクトリに配置し、blivechatを再起動します</p>
<p>注意：ほとんどのプラグインは、「サーバを介してメッセージを転送する」オプションを有効にし、メッセージを受信するために
  ルームに接続する必要があります</p>
<p><a target="_blank" href="https://www.bilibili.com/video/BV1nZ42187TX/">紹介動画</a></p>
<p><a target="_blank" href="https://github.com/xfgryujk/blivechat/wiki/%E6%8F%92%E4%BB%B6%E7%B3%BB%E7%BB%9F"
  >プラグイン開発ドキュメント</a></p>
`,
    author: '作者：',
    disabledByServer: 'プラグインの管理は、サーバーによって無効にされています',
    admin: '管理',
    connected: '接続済み',
    unconnected: '未接続',
  },
}
