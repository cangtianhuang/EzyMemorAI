<!-- src/views/Init.vue -->
<template>
  <div class="main-container">
    <div class="init-section">
      <form @submit.prevent="submitInitForm">
        <div class="mb-4">
          <label for="target_dir" class="form-label">目标目录/文件:</label>
          <input
            type="text"
            class="form-control"
            id="target_dir"
            v-model="targetDir"
            :disabled="formLocked"
            required
          />
        </div>

        <div class="mb-4">
          <label for="vector_store_path" class="form-label">储存地址:</label>
          <input
            type="text"
            class="form-control"
            id="vector_store_path"
            v-model="vectorStorePath"
            :disabled="formLocked"
            required
          />
        </div>

        <div class="d-flex gap-3 mb-4">
          <button type="submit" class="btn btn-init" :disabled="formLocked">
            {{ formLocked ? 'AI已初始化' : '初始化 AI' }}
          </button>
          <button
            type="button"
            class="btn btn-unlock ms-2"
            v-if="formLocked"
            @click="unlockSettings"
          >
            解锁设置
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Init',
  data() {
    return {
      targetDir: '',
      vectorStorePath: '',
      formLocked: false,
    };
  },
  methods: {
    async submitInitForm() {
      const formData = new FormData();
      formData.append('target_dir', this.targetDir);
      formData.append('vector_store_path', this.vectorStorePath);

      try {
        const response = await fetch('/', {
          method: 'POST',
          body: formData,
          headers: {
            Accept: 'application/json',
          },
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || 'AI初始化失败');
        }

        this.formLocked = true;

        // 显示成功通知
        this.$root.$emit('show-toast', { message: data.message || 'AI初始化成功', type: 'success' });

        // 跳转到聊天页面
        this.$router.push({ name: 'Chat' });
      } catch (error) {
        // 显示错误通知
        this.$root.$emit('show-toast', { message: error.message, type: 'error' });
      }
    },
    async unlockSettings() {
      try {
        const response = await fetch('/reset', {
          method: 'POST',
          headers: {
            Accept: 'application/json',
          },
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || '重置失败');
        }

        this.formLocked = false;
        this.targetDir = '';
        this.vectorStorePath = '';

        // 显示成功通知
        this.$root.$emit('show-toast', { message: data.message || '重置成功', type: 'success' });
      } catch (error) {
        // 显示错误通知
        this.$root.$emit('show-toast', { message: error.message, type: 'error' });
      }
    },
  },
};
</script>

<style scoped>
.main-container {
  display: flex;
  flex: 1;
  width: 100%;
  overflow: hidden;
}

.init-section {
  width: 100%;
  background-color: var(--sidebar-bg-color);
  padding: 2rem;
  overflow-y: auto;
}

.form-label {
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  font-weight: 500;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.btn:disabled {
  background-color: #d1d5db;
}

.btn-init {
  background-color: var(--success-color);
  color: white;
}

.btn-init:hover {
  background-color: #059669;
  color: white;
}

.btn-unlock {
  background-color: var(--danger-color);
  color: white;
}

.btn-unlock:hover {
  background-color: #dc2626;
  color: black;
}

.form-control {
  border: 1px solid #e5e7eb;
  transition: border-color 0.15s ease-in-out;
}

.form-control:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.1);
}
</style>