<template>
  <div class="file-sorting-view">
    <h2>File Sorting</h2>
    <div class="path-selector">
      <PathSelector v-model="selectedPath" />
      <button @click="previewSorting">Preview Sorting</button>
    </div>
    <div class="file-trees" v-if="originalStructure && sortedStructure">
      <div class="file-tree">
        <h3>Original Structure</h3>
        <FileTree :structure="originalStructure" />
      </div>
      <div class="file-tree">
        <h3>AI-Sorted Structure</h3>
        <FileTree :structure="sortedStructure" />
      </div>
    </div>
    <div class="apply-button" v-if="sortedStructure">
      <button @click="applySorting">Apply Sorting</button>
    </div>
  </div>
</template>

<script>
import PathSelector from '@/components/PathSelector.vue';
import FileTree from '@/components/FileTree.vue';
import { getSortingPreview, applySorting } from '@/api/fileSorting';

export default {
  components: { PathSelector, FileTree },
  data() {
    return {
      selectedPath: '',
      originalStructure: null,
      sortedStructure: null,
    };
  },
  methods: {
    async previewSorting() {
      if (this.selectedPath) {
        const response = await getSortingPreview(this.selectedPath);
        this.originalStructure = response.data.originalStructure;
        this.sortedStructure = response.data.sortedStructure;
      }
    },
    async applySorting() {
      if (this.selectedPath) {
        await applySorting(this.selectedPath);
        alert('File sorting applied successfully.');
        this.originalStructure = null;
        this.sortedStructure = null;
        this.selectedPath = '';
      }
    },
  },
};
</script>

<style scoped>
.file-sorting-view {
  padding: 16px;
}

.path-selector {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.path-selector button {
  margin-left: 8px;
}

.file-trees {
  display: flex;
  justify-content: space-between;
}

.file-tree {
  width: 45%;
}

.apply-button {
  margin-top: 16px;
  text-align: center;
}

.apply-button button {
  padding: 10px 20px;
}
</style>
