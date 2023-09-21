<template>
  <div>
    <p>
      <el-form :model="form" ref="form" label-width="150px">
        <el-tabs type="border-card">
          <el-tab-pane :label="$t('home.general')">
            <template v-if="form.roomKeyType === 1">
              <p>
                <el-alert :title="$t('home.useAuthCodeWarning')" type="warning" show-icon :closable="false"></el-alert>
              </p>
              <el-form-item
                :label="$t('home.room')" prop="roomId" :rules="[
                  { required: true, message: $t('home.roomIdEmpty') },
                  { type: 'integer', min: 1, message: $t('home.roomIdInteger') }
                ]"
              >
                <el-row>
                  <el-col :span="6">
                    <el-select v-model="form.roomKeyType" style="width: 100%">
                      <el-option :label="$t('home.authCode')" :value="2"></el-option>
                      <el-option :label="$t('home.roomId')" :value="1"></el-option>
                    </el-select>
                  </el-col>
                  <el-col :span="18">
                    <el-input v-model.number="form.roomId" type="number" min="1"></el-input>
                  </el-col>
                </el-row>
              </el-form-item>
            </template>

            <el-form-item v-else-if="form.roomKeyType === 2"
              :label="$t('home.room')" prop="authCode" :rules="[
                { required: true, message: $t('home.authCodeEmpty') },
                { pattern: /^[0-9A-Z]{12,14}$/, message: $t('home.authCodeFormatError') }
              ]"
            >
              <el-row>
                <el-col :span="6">
                  <el-select v-model="form.roomKeyType" style="width: 100%">
                    <el-option :label="$t('home.authCode')" :value="2"></el-option>
                    <el-option :label="$t('home.roomId')" :value="1"></el-option>
                  </el-select>
                </el-col>
                <el-col :span="18">
                  <el-tooltip placement="top-start">
                    <div slot="content">
                      <!-- 不知道为什么router-link获取不到$router，还是用el-link了，不过会有一次丑陋的刷新 -->
                      <el-link
                        type="primary" :href="$router.resolve({ name: 'help' }).href"
                      >{{ $t('home.howToGetAuthCode') }}</el-link>
                    </div>
                    <el-input v-model.number="form.authCode"></el-input>
                  </el-tooltip>
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
          <p v-if="obsRoomUrl.length > 1024">
            <el-alert :title="$t('home.urlTooLong')" type="warning" show-icon :closable="false"></el-alert>
          </p>
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
      },
      // 因为$refs.form.validate是异步的所以不能直接用计算属性
      // getUnvalidatedRoomUrl -> unvalidatedRoomUrl -> updateRoomUrl -> roomUrl
      roomUrl: '',
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
    unvalidatedRoomUrl() {
      return this.getUnvalidatedRoomUrl(false)
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
    unvalidatedRoomUrl: 'updateRoomUrl',
    roomUrl: _.debounce(function() {
      window.localStorage.roomKeyType = this.form.roomKeyType
      window.localStorage.roomId = this.form.roomId
      window.localStorage.authCode = this.form.authCode
      chatConfig.setLocalConfig(this.form)
    }, 500)
  },
  mounted() {
    this.updateServerConfig()
    this.updateRoomUrl()
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
    async updateRoomUrl() {
      // 防止切换roomKeyType时校验的还是老规则
      await this.$nextTick()
      try {
        await this.$refs.form.validate()
      } catch {
        this.roomUrl = ''
        return
      }
      // 没有异步的校验规则，应该不需要考虑竞争条件
      this.roomUrl = this.unvalidatedRoomUrl
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
      window.open(this.getUnvalidatedRoomUrl(true), 'test room', 'menubar=0,location=0,scrollbars=0,toolbar=0,width=600,height=600')
    },
    getUnvalidatedRoomUrl(isTestRoom) {
      // 重要的字段放在前面，因为如果被截断就连接不了房间了
      let frontFields = {
        roomKeyType: this.form.roomKeyType
      }
      let backFields = {
        lang: this.$i18n.locale,
        emoticons: JSON.stringify(this.form.emoticons)
      }
      let ignoredNames = new Set(['roomId', 'authCode'])
      let query = { ...frontFields }
      for (let name in this.form) {
        if (!(name in frontFields || name in backFields || ignoredNames.has(name))) {
          query[name] = this.form[name]
        }
      }
      Object.assign(query, backFields)

      // 去掉和默认值相同的字段，缩短URL长度
      query = Object.fromEntries(Object.entries(query).filter(
        ([name, value]) => {
          let defaultValue = chatConfig.DEFAULT_CONFIG[name]
          if (defaultValue === undefined) {
            return true
          }
          if (typeof defaultValue === 'object') {
            defaultValue = JSON.stringify(defaultValue)
          }
          return value !== defaultValue
        }
      ))

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
