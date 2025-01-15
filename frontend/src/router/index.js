import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import ToolsView from '../views/ToolsView.vue'
import PipelinesView from '../views/PipelinesView.vue'
import ExecutionsView from '../views/ExecutionsView.vue'
import ReportsView from '../views/ReportsView.vue'
import SettingsView from '../views/SettingsView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/AboutView.vue'),
    },
    {
      path: '/tools',
      name: 'tools',
      component: ToolsView
    },
    {
      path: '/pipelines',
      name: 'pipelines',
      component: PipelinesView
    },
    {
      path: '/executions',
      name: 'executions',
      component: ExecutionsView
    },
    {
      path: '/reports',
      name: 'reports',
      component: ReportsView
    },
    {
      path: '/settings',
      name: 'settings',
      component: SettingsView
    }
  ],
})

export default router
