<template>
  <div class="path-selector">
    <input
      type="text"
      v-model="path"
      placeholder="Enter directory path"
      @input="$emit('update:modelValue', path)"
    />
    <!-- Alternatively, if Electron or a desktop app, use dialog to select folder -->
  </div>
</template>

<script>
export default {
  props: {
    modelValue: {
      type: String,
      default: '',
    },
  },
  data() {
    return {
      path: this.modelValue,
    };
  },
  watch: {
    modelValue(newValue) {
      this.path = newValue;
    },
  },
};
</script>

<style scoped>
.path-selector input {
  width: 300px;
  padding: 8px;
}
</style>
