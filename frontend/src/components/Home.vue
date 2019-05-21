<template>
  <div>
    房间ID：
    <input type="number" min="1" v-model="roomId" />
    <button @click="go">进入</button>
  </div>
</template>

<script>
export default {
  name: 'Home',
  data() {
    return {
      roomId: window.localStorage.roomId || '1'
    }
  },
  methods: {
    go() {
      window.localStorage.roomId = this.roomId
      this.$router.push({name: 'room', params: {roomId: this.roomId}})
    }
  }
}
</script>
