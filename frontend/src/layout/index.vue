<template>
  <el-container class="app-wrapper" :class="{mobile: isMobile}">
    <div v-show="isMobile && !hideSidebar" class="drawer-bg" @click="hideSidebar = true"></div>
    <el-aside width="230px" class="sidebar-container" :class="{'hide-sidebar': hideSidebar}">
      <div class="logo-container">
        <router-link to="/">
          <img src="@/assets/img/logo.png" class="sidebar-logo">
          <h1 class="sidebar-title">blivechat</h1>
        </router-link>
      </div>
      <div class="version">
        v1.5.3
      </div>
      <sidebar></sidebar>
    </el-aside>
    <el-main>
      <el-button v-show="isMobile" class="menu-button" icon="el-icon-s-unfold" @click="hideSidebar = false"></el-button>
      <keep-alive>
        <router-view></router-view>
      </keep-alive>
    </el-main>
  </el-container>
</template>

<script>
import Sidebar from './Sidebar.vue'

export default {
  name: 'Layout',
  components: {
    Sidebar
  },
  data() {
    return {
      isMobile: false,
      hideSidebar: true
    }
  },
  mounted() {
    window.addEventListener('resize', this.onResize)
    this.onResize()
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.onResize)
  },
  methods: {
    onResize() {
      this.isMobile = document.body.clientWidth <= 992
    }
  }
}
</script>

<style>
html {
  font-family: "Helvetica Neue", Helvetica, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "\5FAE \8F6F \96C5 \9ED1 ", "微软雅黑", Arial, sans-serif;
}

html, body, #app, .app-wrapper, .sidebar-container {
  height: 100%;
}

body {
  margin: 0;
  background-color: #f6f8fa;
}

a, a:focus, a:hover {
  text-decoration: none;
}

.drawer-bg {
  background: #000;
  opacity: 0.3;
  width: 100%;
  top: 0;
  height: 100%;
  position: absolute;
  z-index: 999;
}

.sidebar-container {
  background-color: #304156;
  overflow: hidden;
}

.app-wrapper.mobile .sidebar-container {
  position: fixed;
  top: 0;
  left: 0;
  transition-duration: 0.3s;
  z-index: 1001;
}

.app-wrapper.mobile .sidebar-container.hide-sidebar {
  pointer-events: none;
  transition-duration: 0.3s;
  transform: translate3d(-230px, 0, 0);
}

.sidebar-container .logo-container {
  width: 100%;
  height: 50px;
  line-height: 50px;
  background: #2b2f3a;
  text-align: center;
}

.sidebar-container .logo-container .sidebar-logo {
  width: 32px;
  height: 32px;
  vertical-align: middle;
  margin-right: 12px;
}

.sidebar-container .logo-container .sidebar-title {
  display: inline-block;
  margin: 0;
  color: #fff;
  font-weight: 600;
  line-height: 50px;
  font-size: 14px;
  font-family: Avenir, Helvetica Neue, Arial, Helvetica, sans-serif;
  vertical-align: middle;
}

.sidebar-container .version {
  height: 30px;
  background: #2b2f3a;
  color: #aaa;
  font-weight: 600;
  line-height: 30px;
  font-size: 14px;
  vertical-align: middle;
  text-align: center;
}

.sidebar-container .is-horizontal {
  display: none;
}
</style>
