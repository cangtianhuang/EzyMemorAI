<template>
  <div :class="['chat-bubble', message.sender]">
    <img :src="avatar" alt="Avatar" class="avatar" />
    <div class="content" v-html="renderedContent"></div>
  </div>
</template>

<script>
import { marked } from 'marked';

export default {
  props: {
    message: {
      type: Object,
      required: true,
    },
  },
  computed: {
    avatar() {
      return this.message.sender === 'user' ? '/assets/user-avatar.png' : '/assets/bot-avatar.png';
    },
    renderedContent() {
      return marked(this.message.content);
    },
  },
};
</script>

<style scoped>
.chat-bubble {
  display: flex;
  margin-bottom: 12px;
}
.chat-bubble.user {
  flex-direction: row-reverse;
}
.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  margin: 0 8px;
}
.content {
  max-width: 70%;
  background-color: #f0f0f0;
  padding: 12px;
  border-radius: 8px;
}
</style>
