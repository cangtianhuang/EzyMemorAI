<!-- src/views/FileOrganizing.vue -->
<template>
  <div class="fileOrganizing-page">
    <h2>文件智能整理</h2>
    <p>以下是AI为您整理的文件预览：</p>

    <div class="file-list">
      <div v-for="file in files" :key="file.id" class="file-item">
        <div class="file-info">
          <div class="file-name">{{ file.name }}</div>
          <div class="file-path">{{ file.path }}</div>
        </div>
        <div class="file-actions">
          <button class="btn btn-primary btn-sm" @click="moveFile(file.id)">移动</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FileOrganizing',
  data() {
    return {
      files: [],
    };
  },
  created() {
    this.fetchFiles();
  },
  methods: {
    async fetchFiles() {
      try {
        const response = await fetch('/api/files', {
          method: 'GET',
          headers: {
            Accept: 'application/json',
          },
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || '无法获取文件列表');
        }

        this.files = data.files;
      } catch (error) {
        this.$root.$emit('show-toast', { message: error.message, type: 'error' });
      }
    },
    async moveFile(fileId) {
      try {
        const response = await fetch(`/api/files/${fileId}/move`, {
          method: 'POST',
          headers: {
            Accept: 'application/json',
          },
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || '无法移动文件');
        }

        this.$root.$emit('show-toast', { message: data.message || '文件移动成功', type: 'success' });

        // 更新文件列表
        this.fetchFiles();
      } catch (error) {
        this.$root.$emit('show-toast', { message: error.message, type: 'error' });
      }
    },
  },
};
</script>

<style scoped>
.fileorganizing-page {
  padding: 2rem;
}

.file-list {
  margin-top: 1.5rem;
}

.file-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.file-info {
  flex: 1;
}

.file-name {
  font-weight: 500;
}

.file-path {
  color: var(--text-secondary-color);
  font-size: 0.875rem;
}

.file-actions button {
  padding: 0.5rem 1rem;
}
</style>
