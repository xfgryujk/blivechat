<template>
  <div>
    <p>
      <el-form :model="form" ref="form" label-width="150px">
        <el-tabs type="border-card">
          <el-tab-pane :label="$t('home.general')">
            <el-form-item :label="$t('home.room')" required :prop="form.roomKeyType === 1 ? 'roomId' : 'authCode'">
              <el-row>
                <el-col :span="6">
                  <el-select v-model="form.roomKeyType" style="width: 100%">
                    <el-option :label="$t('home.authCode')" :value="2"></el-option>
                    <el-option :label="$t('home.roomId')" :value="1"></el-option>
                  </el-select>
                </el-col>
                <el-col :span="18">
                  <el-input v-if="form.roomKeyType === 1"
                    v-model.number="form.roomId" type="number" min="1" :rules="[
                      {required: true, message: $t('home.roomIdEmpty'), trigger: 'blur'},
                      {type: 'integer', min: 1, message: $t('home.roomIdInteger'), trigger: 'blur'}
                    ]"
                  ></el-input>
                  <el-input v-else
                    v-model.number="form.authCode" :rules="[
                      {required: true, message: $t('home.authCodeEmpty'), trigger: 'blur'}
                    ]"
                  ></el-input>
                </el-col>
              </el-row>
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

          <el-tab-pane :label="$t('home.emoticon')">
            <el-table :data="form.emoticons">
              <el-table-column prop="keyword" :label="$t('home.emoticonKeyword')" width="170">
                <template slot-scope="scope">
                  <el-input v-model="scope.row.keyword"></el-input>
                </template>
              </el-table-column>
              <el-table-column prop="url" :label="$t('home.emoticonUrl')">
                <template slot-scope="scope">
                  <el-input v-model="scope.row.url"></el-input>
                </template>
              </el-table-column>
              <el-table-column :label="$t('home.operation')" width="170">
                <template slot-scope="scope">
                  <el-button-group>
                    <el-button type="primary" icon="el-icon-upload2" :disabled="!serverConfig.enableUploadFile"
                      @click="uploadEmoticon(scope.row)"
                    ></el-button>
                    <el-button type="danger" icon="el-icon-minus" @click="delEmoticon(scope.$index)"></el-button>
                  </el-button-group>
                </template>
              </el-table-column>
            </el-table>
            <p>
              <el-button type="primary" icon="el-icon-plus" @click="addEmoticon">{{$t('home.addEmoticon')}}</el-button>
            </p>
          </el-tab-pane>
        </el-tabs>
      </el-form>
    </p>

    <p>
      <el-card>
        <el-form :model="form" label-width="150px">
          <el-form-item :label="$t('home.roomUrl')">
            <el-input ref="roomUrlInput" readonly :value="obsRoomUrl" style="width: calc(100% - 8em); margin-right: 1em;"></el-input>
            <el-button type="primary" icon="el-icon-copy-document" @click="copyUrl"></el-button>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :disabled="!roomUrl" @click="enterRoom">{{$t('home.enterRoom')}}</el-button>
            <el-button @click="enterTestRoom">{{$t('home.enterTestRoom')}}</el-button>
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
import download from 'downloadjs'

import { mergeConfig } from '@/utils'
import * as mainApi from '@/api/main'
import * as chatConfig from '@/api/chatConfig'

export default {
  name: 'Home',
  data() {
    return {
      serverConfig: {
        enableTranslate: true,
        enableUploadFile: true,
        loaderUrl: ''
      },
      form: {
        ...chatConfig.getLocalConfig(),
        roomKeyType: parseInt(window.localStorage.roomKeyType || '2'),
        roomId: parseInt(window.localStorage.roomId || '1'),
        authCode: window.localStorage.authCode || '',
      }
    }
  },
  computed: {
    roomKeyValue() {
      if (this.form.roomKeyType === 1) {
        return this.form.roomId
      } else {
        return this.form.authCode
      }
    },
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
      window.localStorage.roomKeyType = this.form.roomKeyType
      window.localStorage.roomId = this.form.roomId
      window.localStorage.authCode = this.form.authCode
      chatConfig.setLocalConfig(this.form)
    }, 500)
  },
  mounted() {
    this.updateServerConfig()
  },
  methods: {
    async updateServerConfig() {
      try {
        this.serverConfig = (await mainApi.getServerInfo()).config
      } catch (e) {
        this.$message.error(`Failed to fetch server information: ${e}`)
        throw e
      }
    },

    addEmoticon() {
      this.form.emoticons.push({
        keyword: '[Kappa]',
        url: ''
      })
    },
    delEmoticon(index) {
      this.form.emoticons.splice(index, 1)
    },
    uploadEmoticon(emoticon) {
      let input = document.createElement('input')
      input.type = 'file'
      input.accept = 'image/png, image/jpeg, image/jpg, image/gif'
      input.onchange = async() => {
        let file = input.files[0]
        if (file.size > 1024 * 1024) {
          this.$message.error(this.$t('home.emoticonFileTooLarge'))
          return
        }

        let res
        try {
          res = await mainApi.uploadEmoticon(file)
        } catch (e) {
          this.$message.error(`Failed to upload: ${e}`)
          throw e
        }
        emoticon.url = res.url
      }
      input.click()
    },

    enterRoom() {
      window.open(this.roomUrl, `room ${this.roomKeyValue}`, 'menubar=0,location=0,scrollbars=0,toolbar=0,width=600,height=600')
    },
    enterTestRoom() {
      window.open(this.getRoomUrl(true), 'test room', 'menubar=0,location=0,scrollbars=0,toolbar=0,width=600,height=600')
    },
    getRoomUrl(isTestRoom) {
      if (!isTestRoom && !this.roomKeyValue) {
        return ''
      }

      let query = {
        ...this.form,
        emoticons: JSON.stringify(this.form.emoticons),
        lang: this.$i18n.locale
      }
      delete query.roomId
      delete query.authCode

      let resolved
      if (isTestRoom) {
        resolved = this.$router.resolve({ name: 'test_room', query })
      } else {
        resolved = this.$router.resolve({ name: 'room', params: { roomKeyValue: this.roomKeyValue }, query })
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
          this.importConfigFromObj(cfg)
        }
        reader.readAsText(input.files[0])
      }
      input.click()
    },
    importConfigFromObj(cfg) {
      cfg = mergeConfig(cfg, chatConfig.deepCloneDefaultConfig())
      chatConfig.sanitizeConfig(cfg)
      this.form = {
        ...cfg,
        roomKeyType: this.form.roomKeyType,
        roomId: this.form.roomId,
        authCode: this.form.authCode
      }
    }
  }
}
</script>
