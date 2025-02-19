<template>
  <ul class="file-tree">
    <li v-for="(item, index) in structure" :key="index">
      <span>{{ item.name }}</span>
      <FileTree v-if="item.children" :structure="item.children" />
    </li>
  </ul>
</template>

<script>
export default {
  props: {
    structure: {
      type: Array,
      required: true,
    },
  },
};
</script>

<style scoped>
.file-tree {
  list-style-type: none;
  padding-left: 20px;
}

.file-tree li {
  margin: 4px 0;
}

.file-tree span {
  cursor: default;
}
</style>
