<template>
  <div class="sidebar">
    <div class="logo">
      <img src="@/assets/logo.png" alt="Logo" />
      <span>EzyMemor AI</span>
    </div>
    <nav>
      <ul>
        <li :class="{ active: isActive('/') }">
          <router-link to="/">Welcome</router-link>
        </li>
        <li :class="{ active: isActive('/chat') }">
          <router-link to="/chat">Intelligent Chat</router-link>
        </li>
        <li :class="{ active: isActive('/file-sorting') }">
          <router-link to="/file-sorting">File Sorting</router-link>
        </li>
        <li :class="{ active: isActive('/monitoring') }">
          <router-link to="/monitoring">Monitoring</router-link>
        </li>
        <li :class="{ active: isActive('/settings') }">
          <router-link to="/settings">Settings</router-link>
        </li>
      </ul>
    </nav>
  </div>
</template>

<script>
import { useRoute } from 'vue-router';

export default {
  setup() {
    const route = useRoute();
    const isActive = (path) => route.path === path;

    return { isActive };
  },
};
</script>

<style scoped>
.sidebar {
  width: 200px;
  background-color: #2c3e50;
  color: #ecf0f1;
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
  padding-top: 16px;
}

.logo {
  display: flex;
  align-items: center;
  padding: 0 16px;
  margin-bottom: 24px;
}

.logo img {
  width: 32px;
  height: 32px;
  margin-right: 8px;
}

.logo span {
  font-size: 18px;
  font-weight: bold;
}

nav ul {
  list-style-type: none;
  padding: 0;
}

nav li {
  margin-bottom: 12px;
}

nav li a {
  color: inherit;
  text-decoration: none;
  display: block;
  padding: 8px 16px;
}

nav li.active {
  background-color: #34495e;
}

nav li a:hover {
  background-color: #34495e;
}
</style>
