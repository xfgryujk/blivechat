import Vue from 'vue'
import VueRouter from 'vue-router'

import App from './App.vue'
import Home from './components/Home.vue'
import Room from './components/Room.vue'
import NotFound from './components/NotFound.vue'

Vue.use(VueRouter)

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
