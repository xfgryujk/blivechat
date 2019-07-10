import Vue from 'vue'
import VueRouter from 'vue-router'
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
import VueI18n from 'vue-i18n'
import axios from 'axios'

import App from './App.vue'
import Layout from './layout'
import Home from './views/Home.vue'
import StyleGenerator from './views/StyleGenerator'
import Room from './views/Room.vue'
import NotFound from './views/NotFound.vue'

import zh from './lang/zh'
import ja from './lang/ja'
import en from './lang/en'

if (process.env.NODE_ENV === 'development') {
  // 开发时使用localhost:12450
  axios.defaults.baseURL = 'http://localhost:12450'
}

Vue.use(VueRouter)
Vue.use(ElementUI)
Vue.use(VueI18n)

Vue.config.ignoredElements = [
  /^yt-/
]

const router = new VueRouter({
  mode: 'history',
  routes: [
    {
      path: '/',
      component: Layout,
      children: [
        {path: '', component: Home},
        {path: 'stylegen', name: 'stylegen', component: StyleGenerator}
      ]
    },
    {path: '/room/:roomId', name: 'room', component: Room},
    {path: '*', component: NotFound}
  ]
})

let locale = window.localStorage.lang
if (!locale) {
  let lang = navigator.language
  if (lang.startsWith('zh')) {
    locale = 'zh'
  } else if (lang.startsWith('ja')) {
    locale = 'ja'
  } else {
    locale = 'en'
  }
}
const i18n = new VueI18n({
  locale,
  fallbackLocale: 'en',
  messages: {
    zh, ja, en
  }
})

new Vue({
  render: h => h(App),
  router,
  i18n
}).$mount('#app')
