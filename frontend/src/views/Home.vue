<template>
  <div>
    <el-form :model="form" ref="form" label-width="100px" :rules="{
      roomId: [
        {required: true, message: '房间ID不能为空', trigger: 'blur'},
        {type: 'integer', min: 1, message: '房间ID必须为正整数', trigger: 'blur'}
      ]
    }">
      <el-form-item label="房间ID" required prop="roomId">
        <el-input v-model.number="form.roomId" type="number" min="1"></el-input>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="enter">进入</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
export default {
  name: 'Home',
  data() {
    return {
      form: {
        roomId: window.localStorage.roomId || 1
      }
    }
  },
  methods: {
    enter() {
      this.$refs.form.validate(valid => {
        if (!valid) {
          return
        }
        window.localStorage.roomId = this.form.roomId
        this.$router.push({name: 'room', params: {roomId: this.form.roomId}})
      })
    }
  }
}
</script>
