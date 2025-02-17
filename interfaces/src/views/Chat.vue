<!-- src/views/Chat.vue -->
<template>
  <div class="chat-section">
    <h4>聊天</h4>
    <div class="chat-container">
      <div class="messages-container" @scroll="handleScroll">
        <ChatMessage v-for="(message, index) in messages" :key="index" :message="message" />
      </div>
    </div>
    <div class="chat-input-container">
      <div class="chat-form">
        <div class="form-group mb-0">
          <input
            type="text"
            class="form-control"
            v-model="question"
            placeholder="请输入您的查询..."
            @keypress.enter="sendMessage"
            required
          />
        </div>
        <button type="button" class="btn btn-primary" @click="sendMessage">提交查询</button>
      </div>
    </div>
  </div>
</template>

<script>
import ChatMessage from '../components/ChatMessage.vue';

export default {
  name: 'Chat',
  components: {
    ChatMessage,
  },
  data() {
    return {
      messages: [],
      question: '',
    };
  },
  methods: {
    async sendMessage() {
      if (this.question.trim() === '') return;

      // 添加用户消息
      this.messages.push({ sender: 'user', text: this.question });

      const userMessage = this.question;

      // 清空输入框
      this.question = '';

      // 显示“正在思考中...”消息
      const loadingMessage = { sender: 'ai', text: '正在思考中...', isLoading: true };
      this.messages.push(loadingMessage);

      try {
        const formData = new FormData();
        formData.append('question', userMessage);

        const response = await fetch('/', {
          method: 'POST',
          body: formData,
          headers: {
            Accept: 'application/json',
          },
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || '查询失败');
        }

        // 移除“正在思考中...”消息
        this.messages.splice(this.messages.indexOf(loadingMessage), 1);

        // 添加AI回复
        this.messages.push({ sender: 'ai', text: data.answer });
      } catch (error) {
        // 移除“正在思考中...”消息
        this.messages.splice(this.messages.indexOf(loadingMessage), 1);
        // 添加错误消息
        this.messages.push({ sender: 'ai', text: `错误: ${error.message}` });
        // 显示错误通知
        this.$root.$emit('show-toast', { message: error.message, type: 'error' });
      }
    },
    handleScroll() {
      // 如有需要，可以在这里处理滚动事件
    },
  },
  updated() {
    // 消息更新后滚动到底部
    const messagesContainer = this.$el.querySelector('.messages-container');
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  },
};
</script>

<style scoped>
.chat-section {
  padding: 2rem;
  background-color: var(--bg-color);
  display: flex;
  flex-direction: column;
  gap: 1rem;
  height: 100%;
  overflow: hidden;
}

.chat-container {
  flex: 1;
  background-color: var(--card-bg);
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  margin-bottom: 1rem;
  overflow: hidden;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* 自定义滚动条样式 */
.messages-container::-webkit-scrollbar {
  width: 10px;
}
.messages-container::-webkit-scrollbar-thumb {
  background-color: var(--scrollbar-thumb-color);
  border-radius: 5px;
}

.messages-container::-webkit-scrollbar-track {
  background-color: var(--scrollbar-track-color);
}

.messages-container:hover::-webkit-scrollbar-thumb {
  background-color: #c0c4ca;
}

.messages-container::-webkit-scrollbar-thumb:hover {
  background-color: #4c8ed9;
}

.messages-container::-webkit-scrollbar-thumb:active {
  background-color: var(--primary-color);
}

.messages-container.scrolling::-webkit-scrollbar-thumb {
  background-color: var(--primary-color);
}

.chat-input-container {
  background-color: var(--card-bg);
  padding: 1rem;
  border-radius: 12px;
  box-shadow: 0 -2px 5px rgba(0, 0, 0, 0.05);
}

.chat-form {
  display: flex;
  gap: 1rem;
  align-items: flex-end;
}

.chat-form .form-group {
  flex: 1;
  margin: 0;
}

.chat-form .btn {
  height: 42px;
  padding: 0 1.5rem;
}

.form-control {
  border: 1px solid #e5e7eb;
  transition: border-color 0.15s ease-in-out;
}

.form-control:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.1);
}
</style>