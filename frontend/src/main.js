import Vue from 'vue'
import VueRouter from 'vue-router'
import VueI18n from 'vue-i18n'
import {
  Aside, Autocomplete, Badge, Button, Card, Col, ColorPicker, Container, Divider, Form, FormItem, Image,
  Input, Main, Menu, MenuItem, Message, Option, OptionGroup, Radio, RadioGroup, Row, Select, Scrollbar,
  Slider, Submenu, Switch, TabPane, Tabs, Tooltip
} from 'element-ui'
import axios from 'axios'

import App from './App.vue'
import Layout from './layout'
import Home from './views/Home.vue'
import StyleGenerator from './views/StyleGenerator'
import Help from './views/Help'
import Room from './views/Room.vue'
import NotFound from './views/NotFound.vue'

import zh from './lang/zh'
import ja from './lang/ja'
import en from './lang/en'

if (process.env.NODE_ENV === 'development') {
  // 开发时使用localhost:12450
  axios.defaults.baseURL = 'http://localhost:12450'
}
axios.defaults.timeout = 10 * 1000

Vue.use(VueRouter)
Vue.use(VueI18n)
// 初始化element
Vue.use(Aside)
Vue.use(Autocomplete)
Vue.use(Badge)
Vue.use(Button)
Vue.use(Card)
Vue.use(Col)
Vue.use(ColorPicker)
Vue.use(Container)
Vue.use(Divider)
Vue.use(Form)
Vue.use(FormItem)
Vue.use(Image)
Vue.use(Input)
Vue.use(Main)
Vue.use(Menu)
Vue.use(MenuItem)
Vue.use(Option)
Vue.use(OptionGroup)
Vue.use(Radio)
Vue.use(RadioGroup)
Vue.use(Row)
Vue.use(Select)
Vue.use(Scrollbar)
Vue.use(Slider)
Vue.use(Submenu)
Vue.use(Switch)
Vue.use(TabPane)
Vue.use(Tabs)
Vue.use(Tooltip)
Vue.prototype.$message = Message

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
        {path: 'stylegen', name: 'stylegen', component: StyleGenerator},
        {path: 'help', name: 'help', component: Help}
      ]
    },
    {path: '/room/test', name: 'test_room', component: Room, props: route => ({strConfig: route.query})},
    {
      path: '/room/:roomId',
      name: 'room',
      component: Room,
      props(route) {
        let roomId = parseInt(route.params.roomId)
        if (isNaN(roomId)) {
          roomId = null
        }
        return {roomId, strConfig: route.query}
      }
    },
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
