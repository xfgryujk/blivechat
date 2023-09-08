<template>
  <yt-img-shadow class="no-transition" :height="height" :width="width" style="background-color: transparent;" loaded>
    <img id="img" class="style-scope yt-img-shadow" alt="" :height="height" :width="width" :src="showImgUrl" @error="onLoadError">
  </yt-img-shadow>
</template>

<script>
import * as chat from '@/api/chat'

export default {
  name: 'ImgShadow',
  props: {
    imgUrl: String,
    height: String,
    width: String
  },
  data() {
    return {
      showImgUrl: this.imgUrl
    }
  },
  watch: {
    imgUrl(val) {
      this.showImgUrl = val
    }
  },
  methods: {
    onLoadError() {
      if (this.showImgUrl !== chat.DEFAULT_AVATAR_URL) {
        this.showImgUrl = chat.DEFAULT_AVATAR_URL
      }
    }
  }
}
</script>

<style src="@/assets/css/youtube/yt-img-shadow.css"></style>
