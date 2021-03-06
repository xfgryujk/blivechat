<template>
  <el-form label-width="150px" size="mini">
    <h3>{{$t('stylegen.outlines')}}</h3>
    <el-form-item :label="$t('stylegen.showOutlines')">
      <el-switch v-model="form.showOutlines"></el-switch>
    </el-form-item>
    <el-form-item :label="$t('stylegen.outlineSize')">
      <el-input v-model.number="form.outlineSize" type="number" min="0"></el-input>
    </el-form-item>
    <el-form-item :label="$t('stylegen.outlineColor')">
      <el-color-picker v-model="form.outlineColor"></el-color-picker>
    </el-form-item>

    <h3>{{$t('stylegen.avatars')}}</h3>
    <el-form-item :label="$t('stylegen.showAvatars')">
      <el-switch v-model="form.showAvatars"></el-switch>
    </el-form-item>
    <el-form-item :label="$t('stylegen.avatarSize')">
      <el-input v-model.number="form.avatarSize" type="number" min="0"></el-input>
    </el-form-item>

    <h3>{{$t('stylegen.userNames')}}</h3>
    <el-form-item :label="$t('stylegen.showUserNames')">
      <el-switch v-model="form.showUserNames"></el-switch>
    </el-form-item>
    <el-form-item :label="$t('stylegen.font')">
      <el-autocomplete v-model="form.userNameFont" :fetch-suggestions="getFontSuggestions"></el-autocomplete>
    </el-form-item>
    <el-form-item :label="$t('stylegen.fontSize')">
      <el-input v-model.number="form.userNameFontSize" type="number" min="0"></el-input>
    </el-form-item>
    <el-form-item :label="$t('stylegen.lineHeight')">
      <el-input v-model.number="form.userNameLineHeight" type="number" min="0"></el-input>
    </el-form-item>
    <el-form-item :label="$t('stylegen.normalColor')">
      <el-color-picker v-model="form.userNameColor"></el-color-picker>
    </el-form-item>
    <el-form-item :label="$t('stylegen.ownerColor')">
      <el-color-picker v-model="form.ownerUserNameColor"></el-color-picker>
    </el-form-item>
    <el-form-item :label="$t('stylegen.moderatorColor')">
      <el-color-picker v-model="form.moderatorUserNameColor"></el-color-picker>
    </el-form-item>
    <el-form-item :label="$t('stylegen.memberColor')">
      <el-color-picker v-model="form.memberUserNameColor"></el-color-picker>
    </el-form-item>
    <el-form-item :label="$t('stylegen.showBadges')">
      <el-switch v-model="form.showBadges"></el-switch>
    </el-form-item>
    <el-form-item :label="$t('stylegen.showColon')">
      <el-switch v-model="form.showColon"></el-switch>
    </el-form-item>

    <h3>{{$t('stylegen.messages')}}</h3>
    <el-form-item :label="$t('stylegen.font')">
      <el-autocomplete v-model="form.messageFont" :fetch-suggestions="getFontSuggestions"></el-autocomplete>
    </el-form-item>
    <el-form-item :label="$t('stylegen.fontSize')">
      <el-input v-model.number="form.messageFontSize" type="number" min="0"></el-input>
    </el-form-item>
    <el-form-item :label="$t('stylegen.lineHeight')">
      <el-input v-model.number="form.messageLineHeight" type="number" min="0"></el-input>
    </el-form-item>
    <el-form-item :label="$t('stylegen.color')">
      <el-color-picker v-model="form.messageColor"></el-color-picker>
    </el-form-item>
    <el-form-item :label="$t('stylegen.onNewLine')">
      <el-switch v-model="form.messageOnNewLine"></el-switch>
    </el-form-item>

    <h3>{{$t('stylegen.time')}}</h3>
    <el-form-item :label="$t('stylegen.showTime')">
      <el-switch v-model="form.showTime"></el-switch>
    </el-form-item>
    <el-form-item :label="$t('stylegen.font')">
      <el-autocomplete v-model="form.timeFont" :fetch-suggestions="getFontSuggestions"></el-autocomplete>
    </el-form-item>
    <el-form-item :label="$t('stylegen.fontSize')">
      <el-input v-model.number="form.timeFontSize" type="number" min="0"></el-input>
    </el-form-item>
    <el-form-item :label="$t('stylegen.lineHeight')">
      <el-input v-model.number="form.timeLineHeight" type="number" min="0"></el-input>
    </el-form-item>
    <el-form-item :label="$t('stylegen.color')">
      <el-color-picker v-model="form.timeColor"></el-color-picker>
    </el-form-item>

    <h3>{{$t('stylegen.backgrounds')}}</h3>
    <el-form-item :label="$t('stylegen.bgColor')">
      <el-color-picker v-model="form.bgColor" show-alpha></el-color-picker>
    </el-form-item>
    <el-form-item :label="$t('stylegen.useBarsInsteadOfBg')">
      <el-switch v-model="form.useBarsInsteadOfBg"></el-switch>
    </el-form-item>
    <el-form-item :label="$t('stylegen.messageBgColor')">
      <el-color-picker v-model="form.messageBgColor" show-alpha></el-color-picker>
    </el-form-item>
    <el-form-item :label="$t('stylegen.ownerMessageBgColor')">
      <el-color-picker v-model="form.ownerMessageBgColor" show-alpha></el-color-picker>
    </el-form-item>
    <el-form-item :label="$t('stylegen.moderatorMessageBgColor')">
      <el-color-picker v-model="form.moderatorMessageBgColor" show-alpha></el-color-picker>
    </el-form-item>
    <el-form-item :label="$t('stylegen.memberMessageBgColor')">
      <el-color-picker v-model="form.memberMessageBgColor" show-alpha></el-color-picker>
    </el-form-item>

    <h3>{{$t('stylegen.scAndNewMember')}}</h3>
    <el-form-item :label="$t('stylegen.firstLineFont')">
      <el-autocomplete v-model="form.firstLineFont" :fetch-suggestions="getFontSuggestions"></el-autocomplete>
    </el-form-item>
    <el-form-item :label="$t('stylegen.firstLineFontSize')">
      <el-input v-model.number="form.firstLineFontSize" type="number" min="0"></el-input>
    </el-form-item>
    <el-form-item :label="$t('stylegen.firstLineLineHeight')">
      <el-input v-model.number="form.firstLineLineHeight" type="number" min="0"></el-input>
    </el-form-item>
    <el-form-item :label="$t('stylegen.firstLineColor')">
      <el-color-picker v-model="form.firstLineColor"></el-color-picker>
    </el-form-item>
    <el-form-item :label="$t('stylegen.secondLineFont')">
      <el-autocomplete v-model="form.secondLineFont" :fetch-suggestions="getFontSuggestions"></el-autocomplete>
    </el-form-item>
    <el-form-item :label="$t('stylegen.secondLineFontSize')">
      <el-input v-model.number="form.secondLineFontSize" type="number" min="0"></el-input>
    </el-form-item>
    <el-form-item :label="$t('stylegen.secondLineLineHeight')">
      <el-input v-model.number="form.secondLineLineHeight" type="number" min="0"></el-input>
    </el-form-item>
    <el-form-item :label="$t('stylegen.secondLineColor')">
      <el-color-picker v-model="form.secondLineColor"></el-color-picker>
    </el-form-item>
    <el-form-item :label="$t('stylegen.scContentLineFont')">
      <el-autocomplete v-model="form.scContentFont" :fetch-suggestions="getFontSuggestions"></el-autocomplete>
    </el-form-item>
    <el-form-item :label="$t('stylegen.scContentLineFontSize')">
      <el-input v-model.number="form.scContentFontSize" type="number" min="0"></el-input>
    </el-form-item>
    <el-form-item :label="$t('stylegen.scContentLineLineHeight')">
      <el-input v-model.number="form.scContentLineHeight" type="number" min="0"></el-input>
    </el-form-item>
    <el-form-item :label="$t('stylegen.scContentLineColor')">
      <el-color-picker v-model="form.scContentColor"></el-color-picker>
    </el-form-item>
    <el-form-item :label="$t('stylegen.showNewMemberBg')">
      <el-switch v-model="form.showNewMemberBg"></el-switch>
    </el-form-item>
    <el-form-item :label="$t('stylegen.showScTicker')">
      <el-switch v-model="form.showScTicker"></el-switch>
    </el-form-item>
    <el-form-item :label="$t('stylegen.showOtherThings')">
      <el-switch v-model="form.showOtherThings"></el-switch>
    </el-form-item>

    <h3>{{$t('stylegen.animation')}}</h3>
    <el-form-item :label="$t('stylegen.animateIn')">
      <el-switch v-model="form.animateIn"></el-switch>
    </el-form-item>
    <el-form-item :label="$t('stylegen.fadeInTime')">
      <el-input v-model.number="form.fadeInTime" type="number" min="0"></el-input>
    </el-form-item>
    <el-form-item :label="$t('stylegen.animateOut')">
      <el-switch v-model="form.animateOut"></el-switch>
    </el-form-item>
    <el-form-item :label="$t('stylegen.animateOutWaitTime')">
      <el-input v-model.number="form.animateOutWaitTime" type="number" min="0"></el-input>
    </el-form-item>
    <el-form-item :label="$t('stylegen.fadeOutTime')">
      <el-input v-model.number="form.fadeOutTime" type="number" min="0"></el-input>
    </el-form-item>
    <el-form-item :label="$t('stylegen.slide')">
      <el-switch v-model="form.slide"></el-switch>
    </el-form-item>
    <el-form-item :label="$t('stylegen.reverseSlide')">
      <el-switch v-model="form.reverseSlide"></el-switch>
    </el-form-item>
    <el-form-item>
      <el-button type="primary" @click="$emit('playAnimation')">{{$t('stylegen.playAnimation')}}</el-button>
    </el-form-item>
  </el-form>
</template>

<script>
import _ from 'lodash'

import * as stylegen from './stylegen'
import * as fonts from './fonts'

export default {
  name: 'Legacy',
  props: {
    value: String
  },
  data() {
    let stylegenConfig = stylegen.getLocalConfig()
    return {
      FONTS: fonts.ALL_FONTS,

      form: {...stylegenConfig}
    }
  },
  computed: {
    result() {
      return stylegen.getStyle(this.form)
    }
  },
  watch: {
    result(val) {
      this.$emit('input', val)
      this.saveResult()
    }
  },
  created() {
    this.$emit('input', this.result)
  },
  methods: {
    getFontSuggestions(query, callback) {
      let res = this.FONTS.map(font => {return {value: font}})
      if (query) {
        query = query.toLowerCase()
        res = res.filter(
          font => font.value.toLowerCase().indexOf(query) !== -1
        )
      }
      callback(res)
    },
    saveResult: _.debounce(function() {
      stylegen.setLocalConfig(this.form)
    }, 500),
    resetConfig() {
      this.form = {...stylegen.DEFAULT_CONFIG}
    }
  }
}
</script>
