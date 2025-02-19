<template>
  <div class="monitoring-view">
    <h2>Monitoring</h2>
    <MonitoringList :monitoredPaths="monitoredPaths" @removePath="removePath" />
    <div class="add-path">
      <input v-model="newPath" placeholder="Enter path to monitor" @keyup.enter="addPath" />
      <button @click="addPath">Add Path</button>
    </div>
    <div class="changes">
      <h3>Latest Changes</h3>
      <ul>
        <li v-for="(change, index) in changes" :key="index">
          {{ change }}
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import MonitoringList from '@/components/MonitoringList.vue';
import { getMonitoredPaths, addMonitoredPath, removeMonitoredPath, getFileChanges } from '@/api/monitoring';

export default {
  components: { MonitoringList },
  data() {
    return {
      monitoredPaths: [],
      newPath: '',
      changes: [],
    };
  },
  async created() {
    await this.fetchMonitoredPaths();
    await this.fetchFileChanges();
  },
  methods: {
    async fetchMonitoredPaths() {
      const response = await getMonitoredPaths();
      this.monitoredPaths = response.data.paths;
    },
    async fetchFileChanges() {
      const response = await getFileChanges();
      this.changes = response.data.changes;
    },
    async addPath() {
      if (this.newPath.trim()) {
        await addMonitoredPath(this.newPath.trim());
        await this.fetchMonitoredPaths();
        this.newPath = '';
      }
    },
    async removePath(path) {
      await removeMonitoredPath(path);
      await this.fetchMonitoredPaths();
    },
  },
};
</script>

<style scoped>
.monitoring-view {
  padding: 16px;
}

.add-path {
  margin-top: 16px;
}

.add-path input {
  width: 300px;
  padding: 8px;
  margin-right: 8px;
}

.changes {
  margin-top: 24px;
}
</style>
