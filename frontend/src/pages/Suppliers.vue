<template>
  <div>
    <h1>This is Suppliers Page</h1>
    <div v-if="apiStatus">
      <h3>API Status:</h3>
      <p>Message: {{ apiStatus.message }}</p>
      <p>Status: {{ apiStatus.status }}</p>
      <p>Version: {{ apiStatus.version }}</p>
    </div>
    <div v-if="loading">Loading...</div>
    <div v-if="error" style="color: red;">Error: {{ error }}</div>
  </div>
</template>

<script>
import api from '@/services/api';

export default {
  name: 'SuppliersView',
  data() {
    return {
      apiStatus: null,
      loading: false,
      error: null
    };
  },
  async mounted() {
    await this.checkApiStatus();
  },
  methods: {
    async checkApiStatus() {
      this.loading = true;
      this.error = null;
      
      try {
        // Correct endpoint: /status/
        const response = await api.get('/status/');
        this.apiStatus = response.data;
        console.log('API Response:', response.data);
      } catch (error) {
        this.error = error.message;
        console.error('API Error:', error);
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>