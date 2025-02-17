<!-- src/components/Toast.vue -->
<template>
  <div :class="['toast', type, show ? 'show' : '']" @mouseenter="pauseTimer" @mouseleave="resumeTimer">
    <div style="display: flex; align-items: center; gap: 10px;">
      {{ message }}
    </div>
  </div>
</template>

<script>
export default {
  name: 'Toast',
  props: {
    message: String,
    type: {
      type: String,
      default: 'success',
    },
  },
  data() {
    return {
      show: false,
      timer: null,
    };
  },
  mounted() {
    this.show = true;
    this.timer = setTimeout(() => {
      this.show = false;
      this.$emit('close');
    }, 3000);
  },
  methods: {
    pauseTimer() {
      clearTimeout(this.timer);
    },
    resumeTimer() {
      this.timer = setTimeout(() => {
        this.show = false;
        this.$emit('close');
      }, 1000);
    },
  },
};
</script>

<style scoped>
.toast {
  min-width: 250px;
  padding: 15px 20px;
  border-radius: 8px;
  color: white;
  font-weight: 500;
  opacity: 0;
  transform: translateX(-100%);
  transition: all 0.3s ease-in-out;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  margin-bottom: 10px;
}

.toast.show {
  opacity: 1;
  transform: translateX(0);
}

.toast.success {
  background-color: var(--success-color, #10b981);
}

.toast.error {
  background-color: var(--danger-color, #ef4444);
}

.toast.info {
  background-color: var(--primary-color, #2563eb);
}

.toast.warning {
  background-color: #f59e0b;
}
</style>