import Vue from 'vue'
import VueRouter from 'vue-router'
import {
  Aside, Autocomplete, Badge, Button, ButtonGroup, Card, Col, ColorPicker, Container, Divider, Form, FormItem, Image,
  Input, Link, Main, Menu, MenuItem, Message, Option, OptionGroup, Radio, RadioGroup, Row, Select, Scrollbar,
  Slider, Submenu, Switch, Table, TableColumn, TabPane, Tabs, Tooltip
} from 'element-ui'
import axios from 'axios'

import * as i18n from './i18n'
import App from './App'
import Layout from './layout'
import Home from './views/Home'
import StyleGenerator from './views/StyleGenerator'
import Help from './views/Help'
import Room from './views/Room'
import NotFound from './views/NotFound'

axios.defaults.timeout = 10 * 1000

Vue.use(VueRouter)
// 初始化element
Vue.use(Aside)
Vue.use(Autocomplete)
Vue.use(Badge)
Vue.use(Button)
Vue.use(ButtonGroup)
Vue.use(Card)
Vue.use(Col)
Vue.use(ColorPicker)
Vue.use(Container)
Vue.use(Divider)
Vue.use(Form)
Vue.use(FormItem)
Vue.use(Image)
Vue.use(Input)
Vue.use(Link)
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
Vue.use(Table)
Vue.use(TableColumn)
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
        { path: '', name: 'home', component: Home },
        { path: 'stylegen', name: 'stylegen', component: StyleGenerator },
        { path: 'help', name: 'help', component: Help }
      ]
    },
    {
      path: '/room/test',
      name: 'test_room',
      component: Room,
      props: route => ({ strConfig: route.query })
    },
    {
      path: '/room/:roomKeyValue',
      name: 'room',
      component: Room,
      props(route) {
        let roomKeyType = parseInt(route.query.roomKeyType) || 1
        if (roomKeyType < 1 || roomKeyType > 2) {
          roomKeyType = 1
        }

        let roomKeyValue = route.params.roomKeyValue
        if (roomKeyType === 1) {
          roomKeyValue = parseInt(roomKeyValue) || null
        } else {
          roomKeyValue = roomKeyValue || null
        }
        return { roomKeyType, roomKeyValue, strConfig: route.query }
      }
    },
    { path: '*', component: NotFound }
  ]
})

new Vue({
  render: h => h(App),
  router,
  i18n: i18n.i18n
}).$mount('#app')
