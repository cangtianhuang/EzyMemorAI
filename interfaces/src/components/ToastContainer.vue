<!-- src/components/ToastContainer.vue -->
<template>
  <div id="toast-container">
    <Toast
      v-for="(toast, index) in toasts"
      :key="index"
      :message="toast.message"
      :type="toast.type"
      @close="removeToast(index)"
    />
  </div>
</template>

<script>
import Toast from './Toast.vue';

export default {
  name: 'ToastContainer',
  components: {
    Toast,
  },
  data() {
    return {
      toasts: [],
    };
  },
  created() {
    this.$root.$on('show-toast', this.addToast);
  },
  methods: {
    addToast(toast) {
      this.toasts.push(toast);
    },
    removeToast(index) {
      this.toasts.splice(index, 1);
    },
  },
};
</script>

<style scoped>
#toast-container {
  position: fixed;
  bottom: 20px;
  left: 20px;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
</style>