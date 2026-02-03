import { createRouter, createWebHistory } from 'vue-router'
import Login from '@/views/Login.vue'
import Register from '@/views/Register.vue'
import AdminDashboard from '@/views/admin/dashboard.vue'
import AdminStudents from '@/views/admin/AdminStudents.vue'
import AdminCompanies from '@/views/admin/AdminCompanies.vue'
import AdminDrives from '@/views/admin/AdminDrives.vue'
import AdminApplications from '@/views/admin/AdminApplications.vue'
import StudentDashboard from '@/views/student/StudentDashboard.vue'
import CompanyDashboard from '@/views/company/CompanyDashboard.vue'
import Home from '@/home.vue'
import { authState } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', component: Home },
    { path: '/login', component: Login },
    { path: '/register', component: Register },
    { path: '/admin/dashboard', component: AdminDashboard, meta: { requiresAuth: true, role: 'admin' } },
    { path: '/admin/students', component: AdminStudents, meta: { requiresAuth: true, role: 'admin' } },
    { path: '/admin/companies', component: AdminCompanies, meta: { requiresAuth: true, role: 'admin' } },
    { path: '/admin/drives', component: AdminDrives, meta: { requiresAuth: true, role: 'admin' } },
    { path: '/admin/applications', component: AdminApplications, meta: { requiresAuth: true, role: 'admin' } },
    { path: '/student/dashboard', component: StudentDashboard, meta: { requiresAuth: true, role: 'student' } },
    { path: '/company/dashboard', component: CompanyDashboard, meta: { requiresAuth: true, role: 'company' } }
  ],
})

router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !authState.isLoggedIn) {
    return next("/login");
  }

  if (to.meta.role && to.meta.role !== authState.role) {
    return next("/login");
  }

  next();
});

export default router;
