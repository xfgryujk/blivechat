<template>
  <chat-renderer ref="renderer" :maxNumber="config.maxNumber" :showGiftName="config.showGiftName"></chat-renderer>
</template>

<script>
import * as i18n from '@/i18n'
import { mergeConfig, toBool, toInt } from '@/utils'
import * as trie from '@/utils/trie'
import * as pronunciation from '@/utils/pronunciation'
import * as chatConfig from '@/api/chatConfig'
import * as chat from '@/api/chat'
import ChatClientTest from '@/api/chat/ChatClientTest'
import ChatClientDirect from '@/api/chat/ChatClientDirect'
import ChatClientRelay from '@/api/chat/ChatClientRelay'
import ChatRenderer from '@/components/ChatRenderer'
import * as constants from '@/components/ChatRenderer/constants'

export default {
  name: 'Room',
  components: {
    ChatRenderer
  },
  props: {
    roomId: {
      type: Number,
      default: null
    },
    strConfig: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    return {
      config: chatConfig.deepCloneDefaultConfig(),
      chatClient: null,
      pronunciationConverter: null,
      textEmoticons: [], // 官方的文本表情
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
    blockUsersTrie() {
      let blockUsers = this.config.blockUsers.split('\n')
      let res = new trie.Trie()
      for (let user of blockUsers) {
        if (user !== '') {
          res.set(user, true)
        }
      }
      return res
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
    this.initConfig()
    this.initChatClient()
    this.initTextEmoticons()
    if (this.config.giftUsernamePronunciation !== '') {
      this.pronunciationConverter = new pronunciation.PronunciationConverter()
      this.pronunciationConverter.loadDict(this.config.giftUsernamePronunciation)
    }

    // 提示用户已加载
    this.$message({
      message: 'Loaded',
      duration: '500'
    })
  },
  beforeDestroy() {
    if (this.chatClient) {
      this.chatClient.stop()
    }
  },
  methods: {
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

      cfg.minGiftPrice = toInt(cfg.minGiftPrice, chatConfig.DEFAULT_CONFIG.minGiftPrice)
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

      cfg.relayMessagesByServer = toBool(cfg.relayMessagesByServer)
      cfg.autoTranslate = toBool(cfg.autoTranslate)
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
    initChatClient() {
      if (this.roomId === null) {
        this.chatClient = new ChatClientTest()
      } else {
        if (!this.config.relayMessagesByServer) {
          this.chatClient = new ChatClientDirect(this.roomId)
        } else {
          this.chatClient = new ChatClientRelay(this.roomId, this.config.autoTranslate)
        }
      }
      this.chatClient.onAddText = this.onAddText
      this.chatClient.onAddGift = this.onAddGift
      this.chatClient.onAddMember = this.onAddMember
      this.chatClient.onAddSuperChat = this.onAddSuperChat
      this.chatClient.onDelSuperChat = this.onDelSuperChat
      this.chatClient.onUpdateTranslation = this.onUpdateTranslation
      this.chatClient.start()
    },
    async initTextEmoticons() {
      this.textEmoticons = await chat.getTextEmoticons()
    },

    start() {
      this.chatClient.start()
    },
    stop() {
      this.chatClient.stop()
    },

    onAddText(data) {
      if (!this.config.showDanmaku || !this.filterTextMessage(data) || this.mergeSimilarText(data.content)) {
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
        richContent: this.getRichContent(data),
        privilegeType: data.privilegeType,
        repeated: 1,
        translation: data.translation
      }
      this.$refs.renderer.addMessage(message)
    },
    onAddGift(data) {
      if (!this.config.showGift) {
        return
      }
      let price = data.totalCoin / 1000
      if (this.mergeSimilarGift(data.authorName, price, data.giftName, data.num)) {
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
        giftName: data.giftName,
        num: data.num
      }
      this.$refs.renderer.addMessage(message)
    },
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
    onDelSuperChat(data) {
      this.$refs.renderer.delMessages(data.ids)
    },
    onUpdateTranslation(data) {
      if (!this.config.autoTranslate) {
        return
      }
      this.$refs.renderer.updateMessage(data.id, { translation: data.translation })
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
      return !this.blockUsersTrie.has(authorName)
    },
    mergeSimilarText(content) {
      if (!this.config.mergeSimilarDanmaku) {
        return false
      }
      return this.$refs.renderer.mergeSimilarText(content)
    },
    mergeSimilarGift(authorName, price, giftName, num) {
      if (!this.config.mergeGift) {
        return false
      }
      return this.$refs.renderer.mergeSimilarGift(authorName, price, giftName, num)
    },
    getPronunciation(text) {
      if (this.pronunciationConverter === null) {
        return ''
      }
      return this.pronunciationConverter.getPronunciation(text)
    },
    getRichContent(data) {
      let richContent = []

      // B站官方表情
      if (data.emoticon !== null) {
        richContent.push({
          type: constants.CONTENT_TYPE_IMAGE,
          text: data.content,
          url: data.emoticon
        })
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
          url: matchEmoticon.url
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
      return richContent
    }
  }
}
</script>
