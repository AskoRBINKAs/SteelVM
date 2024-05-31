import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// Import Bootstrap and BootstrapVue CSS files (order is important)

// Make BootstrapVue available throughout your project
// Optionally install the BootstrapVue icon components plugin

const app = createApp(App)

app.use(router)
app.mount('#app')
