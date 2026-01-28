import { createRouter, createWebHistory } from 'vue-router'
import Login from '@/views/Login.vue'
import Register from '@/views/Register.vue'
import AdminDashboard from '@/views/admin/AdminDashboard.vue'
import StudentDashboard from '@/views/student/StudentDashboard.vue'
import CompanyDashboard from '@/views/company/CompanyDashboard.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', redirect: '/login' },
    { path: '/login', component: Login },
    { path: '/register', component: Register },
    { path: '/admin/dashboard', component: AdminDashboard, meta: { requiresAuth: true, role: 'admin' } },
    { path: '/student/dashboard', component: StudentDashboard, meta: { requiresAuth: true, role: 'Student' } },
    { path: '/company/dashboard', component: CompanyDashboard, meta: { requiresAuth: true, role: 'company' } }
  ],
})

router.beforeEach((to, from, next) => {
  const access_token = localStorage.getItem("access_token");
  const role = localStorage.getItem("role");

  if (to.meta.requiresAuth && !access_token) {
    return next("/login");
  }

  if (to.meta.role && to.meta.role !== role) {
    return next("/login");
  }

  next();
});

export default router;
