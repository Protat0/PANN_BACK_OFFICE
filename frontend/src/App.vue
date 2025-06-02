<template>
  <div>
    <h1>POS System</h1>
    <button @click="testAPI">Test Backend Connection</button>
    <div v-if="apiResponse">
      <h3>Backend Response:</h3>
      <pre>{{ apiResponse }}</pre>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      apiResponse: null
    }
  },
  methods: {
    async testAPI() {
      try {
        const response = await axios.get('http://localhost:8000/api/status/')
        this.apiResponse = response.data
      } catch (error) {
        console.error('API Error:', error)
        this.apiResponse = 'Connection failed!'
      }
    }
  }
}
</script>