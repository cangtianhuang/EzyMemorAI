// src/router/index.js

import { createRouter, createWebHistory } from 'vue-router';
import WelcomeView from '@/views/WelcomeView.vue';
import ChatView from '@/views/ChatView.vue';
import FileSortingView from '@/views/FileSortingView.vue';
import MonitoringView from '@/views/MonitoringView.vue';
import SettingsView from '@/views/SettingsView.vue';

const routes = [
  { path: '/', name: 'Welcome', component: WelcomeView },
  { path: '/chat', name: 'Chat', component: ChatView },
  { path: '/file-sorting', name: 'FileSorting', component: FileSortingView },
  { path: '/monitoring', name: 'Monitoring', component: MonitoringView },
  { path: '/settings', name: 'Settings', component: SettingsView },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;