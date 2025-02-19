<template>
  <div class="welcome-view">
    <WelcomeTitle />
  </div>
</template>

<script>
import WelcomeTitle from '@/components/WelcomeTitle.vue';

export default {
  components: { WelcomeTitle },
};
</script>

<style scoped>
.welcome-view {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}
</style>