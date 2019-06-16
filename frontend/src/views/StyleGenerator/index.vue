<template>
  <el-row>
    <el-col :span="12">
      <el-form label-width="150px" size="mini">
        <h3>描边</h3>
        <el-form-item label="显示描边">
          <el-switch v-model="form.showOutlines"></el-switch>
        </el-form-item>
        <el-form-item label="描边尺寸">
          <el-input v-model.number="form.outlineSize" type="number" min="0"></el-input>
        </el-form-item>
        <el-form-item label="描边颜色">
          <el-color-picker v-model="form.outlineColor"></el-color-picker>
        </el-form-item>

        <h3>头像</h3>
        <el-form-item label="显示头像">
          <el-switch v-model="form.showAvatars"></el-switch>
        </el-form-item>
        <el-form-item label="头像尺寸">
          <el-input v-model.number="form.avatarSize" type="number" min="0"></el-input>
        </el-form-item>

        <h3>用户名</h3>
        <el-form-item label="字体">
          <el-autocomplete v-model="form.userNameFont" :fetch-suggestions="getFontSuggestions"></el-autocomplete>
        </el-form-item>
        <el-form-item label="字体尺寸">
          <el-input v-model.number="form.userNameFontSize" type="number" min="0"></el-input>
        </el-form-item>
        <el-form-item label="行高（0为默认）">
          <el-input v-model.number="form.userNameLineHeight" type="number" min="0"></el-input>
        </el-form-item>
        <el-form-item label="普通颜色">
          <el-color-picker v-model="form.userNameColor"></el-color-picker>
        </el-form-item>
        <el-form-item label="主播颜色">
          <el-color-picker v-model="form.ownerUserNameColor"></el-color-picker>
        </el-form-item>
        <el-form-item label="房管颜色">
          <el-color-picker v-model="form.moderatorUserNameColor"></el-color-picker>
        </el-form-item>
        <el-form-item label="舰长颜色">
          <el-color-picker v-model="form.memberUserNameColor"></el-color-picker>
        </el-form-item>
        <el-form-item label="显示勋章">
          <el-switch v-model="form.showBadges"></el-switch>
        </el-form-item>
        <el-form-item label="用户名后显示冒号">
          <el-switch v-model="form.showColon"></el-switch>
        </el-form-item>

        <h3>消息</h3>
        <el-form-item label="字体">
          <el-autocomplete v-model="form.messageFont" :fetch-suggestions="getFontSuggestions"></el-autocomplete>
        </el-form-item>
        <el-form-item label="字体尺寸">
          <el-input v-model.number="form.messageFontSize" type="number" min="0"></el-input>
        </el-form-item>
        <el-form-item label="行高（0为默认）">
          <el-input v-model.number="form.messageLineHeight" type="number" min="0"></el-input>
        </el-form-item>
        <el-form-item label="颜色">
          <el-color-picker v-model="form.messageColor"></el-color-picker>
        </el-form-item>
        <el-form-item label="在新行显示">
          <el-switch v-model="form.messageOnNewLine"></el-switch>
        </el-form-item>

        <h3>时间</h3>
        <el-form-item label="显示时间">
          <el-switch v-model="form.showTime"></el-switch>
        </el-form-item>
        <el-form-item label="字体">
          <el-autocomplete v-model="form.timeFont" :fetch-suggestions="getFontSuggestions"></el-autocomplete>
        </el-form-item>
        <el-form-item label="字体尺寸">
          <el-input v-model.number="form.timeFontSize" type="number" min="0"></el-input>
        </el-form-item>
        <el-form-item label="行高（0为默认）">
          <el-input v-model.number="form.timeLineHeight" type="number" min="0"></el-input>
        </el-form-item>
        <el-form-item label="颜色">
          <el-color-picker v-model="form.timeColor"></el-color-picker>
        </el-form-item>

        <h3>背景</h3>
        <el-form-item label="背景色">
          <el-color-picker v-model="form.bgColor" show-alpha></el-color-picker>
        </el-form-item>
        <el-form-item label="用条代替背景">
          <el-switch v-model="form.useBarsInsteadOfBg"></el-switch>
        </el-form-item>
        <el-form-item label="消息背景色">
          <el-color-picker v-model="form.messageBgColor" show-alpha></el-color-picker>
        </el-form-item>
        <el-form-item label="主播消息背景色">
          <el-color-picker v-model="form.ownerMessageBgColor" show-alpha></el-color-picker>
        </el-form-item>
        <el-form-item label="房管消息背景色">
          <el-color-picker v-model="form.moderatorMessageBgColor" show-alpha></el-color-picker>
        </el-form-item>
        <el-form-item label="舰长消息背景色">
          <el-color-picker v-model="form.memberMessageBgColor" show-alpha></el-color-picker>
        </el-form-item>

        <h3>礼物、舰长</h3>
        <el-form-item label="第一行字体">
          <el-autocomplete v-model="form.firstLineFont" :fetch-suggestions="getFontSuggestions"></el-autocomplete>
        </el-form-item>
        <el-form-item label="第一行字体尺寸">
          <el-input v-model.number="form.firstLineFontSize" type="number" min="0"></el-input>
        </el-form-item>
        <el-form-item label="第一行行高（0为默认）">
          <el-input v-model.number="form.firstLineLineHeight" type="number" min="0"></el-input>
        </el-form-item>
        <el-form-item label="第一行颜色">
          <el-color-picker v-model="form.firstLineColor"></el-color-picker>
        </el-form-item>
        <el-form-item label="第二行字体">
          <el-autocomplete v-model="form.secondLineFont" :fetch-suggestions="getFontSuggestions"></el-autocomplete>
        </el-form-item>
        <el-form-item label="第二行字体尺寸">
          <el-input v-model.number="form.secondLineFontSize" type="number" min="0"></el-input>
        </el-form-item>
        <el-form-item label="第二行行高（0为默认）">
          <el-input v-model.number="form.secondLineLineHeight" type="number" min="0"></el-input>
        </el-form-item>
        <el-form-item label="第二行颜色">
          <el-color-picker v-model="form.secondLineColor"></el-color-picker>
        </el-form-item>
        <el-form-item label="SuperChat内容字体">
          <el-autocomplete v-model="form.scContentFont" :fetch-suggestions="getFontSuggestions"></el-autocomplete>
        </el-form-item>
        <el-form-item label="SuperChat字体尺寸">
          <el-input v-model.number="form.scContentFontSize" type="number" min="0"></el-input>
        </el-form-item>
        <el-form-item label="SuperChat行高（0为默认）">
          <el-input v-model.number="form.scContentLineHeight" type="number" min="0"></el-input>
        </el-form-item>
        <el-form-item label="SuperChat颜色">
          <el-color-picker v-model="form.scContentColor"></el-color-picker>
        </el-form-item>
        <el-form-item label="显示新舰长背景">
          <el-switch v-model="form.showNewMemberBg"></el-switch>
        </el-form-item>
        <el-form-item label="显示SuperChat贴纸">
          <el-switch v-model="form.showScTicker"></el-switch>
        </el-form-item>
        <el-form-item label="显示SuperChat贴纸之外的内容">
          <el-switch v-model="form.showOtherThings"></el-switch>
        </el-form-item>

        <h3>动画</h3>
        <el-form-item label="进入动画">
          <el-switch v-model="form.animateIn"></el-switch>
        </el-form-item>
        <el-form-item label="淡入时间（毫秒）">
          <el-input v-model.number="form.fadeInTime" type="number" min="0"></el-input>
        </el-form-item>
        <el-form-item label="移除旧消息">
          <el-switch v-model="form.animateOut"></el-switch>
        </el-form-item>
        <el-form-item label="等待时间（秒）">
          <el-input v-model.number="form.animateOutWaitTime" type="number" min="0"></el-input>
        </el-form-item>
        <el-form-item label="淡出时间（毫秒）">
          <el-input v-model.number="form.fadeOutTime" type="number" min="0"></el-input>
        </el-form-item>
        <el-form-item label="滑动">
          <el-switch v-model="form.slide"></el-switch>
        </el-form-item>
        <el-form-item label="反向滑动">
          <el-switch v-model="form.reverseSlide"></el-switch>
        </el-form-item>

        <h3>结果</h3>
        <el-form-item label="CSS">
          <el-input v-model="result" ref="result" type="textarea" :rows="10"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="copyResult">复制</el-button>
          <el-button @click="resetConfig">恢复默认设置</el-button>
        </el-form-item>
      </el-form>
    </el-col>
    <el-col :span="12">
      预览
    </el-col>
  </el-row>
</template>

<script>
import _ from 'lodash'

import stylegen from './stylegen'
import fonts from './fonts'

export default {
  name: 'StyleGenerator',
  data() {
    let config = stylegen.getLocalConfig()
    return {
      FONTS: [...fonts.LOCAL_FONTS, ...fonts.NETWORK_FONTS],
      form: {...config},
      result: stylegen.getStyle(config)
    }
  },
  computed: {
    computedResult() {
      return stylegen.getStyle(this.form)
    }
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
    copyResult() {
      this.$refs.result.select()
      document.execCommand('Copy')
    },
    resetConfig() {
      this.form = {...stylegen.DEFAULT_CONFIG}
    }
  },
  watch: {
    computedResult: _.debounce(function (result) {
      this.result = result
      stylegen.setLocalConfig(this.form)
    }, 500)
  }
}
</script>

<style scoped>
.el-form {
  max-width: 800px;
}
</style>
