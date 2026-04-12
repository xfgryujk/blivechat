<template>
  <el-card shadow="never">
    <el-form label-width="150px" size="mini">
      <el-collapse>
        <el-collapse-item>
          <template slot="title">
            <h3>{{ $t('stylegen.avatars') }}</h3>
          </template>
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.showAvatars')">
                <el-switch v-model="form.showAvatars"></el-switch>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.avatarSize')">
                <el-input v-model.number="form.avatarSize" type="number" min="0"></el-input>
              </el-form-item>
            </el-col>
          </el-row>
        </el-collapse-item>

        <el-collapse-item>
          <template slot="title">
            <h3>{{ $t('stylegen.userNames') }}</h3>
          </template>
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.showUserNames')">
                <el-switch v-model="form.showUserNames"></el-switch>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.font')">
                <font-select v-model="form.userNameFont"></font-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.fontSize')">
                <el-input v-model.number="form.userNameFontSize" type="number" min="0"></el-input>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.lineHeight')">
                <el-input v-model.number="form.userNameLineHeight" type="number" min="0"></el-input>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.normalColor')">
                <el-color-picker v-model="form.userNameColor"></el-color-picker>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.memberColor')">
                <el-color-picker v-model="form.memberUserNameColor"></el-color-picker>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.moderatorColor')">
                <el-color-picker v-model="form.moderatorUserNameColor"></el-color-picker>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.ownerColor')">
                <el-color-picker v-model="form.ownerUserNameColor"></el-color-picker>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.showBadges')">
                <el-switch v-model="form.showBadges"></el-switch>
              </el-form-item>
            </el-col>
          </el-row>
        </el-collapse-item>

        <el-collapse-item>
          <template slot="title">
            <h3>{{ $t('stylegen.messages') }}</h3>
          </template>
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.font')">
                <font-select v-model="form.messageFont"></font-select>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.color')">
                <el-color-picker v-model="form.messageColor"></el-color-picker>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.fontSize')">
                <el-input v-model.number="form.messageFontSize" type="number" min="0"></el-input>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.lineHeight')">
                <el-input v-model.number="form.messageLineHeight" type="number" min="0"></el-input>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.emoticonSize')">
                <el-input v-model.number="form.emoticonSize" type="number" min="0"></el-input>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.largeEmoticonSize')">
                <el-input v-model.number="form.largeEmoticonSize" type="number" min="0"></el-input>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.messageReverseScroll')">
                <el-switch v-model="form.messageReverseScroll"></el-switch>
              </el-form-item>
            </el-col>
          </el-row>
        </el-collapse-item>

        <el-collapse-item>
          <template slot="title">
            <h3>{{ $t('stylegen.time') }}</h3>
          </template>
          <el-form-item :label="$t('stylegen.showTime')">
            <el-switch v-model="form.showTime"></el-switch>
          </el-form-item>
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.font')">
                <font-select v-model="form.timeFont"></font-select>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.color')">
                <el-color-picker v-model="form.timeColor"></el-color-picker>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.fontSize')">
                <el-input v-model.number="form.timeFontSize" type="number" min="0"></el-input>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.lineHeight')">
                <el-input v-model.number="form.timeLineHeight" type="number" min="0"></el-input>
              </el-form-item>
            </el-col>
          </el-row>
        </el-collapse-item>

        <el-collapse-item>
          <template slot="title">
            <h3>{{ $t('stylegen.backgrounds') }}</h3>
          </template>
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.bgColor')">
                <el-color-picker v-model="form.bgColor" show-alpha></el-color-picker>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.showLargeEmoticonBg')">
                <el-switch v-model="form.showLargeEmoticonBg"></el-switch>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.messageBgColor')">
                <el-color-picker v-model="form.messageBgColor"></el-color-picker>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.memberMessageBgColor')">
                <el-color-picker v-model="form.memberMessageBgColor"></el-color-picker>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.moderatorMessageBgColor')">
                <el-color-picker v-model="form.moderatorMessageBgColor"></el-color-picker>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.ownerMessageBgColor')">
                <el-color-picker v-model="form.ownerMessageBgColor"></el-color-picker>
              </el-form-item>
            </el-col>
          </el-row>
        </el-collapse-item>

        <el-collapse-item>
          <template slot="title">
            <h3>{{ $t('stylegen.scAndNewMember') }}</h3>
          </template>
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.firstLineFont')">
                <font-select v-model="form.firstLineFont"></font-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.firstLineFontSize')">
                <el-input v-model.number="form.firstLineFontSize" type="number" min="0"></el-input>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.firstLineLineHeight')">
                <el-input v-model.number="form.firstLineLineHeight" type="number" min="0"></el-input>
              </el-form-item>
            </el-col>
          </el-row>
          <el-divider></el-divider>

          <el-row :gutter="20">
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.secondLineFont')">
                <font-select v-model="form.secondLineFont"></font-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.secondLineFontSize')">
                <el-input v-model.number="form.secondLineFontSize" type="number" min="0"></el-input>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.secondLineLineHeight')">
                <el-input v-model.number="form.secondLineLineHeight" type="number" min="0"></el-input>
              </el-form-item>
            </el-col>
          </el-row>
          <el-divider></el-divider>

          <el-row :gutter="20">
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.scContentLineFont')">
                <font-select v-model="form.scContentFont"></font-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.scContentLineFontSize')">
                <el-input v-model.number="form.scContentFontSize" type="number" min="0"></el-input>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.scContentLineLineHeight')">
                <el-input v-model.number="form.scContentLineHeight" type="number" min="0"></el-input>
              </el-form-item>
            </el-col>
          </el-row>
          <el-divider></el-divider>

          <el-row :gutter="20">
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.showScTicker')">
                <el-switch v-model="form.showScTicker"></el-switch>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.showOtherThings')">
                <el-switch v-model="form.showOtherThings"></el-switch>
              </el-form-item>
            </el-col>
          </el-row>
        </el-collapse-item>

        <el-collapse-item>
          <template slot="title">
            <h3>{{ $t('stylegen.animation') }}</h3>
          </template>
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.animateIn')">
                <el-switch v-model="form.animateIn"></el-switch>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.fadeInTime')">
                <el-input v-model.number="form.fadeInTime" type="number" min="0"></el-input>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.animateOut')">
                <el-switch v-model="form.animateOut"></el-switch>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.fadeOutTime')">
                <el-input v-model.number="form.fadeOutTime" type="number" min="0"></el-input>
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item :label="$t('stylegen.animateOutWaitTime')">
            <el-input v-model.number="form.animateOutWaitTime" type="number" min="0"></el-input>
          </el-form-item>
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.slide')">
                <el-switch v-model="form.slide"></el-switch>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.reverseSlide')">
                <el-switch v-model="form.reverseSlide"></el-switch>
              </el-form-item>
            </el-col>
          </el-row>
        </el-collapse-item>
      </el-collapse>
    </el-form>
  </el-card>
</template>

<script>
import _ from 'lodash'

import FontSelect from './FontSelect'
import * as common from './common'
import { mergeConfig } from '@/utils'

export const DEFAULT_CONFIG = {
  showAvatars: true,
  avatarSize: 40,

  showUserNames: true,
  userNameFont: 'Noto Sans SC',
  userNameFontSize: 20,
  userNameLineHeight: 0,
  userNameColor: '#cccccc',
  ownerUserNameColor: '#ffd600',
  moderatorUserNameColor: '#5e84f1',
  memberUserNameColor: '#0f9d58',
  showBadges: true,

  messageFont: 'Noto Sans SC',
  messageFontSize: 18,
  messageLineHeight: 0,
  messageColor: '#000000',
  emoticonSize: 18,
  largeEmoticonSize: 36,
  messageReverseScroll: false,

  showTime: false,
  timeFont: 'Noto Sans SC',
  timeFontSize: 16,
  timeLineHeight: 0,
  timeColor: '#999999',

  bgColor: 'rgba(0, 0, 0, 0)',
  messageBgColor: '#ffffff',
  ownerMessageBgColor: 'rgba(231, 199, 30, 1)',
  moderatorMessageBgColor: 'rgba(41, 95, 251, 1)',
  memberMessageBgColor: 'rgba(43, 234, 43, 1)',
  showLargeEmoticonBg: true,

  firstLineFont: 'Noto Sans SC',
  firstLineFontSize: 20,
  firstLineLineHeight: 0,
  secondLineFont: 'Noto Sans SC',
  secondLineFontSize: 18,
  secondLineLineHeight: 0,
  scContentFont: 'Noto Sans SC',
  scContentFontSize: 18,
  scContentLineHeight: 0,
  showScTicker: false,
  showOtherThings: true,

  animateIn: true,
  fadeInTime: 200, // ms
  animateOut: false,
  animateOutWaitTime: 30, // s
  fadeOutTime: 200, // ms
  slide: true,
  reverseSlide: false
}

export default {
  name: 'LineLike',
  components: {
    FontSelect
  },
  props: {
    value: String
  },
  data() {
    return {
      form: this.loadConfig()
    }
  },
  computed: {
    result() {
      let styles = [
        this.importStyle,
        this.variableStyle,
        common.COMMON_STYLE,
        this.paddingStyle,
        this.avatarStyle,
        this.userNameStyle,
        this.messageStyle,
        this.timeStyle,
        this.backgroundStyle,
        this.scAndNewMemberStyle,
        this.animationStyle,
      ]
      let result = styles.filter(style => style).join('\n\n')
      return `${result}\n`
    },
    importStyle() {
      let allFonts = []
      for (let name of ['userNameFont', 'messageFont', 'timeFont', 'firstLineFont', 'secondLineFont', 'scContentFont']) {
        allFonts.push(this.form[name])
      }
      return common.getImportStyle(allFonts)
    },
    variableStyle() {
      return `yt-live-chat-renderer {
  ${common.getVariableStyle(this.form)}

  /* 背景色 Background colors
    普通、舰长、房管、主播 */
  --text-msg-bg-color: ${this.form.messageBgColor ?? '#ffffff'};
  --text-msg-bg-color-member: ${this.form.memberMessageBgColor ?? '#ffffff'};
  --text-msg-bg-color-moderator: ${this.form.moderatorMessageBgColor ?? '#ffffff'};
  --text-msg-bg-color-owner: ${this.form.ownerMessageBgColor ?? '#ffffff'};

  /* 付费、上舰消息 Super Chats / Membership messages */
  --paid-msg-line-1-size: calc(${this.form.firstLineFontSize} * var(--font-base-size));
  --paid-msg-line-2-size: calc(${this.form.secondLineFontSize} * var(--font-base-size));
  --paid-msg-content-size: calc(${this.form.scContentFontSize} * var(--font-base-size));
  --membership-msg-bg-color: var(--username-color-member);
}`
    },
    paddingStyle() {
      return `/* 减少两侧间距 Reduce side padding */
yt-live-chat-text-message-renderer {
  padding-inline: 4px;
}`
    },
    avatarStyle() {
      return common.getAvatarStyle(this.form)
    },
    userNameStyle() {
      return `/* 用户名 Channel names */
yt-live-chat-text-message-renderer yt-live-chat-author-chip {
  margin-bottom: 5px;
}

yt-live-chat-text-message-renderer #author-name {
  ${this.form.showUserNames ? '' : 'display: none;'}
  color: var(--username-color);
  font-family: ${common.fontsStrToCss(this.form.userNameFont)};
  font-size: var(--username-size);
  line-height: calc(${this.form.userNameLineHeight || (this.form.userNameFontSize + 2)} *  var(--font-base-size));
}

${common.getUserNameStyle(this.form)}`
    },
    messageStyle() {
      return `/* 文本消息 Text messages */
yt-live-chat-text-message-renderer :is(#message, #message *) {
  color: var(--text-content-color);
  font-family: ${common.fontsStrToCss(this.form.messageFont)};
  font-size: var(--text-content-size);
  line-height: calc(${this.form.messageLineHeight || (this.form.messageFontSize + 2)} *  var(--font-base-size));
}

/* 气泡背景 Bubble background */
yt-live-chat-text-message-renderer #message {
  display: block;
  position: relative;
  width: fit-content;
  overflow: visible;
  padding: 15px;
  border-radius: 24px;
}

/* 气泡旁边的三角形箭头 The triangle beside the bubble */
yt-live-chat-text-message-renderer #message::before {
  content: "";
  display: inline-block;
  position: absolute;
  top: -3px;
  left: -10px;
  border: 8px solid transparent;
  border-right: 18px solid;
  transform: rotate(35deg);
}

${this.form.showLargeEmoticonBg ? '' : `/* 适配隐藏大表情背景 For Hiding background of large emotes */
yt-live-chat-text-message-renderer #message:has(.emoji.blc-large-emoji)::before {
  content: none;
}

yt-live-chat-text-message-renderer #message:has(.emoji.blc-large-emoji) {
  padding: 0;
}`}

${common.EMOTICON_STYLE}

${common.getReverseScrollStyle(this.form)}`
    },
    timeStyle() {
      return common.getTimeStyle(this.form)
    },
    backgroundStyle() {
      return `/* 背景色 Background colors */
body {
  background-color: ${this.form.bgColor ?? 'transparent'};
}

${this.getBgStyleForAuthorType('')}

${this.getBgStyleForAuthorType('owner')}

${this.getBgStyleForAuthorType('moderator')}

${this.getBgStyleForAuthorType('member')}

${this.form.showLargeEmoticonBg ? '' : `/* 隐藏大表情背景 Hide background of large emotes */
yt-live-chat-text-message-renderer #message:has(.emoji.blc-large-emoji) {
  background-color: transparent;
}`}`
    },
    scAndNewMemberStyle() {
      return `/* 付费、上舰消息 Super Chats / Membership messages */
yt-live-chat-paid-message-renderer {
  margin: 4px 0;
}

${this.scAndNewMemberFontStyle}

yt-live-chat-membership-item-renderer :is(#card, #header) {
  background-color: var(--membership-msg-bg-color);
  margin: 4px 0;
}

${this.scTickerStyle}

${this.form.showOtherThings ? '' : `yt-live-chat-item-list-renderer {
  display: none;
}`}`
    },
    scAndNewMemberFontStyle() {
      return `yt-live-chat-paid-message-renderer :is(#author-name, #author-name *),
yt-live-chat-membership-item-renderer :is(#header-content-inner-column, #header-content-inner-column *) {
  font-family: ${common.fontsStrToCss(this.form.firstLineFont)};
  font-size: var(--paid-msg-line-1-size);
  line-height: calc(${this.form.firstLineLineHeight || (this.form.firstLineFontSize + 2)} *  var(--font-base-size));
}

yt-live-chat-paid-message-renderer :is(#purchase-amount, #purchase-amount *),
yt-live-chat-membership-item-renderer :is(#header-subtext, #header-subtext *) {
  font-family: ${common.fontsStrToCss(this.form.secondLineFont)};
  font-size: var(--paid-msg-line-2-size);
  line-height: calc(${this.form.secondLineLineHeight || (this.form.secondLineFontSize + 2)} *  var(--font-base-size));
}

yt-live-chat-paid-message-renderer :is(#content, #content *) {
  font-family: ${common.fontsStrToCss(this.form.scContentFont)};
  font-size: var(--paid-msg-content-size);
  line-height: calc(${this.form.scContentLineHeight || (this.form.scContentFontSize + 2)} *  var(--font-base-size));
}`
    },
    scTickerStyle() {
      if (!this.form.showScTicker) {
        return `yt-live-chat-ticker-renderer {
  display: none;
}`
      } else {
        return `/* SC固定栏 Super Chat ticker */
yt-live-chat-ticker-paid-message-item-renderer,
yt-live-chat-ticker-paid-message-item-renderer * {
  font-family: ${common.fontsStrToCss(this.form.secondLineFont)};
  font-size: var(--paid-msg-line-2-size);
  line-height: calc(${this.form.secondLineLineHeight || (this.form.secondLineFontSize + 2)} *  var(--font-base-size));
}`
      }
    },
    animationStyle() {
      return common.getAnimationStyle(this.form)
    }
  },
  watch: {
    result(val) {
      this.$emit('input', val)
      this.saveConfig()
    }
  },
  mounted() {
    this.$emit('input', this.result)
  },
  methods: {
    saveConfig: _.debounce(function() {
      let config = mergeConfig(this.form, DEFAULT_CONFIG)
      window.localStorage.stylegenLineLikeConfig = JSON.stringify(config)
    }, 500),
    loadConfig() {
      try {
        return mergeConfig(JSON.parse(window.localStorage.stylegenLineLikeConfig), DEFAULT_CONFIG)
      } catch {
        return { ...DEFAULT_CONFIG }
      }
    },
    resetConfig() {
      this.form = { ...DEFAULT_CONFIG }
    },

    getBgStyleForAuthorType(authorType) {
      let typeSelector = authorType ? `[author-type="${authorType}"]` : ''
      let varName = authorType ? `--text-msg-bg-color-${authorType}` : '--text-msg-bg-color'
      return `yt-live-chat-text-message-renderer${typeSelector} #message {
  background-color: var(${varName});
}

yt-live-chat-text-message-renderer${typeSelector} #message::before {
  border-right-color: var(${varName});
}`
    }
  }
}
</script>
