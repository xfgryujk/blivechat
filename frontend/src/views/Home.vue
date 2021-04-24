<template>
  <div>
    <p>
      <el-form :model="form" ref="form" label-width="150px" :rules="{
        roomId: [
          {required: true, message: $t('home.roomIdEmpty'), trigger: 'blur'},
          {type: 'integer', min: 1, message: $t('home.roomIdInteger'), trigger: 'blur'}
        ]
      }">
        <el-tabs type="border-card">
          <el-tab-pane :label="$t('home.general')">
            <el-form-item :label="$t('home.roomId')" required prop="roomId">
              <el-input v-model.number="form.roomId" type="number" min="1"></el-input>
            </el-form-item>
            <el-row :gutter="20">
              <el-col :xs="24" :sm="8">
                <el-form-item :label="$t('home.showDanmaku')">
                  <el-switch v-model="form.showDanmaku"></el-switch>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="8">
                <el-form-item :label="$t('home.showGift')">
                  <el-switch v-model="form.showGift"></el-switch>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="8">
                <el-form-item :label="$t('home.showGiftName')">
                  <el-switch v-model="form.showGiftName"></el-switch>
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :xs="24" :sm="8">
                <el-form-item :label="$t('home.mergeSimilarDanmaku')">
                  <el-switch v-model="form.mergeSimilarDanmaku"></el-switch>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="8">
                <el-form-item :label="$t('home.mergeGift')">
                  <el-switch v-model="form.mergeGift"></el-switch>
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :xs="24" :sm="8">
                <el-form-item :label="$t('home.minGiftPrice')">
                  <el-input v-model.number="form.minGiftPrice" type="number" min="0"></el-input>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="8">
                <el-form-item :label="$t('home.maxNumber')">
                  <el-input v-model.number="form.maxNumber" type="number" min="1"></el-input>
                </el-form-item>
              </el-col>
            </el-row>
          </el-tab-pane>

          <el-tab-pane :label="$t('home.block')">
            <el-row :gutter="20">
              <el-col :xs="24" :sm="8">
                <el-form-item :label="$t('home.giftDanmaku')">
                  <el-switch v-model="form.blockGiftDanmaku"></el-switch>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="8">
                <el-form-item :label="$t('home.informalUser')">
                  <el-switch v-model="form.blockNewbie"></el-switch>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="8">
                <el-form-item :label="$t('home.unverifiedUser')">
                  <el-switch v-model="form.blockNotMobileVerified"></el-switch>
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :xs="24" :sm="12">
                <el-form-item :label="$t('home.blockLevel')">
                  <el-slider v-model="form.blockLevel" show-input :min="0" :max="60"></el-slider>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="12">
                <el-form-item :label="$t('home.blockMedalLevel')">
                  <el-slider v-model="form.blockMedalLevel" show-input :min="0" :max="40"></el-slider>
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item :label="$t('home.blockKeywords')">
              <el-input v-model="form.blockKeywords" type="textarea" :rows="5" :placeholder="$t('home.onePerLine')"></el-input>
            </el-form-item>
            <el-form-item :label="$t('home.blockUsers')">
              <el-input v-model="form.blockUsers" type="textarea" :rows="5" :placeholder="$t('home.onePerLine')"></el-input>
            </el-form-item>
          </el-tab-pane>

          <el-tab-pane :label="$t('home.advanced')">
            <el-row :gutter="20">
              <el-col :xs="24" :sm="8">
                <el-form-item :label="$t('home.relayMessagesByServer')">
                  <el-switch v-model="form.relayMessagesByServer"></el-switch>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="8">
                <el-form-item :label="$t('home.autoTranslate')">
                  <el-switch v-model="form.autoTranslate" :disabled="!serverConfig.enableTranslate || !form.relayMessagesByServer"></el-switch>
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item :label="$t('home.giftUsernamePronunciation')">
              <el-radio-group v-model="form.giftUsernamePronunciation">
                <el-radio label="">{{$t('home.dontShow')}}</el-radio>
                <el-radio label="pinyin">{{$t('home.pinyin')}}</el-radio>
                <el-radio label="kana">{{$t('home.kana')}}</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-tab-pane>
        </el-tabs>
      </el-form>
    </p>

    <p>
      <el-card>
        <el-form :model="form" label-width="150px">
          <el-form-item :label="$t('home.roomUrl')">
            <el-input ref="roomUrlInput" readonly :value="obsRoomUrl" style="width: calc(100% - 8em); margin-right: 1em;"></el-input>
            <el-button type="primary" @click="copyUrl">{{$t('home.copy')}}</el-button>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :disabled="!roomUrl" @click="enterRoom">{{$t('home.enterRoom')}}</el-button>
            <el-button :disabled="!roomUrl" @click="enterTestRoom">{{$t('home.enterTestRoom')}}</el-button>
            <el-button @click="exportConfig">{{$t('home.exportConfig')}}</el-button>
            <el-button @click="importConfig">{{$t('home.importConfig')}}</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </p>
  </div>
</template>

<script>
import _ from 'lodash'
import axios from 'axios'
import download from 'downloadjs'

import {mergeConfig} from '@/utils'
import * as chatConfig from '@/api/chatConfig'

export default {
  name: 'Home',
  data() {
    return {
      serverConfig: {
        enableTranslate: true,
        loaderUrl: ''
      },
      form: {
        roomId: parseInt(window.localStorage.roomId || '1'),
        ...chatConfig.getLocalConfig()
      }
    }
  },
  computed: {
    roomUrl() {
      return this.getRoomUrl(false)
    },
    obsRoomUrl() {
      if (this.roomUrl === '') {
        return ''
      }
      if (this.serverConfig.loaderUrl === '') {
        return this.roomUrl
      }
      let url = new URL(this.serverConfig.loaderUrl)
      url.searchParams.append('url', this.roomUrl)
      return url.href
    }
  },
  watch: {
    roomUrl: _.debounce(function() {
      window.localStorage.roomId = this.form.roomId
      chatConfig.setLocalConfig(this.form)
    }, 500)
  },
  mounted() {
    this.updateServerConfig()
  },
  methods: {
    async updateServerConfig() {
      try {
        this.serverConfig = (await axios.get('/api/server_info')).data.config
      } catch (e) {
        this.$message.error('Failed to fetch server information: ' + e)
      }
    },
    enterRoom() {
      window.open(this.roomUrl, `room ${this.form.roomId}`, 'menubar=0,location=0,scrollbars=0,toolbar=0,width=600,height=600')
    },
    enterTestRoom() {
      window.open(this.getRoomUrl(true), 'test room', 'menubar=0,location=0,scrollbars=0,toolbar=0,width=600,height=600')
    },
    getRoomUrl(isTestRoom) {
      if (isTestRoom && this.form.roomId === '') {
        return ''
      }
      let query = {...this.form}
      delete query.roomId
      let resolved
      if (isTestRoom) {
        resolved = this.$router.resolve({name: 'test_room', query})
      } else {
        resolved = this.$router.resolve({name: 'room', params: {roomId: this.form.roomId}, query})
      }
      return `${window.location.protocol}//${window.location.host}${resolved.href}`
    },
    copyUrl() {
      this.$refs.roomUrlInput.select()
      document.execCommand('Copy')
    },
    exportConfig() {
      let cfg = mergeConfig(this.form, chatConfig.DEFAULT_CONFIG)
      download(JSON.stringify(cfg, null, 2), 'blivechat.json', 'application/json')
    },
    importConfig() {
      let input = document.createElement('input')
      input.type = 'file'
      input.accept = 'application/json'
      input.onchange = () => {
        let reader = new window.FileReader()
        reader.onload = () => {
          let cfg
          try {
            cfg = JSON.parse(reader.result)
          } catch (e) {
            this.$message.error(this.$t('home.failedToParseConfig') + e)
            return
          }
          cfg = mergeConfig(cfg, chatConfig.DEFAULT_CONFIG)
          this.form = {roomId: this.form.roomId, ...cfg}
        }
        reader.readAsText(input.files[0])
      }
      input.click()
    }
  }
}
</script>
