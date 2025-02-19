<template>
  <div class="settings-view">
    <h2>Settings</h2>
    <SettingsForm :settings="settings" @saveSettings="saveSettings" />
  </div>
</template>

<script>
import SettingsForm from '@/components/SettingsForm.vue';
import {getSettings, updateSettings} from '@/api/settings';

export default {
  components: {SettingsForm},
  data() {
    return {
      settings: {},
    };
  },
  async created() {
    await this.fetchSettings();
  },
  methods: {
    async fetchSettings() {
      const response = await getSettings();
      this.settings = response.data;
    },
    async saveSettings(updatedSettings) {
      await updateSettings(updatedSettings);
      this.settings = updatedSettings;
    },
  },
};
</script>

<style scoped>
.settings-view {
  padding: 16px;
}
</style>
