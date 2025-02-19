<template>
  <div class="chat-view">
    <MessageList :messages="messages" />
    <div class="input-box">
      <input v-model="newMessage" @keyup.enter="sendMessage" placeholder="Type a message..." />
    </div>
  </div>
</template>

<script>
import MessageList from '@/components/MessageList.vue';
import { useChatStore } from '@/store/chat';
import { sendMessage } from '@/api/chat';

export default {
  components: { MessageList },
  setup() {
    const chatStore = useChatStore();
    const newMessage = ref('');

    const sendMessageHandler = async () => {
      const message = newMessage.value.trim();
      if (message) {
        chatStore.addMessage({ sender: 'user', content: message });
        newMessage.value = '';
        const response = await sendMessage(message);
        chatStore.addMessage({ sender: 'bot', content: response.data.reply });
      }
    };

    return {
      messages: chatStore.messages,
      newMessage,
      sendMessage: sendMessageHandler,
    };
  },
};
</script>

<style scoped>
.chat-view {
  display: flex;
  flex-direction: column;
  height: 100%;
}
.input-box {
  padding: 16px;
  border-top: 1px solid #ccc;
}
</style>
