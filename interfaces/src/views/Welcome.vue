<!-- src/views/Welcome.vue -->
<template>
  <div class="welcome-page">
    <h1>欢迎使用 EzyMemor AI</h1>
    <p>
      EzyMemor AI 是一个智能助手，帮助您管理和查询文件。
    </p>
    <p>
      请使用左侧的导航栏来开始使用。
    </p>
  </div>
</template>

<script>
export default {
  name: 'Welcome',
};
</script>

<style scoped>
.welcome-page {
  padding: 2rem;
  text-align: center;
}

.welcome-page h1 {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.welcome-page p {
  font-size: 1.25rem;
  color: var(--text-secondary-color);
}
</style>
