import Vue from 'vue'
import VueRouter from 'vue-router'
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'

import App from './App.vue'
import Layout from './layout'
import Home from './views/Home.vue'
import Room from './views/Room'
import NotFound from './views/NotFound.vue'

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
        {path: '', component: Home}
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
