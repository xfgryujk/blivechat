<template>
  <el-row :gutter="20">
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
        <el-form-item label="SuperChat内容字体尺寸">
          <el-input v-model.number="form.scContentFontSize" type="number" min="0"></el-input>
        </el-form-item>
        <el-form-item label="SuperChat内容行高（0为默认）">
          <el-input v-model.number="form.scContentLineHeight" type="number" min="0"></el-input>
        </el-form-item>
        <el-form-item label="SuperChat内容颜色">
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
        <el-form-item>
          <el-button type="primary" @click="playAnimation">播放动画</el-button>
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
      <div id="example-container">
        <div id="fakebody">
          <chat-renderer :messages="messages" :css="exampleCss"></chat-renderer>
        </div>
      </div>
    </el-col>
  </el-row>
</template>

<script>
import _ from 'lodash'

import stylegen from './stylegen'
import fonts from './fonts'
import ChatRenderer from '@/components/ChatRenderer'

let time = new Date()
let textMessageTemplate = {
  id: 0,
  type: 0, // TextMessage
  avatarUrl: 'https://static.hdslb.com/images/member/noface.gif',
  time: `${time.getMinutes()}:${time.getSeconds()}`,
  authorName: '',
  authorType: 0,
  content: '',
  repeated: 1
}
let legacyPaidMessageTemplate = {
  id: 0,
  type: 1, // LegacyPaidMessage
  avatarUrl: 'https://static.hdslb.com/images/member/noface.gif',
  time: `${time.getMinutes()}:${time.getSeconds()}`,
  authorName: '',
  title: 'NEW MEMBER!',
  content: ''
}
let paidMessageTemplate = {
  id: 0,
  type: 2, // PaidMessage
  avatarUrl: 'https://static.hdslb.com/images/member/noface.gif',
  authorName: '',
  price: 0,
  time: `${time.getMinutes()}:${time.getSeconds()}`,
  content: ''
}
let nextId = 0
const EXAMPLE_MESSAGES = [
  {
    ...textMessageTemplate,
    id: nextId++,
    authorName: 'mob路人',
    content: '8888888888',
    repeated: 12
  }, {
    ...textMessageTemplate,
    id: nextId++,
    authorName: 'member舰长',
    authorType: 1,
    content: '草',
    repeated: 3
  }, {
    ...textMessageTemplate,
    id: nextId++,
    authorName: 'admin房管',
    authorType: 2,
    content: 'kksk'
  }, {
    ...legacyPaidMessageTemplate,
    id: nextId++,
    authorName: 'Paryi',
    content: 'Welcome Paryi'
  }, {
    ...paidMessageTemplate,
    id: nextId++,
    authorName: '石油佬',
    price: 1245,
    content: 'Sent 小电视飞船x1'
  }, {
    ...textMessageTemplate,
    id: nextId++,
    authorName: 'streamer主播',
    authorType: 3,
    content: '感谢石油佬送的小电视'
  }, {
    ...paidMessageTemplate,
    id: nextId++,
    authorName: '臭DD',
    price: 28,
    content: 'Sent 礼花x1'
  }
]

export default {
  name: 'StyleGenerator',
  components: {
    ChatRenderer
  },
  data() {
    let config = stylegen.getLocalConfig()
    let result = stylegen.getStyle(config)
    return {
      FONTS: [...fonts.LOCAL_FONTS, ...fonts.NETWORK_FONTS],
      form: {...config},
      result,
      exampleCss: result.replace(/^body\b/gm, '#fakebody'),
      messages: EXAMPLE_MESSAGES
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
    playAnimation() {
      this.messages = []
      this.$nextTick(() => this.messages = EXAMPLE_MESSAGES)
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
    computedResult: _.debounce(function (val) {
      this.result = val
      stylegen.setLocalConfig(this.form)
    }, 500),
    result (val) {
      this.exampleCss = val.replace(/^body\b/gm, '#fakebody')
    }
  }
}
</script>

<style scoped>
.el-form {
  max-width: 800px;
}

#example-container {
  position: fixed;
  top: 30px;
  right: 30px;
  width: 400px;
  height: calc(100vh - 110px);

  background-color: #444;
  background-image:
    -moz-linear-gradient(45deg, #333 25%, transparent 25%),
    -moz-linear-gradient(-45deg, #333 25%, transparent 25%),
    -moz-linear-gradient(45deg, transparent 75%, #333 75%),
    -moz-linear-gradient(-45deg, transparent 75%, #333 75%);
  background-image:
    -webkit-gradient(linear, 0 100%, 100% 0, color-stop(.25, #333), color-stop(.25, transparent)),
    -webkit-gradient(linear, 0 0, 100% 100%, color-stop(.25, #333), color-stop(.25, transparent)),
    -webkit-gradient(linear, 0 100%, 100% 0, color-stop(.75, transparent), color-stop(.75, #333)),
    -webkit-gradient(linear, 0 0, 100% 100%, color-stop(.75, transparent), color-stop(.75, #333));

  -moz-background-size:32px 32px;
  background-size:32px 32px;
  -webkit-background-size:32px 32px;

  background-position:0 0, 16px 0, 16px -16px, 0px 16px;

  padding: 25px;
}

#fakebody {
  outline: 1px #999 dashed;
  height: 100%;
}
</style>
