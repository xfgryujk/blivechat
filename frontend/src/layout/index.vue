<template>
  <el-container class="app-wrapper">
    <el-aside width="200px" class="sidebar-container">
      <div class="logo-container">
        <router-link to="/">
          <img src="@/assets/img/logo.png" class="sidebar-logo">
          <h1 class="sidebar-title">blivechat</h1>
        </router-link>
      </div>
      <sidebar></sidebar>
    </el-aside>
    <el-main>
      <router-view></router-view>
    </el-main>
  </el-container>
</template>

<script>
import Sidebar from './Sidebar.vue'

export default {
  name: 'Layout',
  components: {
    Sidebar
  }
}
</script>

<style>
html, body, #app, .app-wrapper, .sidebar-container {
  height: 100%;
}

body {
  margin: 0;
}

a, a:focus, a:hover {
  text-decoration: none;
}

.sidebar-container {
  background-color: #304156;
  overflow: hidden;
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

.sidebar-container .is-horizontal {
  display: none;
}
</style>
