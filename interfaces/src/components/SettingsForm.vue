<template>
  <form class="settings-form" @submit.prevent="onSubmit">
    <div class="form-group">
      <label for="apiKey">OpenAI API Key</label>
      <input
        type="text"
        id="apiKey"
        v-model="form.apiKey"
        :class="{ invalid: errors.apiKey }"
        placeholder="Enter your OpenAI API Key"
      />
      <span v-if="errors.apiKey" class="error-message">{{ errors.apiKey }}</span>
    </div>
    <div class="form-group">
      <label for="dbPath">Database File Path</label>
      <input
        type="text"
        id="dbPath"
        v-model="form.dbPath"
        :class="{ invalid: errors.dbPath }"
        placeholder="Enter the path to the database file"
      />
      <span v-if="errors.dbPath" class="error-message">{{ errors.dbPath }}</span>
    </div>
    <!-- Add more settings fields as needed -->
    <button type="submit">Save Settings</button>
  </form>
</template>

<script>
export default {
  props: {
    settings: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      form: { ...this.settings },
      errors: {},
    };
  },
  methods: {
    validate() {
      this.errors = {};
      if (!this.form.apiKey) {
        this.errors.apiKey = 'API Key is required.';
      }
      if (!this.form.dbPath) {
        this.errors.dbPath = 'Database file path is required.';
      }
      return Object.keys(this.errors).length === 0;
    },
    onSubmit() {
      if (this.validate()) {
        this.$emit('saveSettings', { ...this.form });
      }
    },
  },
};
</script>

<style scoped>
.settings-form {
  max-width: 400px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
}

.form-group input {
  width: 100%;
  padding: 8px;
  box-sizing: border-box;
}

.form-group input.invalid {
  border-color: #e74c3c;
}

.error-message {
  color: #e74c3c;
  font-size: 12px;
}

button {
  padding: 10px 16px;
  background-color: #3498db;
  color: #fff;
  border: none;
  cursor: pointer;
  border-radius: 4px;
}

button:hover {
  background-color: #2980b9;
}
</style>
