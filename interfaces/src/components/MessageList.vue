<template>
  <div class="monitoring-list">
    <ul>
      <li v-for="(path, index) in monitoredPaths" :key="index">
        <span>{{ path }}</span>
        <button @click="$emit('removePath', path)">Remove</button>
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  props: {
    monitoredPaths: {
      type: Array,
      required: true,
    },
  },
};
</script>

<style scoped>
.monitoring-list ul {
  list-style-type: none;
  padding: 0;
}

.monitoring-list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.monitoring-list button {
  background-color: #e74c3c;
  color: #fff;
  border: none;
  padding: 6px 12px;
  cursor: pointer;
  border-radius: 4px;
}

.monitoring-list button:hover {
  background-color: #c0392b;
}
</style>
