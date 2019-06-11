<template>
  <el-scrollbar wrap-class="scrollbar-wrapper">
    <el-menu
      router
      background-color="#304156"
      text-color="#bfcbd9"
      active-text-color="rgb(64, 158, 255)"
      :default-active="$route.path"
    >
      <el-menu-item index="/">
        <i class="el-icon-s-home"></i>首页
      </el-menu-item>
      <el-menu-item :index="$router.resolve({name: 'stylegen'}).href">
        <i class="el-icon-brush"></i>样式生成器
      </el-menu-item>
      <a href="https://github.com/xfgryujk/blivechat" target="_blank">
        <el-menu-item>
          <i class="el-icon-share"></i>项目地址
        </el-menu-item>
      </a>
    </el-menu>
  </el-scrollbar>
</template>

<script>
export default {
  name: 'Sidebar'
}
</script>

<style>
.el-scrollbar {
  height: 100%;
}

.scrollbar-wrapper {
  overflow-x: hidden !important;
}

.scrollbar-wrapper .el-menu {
  border: none;
}
</style>
