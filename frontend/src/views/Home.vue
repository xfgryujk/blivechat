<template>
  <el-form :model="form" ref="form" label-width="150px" :rules="{
    roomId: [
      {required: true, message: '房间ID不能为空', trigger: 'blur'},
      {type: 'integer', min: 1, message: '房间ID必须为正整数', trigger: 'blur'}
    ]
  }">
    <el-tabs>
      <el-tab-pane label="常规">
        <el-form-item label="房间ID" required prop="roomId">
          <el-input v-model.number="form.roomId" type="number" min="1"></el-input>
        </el-form-item>
        <el-form-item label="最低显示礼物价格" prop="minGiftPrice">
          <el-input v-model.number="form.minGiftPrice" type="number" min="0"></el-input>
        </el-form-item>
        <el-form-item label="合并相似弹幕" prop="mergeSimilarDanmaku">
          <el-switch v-model="form.mergeSimilarDanmaku"></el-switch>
        </el-form-item>
      </el-tab-pane>

      <el-tab-pane label="屏蔽">
        <el-form-item label="礼物弹幕" prop="blockGiftDanmaku">
          <el-switch v-model="form.blockGiftDanmaku"></el-switch>
        </el-form-item>
        <el-form-item label="用户等级低于" prop="blockLevel">
          <el-slider v-model="form.blockLevel" show-input :min="0" :max="60"></el-slider>
        </el-form-item>
        <el-form-item label="非正式会员" prop="blockNewbie">
          <el-switch v-model="form.blockNewbie"></el-switch>
        </el-form-item>
        <el-form-item label="未绑定手机用户" prop="blockNotMobileVerified">
          <el-switch v-model="form.blockNotMobileVerified"></el-switch>
        </el-form-item>
        <el-form-item label="屏蔽关键词" prop="blockKeywords">
          <el-input v-model="form.blockKeywords" type="textarea" :rows="5" placeholder="一行一个"></el-input>
        </el-form-item>
        <el-form-item label="屏蔽用户" prop="blockUsers">
          <el-input v-model="form.blockUsers" type="textarea" :rows="5" placeholder="一行一个"></el-input>
        </el-form-item>
      </el-tab-pane>

      <el-tab-pane label="样式">
        <el-form-item label="CSS" prop="css">
          <el-input v-model="form.css" type="textarea" :rows="20"></el-input>
        </el-form-item>
      </el-tab-pane>
    </el-tabs>
    
    <el-divider></el-divider>
    <el-form-item label="房间URL" v-show="roomUrl">
      <el-input ref="roomUrlInput" readonly :value="roomUrl" style="width: calc(100% - 6em); margin-right: 1em;"></el-input>
      <el-button type="primary" @click="copyUrl">复制</el-button>
    </el-form-item>
    <el-form-item>
      <el-button type="primary" @click="saveConfig">保存配置</el-button>
      <el-button type="primary" :disabled="!roomUrl" @click="enterRoom">进入房间</el-button>
    </el-form-item>
  </el-form>
</template>

<script>
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
          this.$message.error('保存失败：' + e)
          return
        }
        this.$message({message: '保存成功', type: 'success'})

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
    }
  }
}
</script>

<style scoped>
.el-form {
  max-width: 800px;
}
</style>
