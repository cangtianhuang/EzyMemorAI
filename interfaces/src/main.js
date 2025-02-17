import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import './assets/styles.css'; // 全局样式
import 'bootstrap/dist/css/bootstrap.min.css'; // 引入Bootstrap样式

createApp(App).use(router).mount('#app');
