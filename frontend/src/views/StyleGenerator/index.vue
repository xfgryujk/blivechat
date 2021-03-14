<template>
  <el-row :gutter="20">
    <el-col :sm="24" :md="16">
      <el-tabs v-model="activeTab">
        <el-tab-pane :label="$t('stylegen.legacy')" name="legacy">
          <legacy ref="legacy" v-model="subComponentResults.legacy" @playAnimation="playAnimation"></legacy>
        </el-tab-pane>
        <el-tab-pane :label="$t('stylegen.lineLike')" name="lineLike">
          <line-like ref="lineLike" v-model="subComponentResults.lineLike" @playAnimation="playAnimation"></line-like>
        </el-tab-pane>
      </el-tabs>

      <el-form label-width="150px" size="mini">
        <h3>{{$t('stylegen.result')}}</h3>
        <el-card shadow="never">
          <el-form-item label="CSS">
            <el-input v-model="inputResult" ref="result" type="textarea" :rows="20"></el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="copyResult">{{$t('stylegen.copy')}}</el-button>
            <el-button @click="resetConfig">{{$t('stylegen.resetConfig')}}</el-button>
          </el-form-item>
        </el-card>
      </el-form>
    </el-col>

    <el-col :sm="24" :md="8">
      <div id="example-container" :style="{top: `${exampleTop}px`}">
        <div id="fakebody">
          <chat-renderer ref="renderer" :css="exampleCss"></chat-renderer>
        </div>
      </div>
    </el-col>
  </el-row>
</template>

<script>
import _ from 'lodash'

import Legacy from './Legacy'
import LineLike from './LineLike'
import ChatRenderer from '@/components/ChatRenderer'
import * as constants from '@/components/ChatRenderer/constants'

let time = new Date()
let textMessageTemplate = {
  id: 0,
  addTime: time,
  type: constants.MESSAGE_TYPE_TEXT,
  avatarUrl: 'https://static.hdslb.com/images/member/noface.gif',
  time: time,
  authorName: '',
  authorType: constants.AUTHRO_TYPE_NORMAL,
  content: '',
  privilegeType: 0,
  repeated: 1,
  translation: ''
}
let membershipItemTemplate = {
  id: 0,
  addTime: time,
  type: constants.MESSAGE_TYPE_MEMBER,
  avatarUrl: 'https://static.hdslb.com/images/member/noface.gif',
  time: time,
  authorName: '',
  privilegeType: 3,
  title: 'New member'
}
let paidMessageTemplate = {
  id: 0,
  addTime: time,
  type: constants.MESSAGE_TYPE_SUPER_CHAT,
  avatarUrl: 'https://static.hdslb.com/images/member/noface.gif',
  authorName: '',
  price: 0,
  time: time,
  content: '',
  translation: ''
}
let nextId = 0
const EXAMPLE_MESSAGES = [
  {
    ...textMessageTemplate,
    id: (nextId++).toString(),
    authorName: 'mob路人',
    content: '8888888888',
    repeated: 12
  },
  {
    ...textMessageTemplate,
    id: (nextId++).toString(),
    authorName: 'member舰长',
    authorType:  constants.AUTHRO_TYPE_MEMBER,
    content: '草',
    privilegeType: 3,
    repeated: 3
  },
  {
    ...textMessageTemplate,
    id: (nextId++).toString(),
    authorName: 'admin房管',
    authorType: constants.AUTHRO_TYPE_ADMIN,
    content: 'kksk'
  },
  {
    ...membershipItemTemplate,
    id: (nextId++).toString(),
    authorName: 'xfgryujk'
  },
  {
    ...paidMessageTemplate,
    id: (nextId++).toString(),
    authorName: '小陈',
    price: 66600,
    content: 'Sent 小电视飞船x100'
  },
  {
    ...textMessageTemplate,
    id: (nextId++).toString(),
    authorName: 'streamer主播',
    authorType: constants.AUTHRO_TYPE_OWNER,
    content: '老板大气，老板身体健康'
  },
  {
    ...paidMessageTemplate,
    id: (nextId++).toString(),
    authorName: '叔叔 / おじさん',
    price: 30,
    content: '言いたいことがあるんだよ！'
  }
]

export default {
  name: 'StyleGenerator',
  components: {
    Legacy, LineLike, ChatRenderer
  },
  data() {
    // 数据流：
    //                                                   输入框 --\
    // 子组件 -> subComponentResults -> subComponentResult -> inputResult -> 防抖延迟0.5s后 -> debounceResult -> exampleCss
    return {
      // 子组件的结果
      subComponentResults: {
        legacy: '',
        lineLike: ''
      },
      activeTab: 'legacy',
      // 输入框的结果
      inputResult: '',
      // 防抖后延迟变化的结果
      debounceResult: '',

      exampleTop: 0
    }
  },
  computed: {
    // 子组件的结果
    subComponentResult() {
      return this.subComponentResults[this.activeTab]
    },
    // 应用到预览上的CSS
    exampleCss() {
      return this.debounceResult.replace(/^body\b/gm, '#fakebody')
    }
  },
  watch: {
    subComponentResult(val) {
      this.inputResult = val
    },
    inputResult: _.debounce(function(val) {
      this.debounceResult = val
    }, 500)
  },
  mounted() {
    this.debounceResult = this.inputResult = this.subComponentResult

    this.$refs.renderer.addMessages(EXAMPLE_MESSAGES)

    this.$parent.$el.addEventListener('scroll', this.onParentScroll)
  },
  beforeDestroy() {
    this.$parent.$el.removeEventListener('scroll', this.onParentScroll)
  },
  methods: {
    onParentScroll(event) {
      if (document.body.clientWidth <= 992) {
        this.exampleTop = 0
      } else {
        this.exampleTop = event.target.scrollTop
      }
    },
    async playAnimation() {
      this.$refs.renderer.clearMessages()
      await this.$nextTick()
      this.$refs.renderer.addMessages(EXAMPLE_MESSAGES)
    },
    copyResult() {
      this.$refs.result.select()
      document.execCommand('Copy')
    },
    resetConfig() {
      this.$refs[this.activeTab].resetConfig()
      this.inputResult = this.subComponentResult
    }
  }
}
</script>

<style scoped>
#example-container {
  position: relative;
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

  -moz-background-size: 32px 32px;
  background-size: 32px 32px;
  -webkit-background-size: 32px 32px;

  background-position: 0 0, 16px 0, 16px -16px, 0px 16px;

  padding: 25px;

  resize: both;
  overflow: hidden;
}

#fakebody {
  outline: 1px #999 dashed;
  height: 100%;
}
</style>
