import Vue from 'vue'
import VueRouter from 'vue-router'
import axios from 'axios'
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'

import * as i18n from './i18n'
import App from './App'
import NotFound from './views/NotFound'

axios.defaults.timeout = 10 * 1000

Vue.use(VueRouter)
Vue.use(ElementUI)

Vue.config.ignoredElements = [
  /^yt-/
]

const router = new VueRouter({
  mode: 'history',
  routes: [
    {
      path: '/',
      component: () => import('./layout'),
      children: [
        { path: '', name: 'home', component: () => import('./views/Home') },
        { path: 'stylegen', name: 'stylegen', component: () => import('./views/StyleGenerator') },
        { path: 'help', name: 'help', component: () => import('./views/Help') },
        { path: 'plugins', name: 'plugins', component: () => import('./views/Plugins') },
      ]
    },
    {
      path: '/room/test',
      name: 'test_room',
      component: () => import('./views/Room'),
      props: route => ({ strConfig: route.query })
    },
    {
      path: '/room/:roomKeyValue',
      name: 'room',
      component: () => import('./views/Room'),
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
