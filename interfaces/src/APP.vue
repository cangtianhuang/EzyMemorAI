<!-- src/App.vue -->
<template>
  <div id="app">
    <Header />
    <div class="main-content">
      <Sidebar />
      <div class="content-wrapper">
        <router-view />
      </div>
    </div>
    <ToastContainer />
  </div>
</template>

<script>
import Header from './components/Header.vue';
import Sidebar from './components/Sidebar.vue';
import ToastContainer from './components/ToastContainer.vue';

export default {
  components: {
    Header,
    Sidebar,
    ToastContainer,
  },
};
</script>

<style>
.main-content {
  display: flex;
  height: calc(100vh - 64px);
}

.content-wrapper {
  flex: 1;
  overflow-y: auto;
}
</style>