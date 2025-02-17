<!-- src/views/Settings.vue -->
<template>
  <div class="settings-page">
    <h2>设置</h2>
    <form @submit.prevent="saveSettings">
      <div class="mb-4">
        <label for="api_key" class="form-label">API Key:</label>
        <input
          type="text"
          class="form-control"
          id="api_key"
          v-model="settings.api_key"
          required
        />
      </div>
      <div class="mb-4">
        <label for="language" class="form-label">语言设置:</label>
        <select
          class="form-control"
          id="language"
          v-model="settings.language"
        >
          <option value="zh">中文</option>
          <option value="en">英语</option>
          <!-- 可以添加更多语言选项 -->
        </select>
      </div>
      <button type="submit" class="btn btn-primary">保存设置</button>
    </form>
  </div>
</template>

<script>
export default {
  name: 'Settings',
  data() {
    return {
      settings: {
        api_key: '',
        language: 'zh',
      },
    };
  },
  created() {
    this.fetchSettings();
  },
  methods: {
    async fetchSettings() {
      try {
        const response = await fetch('/api/settings', {
          method: 'GET',
          headers: {
            Accept: 'application/json',
          },
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || '无法获取设置');
        }

        this.settings = data.settings;
      } catch (error) {
        this.$root.$emit('show-toast', { message: error.message, type: 'error' });
      }
    },
    async saveSettings() {
      try {
        const response = await fetch('/api/settings', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Accept: 'application/json',
          },
          body: JSON.stringify(this.settings),
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || '无法保存设置');
        }

        this.$root.$emit('show-toast', { message: data.message || '设置已保存', type: 'success' });
      } catch (error) {
        this.$root.$emit('show-toast', { message: error.message, type: 'error' });
      }
    },
  },
};
</script>

<style scoped>
.settings-page {
  padding: 2rem;
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
</style>
