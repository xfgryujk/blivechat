<template>
  <div>
    <h1>{{ $t('help.help') }}</h1>
    <p>{{ $t('help.p1') }}</p>
    <p class="img-container"><el-image fit="scale-down" src="/static/img/tutorial/tutorial-1.png"></el-image></p>
    <p>{{ $t('help.p2') }}</p>
    <p class="img-container large-img"><el-image fit="scale-down" src="/static/img/tutorial/tutorial-2.png"></el-image></p>
    <p>{{ $t('help.p3') }}</p>
    <p class="img-container large-img"><el-image fit="scale-down" src="/static/img/tutorial/tutorial-3.png"></el-image></p>
    <p>{{ $t('help.p4') }}</p>
    <p class="img-container"><el-image fit="scale-down" src="/static/img/tutorial/tutorial-4.png"></el-image></p>
    <p>{{ $t('help.p5') }}</p>
    <p class="img-container large-img"><el-image fit="scale-down" src="/static/img/tutorial/tutorial-5.png"></el-image></p>
    <p><br><br><br><br><br><br><br><br>--------------------------------------------------------------------------------------------------------</p>
    <p>喜欢的话可以推荐给别人，专栏求支持_(:з」∠)_ <a href="https://www.bilibili.com/read/cv4594365" target="_blank">https://www.bilibili.com/read/cv4594365</a></p>
    <p>配置官方翻译接口傻瓜式教程 <a href="https://www.bilibili.com/read/cv14663633" target="_blank">https://www.bilibili.com/read/cv14663633</a>。注意必须下载到本地才能改后台配置，本地使用方法看 <a href="https://github.com/xfgryujk/blivechat#%E4%BD%BF%E7%94%A8%E6%96%B9%E6%B3%95" target="_blank">项目地址中的使用方法说明</a></p>
  </div>
</template>

<script>
export default {
  name: 'Help'
}
</script>

<style scoped>
.img-container {
  text-align: center;
}

.img-container.large-img .el-image {
  height: 80vh;
}
</style>
