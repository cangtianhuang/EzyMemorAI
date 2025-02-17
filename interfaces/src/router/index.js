// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import Welcome from '../views/Welcome.vue';
import Init from '../views/Init.vue';
import Chat from '../views/Chat.vue';
import FileOrganizing from '../views/FileOrganizing.vue';
import Settings from '../views/Settings.vue';

const routes = [
  {
    path: '/',
    name: 'Welcome',
    component: Welcome,
  },
  {
    path: '/init',
    name: 'Init',
    component: Init,
  },
  {
    path: '/chat',
    name: 'Chat',
    component: Chat,
  },
  {
    path: '/filesorting',
    name: 'FileSorting',
    component: FileSorting,
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;