import Vue from 'vue'
import VueRouter from 'vue-router'
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
import axios from 'axios'

import App from './App.vue'
import Layout from './layout'
import Home from './views/Home.vue'
import StyleGenerator from './views/StyleGenerator'
import Room from './views/Room.vue'
import NotFound from './views/NotFound.vue'

if (process.env.NODE_ENV === 'development') {
  // 开发时使用localhost:80
  axios.defaults.baseURL = 'http://localhost'
}

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

new Vue({
  render: h => h(App),
  router
}).$mount('#app')
