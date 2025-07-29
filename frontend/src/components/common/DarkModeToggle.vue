<template>
  <button 
    @click="toggleTheme"
    class="theme-toggle-btn"
    :class="{ 'is-dark': isDarkMode }"
  >
    {{ isDarkMode ? '☀️' : '🌙' }}
  </button>
</template>

<script>
export default {
  name: 'DarkModeToggle',
  data() {
    return {
      isDarkMode: false
    }
  },
  mounted() {
    console.log('🔧 DarkModeToggle mounted')
    
    // Check for saved theme
    const savedTheme = localStorage.getItem('pann-theme')
    console.log('💾 Saved theme:', savedTheme)
    
    this.isDarkMode = savedTheme === 'dark'
    this.applyTheme()
  },
  methods: {
    toggleTheme() {
      console.log('🔄 Toggle clicked')
      this.isDarkMode = !this.isDarkMode
      this.applyTheme()
      
      // Save to localStorage
      localStorage.setItem('pann-theme', this.isDarkMode ? 'dark' : 'light')
      console.log('💾 Theme saved:', this.isDarkMode ? 'dark' : 'light')
    },
    applyTheme() {
      const html = document.documentElement
      const body = document.body
      
      console.log('🎨 Applying theme:', this.isDarkMode ? 'dark' : 'light')
      
      if (this.isDarkMode) {
        html.classList.add('dark-theme')
        html.classList.remove('light-theme')
        body.classList.add('dark-theme')
        body.classList.remove('light-theme')
        console.log('🌙 Dark theme applied')
      } else {
        html.classList.add('light-theme')
        html.classList.remove('dark-theme')
        body.classList.add('light-theme')
        body.classList.remove('dark-theme')
        console.log('☀️ Light theme applied')
      }
      
      console.log('📋 HTML classes:', html.classList.toString())
      console.log('📋 Body classes:', body.classList.toString())
    }
  }
}
</script>

<style scoped>
.theme-toggle-btn {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  border: 2px solid #ddd;
  background: white;
  cursor: pointer;
  font-size: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
}

.theme-toggle-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25);
}

.theme-toggle-btn.is-dark {
  background: #333;
  color: white;
  border-color: #555;
}
</style>