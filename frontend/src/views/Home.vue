<template>
  <el-form :model="form" ref="form" label-width="150px" :rules="{
    roomId: [
      {required: true, message: $t('home.roomIdEmpty'), trigger: 'blur'},
      {type: 'integer', min: 1, message: $t('home.roomIdInteger'), trigger: 'blur'}
    ]
  }">
    <el-tabs>
      <el-tab-pane :label="$t('home.general')">
        <el-form-item :label="$t('home.roomId')" required prop="roomId">
          <el-input v-model.number="form.roomId" type="number" min="1"></el-input>
        </el-form-item>
        <el-form-item :label="$t('home.showDanmaku')">
          <el-switch v-model="form.showDanmaku"></el-switch>
        </el-form-item>
        <el-form-item :label="$t('home.showGift')">
          <el-switch v-model="form.showGift"></el-switch>
        </el-form-item>
        <el-form-item :label="$t('home.mergeSimilarDanmaku')">
          <el-switch v-model="form.mergeSimilarDanmaku"></el-switch>
        </el-form-item>
        <el-form-item :label="$t('home.minGiftPrice')">
          <el-input v-model.number="form.minGiftPrice" type="number" min="0"></el-input>
        </el-form-item>
        <el-form-item :label="$t('home.maxSpeed')">
          <el-input v-model.number="form.maxSpeed" type="number" min="0"></el-input>
        </el-form-item>
        <el-form-item :label="$t('home.maxNumber')">
          <el-input v-model.number="form.maxNumber" type="number" min="1"></el-input>
        </el-form-item>
      </el-tab-pane>

      <el-tab-pane :label="$t('home.block')">
        <el-form-item :label="$t('home.giftDanmaku')">
          <el-switch v-model="form.blockGiftDanmaku"></el-switch>
        </el-form-item>
        <el-form-item :label="$t('home.blockLevel')">
          <el-slider v-model="form.blockLevel" show-input :min="0" :max="60"></el-slider>
        </el-form-item>
        <el-form-item :label="$t('home.informalUser')">
          <el-switch v-model="form.blockNewbie"></el-switch>
        </el-form-item>
        <el-form-item :label="$t('home.unverifiedUser')">
          <el-switch v-model="form.blockNotMobileVerified"></el-switch>
        </el-form-item>
        <el-form-item :label="$t('home.blockKeywords')">
          <el-input v-model="form.blockKeywords" type="textarea" :rows="5" :placeholder="$t('home.onePerLine')"></el-input>
        </el-form-item>
        <el-form-item :label="$t('home.blockUsers')">
          <el-input v-model="form.blockUsers" type="textarea" :rows="5" :placeholder="$t('home.onePerLine')"></el-input>
        </el-form-item>
        <el-form-item :label="$t('home.blockMedalLevel')">
          <el-slider v-model="form.blockMedalLevel" show-input :min="0" :max="20"></el-slider>
        </el-form-item>
      </el-tab-pane>

      <el-tab-pane :label="$t('home.style')">
        <el-form-item label="CSS">
          <el-input v-model="form.css" type="textarea" :rows="20"></el-input>
        </el-form-item>
      </el-tab-pane>
    </el-tabs>
    
    <el-divider></el-divider>
    <el-form-item :label="$t('home.roomUrl')" v-show="roomUrl">
      <el-input ref="roomUrlInput" readonly :value="roomUrl" style="width: calc(100% - 6em); margin-right: 1em;"></el-input>
      <el-button type="primary" @click="copyUrl">{{$t('home.copy')}}</el-button>
    </el-form-item>
    <el-form-item>
      <el-button type="primary" @click="saveConfig">{{$t('home.saveConfig')}}</el-button>
      <el-button type="primary" :disabled="!roomUrl" @click="enterRoom">{{$t('home.enterRoom')}}</el-button>
      <el-button type="primary" @click="exportConfig">{{$t('home.exportConfig')}}</el-button>
      <el-button type="primary" @click="importConfig">{{$t('home.importConfig')}}</el-button>
    </el-form-item>
  </el-form>
</template>

<script>
import download from 'downloadjs'

import {mergeConfig} from '@/utils'
import config from '@/api/config'

export default {
  name: 'Home',
  data() {
    return {
      form: {
        roomId: parseInt(window.localStorage.roomId || '1'),
        ...config.getLocalConfig()
      },
      roomUrl: ''
    }
  },
  methods: {
    saveConfig() {
      this.$refs.form.validate(async valid => {
        if (!valid) {
          return
        }
        window.localStorage.roomId = this.form.roomId
        config.setLocalConfig(this.form)

        try {
          if (window.localStorage.configId) {
            try {
              await config.setRemoteConfig(window.localStorage.configId, this.form)
            } catch (e) { // 404
              window.localStorage.configId = (await config.createRemoteConfig(this.form)).id
            }
          } else {
            window.localStorage.configId = (await config.createRemoteConfig(this.form)).id
          }
        } catch (e) {
          this.$message.error(this.$t('home.failedToSave') + e)
          return
        }
        this.$message({message: this.$t('home.successfullySaved'), type: 'success'})

        let resolved = this.$router.resolve({name: 'room', params: {roomId: this.form.roomId},
          query: {config_id: window.localStorage.configId}})
        this.roomUrl = `http://${window.location.host}${resolved.href}`
      })
    },
    enterRoom() {
      window.open(this.roomUrl, `room ${this.form.roomId}`, 'menubar=0,location=0,scrollbars=0,toolbar=0,width=600,height=600')
    },
    copyUrl() {
      this.$refs.roomUrlInput.select()
      document.execCommand('Copy')
    },
    exportConfig() {
      let cfg = mergeConfig(this.form, config.DEFAULT_CONFIG)
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
          cfg = mergeConfig(cfg, config.DEFAULT_CONFIG)
          this.form = {roomId: this.form.roomId, ...cfg}
        }
        reader.readAsText(input.files[0])
      }
      input.click()
    }
  }
}
</script>

<style scoped>
.el-form {
  max-width: 800px;
}
</style>
