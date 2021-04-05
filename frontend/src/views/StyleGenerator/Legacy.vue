<template>
  <div>
    <el-form label-width="150px" size="mini">
      <h3>{{$t('stylegen.outlines')}}</h3>
      <el-card shadow="never">
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
      </el-card>

      <h3>{{$t('stylegen.avatars')}}</h3>
      <el-card shadow="never">
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
      </el-card>

      <h3>{{$t('stylegen.userNames')}}</h3>
      <el-card shadow="never">
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
      </el-card>

      <h3>{{$t('stylegen.messages')}}</h3>
      <el-card shadow="never">
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
        <el-form-item :label="$t('stylegen.onNewLine')">
          <el-switch v-model="form.messageOnNewLine"></el-switch>
        </el-form-item>
      </el-card>

      <h3>{{$t('stylegen.time')}}</h3>
      <el-card shadow="never">
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
      </el-card>

      <h3>{{$t('stylegen.backgrounds')}}</h3>
      <el-card shadow="never">
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
      </el-card>

      <h3>{{$t('stylegen.scAndNewMember')}}</h3>
      <el-card shadow="never">
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
      </el-card>

      <h3>{{$t('stylegen.animation')}}</h3>
      <el-card shadow="never">
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
      </el-card>
    </el-form>
  </div>
</template>

<script>
import _ from 'lodash'

import FontSelect from './FontSelect'
import * as common from './common'
import {mergeConfig} from '@/utils'

export const DEFAULT_CONFIG = {
  showOutlines: true,
  outlineSize: 2,
  outlineColor: '#000000',

  showAvatars: true,
  avatarSize: 24,

  showUserNames: true,
  userNameFont: 'Changa One',
  userNameFontSize: 20,
  userNameLineHeight: 0,
  userNameColor: '#cccccc',
  ownerUserNameColor: '#ffd600',
  moderatorUserNameColor: '#5e84f1',
  memberUserNameColor: '#0f9d58',
  showBadges: true,
  showColon: true,

  messageFont: 'Imprima',
  messageFontSize: 18,
  messageLineHeight: 0,
  messageColor: '#ffffff',
  messageOnNewLine: false,

  showTime: false,
  timeFont: 'Imprima',
  timeFontSize: 16,
  timeLineHeight: 0,
  timeColor: '#999999',

  bgColor: 'rgba(0, 0, 0, 0)',
  useBarsInsteadOfBg: false,
  messageBgColor: 'rgba(204, 204, 204, 0)',
  ownerMessageBgColor: 'rgba(255, 214, 0, 0)',
  moderatorMessageBgColor: 'rgba(94, 132, 241, 0)',
  memberMessageBgColor: 'rgba(15, 157, 88, 0)',

  firstLineFont: 'Changa One',
  firstLineFontSize: 20,
  firstLineLineHeight: 0,
  firstLineColor: '#ffffff',
  secondLineFont: 'Imprima',
  secondLineFontSize: 18,
  secondLineLineHeight: 0,
  secondLineColor: '#ffffff',
  scContentFont: 'Imprima',
  scContentFontSize: 18,
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
      return `${this.importStyle}

${common.COMMON_STYLE}

${this.paddingStyle}

${this.outlineStyle}

${this.avatarStyle}

${this.userNameStyle}

${this.messageStyle}

${this.timeStyle}

${this.backgroundStyle}

${this.scAndNewMemberStyle}

${this.animationStyle}
`
    },
    importStyle() {
      let allFonts = []
      for (let name of ['userNameFont', 'messageFont', 'timeFont', 'firstLineFont', 'secondLineFont', 'scContentFont']) {
        allFonts.push(this.form[name])
      }
      return common.getImportStyle(allFonts)
    },
    paddingStyle() {
      return `/* Reduce side padding */
yt-live-chat-text-message-renderer {
  padding-left: ${this.form.useBarsInsteadOfBg ? 20 : 4}px !important;
  padding-right: 4px !important;
}`
    },
    outlineStyle() {
      return `/* Outlines */
yt-live-chat-renderer * {
  ${this.showOutlinesStyle}
  font-family: "${common.cssEscapeStr(this.form.messageFont)}"${common.FALLBACK_FONTS};
  font-size: ${this.form.messageFontSize}px !important;
  line-height: ${this.form.messageLineHeight || this.form.messageFontSize}px !important;
}`
    },
    showOutlinesStyle () {
      if (!this.form.showOutlines || !this.form.outlineSize) {
        return ''
      }
      let shadow = []
      for (let x = -this.form.outlineSize; x <= this.form.outlineSize; x += Math.ceil(this.form.outlineSize / 4)) {
        for (let y = -this.form.outlineSize; y <= this.form.outlineSize; y += Math.ceil(this.form.outlineSize / 4)) {
          shadow.push(`${x}px ${y}px ${this.form.outlineColor}`)
        }
      }
      return `text-shadow: ${shadow.join(', ')};`
    },
    avatarStyle() {
      return common.getAvatarStyle(this.form)
    },
    userNameStyle() {
      return `/* Channel names */
yt-live-chat-text-message-renderer #author-name[type="owner"],
yt-live-chat-text-message-renderer yt-live-chat-author-badge-renderer[type="owner"] {
  ${this.form.ownerUserNameColor ? `color: ${this.form.ownerUserNameColor} !important;` : ''}
}

yt-live-chat-text-message-renderer #author-name[type="moderator"],
yt-live-chat-text-message-renderer yt-live-chat-author-badge-renderer[type="moderator"] {
  ${this.form.moderatorUserNameColor ? `color: ${this.form.moderatorUserNameColor} !important;` : ''}
}

yt-live-chat-text-message-renderer #author-name[type="member"],
yt-live-chat-text-message-renderer yt-live-chat-author-badge-renderer[type="member"] {
  ${this.form.memberUserNameColor ? `color: ${this.form.memberUserNameColor} !important;` : ''}
}

yt-live-chat-text-message-renderer #author-name {
  ${this.form.showUserNames ? '' : 'display: none !important;'}
  ${this.form.userNameColor ? `color: ${this.form.userNameColor} !important;` : ''}
  font-family: "${common.cssEscapeStr(this.form.userNameFont)}"${common.FALLBACK_FONTS};
  font-size: ${this.form.userNameFontSize}px !important;
  line-height: ${this.form.userNameLineHeight || this.form.userNameFontSize}px !important;
}

${!this.form.showColon ? '' : `/* Show colon */
yt-live-chat-text-message-renderer #author-name::after {
  content: ":";
  margin-left: ${this.form.outlineSize}px;
}`}

/* Hide badges */
yt-live-chat-text-message-renderer #chat-badges {
  ${this.form.showBadges ? '' : 'display: none !important;'}
  vertical-align: text-top !important;
}`
    },
    messageStyle() {
      return `/* Messages */
yt-live-chat-text-message-renderer #message,
yt-live-chat-text-message-renderer #message * {
  ${this.form.messageColor ? `color: ${this.form.messageColor} !important;` : ''}
  font-family: "${common.cssEscapeStr(this.form.messageFont)}"${common.FALLBACK_FONTS};
  font-size: ${this.form.messageFontSize}px !important;
  line-height: ${this.form.messageLineHeight || this.form.messageFontSize}px !important;
}

${!this.form.messageOnNewLine ? '' : `yt-live-chat-text-message-renderer #message {
  display: block !important;
  overflow: visible !important;
}`}`
    },
    timeStyle() {
      return common.getTimeStyle(this.form)
    },
    backgroundStyle() {
      return `/* Background colors */
body {
  overflow: hidden;
  ${this.form.bgColor ? `background-color: ${this.form.bgColor};` : ''}
}

${this.getBgStyleForAuthorType('', this.form.messageBgColor)}

${this.getBgStyleForAuthorType('owner', this.form.ownerMessageBgColor)}

${this.getBgStyleForAuthorType('moderator', this.form.moderatorMessageBgColor)}

${this.getBgStyleForAuthorType('member', this.form.memberMessageBgColor)}`
    },
    scAndNewMemberStyle() {
      return `/* SuperChat/Fan Funding Messages */
yt-live-chat-paid-message-renderer {
  margin: 4px 0 !important;
}

${this.scAndNewMemberFontStyle}

yt-live-chat-membership-item-renderer #card,
yt-live-chat-membership-item-renderer #header {
  ${this.showNewMemberBgStyle}
}

${this.scTickerStyle}

${this.form.showOtherThings ? '' : `yt-live-chat-item-list-renderer {
  display: none !important;
}`}`
    },
    scAndNewMemberFontStyle() {
      return `yt-live-chat-paid-message-renderer #author-name,
yt-live-chat-paid-message-renderer #author-name *,
yt-live-chat-membership-item-renderer #header-content-inner-column,
yt-live-chat-membership-item-renderer #header-content-inner-column * {
  ${this.form.firstLineColor ? `color: ${this.form.firstLineColor} !important;` : ''}
  font-family: "${common.cssEscapeStr(this.form.firstLineFont)}"${common.FALLBACK_FONTS};
  font-size: ${this.form.firstLineFontSize}px !important;
  line-height: ${this.form.firstLineLineHeight || this.form.firstLineFontSize}px !important;
}

yt-live-chat-paid-message-renderer #purchase-amount,
yt-live-chat-paid-message-renderer #purchase-amount *,
yt-live-chat-membership-item-renderer #header-subtext,
yt-live-chat-membership-item-renderer #header-subtext * {
  ${this.form.secondLineColor ? `color: ${this.form.secondLineColor} !important;` : ''}
  font-family: "${common.cssEscapeStr(this.form.secondLineFont)}"${common.FALLBACK_FONTS};
  font-size: ${this.form.secondLineFontSize}px !important;
  line-height: ${this.form.secondLineLineHeight || this.form.secondLineFontSize}px !important;
}

yt-live-chat-paid-message-renderer #content,
yt-live-chat-paid-message-renderer #content * {
  ${this.form.scContentColor ? `color: ${this.form.scContentColor} !important;` : ''}
  font-family: "${common.cssEscapeStr(this.form.scContentFont)}"${common.FALLBACK_FONTS};
  font-size: ${this.form.scContentFontSize}px !important;
  line-height: ${this.form.scContentLineHeight || this.form.scContentFontSize}px !important;
}`
    },
    showNewMemberBgStyle() {
      if (this.form.showNewMemberBg) {
        return `background-color: ${this.form.memberUserNameColor} !important;
  margin: 4px 0 !important;`
      } else {
        return `background-color: transparent !important;
  box-shadow: none !important;
  margin: 0 !important;`
      }
    },
    scTickerStyle() {
      return `${this.form.showScTicker ? '' : `yt-live-chat-ticker-renderer {
  display: none !important;
}`}

/* SuperChat Ticker */
yt-live-chat-ticker-paid-message-item-renderer,
yt-live-chat-ticker-paid-message-item-renderer *,
yt-live-chat-ticker-sponsor-item-renderer,
yt-live-chat-ticker-sponsor-item-renderer * {
  ${this.form.secondLineColor ? `color: ${this.form.secondLineColor} !important;` : ''}
  font-family: "${common.cssEscapeStr(this.form.secondLineFont)}"${common.FALLBACK_FONTS};
}`
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
  created() {
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
        return {...DEFAULT_CONFIG}
      }
    },
    resetConfig() {
      this.form = {...DEFAULT_CONFIG}
    },

    getBgStyleForAuthorType(authorType, color) {
      let typeSelector = authorType ? `[author-type="${authorType}"]` : ''
      if (!this.form.useBarsInsteadOfBg) {
        return `yt-live-chat-text-message-renderer${typeSelector},
yt-live-chat-text-message-renderer${typeSelector}[is-highlighted] {
  ${color ? `background-color: ${color} !important;` : ''}
}`
      } else {
        return `yt-live-chat-text-message-renderer${typeSelector}::after {
  ${color ? `border: 2px solid ${color};` : ''}
  content: "";
  position: absolute;
  display: block;
  left: 8px;
  top: 4px;
  bottom: 4px;
  width: 1px;
  box-sizing: border-box;
  border-radius: 2px;
}`
      }
    }
  }
}
</script>
