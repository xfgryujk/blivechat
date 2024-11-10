<template>
  <chat-renderer ref="renderer" :maxNumber="config.maxNumber" :showGiftName="config.showGiftName"></chat-renderer>
</template>

<script>
import * as i18n from '@/i18n'
import { mergeConfig, toBool, toInt, toFloat } from '@/utils'
import * as trie from '@/utils/trie'
import * as pronunciation from '@/utils/pronunciation'
import * as chatConfig from '@/api/chatConfig'
import * as chat from '@/api/chat'
import * as chatModels from '@/api/chat/models'
import ChatRenderer from '@/components/ChatRenderer'
import * as constants from '@/components/ChatRenderer/constants'

export default {
  name: 'Room',
  components: {
    ChatRenderer
  },
  props: {
    roomKeyType: {
      type: Number,
      default: 1
    },
    roomKeyValue: {
      type: [Number, String],
      default: null
    },
    strConfig: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    let customStyleElement = document.createElement('style')
    document.head.appendChild(customStyleElement)
    return {
      config: chatConfig.deepCloneDefaultConfig(),

      chatClient: null,
      textEmoticons: [], // 官方的文本表情（后端配置的）
      pronunciationConverter: null,

      customStyleElement, // 仅用于样式生成器中预览样式
      presetCssLinkElement: null,
    }
  },
  computed: {
    blockKeywordsTrie() {
      let blockKeywords = this.config.blockKeywords.split('\n')
      let res = new trie.Trie()
      for (let keyword of blockKeywords) {
        if (keyword !== '') {
          res.set(keyword, true)
        }
      }
      return res
    },
    blockUsersSet() {
      let blockUsers = this.config.blockUsers.split('\n')
      blockUsers = blockUsers.filter(user => user !== '')
      return new Set(blockUsers)
    },
    emoticonsTrie() {
      let res = new trie.Trie()
      for (let emoticons of [this.config.emoticons, this.textEmoticons]) {
        for (let emoticon of emoticons) {
          if (emoticon.keyword !== '' && emoticon.url !== '') {
            res.set(emoticon.keyword, emoticon)
          }
        }
      }
      return res
    }
  },
  mounted() {
    if (document.visibilityState === 'visible') {
      if (this.roomKeyValue === null) {
        this.init()
      } else {
        // 正式房间要随机延迟加载，防止同时请求导致雪崩
        window.setTimeout(this.init, Math.random() * 3000)
      }
    } else {
      // 当前窗口不可见，延迟到可见时加载，防止OBS中一次并发太多请求（OBS中浏览器不可见时也会加载网页，除非显式设置）
      document.addEventListener('visibilitychange', this.onVisibilityChange)
    }

    window.addEventListener('message', this.onWindowMessage)
  },
  beforeDestroy() {
    window.removeEventListener('message', this.onWindowMessage)

    document.removeEventListener('visibilitychange', this.onVisibilityChange)
    if (this.chatClient) {
      this.chatClient.stop()
    }

    document.head.removeChild(this.customStyleElement)
    if (this.presetCssLinkElement) {
      document.head.removeChild(this.presetCssLinkElement)
    }
  },
  methods: {
    onVisibilityChange() {
      if (document.visibilityState !== 'visible') {
        return
      }
      document.removeEventListener('visibilitychange', this.onVisibilityChange)
      this.init()
    },
    async init() {
      this.initConfig()

      let initChatClientPromise = this.initChatClient()
      this.initTextEmoticons()
      if (this.config.giftUsernamePronunciation !== '') {
        this.pronunciationConverter = new pronunciation.PronunciationConverter()
        this.pronunciationConverter.loadDict(this.config.giftUsernamePronunciation)
      }
      if (this.config.importPresetCss) {
        this.presetCssLinkElement = document.createElement('link')
        this.presetCssLinkElement.rel = 'stylesheet'
        this.presetCssLinkElement.href = '/custom_public/preset.css'
        document.head.appendChild(this.presetCssLinkElement)
      }

      try {
        // 其他初始化就不用等了，就算失败了也不会有很大影响
        await initChatClientPromise
      } catch (e) {
        this.$message.error({
          message: `Failed to load: ${e}`,
          duration: 10 * 1000
        })
        throw e
      }

      // 提示用户已加载
      this.$message({
        message: 'Loaded',
        duration: 500
      })

      this.sendMessageToStylegen('stylegenExampleRoomLoad')
    },
    initConfig() {
      let locale = this.strConfig.lang
      if (locale) {
        i18n.setLocale(locale)
      }

      let cfg = {}
      // 留空的使用默认值
      for (let i in this.strConfig) {
        if (this.strConfig[i] !== '') {
          cfg[i] = this.strConfig[i]
        }
      }
      cfg = mergeConfig(cfg, chatConfig.deepCloneDefaultConfig())

      cfg.minGiftPrice = toFloat(cfg.minGiftPrice, chatConfig.DEFAULT_CONFIG.minGiftPrice)
      cfg.showDanmaku = toBool(cfg.showDanmaku)
      cfg.showGift = toBool(cfg.showGift)
      cfg.showGiftName = toBool(cfg.showGiftName)
      cfg.mergeSimilarDanmaku = toBool(cfg.mergeSimilarDanmaku)
      cfg.mergeGift = toBool(cfg.mergeGift)
      cfg.maxNumber = toInt(cfg.maxNumber, chatConfig.DEFAULT_CONFIG.maxNumber)

      cfg.blockGiftDanmaku = toBool(cfg.blockGiftDanmaku)
      cfg.blockLevel = toInt(cfg.blockLevel, chatConfig.DEFAULT_CONFIG.blockLevel)
      cfg.blockNewbie = toBool(cfg.blockNewbie)
      cfg.blockNotMobileVerified = toBool(cfg.blockNotMobileVerified)
      cfg.blockMedalLevel = toInt(cfg.blockMedalLevel, chatConfig.DEFAULT_CONFIG.blockMedalLevel)

      cfg.showDebugMessages = toBool(cfg.showDebugMessages)
      cfg.relayMessagesByServer = toBool(cfg.relayMessagesByServer)
      cfg.autoTranslate = toBool(cfg.autoTranslate)
      cfg.importPresetCss = toBool(cfg.importPresetCss)

      cfg.emoticons = this.toObjIfJson(cfg.emoticons)

      chatConfig.sanitizeConfig(cfg)
      this.config = cfg
    },
    toObjIfJson(str) {
      if (typeof str !== 'string') {
        return str
      }
      try {
        return JSON.parse(str)
      } catch {
        return {}
      }
    },
    async initChatClient() {
      if (this.roomKeyValue === null) {
        let ChatClientTest = (await import('@/api/chat/ChatClientTest')).default
        this.chatClient = new ChatClientTest()
      } else if (this.config.relayMessagesByServer) {
        let roomKey = {
          type: this.roomKeyType,
          value: this.roomKeyValue
        }
        let ChatClientRelay = (await import('@/api/chat/ChatClientRelay')).default
        this.chatClient = new ChatClientRelay(roomKey, this.config.autoTranslate)
      } else {
        if (this.roomKeyType === 1) {
          let ChatClientDirectWeb = (await import('@/api/chat/ChatClientDirectWeb')).default
          this.chatClient = new ChatClientDirectWeb(this.roomKeyValue)
        } else {
          let ChatClientDirectOpenLive = (await import('@/api/chat/ChatClientDirectOpenLive')).default
          this.chatClient = new ChatClientDirectOpenLive(this.roomKeyValue)
        }
      }

      this.chatClient.msgHandler = this
      this.chatClient.start()
    },
    async initTextEmoticons() {
      this.textEmoticons = await chat.getTextEmoticons()
    },

    sendMessageToStylegen(type, data = null) {
      if (window.parent === window) {
        return
      }
      let msg = { type, data }
      window.parent.postMessage(msg, window.location.origin)
    },
    // 处理样式生成器发送的消息
    onWindowMessage(event) {
      if (event.source !== window.parent) {
        return
      }
      if (event.origin !== window.location.origin) {
        console.warn(`消息origin错误，${event.origin} != ${window.location.origin}`)
        return
      }

      let { type, data } = event.data
      switch (type) {
      case 'roomSetCustomStyle':
        this.customStyleElement.innerText = data.css
        break
      case 'roomStartClient':
        if (this.chatClient) {
          this.chatClient.start()
        }
        break
      case 'roomStopClient':
        if (this.chatClient) {
          this.chatClient.stop()
        }
        break
      }
    },

    /** @param {chatModels.AddTextMsg} data */
    async onAddText(data) {
      if (!this.config.showDanmaku || !this.filterTextMessage(data)) {
        return
      }
      let richContent = await this.getRichContent(data)
      // 合并要放在异步调用后面，因为异步调用后可能有新的消息，会漏合并
      if (this.mergeSimilarText(data.content)) {
        return
      }
      let message = {
        id: data.id,
        type: constants.MESSAGE_TYPE_TEXT,
        avatarUrl: data.avatarUrl,
        time: new Date(data.timestamp * 1000),
        authorName: data.authorName,
        authorType: data.authorType,
        content: data.content,
        richContent: richContent,
        privilegeType: data.privilegeType,
        repeated: 1,
        translation: data.translation
      }
      this.$refs.renderer.addMessage(message)
    },
    /** @param {chatModels.AddGiftMsg} data */
    onAddGift(data) {
      if (!this.config.showGift) {
        return
      }
      let price = data.totalCoin / 1000
      if (this.mergeSimilarGift(data.authorName, price, data.totalFreeCoin, data.giftName, data.num)) {
        return
      }
      if (price < this.config.minGiftPrice) { // 丢人
        return
      }
      let message = {
        id: data.id,
        type: constants.MESSAGE_TYPE_GIFT,
        avatarUrl: data.avatarUrl,
        time: new Date(data.timestamp * 1000),
        authorName: data.authorName,
        authorNamePronunciation: this.getPronunciation(data.authorName),
        price: price,
        // freePrice: data.totalFreeCoin, // 暂时没用到
        giftName: data.giftName,
        num: data.num
      }
      this.$refs.renderer.addMessage(message)
    },
    /** @param {chatModels.AddMemberMsg} data */
    onAddMember(data) {
      if (!this.config.showGift || !this.filterNewMemberMessage(data)) {
        return
      }
      let message = {
        id: data.id,
        type: constants.MESSAGE_TYPE_MEMBER,
        avatarUrl: data.avatarUrl,
        time: new Date(data.timestamp * 1000),
        authorName: data.authorName,
        authorNamePronunciation: this.getPronunciation(data.authorName),
        privilegeType: data.privilegeType,
        title: this.$t('chat.membershipTitle')
      }
      this.$refs.renderer.addMessage(message)
    },
    /** @param {chatModels.AddSuperChatMsg} data */
    onAddSuperChat(data) {
      if (!this.config.showGift || !this.filterSuperChatMessage(data)) {
        return
      }
      if (data.price < this.config.minGiftPrice) { // 丢人
        return
      }
      let message = {
        id: data.id,
        type: constants.MESSAGE_TYPE_SUPER_CHAT,
        avatarUrl: data.avatarUrl,
        authorName: data.authorName,
        authorNamePronunciation: this.getPronunciation(data.authorName),
        price: data.price,
        time: new Date(data.timestamp * 1000),
        content: data.content.trim(),
        translation: data.translation
      }
      this.$refs.renderer.addMessage(message)
    },
    /** @param {chatModels.DelSuperChatMsg} data */
    onDelSuperChat(data) {
      this.$refs.renderer.delMessages(data.ids)
    },
    /** @param {chatModels.UpdateTranslationMsg} data */
    onUpdateTranslation(data) {
      if (!this.config.autoTranslate) {
        return
      }
      this.$refs.renderer.updateMessage(data.id, { translation: data.translation })
    },
    /** @param {chatModels.ChatClientFatalError} error */
    onFatalError(error) {
      this.$message.error({
        message: error.toString(),
        duration: 30 * 1000
      })
      this.onAddText(new chatModels.AddTextMsg({
        authorName: 'blivechat',
        authorType: constants.AUTHOR_TYPE_ADMIN,
        content: this.$t('room.fatalErrorOccurred'),
        authorLevel: 60,
      }))

      if (error.type === chatModels.FATAL_ERROR_TYPE_AUTH_CODE_ERROR) {
        // Read The Fucking Manual
        this.$router.push({ name: 'help' })
      }
    },
    /** @param {chatModels.DebugMsg} data */
    onDebugMsg(data) {
      if (!this.config.showDebugMessages) {
        return
      }
      this.onAddText(new chatModels.AddTextMsg({
        authorName: 'blivechat',
        authorType: constants.AUTHOR_TYPE_ADMIN,
        content: data.content,
        authorLevel: 60,
      }))
    },

    filterTextMessage(data) {
      if (this.config.blockGiftDanmaku && data.isGiftDanmaku) {
        return false
      } else if (this.config.blockLevel > 0 && data.authorLevel < this.config.blockLevel) {
        return false
      } else if (this.config.blockNewbie && data.isNewbie) {
        return false
      } else if (this.config.blockNotMobileVerified && !data.isMobileVerified) {
        return false
      } else if (this.config.blockMedalLevel > 0 && data.medalLevel < this.config.blockMedalLevel) {
        return false
      }
      return this.filterByContent(data.content) && this.filterByAuthorName(data.authorName)
    },
    filterSuperChatMessage(data) {
      return this.filterByContent(data.content) && this.filterByAuthorName(data.authorName)
    },
    filterNewMemberMessage(data) {
      return this.filterByAuthorName(data.authorName)
    },
    filterByContent(content) {
      let blockKeywordsTrie = this.blockKeywordsTrie
      for (let i = 0; i < content.length; i++) {
        let remainContent = content.substring(i)
        if (blockKeywordsTrie.lazyMatch(remainContent) !== null) {
          return false
        }
      }
      return true
    },
    filterByAuthorName(authorName) {
      return !this.blockUsersSet.has(authorName)
    },
    mergeSimilarText(content) {
      if (!this.config.mergeSimilarDanmaku) {
        return false
      }
      return this.$refs.renderer.mergeSimilarText(content)
    },
    mergeSimilarGift(authorName, price, freePrice, giftName, num) {
      if (!this.config.mergeGift) {
        return false
      }
      return this.$refs.renderer.mergeSimilarGift(authorName, price, freePrice, giftName, num)
    },
    getPronunciation(text) {
      if (this.pronunciationConverter === null) {
        return ''
      }
      return this.pronunciationConverter.getPronunciation(text)
    },
    async getRichContent(data) {
      let richContent = []

      // 官方的非文本表情
      if (data.emoticon !== null) {
        richContent.push({
          type: constants.CONTENT_TYPE_IMAGE,
          text: data.content,
          url: data.emoticon,
          width: 0,
          height: 0
        })
        await this.fillImageContentSizes(richContent)
        return richContent
      }

      // 没有文本表情，只能是纯文本
      if (this.config.emoticons.length === 0 && this.textEmoticons.length === 0) {
        richContent.push({
          type: constants.CONTENT_TYPE_TEXT,
          text: data.content
        })
        return richContent
      }

      // 可能含有文本表情，需要解析
      let emoticonsTrie = this.emoticonsTrie
      let startPos = 0
      let pos = 0
      while (pos < data.content.length) {
        let remainContent = data.content.substring(pos)
        let matchEmoticon = emoticonsTrie.lazyMatch(remainContent)
        if (matchEmoticon === null) {
          pos++
          continue
        }

        // 加入之前的文本
        if (pos !== startPos) {
          richContent.push({
            type: constants.CONTENT_TYPE_TEXT,
            text: data.content.slice(startPos, pos)
          })
        }

        // 加入表情
        richContent.push({
          type: constants.CONTENT_TYPE_IMAGE,
          text: matchEmoticon.keyword,
          url: matchEmoticon.url,
          width: 0,
          height: 0
        })
        pos += matchEmoticon.keyword.length
        startPos = pos
      }
      // 加入尾部的文本
      if (pos !== startPos) {
        richContent.push({
          type: constants.CONTENT_TYPE_TEXT,
          text: data.content.slice(startPos, pos)
        })
      }

      await this.fillImageContentSizes(richContent)
      return richContent
    },
    async fillImageContentSizes(richContent) {
      let urlSizeMap = new Map()
      for (let content of richContent) {
        if (content.type === constants.CONTENT_TYPE_IMAGE) {
          urlSizeMap.set(content.url, { width: 0, height: 0 })
        }
      }
      if (urlSizeMap.size === 0) {
        return
      }

      let promises = []
      for (let url of urlSizeMap.keys()) {
        let urlInClosure = url
        promises.push(new Promise(
          resolve => {
            let img = document.createElement('img')
            img.onload = () => {
              let size = urlSizeMap.get(urlInClosure)
              size.width = img.naturalWidth
              size.height = img.naturalHeight
              resolve()
            }
            // 获取失败了默认为0
            img.onerror = resolve
            // 超时保底
            window.setTimeout(resolve, 5000)
            img.src = urlInClosure
          }
        ))
      }
      await Promise.all(promises)

      for (let content of richContent) {
        if (content.type === constants.CONTENT_TYPE_IMAGE) {
          let size = urlSizeMap.get(content.url)
          content.width = size.width
          content.height = size.height
        }
      }
    }
  }
}
</script>
