import Vue from 'vue'
import VueRouter from 'vue-router'

import App from './App.vue'
import Home from './views/Home.vue'
import Room from './views/Room'
import NotFound from './views/NotFound.vue'

Vue.use(VueRouter)

Vue.config.ignoredElements = [
  /^yt-/
]

const router = new VueRouter({
  mode: 'history',
  routes: [
    {path: '/', component: Home},
    {path: '/room/:roomId', name: 'room', component: Room},
    {path: '*', component: NotFound}
  ]
})

new Vue({
  render: h => h(App),
  router
}).$mount('#app')
