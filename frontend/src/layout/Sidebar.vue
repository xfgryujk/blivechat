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
        <i class="el-icon-s-home"></i>{{ $t('sidebar.home') }}
      </el-menu-item>
      <el-menu-item :index="$router.resolve({ name: 'stylegen' }).href">
        <i class="el-icon-brush"></i>{{ $t('sidebar.stylegen') }}
      </el-menu-item>
      <el-menu-item :index="$router.resolve({ name: 'help' }).href">
        <i class="el-icon-question"></i>{{ $t('sidebar.help') }}
      </el-menu-item>
      <el-menu-item :index="$router.resolve({ name: 'plugins' }).href">
        <i class="el-icon-magic-stick"></i>{{ $t('sidebar.plugins') }}
      </el-menu-item>
      <el-submenu index="1">
        <template slot="title">
          <i class="el-icon-link"></i>{{ $t('sidebar.links') }}
        </template>
        <a href="https://github.com/xfgryujk/blivechat" target="_blank">
          <el-menu-item>
            <i class="el-icon-share"></i>{{ $t('sidebar.projectAddress') }}
          </el-menu-item>
        </a>
        <a href="https://github.com/xfgryujk/blivechat/discussions" target="_blank">
          <el-menu-item>
            <i class="el-icon-s-comment"></i>{{ $t('sidebar.discussion') }}
          </el-menu-item>
        </a>
        <a href="https://github.com/xfgryujk/blivechat/wiki" target="_blank">
          <el-menu-item>
            <i class="el-icon-document"></i>{{ $t('sidebar.documentation') }}
          </el-menu-item>
        </a>
        <a href="https://play-live.bilibili.com/details/1694397161340" target="_blank">
          <el-menu-item>
            <i class="el-icon-s-goods"></i>{{ $t('sidebar.mall') }}
          </el-menu-item>
        </a>
        <a href="https://link.bilibili.com/p/center/index#/live-data/gift-list" target="_blank">
          <el-menu-item>
            <i class="el-icon-s-finance"></i>{{ $t('sidebar.giftRecordOfficial') }}
          </el-menu-item>
        </a>
      </el-submenu>
      <el-submenu index="2">
        <template slot="title">
          <i class="el-icon-chat-line-square"></i>Language
        </template>
        <el-menu-item v-for="locale in LOCALES" :key="locale.locale" @click="onSelectLanguage(locale.locale)">
          <template>{{ locale.name }}</template>
        </el-menu-item>
      </el-submenu>
    </el-menu>
  </el-scrollbar>
</template>

<script>
import * as i18n from '@/i18n'

export default {
  name: 'Sidebar',
  data() {
    return {
      LOCALES: [
        { locale: 'zh', name: '中文' },
        { locale: 'ja', name: '日本語' },
        { locale: 'en', name: 'English' }
      ]
    }
  },
  methods: {
    onSelectLanguage(locale) {
      i18n.setLocale(locale)
    }
  }
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
