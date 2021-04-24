<template>
  <el-row :gutter="20">
    <el-col :sm="24" :md="16">
      <el-tabs v-model="activeTab">
        <el-tab-pane :label="$t('stylegen.legacy')" name="legacy">
          <legacy ref="legacy" v-model="subComponentResults.legacy"></legacy>
        </el-tab-pane>
        <el-tab-pane :label="$t('stylegen.lineLike')" name="lineLike">
          <line-like ref="lineLike" v-model="subComponentResults.lineLike"></line-like>
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
      <div :style="{position: 'relative', top: `${exampleTop}px`}">
        <el-form inline style="line-height: 40px">
          <el-form-item :label="$t('stylegen.playAnimation')" style="margin: 0">
            <el-switch v-model="playAnimation" @change="onPlayAnimationChange"></el-switch>
          </el-form-item>
          <el-form-item :label="$t('stylegen.backgrounds')" style="margin: 0 0 0 30px">
            <el-switch v-model="exampleBgLight" :active-text="$t('stylegen.light')" :inactive-text="$t('stylegen.dark')"></el-switch>
          </el-form-item>
        </el-form>
        <div id="example-container" :class="{light: exampleBgLight}">
          <div id="fakebody">
            <room ref="room"></room>
          </div>
        </div>
      </div>
    </el-col>
  </el-row>
</template>

<script>
import _ from 'lodash'

import Legacy from './Legacy'
import LineLike from './LineLike'
import Room from '@/views/Room'

export default {
  name: 'StyleGenerator',
  components: {
    Legacy, LineLike, Room
  },
  data() {
    let styleElement = document.createElement('style')
    document.head.appendChild(styleElement)
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

      styleElement,
      exampleTop: 0,
      playAnimation: true,
      exampleBgLight: false
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
    }, 500),
    exampleCss(val) {
      this.styleElement.innerText = val
    }
  },
  mounted() {
    this.debounceResult = this.inputResult = this.subComponentResult

    this.$parent.$el.addEventListener('scroll', this.onParentScroll)
  },
  beforeDestroy() {
    this.$parent.$el.removeEventListener('scroll', this.onParentScroll)

    document.head.removeChild(this.styleElement)
  },
  methods: {
    onParentScroll(event) {
      if (document.body.clientWidth <= 992) {
        this.exampleTop = 0
      } else {
        this.exampleTop = event.target.scrollTop
      }
    },
    onPlayAnimationChange(value) {
      if (value) {
        this.$refs.room.start()
      } else {
        this.$refs.room.stop()
      }
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
  height: calc(100vh - 150px);

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

#example-container.light {
  background-color: #ddd;
  background-image:
    -moz-linear-gradient(45deg, #eee 25%, transparent 25%),
    -moz-linear-gradient(-45deg, #eee 25%, transparent 25%),
    -moz-linear-gradient(45deg, transparent 75%, #eee 75%),
    -moz-linear-gradient(-45deg, transparent 75%, #eee 75%);
  background-image:
    -webkit-gradient(linear, 0 100%, 100% 0, color-stop(.25, #eee), color-stop(.25, transparent)),
    -webkit-gradient(linear, 0 0, 100% 100%, color-stop(.25, #eee), color-stop(.25, transparent)),
    -webkit-gradient(linear, 0 100%, 100% 0, color-stop(.75, transparent), color-stop(.75, #eee)),
    -webkit-gradient(linear, 0 0, 100% 100%, color-stop(.75, transparent), color-stop(.75, #eee));
}

#fakebody {
  outline: 1px #999 dashed;
  height: 100%;
}
</style>
