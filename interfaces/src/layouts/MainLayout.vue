<template>
  <div class="flex h-screen bg-gray-100">
    <!-- Sidebar -->
    <aside class="w-64 bg-white shadow-lg">
      <div class="flex flex-col h-full">
        <!-- Logo -->
        <div class="p-4 border-b">
          <img src="@/assets/logo.svg" alt="Logo" class="h-8" />
        </div>

        <!-- Navigation Menu -->
        <nav class="flex-1 overflow-y-auto py-4">
          <router-link
            v-for="route in routes"
            :key="route.path"
            :to="route.path"
            class="flex items-center px-6 py-3 text-gray-700 hover:bg-gray-100"
            :class="{ 'bg-gray-100 text-blue-600': isActiveRoute(route.path) }"
          >
            <component :is="route.icon" class="w-5 h-5 mr-3" />
            {{ route.name }}
          </router-link>
        </nav>

        <!-- Settings Link -->
        <div class="p-4 border-t">
          <router-link
            to="/settings"
            class="flex items-center text-gray-700 hover:text-gray-900"
          >
            <settings-icon class="w-5 h-5 mr-3" />
            Settings
          </router-link>
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <div class="flex-1 overflow-hidden">
      <div class="h-full overflow-y-auto px-6 py-8">
        <slot />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { MessageSquare, FolderTree, Activity, Settings } from 'lucide-vue-next'

const route = useRoute()

const routes = [
  { path: '/chat', name: 'Chat', icon: MessageSquare },
  { path: '/file-sorting', name: 'File Sorting', icon: FolderTree },
  { path: '/monitoring', name: 'Monitoring', icon: Activity }
]

const isActiveRoute = (path) => {
  return route.path === path
}
</script>