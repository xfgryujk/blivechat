<template>
  <div>
    <h1>{{$t('help.help')}}</h1>
    <p>{{$t('help.p1')}}</p>
    <p class="img-container"><el-image fit="scale-down" src="/static/img/tutorial/tutorial-1.png"></el-image></p>
    <p>{{$t('help.p2')}}</p>
    <p class="img-container large-img"><el-image fit="scale-down" src="/static/img/tutorial/tutorial-2.png"></el-image></p>
    <p>{{$t('help.p3')}}</p>
    <p class="img-container large-img"><el-image fit="scale-down" src="/static/img/tutorial/tutorial-3.png"></el-image></p>
    <p>{{$t('help.p4')}}</p>
    <p class="img-container"><el-image fit="scale-down" src="/static/img/tutorial/tutorial-4.png"></el-image></p>
    <p>{{$t('help.p5')}}</p>
    <p class="img-container large-img"><el-image fit="scale-down" src="/static/img/tutorial/tutorial-5.png"></el-image></p>
    <p><br><br><br><br><br><br><br><br>--------------------------------------------------------------------------------------------------------</p>
    <p>喜欢的话可以推荐给别人，专栏求支持_(:з」∠)_  <a href="https://www.bilibili.com/read/cv4594365" target="_blank">https://www.bilibili.com/read/cv4594365</a></p>
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
