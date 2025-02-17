<!-- src/components/ChatMessage.vue -->
<template>
  <div :class="['chat-message', message.sender]">
    <div class="sender-info">
      <div class="sender-avatar">{{ avatarLetter }}</div>
      <div class="sender-name">{{ senderName }}</div>
    </div>
    <div class="chat-bubble">
      <div v-if="message.isLoading">正在思考中...</div>
      <div v-else>{{ message.text }}</div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ChatMessage',
  props: {
    message: Object,
  },
  computed: {
    avatarLetter() {
      return this.message.sender === 'user' ? 'U' : 'AI';
    },
    senderName() {
      return this.message.sender === 'user' ? '用户' : 'AI助手';
    },
  },
};
</script>

<style scoped>
.chat-message {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  max-width: 80%;
}

.chat-message.user {
  margin-left: auto;
  flex-direction: row-reverse;
}

.chat-message.ai {
  margin-right: auto;
  flex-direction: row;
}

.sender-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 0 0.75rem;
  min-width: 45px;
}

.chat-message.user .sender-info {
  margin-left: 0.75rem;
  margin-right: 0;
}

.chat-message.ai .sender-info {
  margin-right: 0.75rem;
  margin-left: 0;
}

.sender-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: var(--chat-user-color);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
}
.chat-message.ai .sender-avatar {
  background-color: var(--chat-user-color);
}
.sender-name {
  font-size: 0.75rem;
  color: var(--chat-user-color);
  text-align: center;
}

.chat-bubble {
  padding: 0.75rem 1rem;
  border-radius: 12px;
  position: relative;
  max-width: 100%;
  word-wrap: break-word;
}

.chat-message.user .chat-bubble {
  background-color: var(--chat-user-bg);
  border-top-right-radius: 4px;
}

.chat-message.ai .chat-bubble {
  background-color: var(--chat-ai-bg);
  border-top-left-radius: 4px;
}
</style>