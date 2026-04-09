import { createRouter, createWebHistory } from 'vue-router'
import Login from '@/views/Login.vue'
import Register from '@/views/Register.vue'
import AdminDashboard from '@/views/admin/Dashboard.vue'
import AdminStudents from '@/views/admin/AdminStudents.vue'
import AdminCompanies from '@/views/admin/AdminCompanies.vue'
import AdminDrives from '@/views/admin/AdminDrives.vue'
import AdminApplications from '@/views/admin/AdminApplications.vue'
import CompanyDashboard from '@/views/company/CompanyDashboard.vue'
import CompanyDrivesPage from '@/views/company/CompanyDrivesPage.vue'
import CreateDrive from '@/views/company/CreateDrive.vue'
import CompanyApplications from '@/views/company/CompanyApplications.vue'
import CompanyInterviews from '@/views/company/CompanyInterviews.vue'
import CompanyProfile from '@/views/company/CompanyProfile.vue'
import CompanyResults from '@/views/company/CompanyResults.vue'
import StudentDashboard from '@/views/student/StudentDashboard.vue'
import StudentProfile from '@/views/student/StudentProfile.vue'
import StudentDrives from '@/views/student/StudentDrives.vue'
import StudentApplications from '@/views/student/StudentApplications.vue'
import StudentHistory from '@/views/student/StudentHistory.vue'
import Home from '@/Home.vue'
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
    { path: '/company/dashboard', component: CompanyDashboard, meta: { requiresAuth: true, role: 'company' } },
    { path: '/company/drives', component: CompanyDrivesPage, meta: { requiresAuth: true, role: 'company' } },
    { path: '/company/profile', component: CompanyProfile, meta: { requiresAuth: true, role: 'company' } },
    { path: '/company/create-drive', component: CreateDrive, meta: { requiresAuth: true, role: 'company' } },
    { path: '/company/applications', component: CompanyApplications, meta: { requiresAuth: true, role: 'company' } },
    { path: '/company/interviews', component: CompanyInterviews, meta: { requiresAuth: true, role: 'company' } },
    { path: '/company/results', component: CompanyResults, meta: { requiresAuth: true, role: 'company' } },
    { path: '/student/dashboard', component: StudentDashboard, meta: { requiresAuth: true, role: 'student' } },
    { path: '/student/profile', component: StudentProfile, meta: { requiresAuth: true, role: 'student' } },
    { path: '/student/drives', component: StudentDrives, meta: { requiresAuth: true, role: 'student' } },
    { path: '/student/applications', component: StudentApplications, meta: { requiresAuth: true, role: 'student' } },
    { path: '/student/history', component: StudentHistory, meta: { requiresAuth: true, role: 'student' } },
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
