import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: () => import('../views/HomeView.vue')
  },
  {
    path: '/model/:modelName',
    name: 'model',
    component: () => import('../components/ModelAndRelated.vue'),
    props: true
  },
  {
    path: '/model/:modelName/:id',
    name: 'model-detail',
    component: () => import('../components/ModelAndRelated.vue'),
    props: true
  }
]

const router = createRouter({
  history: createWebHistory('/agmin'),
  routes
})

// Handle next parameter from URL
router.beforeEach((to, from, next) => {
  const nextPath = to.query.next as string
  if (nextPath) {
    // Remove the /agmin prefix if present
    const path = nextPath.startsWith('/agmin') ? nextPath.slice(6) : nextPath
    next(path)
  } else {
    next()
  }
})

export default router 