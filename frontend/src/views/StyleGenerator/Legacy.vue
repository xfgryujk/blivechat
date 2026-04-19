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
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.outlineSize')">
                <el-input v-model.number="form.outlineSize" type="number" min="0"></el-input>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('stylegen.blurryOutline')">
                <el-switch v-model="form.blurryOutline"></el-switch>
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
              <el-form-item :label="$t('stylegen.fontWeight')">
                <font-weight-select v-model="form.messageWeight"></font-weight-select>
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

  showOutlines: true,
  outlineSize: 2,
  outlineColor: '#000000',
  blurryOutline: false,

  showAvatars: true,
  avatarSize: 24,

  showUserNames: true,
  userNameFont: 'Imprima,Noto Sans SC',
  userNameFontSize: 20,
  userNameWeight: 700,
  userNameColor: '#cccccc',
  ownerUserNameColor: '#ffd600',
  moderatorUserNameColor: '#5e84f1',
  memberUserNameColor: '#0f9d58',
  showBadges: true,
  showColon: true,

  messageFont: 'Imprima,Noto Sans SC',
  messageFontSize: 20,
  messageWeight: 700,
  messageColor: '#ffffff',
  messageOnNewLine: false,
  messageReverseScroll: false,
  emoticonSize: 24,
  largeEmoticonSize: 40,

  showTime: false,
  timeFont: 'Imprima,Noto Sans SC',
  timeFontSize: 20,
  timeWeight: 400,
  timeColor: '#999999',

  bgColor: 'rgba(0, 0, 0, 0)',
  useBarsInsteadOfBg: false,
  messageBgColor: 'rgba(204, 204, 204, 0)',
  ownerMessageBgColor: 'rgba(255, 214, 0, 0)',
  moderatorMessageBgColor: 'rgba(94, 132, 241, 0)',
  memberMessageBgColor: 'rgba(15, 157, 88, 0)',

  firstLineFont: 'Imprima,Noto Sans SC',
  firstLineFontSize: 22,
  firstLineWeight: 700,
  firstLineColor: '#ffffff',
  secondLineFont: 'Imprima,Noto Sans SC',
  secondLineFontSize: 20,
  secondLineWeight: 700,
  secondLineColor: '#ffffff',
  scContentFont: 'Imprima,Noto Sans SC',
  scContentFontSize: 20,
  scContentWeight: 700,
  scContentColor: '#ffffff',
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
        this.outlineStyle,
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
  --paid-msg-line-1-weight: ${this.form.firstLineWeight};
  --paid-msg-line-2-color: ${this.form.secondLineColor ?? '#ffffff'};
  --paid-msg-line-2-size: calc(${this.form.secondLineFontSize} * var(--font-base-size));
  --paid-msg-line-2-weight: ${this.form.secondLineWeight};
  --paid-msg-content-color: ${this.form.scContentColor ?? '#ffffff'};
  --paid-msg-content-size: calc(${this.form.scContentFontSize} * var(--font-base-size));
  --paid-msg-content-weight: ${this.form.scContentWeight};
  --membership-msg-bg-color: var(--username-color-member);
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
      if (this.form.blurryOutline) {
        shadow.push(`0 0 ${this.form.outlineSize}px var(--outline-color)`)
      } else {
        for (let x = -this.form.outlineSize; x <= this.form.outlineSize; x += Math.ceil(this.form.outlineSize / 4)) {
          for (let y = -this.form.outlineSize; y <= this.form.outlineSize; y += Math.ceil(this.form.outlineSize / 4)) {
            shadow.push(`${x}px ${y}px var(--outline-color)`)
          }
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
      return `${common.getUserNameStyle(this.form)}

${!this.form.showColon ? '' : `/* 显示冒号 Show colon */
yt-live-chat-text-message-renderer #author-name::after {
  content: ":";
  margin-left: 2px;
}`}`
    },
    messageStyle() {
      return `${common.getMessageStyle(this.form)}

${!this.form.messageOnNewLine ? '' : `yt-live-chat-text-message-renderer #message {
  display: block;
  overflow: visible;
}`}

yt-live-chat-text-message-renderer #message:has(.emoji.blc-large-emoji) {
  vertical-align: top;
}`
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
      return `${common.getScAndNewMemberStyle(this.form)}

yt-live-chat-paid-message-renderer :is(#author-name, #author-name *),
yt-live-chat-membership-item-renderer :is(#header-content-inner-column, #header-content-inner-column *) {
  color: var(--paid-msg-line-1-color);
}

yt-live-chat-paid-message-renderer :is(#purchase-amount, #purchase-amount *),
yt-live-chat-membership-item-renderer :is(#header-subtext, #header-subtext *) {
  color: var(--paid-msg-line-2-color);
}

yt-live-chat-paid-message-renderer :is(#content, #content *) {
  color: var(--paid-msg-content-color);
}

yt-live-chat-ticker-paid-message-item-renderer #content {
  color: var(--paid-msg-line-2-color) !important;
}
`
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
