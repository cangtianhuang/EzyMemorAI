import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './styles/index.css'

// Create Vue application instance
const app = createApp(App)

// Install plugins
app.use(createPinia())
app.use(router)

// Error handling
app.config.errorHandler = (err, vm, info) => {
  console.error('Global error:', err)
  console.error('Vue instance:', vm)
  console.error('Error info:', info)
}

// Mount application
app.mount('#app')

// Development only
if (import.meta.env.DEV) {
  console.log('Running in development mode')
}