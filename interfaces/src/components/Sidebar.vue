<!-- src/components/Sidebar.vue -->
<template>
  <aside class="sidebar">
    <nav>
      <ul>
        <li>
          <router-link to="/" exact-active-class="active">欢迎</router-link>
        </li>
        <li>
          <router-link to="/init" active-class="active">初始化 AI</router-link>
        </li>
        <li>
          <router-link to="/chat" active-class="active">聊天界面</router-link>
        </li>
        <li>
          <router-link to="/filesorting" active-class="active">文件智能整理</router-link>
        </li>
        <li>
          <router-link to="/settings" active-class="active">设置</router-link>
        </li>
      </ul>
    </nav>
  </aside>
</template>

<script>
export default {
  name: 'Sidebar',
};
</script>

<style scoped>
.sidebar {
  width: 200px;
  background-color: var(--sidebar-bg-color);
  padding: 1rem;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.05);
}

nav ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

nav li {
  margin-bottom: 1rem;
}

nav a {
  color: var(--text-color);
  text-decoration: none;
  font-weight: 500;
}

nav a.active {
  color: var(--primary-color);
}

nav a:hover {
  color: var(--primary-color);
}
</style>
