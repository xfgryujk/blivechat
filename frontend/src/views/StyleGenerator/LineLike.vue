<template>
  <el-card shadow="never">
    <el-form label-width="150px" size="mini">
      <el-collapse>
        <el-collapse-item>
          <template slot="title">
            <h3>{{ $t('stylegen.global') }}</h3>
          </template>
          <p>
            <el-alert :title="$t('stylegen.scalingNotice')" type="info" show-icon :closable="false"></el-alert>
          </p>
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.globalScale')">
                <el-input v-model.number="form.globalScale" type="number" min="0" step="0.1"></el-input>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.fontScale')">
                <el-input v-model.number="form.fontScale" type="number" min="0" step="0.1"></el-input>
              </el-form-item>
            </el-col>
          </el-row>
        </el-collapse-item>

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
              <el-form-item :label="$t('stylegen.fontWeight')">
                <font-weight-select v-model="form.userNameWeight"></font-weight-select>
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
              <el-form-item :label="$t('stylegen.fontWeight')">
                <font-weight-select v-model="form.messageWeight"></font-weight-select>
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
              <el-form-item :label="$t('stylegen.fontWeight')">
                <font-weight-select v-model="form.timeWeight"></font-weight-select>
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
              <el-form-item :label="$t('stylegen.firstLineWeight')">
                <font-weight-select v-model="form.firstLineWeight"></font-weight-select>
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
              <el-form-item :label="$t('stylegen.secondLineWeight')">
                <font-weight-select v-model="form.secondLineWeight"></font-weight-select>
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
              <el-form-item :label="$t('stylegen.scContentWeight')">
                <font-weight-select v-model="form.scContentWeight"></font-weight-select>
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
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.animateOutWaitTime')">
                <el-input v-model.number="form.animateOutWaitTime" type="number" min="0"></el-input>
              </el-form-item>
            </el-col>
          </el-row>
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
import FontWeightSelect from './FontWeightSelect'
import * as common from './common'
import { mergeConfig } from '@/utils'

export const DEFAULT_CONFIG = {
  globalScale: 1,
  fontScale: 1,

  showAvatars: true,
  avatarSize: 40,

  showUserNames: true,
  userNameFont: 'Noto Sans SC',
  userNameFontSize: 18,
  userNameWeight: 700,
  userNameColor: '#cccccc',
  ownerUserNameColor: '#ffd600',
  moderatorUserNameColor: '#5e84f1',
  memberUserNameColor: '#0f9d58',
  showBadges: true,

  messageFont: 'Noto Sans SC',
  messageFontSize: 20,
  messageWeight: 700,
  messageColor: '#000000',
  emoticonSize: 24,
  largeEmoticonSize: 60,
  messageReverseScroll: false,

  showTime: false,
  timeFont: 'Noto Sans SC',
  timeFontSize: 18,
  timeWeight: 400,
  timeColor: '#999999',

  bgColor: 'rgba(0, 0, 0, 0)',
  messageBgColor: '#ffffff',
  ownerMessageBgColor: '#F5D401',
  moderatorMessageBgColor: '#3CA0FB',
  memberMessageBgColor: '#3ACD2E',
  showLargeEmoticonBg: false,

  firstLineFont: 'Noto Sans SC',
  firstLineFontSize: 22,
  firstLineWeight: 700,
  secondLineFont: 'Noto Sans SC',
  secondLineFontSize: 20,
  secondLineWeight: 700,
  scContentFont: 'Noto Sans SC',
  scContentFontSize: 20,
  scContentWeight: 700,
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
    FontSelect, FontWeightSelect
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
        this.timeStyle,
        this.userNameStyle,
        this.messageStyle,
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
  --paid-msg-line-1-weight: ${this.form.firstLineWeight};
  --paid-msg-line-2-size: calc(${this.form.secondLineFontSize} * var(--font-base-size));
  --paid-msg-line-2-weight: ${this.form.secondLineWeight};
  --paid-msg-content-size: calc(${this.form.scContentFontSize} * var(--font-base-size));
  --paid-msg-content-weight: ${this.form.scContentWeight};
  --membership-msg-bg-color: var(--username-color-member);
}`
    },
    paddingStyle() {
      return `/* 减少两侧边距 Reduce side padding */
yt-live-chat-text-message-renderer {
  padding-inline: 4px;
}`
    },
    avatarStyle() {
      return common.getAvatarStyle(this.form)
    },
    userNameStyle() {
      return `${common.getUserNameStyle(this.form)}

yt-live-chat-text-message-renderer yt-live-chat-author-chip {
  margin-bottom: 5px;
}`
    },
    messageStyle() {
      return common.getMessageStyle(this.form)
    },
    timeStyle() {
      return common.getTimeStyle(this.form)
    },
    backgroundStyle() {
      return `/* 气泡背景 Bubble background */
yt-live-chat-text-message-renderer #message {
  display: block;
  position: relative;
  width: fit-content;
  overflow: visible;
  padding: calc(12 * var(--base-size)) calc(20 * var(--base-size));
  border-radius: calc(24 * var(--base-size));
}

/* 气泡旁边的三角形箭头 The triangle beside the bubble */
yt-live-chat-text-message-renderer #message::before {
  content: "";
  display: block;
  position: absolute;
  top: 0;
  left: 0;
  border: calc(8 * var(--base-size)) solid transparent;
  border-left-width: calc(18 * var(--base-size));
  border-right: calc(18 * var(--base-size)) solid green;
  transform: translate(-50%, -50%) rotate(35deg);
}

${this.form.showLargeEmoticonBg ? '' : `/* 适配隐藏大表情背景 For hiding background of large emotes */
yt-live-chat-text-message-renderer #message:has(.emoji.blc-large-emoji)::before {
  content: none;
}

yt-live-chat-text-message-renderer #message:has(.emoji.blc-large-emoji) {
  padding: 0;
}`}

/* 背景色 Background colors */
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
      return common.getScAndNewMemberStyle(this.form)
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
