<template>
  <yt-img-shadow class="no-transition" :height="height" :width="width" style="background-color: transparent;" loaded>
    <img id="img" class="style-scope yt-img-shadow" alt="" :height="height" :width="width" :src="imgUrl">
  </yt-img-shadow>
</template>

<script>
export default {
  name: 'ImgShadow',
  props: {
    imgUrl: String,
    height: String,
    width: String
  }
}
</script>

<style src="@/assets/css/youtube/yt-img-shadow.css"></style>
