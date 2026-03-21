<template>
  <div id="app" :data-role="currentRole">
    <NavBar />
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script>
import NavBar from './NavBar.vue'
import { authState } from '@/stores/auth'

export default {
  name: 'App',
  components: {
    NavBar
  },
  computed: {
    currentRole() {
      return authState.role || 'institution'
    }
  },
  watch: {
    currentRole: {
      immediate: true,
      handler(role) {
        document.body.setAttribute('data-role', role || 'institution')
      }
    }
  }
}
</script>

<style>
@import './assets/style.css';
</style>
