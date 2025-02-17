<!-- src/components/Header.vue -->
<template>
  <header class="header">
    <router-link to="/" class="logo">EzyMemor AI</router-link>
  </header>
</template>

<script>
export default {
  name: 'Header',
};
</script>

<style scoped>
.header {
  background-color: var(--card-bg);
  padding: 1rem 2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  width: 100%;
  z-index: 100;
}

.logo {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--primary-color);
  text-decoration: none;
  letter-spacing: -0.5px;
}

.logo:hover {
  color: var(--primary-color);
}
</style>