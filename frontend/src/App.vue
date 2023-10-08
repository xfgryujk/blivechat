<template>
  <div id="app">
    <router-view></router-view>
  </div>
</template>

<script>
export default {
  name: 'app'
}
</script>

<style>
html {
  font-family: "Helvetica Neue", Helvetica, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "\5FAE \8F6F \96C5 \9ED1 ", "微软雅黑", Arial, sans-serif;
}

html, body, #app {
  height: 100%;
}

body {
  margin: 0;
  background-color: #f6f8fa;
}

a, a:focus, a:hover {
  text-decoration: none;
}
</style>
