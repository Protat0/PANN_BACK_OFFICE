// Import Bootstrap CSS and JS
import 'bootstrap/dist/css/bootstrap.min.css'
import * as bootstrap from 'bootstrap/dist/js/bootstrap.bundle.min.js'

// Custom Global Styling
import './assets/styles/colors.css'
import './assets/styles/buttons.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import lucidePlugin from './plugins/lucide.js'

// Make Bootstrap available globally
window.bootstrap = bootstrap

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(lucidePlugin)

app.mount('#app')