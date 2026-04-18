<template>
  <el-card shadow="never">
    <el-form label-width="150px" size="mini">
      <el-collapse>
        <el-collapse-item>
          <template slot="title">
            <h3>{{ $t('stylegen.outlines') }}</h3>
          </template>
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.showOutlines')">
                <el-switch v-model="form.showOutlines"></el-switch>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.outlineColor')">
                <el-color-picker v-model="form.outlineColor"></el-color-picker>
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item :label="$t('stylegen.outlineSize')">
            <el-input v-model.number="form.outlineSize" type="number" min="0"></el-input>
          </el-form-item>
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
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.showColon')">
                <el-switch v-model="form.showColon"></el-switch>
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
              <el-form-item :label="$t('stylegen.onNewLine')">
                <el-switch v-model="form.messageOnNewLine"></el-switch>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.messageReverseScroll')">
                <el-switch v-model="form.messageReverseScroll"></el-switch>
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
              <el-form-item :label="$t('stylegen.useBarsInsteadOfBg')">
                <el-switch v-model="form.useBarsInsteadOfBg"></el-switch>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.messageBgColor')">
                <el-color-picker v-model="form.messageBgColor" show-alpha></el-color-picker>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.memberMessageBgColor')">
                <el-color-picker v-model="form.memberMessageBgColor" show-alpha></el-color-picker>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.moderatorMessageBgColor')">
                <el-color-picker v-model="form.moderatorMessageBgColor" show-alpha></el-color-picker>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.ownerMessageBgColor')">
                <el-color-picker v-model="form.ownerMessageBgColor" show-alpha></el-color-picker>
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
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.firstLineColor')">
                <el-color-picker v-model="form.firstLineColor"></el-color-picker>
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
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.secondLineColor')">
                <el-color-picker v-model="form.secondLineColor"></el-color-picker>
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
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.scContentLineColor')">
                <el-color-picker v-model="form.scContentColor"></el-color-picker>
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

          <el-form-item :label="$t('stylegen.showNewMemberBg')">
            <el-switch v-model="form.showNewMemberBg"></el-switch>
          </el-form-item>
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
  showOutlines: true,
  outlineSize: 2,
  outlineColor: '#000000',

  showAvatars: true,
  avatarSize: 24,

  showUserNames: true,
  userNameFont: 'Imprima,Noto Sans SC',
  userNameFontSize: 20,
  userNameLineHeight: 0,
  userNameColor: '#cccccc',
  ownerUserNameColor: '#ffd600',
  moderatorUserNameColor: '#5e84f1',
  memberUserNameColor: '#0f9d58',
  showBadges: true,
  showColon: true,

  messageFont: 'Imprima,Noto Sans SC',
  messageFontSize: 20,
  messageLineHeight: 0,
  messageColor: '#ffffff',
  messageOnNewLine: false,
  messageReverseScroll: false,
  emoticonSize: 24,
  largeEmoticonSize: 40,

  showTime: false,
  timeFont: 'Imprima,Noto Sans SC',
  timeFontSize: 20,
  timeLineHeight: 0,
  timeColor: '#999999',

  bgColor: 'rgba(0, 0, 0, 0)',
  useBarsInsteadOfBg: false,
  messageBgColor: 'rgba(204, 204, 204, 0)',
  ownerMessageBgColor: 'rgba(255, 214, 0, 0)',
  moderatorMessageBgColor: 'rgba(94, 132, 241, 0)',
  memberMessageBgColor: 'rgba(15, 157, 88, 0)',

  firstLineFont: 'Imprima,Noto Sans SC',
  firstLineFontSize: 22,
  firstLineLineHeight: 0,
  firstLineColor: '#ffffff',
  secondLineFont: 'Imprima,Noto Sans SC',
  secondLineFontSize: 20,
  secondLineLineHeight: 0,
  secondLineColor: '#ffffff',
  scContentFont: 'Imprima,Noto Sans SC',
  scContentFontSize: 20,
  scContentLineHeight: 0,
  scContentColor: '#ffffff',
  showNewMemberBg: true,
  showScTicker: false,
  showOtherThings: true,

  animateIn: false,
  fadeInTime: 200, // ms
  animateOut: false,
  animateOutWaitTime: 30, // s
  fadeOutTime: 200, // ms
  slide: false,
  reverseSlide: false
}

export default {
  name: 'Legacy',
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
        this.outlineStyle,
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

  /* 描边 Outlines */
  --outline-color: ${this.form.outlineColor};

  /* 背景色 Background colors
    普通、舰长、房管、主播 */
  --text-msg-bg-color: ${this.form.messageBgColor ?? 'transparent'};
  --text-msg-bg-color-member: ${this.form.memberMessageBgColor ?? 'transparent'};
  --text-msg-bg-color-moderator: ${this.form.moderatorMessageBgColor ?? 'transparent'};
  --text-msg-bg-color-owner: ${this.form.ownerMessageBgColor ?? 'transparent'};

  /* 付费、上舰消息 Super Chats / Membership messages */
  --paid-msg-line-1-color: ${this.form.firstLineColor ?? '#ffffff'};
  --paid-msg-line-1-size: calc(${this.form.firstLineFontSize} * var(--font-base-size));
  --paid-msg-line-2-color: ${this.form.secondLineColor ?? '#ffffff'};
  --paid-msg-line-2-size: calc(${this.form.secondLineFontSize} * var(--font-base-size));
  --paid-msg-content-color: ${this.form.scContentColor ?? '#ffffff'};
  --paid-msg-content-size: calc(${this.form.scContentFontSize} * var(--font-base-size));
  --membership-msg-bg-color: ${this.form.showNewMemberBg ? 'var(--username-color-member)' : 'transparent'};
}`
    },
    paddingStyle() {
      return `/* 减少两侧边距 Reduce side padding */
yt-live-chat-text-message-renderer {
  padding-inline: ${this.form.useBarsInsteadOfBg ? 20 : 4}px 4px;
}`
    },
    outlineStyle() {
      if (!this.form.showOutlines || !this.form.outlineSize) {
        return ''
      }
      let shadow = []
      for (let x = -this.form.outlineSize; x <= this.form.outlineSize; x += Math.ceil(this.form.outlineSize / 4)) {
        for (let y = -this.form.outlineSize; y <= this.form.outlineSize; y += Math.ceil(this.form.outlineSize / 4)) {
          shadow.push(`${x}px ${y}px var(--outline-color)`)
        }
      }
      return `/* 描边 Outlines */
yt-live-chat-renderer * {
  text-shadow: ${shadow.join(', ')};
}`
    },
    avatarStyle() {
      return common.getAvatarStyle(this.form)
    },
    userNameStyle() {
      return `/* 用户名 Channel names */
yt-live-chat-text-message-renderer #author-name {
  ${this.form.showUserNames ? '' : 'display: none;'}
  color: var(--username-color);
  font-family: ${common.fontsStrToCss(this.form.userNameFont)};
  font-size: var(--username-size);
  line-height: calc(${this.form.userNameLineHeight || (this.form.userNameFontSize * 1.2)} * var(--font-base-size));
}

${common.getUserNameStyle(this.form)}

${!this.form.showColon ? '' : `/* 显示冒号 Show colon */
yt-live-chat-text-message-renderer #author-name::after {
  content: ":";
  margin-left: 2px;
}`}`
    },
    messageStyle() {
      return `/* 文本消息 Text messages */
yt-live-chat-text-message-renderer :is(#message, #message *) {
  color: var(--text-content-color);
  font-family: ${common.fontsStrToCss(this.form.messageFont)};
  font-size: var(--text-content-size);
  line-height: calc(${this.form.messageLineHeight || (this.form.messageFontSize * 1.2)} * var(--font-base-size));
}

${!this.form.messageOnNewLine ? '' : `yt-live-chat-text-message-renderer #message {
  display: block;
  overflow: visible;
}`}

yt-live-chat-text-message-renderer #message:has(.emoji.blc-large-emoji) {
  vertical-align: top;
}

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

${this.getBgStyleForAuthorType('', this.form.messageBgColor)}

${this.getBgStyleForAuthorType('owner', this.form.ownerMessageBgColor)}

${this.getBgStyleForAuthorType('moderator', this.form.moderatorMessageBgColor)}

${this.getBgStyleForAuthorType('member', this.form.memberMessageBgColor)}

${!this.form.useBarsInsteadOfBg ? '' : `yt-live-chat-text-message-renderer::after {
  content: "";
  position: absolute;
  display: block;
  left: 8px;
  top: 4px;
  bottom: 4px;
  width: 1px;
  box-sizing: border-box;
  border-radius: 2px;
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
  ${this.form.showNewMemberBg ? 'margin: 4px 0;' : `box-shadow: none;
  margin: 0;`}
}

${this.scTickerStyle}

${this.form.showOtherThings ? '' : `yt-live-chat-item-list-renderer {
  display: none;
}`}`
    },
    scAndNewMemberFontStyle() {
      let firstLineLineHeight = this.form.firstLineLineHeight || (this.form.firstLineFontSize * 1.2)
      return `yt-live-chat-paid-message-renderer :is(#author-name, #author-name *),
yt-live-chat-membership-item-renderer :is(#header-content-inner-column, #header-content-inner-column *) {
  color: var(--paid-msg-line-1-color);
  font-family: ${common.fontsStrToCss(this.form.firstLineFont)};
  font-size: var(--paid-msg-line-1-size);
  line-height: calc(${firstLineLineHeight} * var(--font-base-size));
}

yt-live-chat-membership-item-renderer yt-live-chat-author-badge-renderer :is(img, yt-icon) {
  width: calc(${firstLineLineHeight} * var(--font-base-size));
  height: calc(${firstLineLineHeight} * var(--font-base-size));
}

yt-live-chat-paid-message-renderer :is(#purchase-amount, #purchase-amount *),
yt-live-chat-membership-item-renderer :is(#header-subtext, #header-subtext *) {
  color: var(--paid-msg-line-2-color);
  font-family: ${common.fontsStrToCss(this.form.secondLineFont)};
  font-size: var(--paid-msg-line-2-size);
  line-height: calc(${this.form.secondLineLineHeight || (this.form.secondLineFontSize * 1.2)} * var(--font-base-size));
}

yt-live-chat-paid-message-renderer :is(#content, #content *) {
  color: var(--paid-msg-content-color);
  font-family: ${common.fontsStrToCss(this.form.scContentFont)};
  font-size: var(--paid-msg-content-size);
  line-height: calc(${this.form.scContentLineHeight || (this.form.scContentFontSize * 1.2)} * var(--font-base-size));
}`
    },
    scTickerStyle() {
      if (!this.form.showScTicker) {
        return `yt-live-chat-ticker-renderer {
  display: none;
}`
      } else {
        let secondLineLineHeight = this.form.secondLineLineHeight || (this.form.secondLineFontSize * 1.2)
        return `/* SC固定栏 Super Chat ticker */
yt-live-chat-ticker-renderer #items {
  height: unset;
}

yt-live-chat-ticker-paid-message-item-renderer #author-photo img {
  width: calc(${secondLineLineHeight} * var(--font-base-size));
  height: calc(${secondLineLineHeight} * var(--font-base-size));
}

yt-live-chat-ticker-paid-message-item-renderer #content {
  height: unset;
  color: var(--paid-msg-line-2-color) !important;
  font-family: ${common.fontsStrToCss(this.form.secondLineFont)};
  font-size: var(--paid-msg-line-2-size);
  line-height: calc(${secondLineLineHeight} * var(--font-base-size));
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
      window.localStorage.stylegenConfig = JSON.stringify(config)
    }, 500),
    loadConfig() {
      try {
        return mergeConfig(JSON.parse(window.localStorage.stylegenConfig), DEFAULT_CONFIG)
      } catch {
        return { ...DEFAULT_CONFIG }
      }
    },
    resetConfig() {
      this.form = { ...DEFAULT_CONFIG }
    },

    getBgStyleForAuthorType(authorType, color) {
      if (!color) {
        return ''
      }
      let typeSelector = authorType ? `[author-type="${authorType}"]` : ''
      let varName = authorType ? `--text-msg-bg-color-${authorType}` : '--text-msg-bg-color'
      if (!this.form.useBarsInsteadOfBg) {
        return `yt-live-chat-text-message-renderer${typeSelector} {
  background-color: var(${varName});
}`
      } else {
        return `yt-live-chat-text-message-renderer${typeSelector}::after {
  border: 2px solid var(${varName});
}`
      }
    }
  }
}
</script>
