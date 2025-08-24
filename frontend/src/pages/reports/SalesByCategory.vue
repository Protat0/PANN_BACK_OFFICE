<template>
  <div class="SBC-page">
    <!-- ========================================== -->
    <!-- TOP SECTION: Analytics & Chart -->
    <!-- ========================================== -->
    <div class="TopContainer">
      <!-- Left: Top Categories List -->
      <div class="LC-SBC">
        <div class="LCL1">
          <h1>Top Categories</h1>
          <h3>Net Sales</h3>
        </div>
        
        <!-- Loading state for top categories -->
        <div v-if="loadingTopItems" class="loading-state-small">
          <div class="spinner-border-sm"></div>
          <p>Loading top categories...</p>
        </div>
        
        <!-- Top categories list -->
        <ul v-else-if="topItems && topItems.length > 0" class="LCL2">
          <li v-for="(item, index) in topItems" :key="index" class="list-item">
            <span class="item-name" style="font-weight:bold; font-size: 25px;">{{ item.name }}</span>
            <span class="item-price" style="color:green; font-size: 15px;">{{ item.price }}</span>
          </li>
        </ul>
        
        <!-- Empty state for top categories -->
        <div v-else class="empty-state-small">
          <p>No category data available</p>
          <button @click="getTopItems" class="btn btn-sm btn-primary">Retry Loading</button>
        </div>
      </div>
      
      <div class="divider"></div>
      
      <!-- Right: Sales Chart -->
      <div class="RC-SBC">
        <div class="chart-header">
          <h1>Sales Chart</h1>
          <select v-model="selectedFrequency" @change="onFrequencyChange" class="frequency-dropdown">
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
            <option value="yearly">Yearly</option>
          </select>
        </div>
        <div class="chart-container">
          <div v-if="loadingChart" class="chart-loading">
            <div class="spinner-border text-primary"></div>
            <p>Loading chart data...</p>
          </div>
          <PieChartView v-else :chartData="chartData" :selectedFrequency="selectedFrequency" />
        </div>
      </div>
    </div>
    
    <!-- ========================================== -->
    <!-- BOTTOM SECTION: Category Analysis -->
    <!-- ========================================== -->
    <div class="BottomContainer">
      <!-- Header with Date Range Info -->
      <div class="transaction-header">
        <div class="header-left">
          <h1>Category Analysis</h1>
        </div>
        <div class="header-actions">
          <!-- Auto-refresh status and controls (same as logs page) -->
          <div class="auto-refresh-status">
            <i class="bi bi-arrow-repeat text-success" :class="{ 'spinning': loading }"></i>
            <span class="status-text">
              <span v-if="autoRefreshEnabled">Updates in {{ countdown }}s </span>
              <span v-else>Auto-refresh disabled</span>
            </span>
            
            <!-- Toggle button -->
            <button 
              class="btn btn-sm"
              :class="autoRefreshEnabled ? 'btn-outline-secondary' : 'btn-outline-success'"
              @click="toggleAutoRefresh"
            >
              {{ autoRefreshEnabled ? 'Disable' : 'Enable' }}
            </button>
          </div>
          
          <!-- Connection health indicator (same as logs page) -->
          <div class="connection-indicator" :class="getConnectionStatus()">
            <i :class="getConnectionIcon()"></i>
            <span class="connection-text">{{ getConnectionText() }}</span>
          </div>
          
          <!-- Emergency Refresh - Only show if error or connection lost -->
          <button 
            v-if="error || connectionLost" 
            class="btn btn-warning" 
            @click="emergencyReconnect"
            :disabled="loading"
          >
            <i class="bi bi-arrow-clockwise" :class="{ 'spinning': loading }"></i>
            {{ loading ? 'Reconnecting...' : 'Reconnect' }}
          </button>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        <div class="spinner-border text-primary"></div>
        <p>Loading category data...</p>
      </div>

      <!-- Category Table -->
      <div v-else class="table-container">
        <table class="table table-striped">
          <thead>
            <tr>
              <th scope="col">Category</th>
              <th scope="col">Description</th>
              <th scope="col">Sub-Categories</th>
              <th scope="col">Total Items Sold</th>
              <th scope="col">Total Net Sales</th>
              <th scope="col"># of Products</th>
            </tr>
          </thead>
          <tbody class="table-group-divider">
            <tr v-for="category in categories" :key="category.id || category._id">
              <td class="category-name">{{ category.name || category.category_name }}</td>
              <td class="category-description">{{ category.description || 'N/A' }}</td>
              <td class="sub-categories">{{ formatSubCategories(category.sub_categories) }}</td>
              <td class="items-sold">{{ formatNumber(category.total_items_sold) }}</td>
              <td class="net-sales">
                <span class="total-amount">{{ formatCurrency(category.total_net_sales || 0) }}</span>
              </td>
              <td class="product-count">{{ category.product_count || 0 }}</td>
            </tr>
          </tbody>
        </table>
        
        <!-- Empty State -->
        <div v-if="categories.length === 0 && !loading" class="empty-state">
          <i class="bi bi-grid" style="font-size: 3rem; color: #6b7280;"></i>
          <p>No categories found for this time period</p>
          <button class="btn btn-primary" @click="refreshData">
            <i class="bi bi-arrow-clockwise"></i> Refresh Data
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import PieChartView from '@/components/PieChartView.vue';
import CategoryService from '@/services/apiCategory';

export default {
  name: 'SalesByCategory',
  components: {
    PieChartView
  },
  
  // ====================================================================
  // COMPONENT DATA
  // ====================================================================
  data() {
    return {
      // Loading states
      loading: false,
      loadingTopItems: false,
      loadingChart: false,
      
      // Chart and analytics with date filtering
      selectedFrequency: 'monthly',
      currentDateRange: null, // Track current date range for display
      topItems: [],
      chartData: {
        labels: ['Loading...'],
        datasets: [{
          label: 'Sales Amount',
          data: [0],
          backgroundColor: ['#e5e7eb'],
          borderColor: ['#d1d5db'],
          borderWidth: 1
        }]
      },
      
      // Category data
      categories: [],

      autoRefreshEnabled: true,
      autoRefreshInterval: 30000, // 30 seconds
      baseRefreshInterval: 30000,
      autoRefreshTimer: null,
      countdown: 30,
      countdownTimer: null,
      
      // Connection health tracking
      connectionLost: false,
      consecutiveErrors: 0,
      lastSuccessfulLoad: null,
      
      // Smart refresh rate tracking
      recentActivity: [],
    };
  },

  // ====================================================================
  // COMPUTED PROPERTIES
  // ====================================================================
  computed: {
    /**
     * Format date range for display
     */
    dateRangeDisplay() {
      if (!this.currentDateRange) return '';
      
      const startDate = new Date(this.currentDateRange.start_date);
      const endDate = new Date(this.currentDateRange.end_date);
      
      const options = { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
      };
      
      return `${startDate.toLocaleDateString('en-US', options)} - ${endDate.toLocaleDateString('en-US', options)}`;
    }
  },
  
  // ====================================================================
  // LIFECYCLE HOOKS
  // ====================================================================
  async mounted() {
    console.log("=== SalesByCategory Component Mounted ===");
    
    try {
      await this.loadAllCategoryData();
      
      // Start auto-refresh
      if (this.autoRefreshEnabled) {
        this.startAutoRefresh();
      }
      
      console.log("✅ All category data loaded");
    } catch (error) {
      console.error("❌ Category data loading failed:", error);
    }
  },

beforeUnmount() {
  this.stopAutoRefresh();
  console.log('🧹 Component cleanup complete');
},
  
  // ====================================================================
  // METHODS
  // ====================================================================
  methods: {
    // ================================================================
    // DATA LOADING METHODS
    // ================================================================
    
    /**
     * Load all category data - SIMPLIFIED: No period filtering for top items
     */
    async loadAllCategoryData() {
      try {
        console.log("=== Loading All Category Data (Initial/Refresh) ===");
        this.loading = true;
        this.loadingTopItems = true;
        this.loadingChart = true;
            
        if (!CategoryService?.CategoryData) {
          throw new Error("CategoryData method not found in CategoryService");
        }
        
        console.log("Calling CategoryService.CategoryData()...");
        
        // Call basic API (no date filtering for initial load)
        let response;
        try {
          response = await CategoryService.CategoryData();
        } catch (error) {
          console.error("Error calling CategoryService:", error);
          throw error;
        }
        
        console.log("=== CATEGORY API RESPONSE DEBUG ===");
        console.log("Raw API Response:", response);
        
        // Extract categories from response
        let categoryData = this.extractCategoryData(response);
        
        if (categoryData && categoryData.length > 0) {
          // Process all data for initial load (top items and table use all data)
          await this.processCategoryData(categoryData);
          
          // Separately update chart with period-specific data
          await this.updateChartWithCurrentFrequency();
          
          console.log("✅ All category data processed successfully");
        } else {
          console.warn("No category data found, using fallback data");
          this.setFallbackData();
        }
        
        // ✅ CONNECTION HEALTH TRACKING - Move this to success block
        this.connectionLost = false;
        this.consecutiveErrors = 0;
        this.lastSuccessfulLoad = Date.now();

      } catch (error) {
        console.error("❌ Error loading category data:", error);
        
        // Handle connection errors
        this.consecutiveErrors++;
        
        if (this.consecutiveErrors >= 3) {
          this.connectionLost = true;
          console.log('Connection marked as lost after 3 consecutive errors');
        }
        
        this.setFallbackData();
      } finally {
        this.loading = false;
        this.loadingTopItems = false;
        this.loadingChart = false;
      }
    },

    /**
     * Update chart with current frequency (separate from top items and table)
     */
    async updateChartWithCurrentFrequency() {
      try {
        const dateRange = this.calculateDateRange(this.selectedFrequency);
        this.currentDateRange = dateRange;
        
        // Try to get period-specific data for chart
        const requestParams = {
          start_date: dateRange.start_date,
          end_date: dateRange.end_date,
          frequency: this.selectedFrequency
        };
        
        let response;
        try {
          response = await CategoryService.CategoryData(requestParams);
        } catch (apiError) {
          // If API doesn't support date filtering, use client-side filtering
          response = await CategoryService.CategoryData();
        }
        
        let chartData = this.extractCategoryData(response);
        
        if (chartData && chartData.length > 0) {
          // Apply client-side filtering if API doesn't support it
          if (!response?.date_filter_applied) {
            chartData = this.filterCategoriesByDate(chartData, dateRange);
          }
          
          // Update ONLY the chart
          this.updateChartData(chartData.slice(0, 6));
          console.log("✅ Chart updated with frequency data");
        } else {
          // Update chart label at minimum
          if (this.chartData.datasets[0]) {
            this.chartData.datasets[0].label = `Category Sales (${this.selectedFrequency})`;
          }
        }
        
      } catch (error) {
        console.warn("Could not get period-specific chart data, using general data");
        // Chart will use the default data
      }
    },

    /**
     * Extract category data from various response formats
     */
    extractCategoryData(response) {
      let categoryData = [];
      
      // Try different response structures
      if (response?.data?.data && Array.isArray(response.data.data)) {
        categoryData = response.data.data;
        console.log("Found categories in response.data.data");
      } else if (response?.data?.items && Array.isArray(response.data.items)) {
        categoryData = response.data.items;
        console.log("Found categories in response.data.items");
      } else if (Array.isArray(response?.data)) {
        categoryData = response.data;
        console.log("Found categories in response.data (array)");
      } else if (Array.isArray(response)) {
        categoryData = response;
        console.log("Found categories directly in response (array)");
      } else if (response?.success && response?.data) {
        // Handle success wrapper
        if (Array.isArray(response.data)) {
          categoryData = response.data;
        } else if (response.data.categories && Array.isArray(response.data.categories)) {
          categoryData = response.data.categories;
        }
        console.log("Found categories in success response");
      }
      
      console.log("Extracted category data:", categoryData);
      console.log("Category data length:", categoryData.length);
      return categoryData;
    },

    /**
     * Client-side filtering by date range (fallback)
     */
    filterCategoriesByDate(categories, dateRange) {
      console.log("=== Client-side Date Filtering ===");
      console.log("Original categories:", categories.length);
      console.log("Date range:", dateRange);
      
      const startDate = new Date(dateRange.start_date);
      const endDate = new Date(dateRange.end_date);
      
      const filteredCategories = categories.filter(category => {
        // Use date_created, last_updated, or any available date field
        const categoryDate = new Date(
          category.date_created || 
          category.last_updated || 
          category.created_at ||
          category.updated_at
        );
        
        if (isNaN(categoryDate.getTime())) {
          // If no valid date, include in results (don't exclude due to missing dates)
          console.warn("Invalid date for category:", category.category_name, "- including in results");
          return true;
        }
        
        const isInRange = categoryDate >= startDate && categoryDate <= endDate;
        
        if (!isInRange) {
          console.log(`Filtering out ${category.category_name} - date ${categoryDate.toISOString()} outside range`);
        }
        
        return isInRange;
      });
      
      console.log("Filtered categories:", filteredCategories.length);
      
      // If filtering results in empty data, show message but keep some data for display
      if (filteredCategories.length === 0) {
        console.warn("No categories found in date range, showing recent data");
        // Return the most recent categories instead of empty results
        return categories.slice(0, 10);
      }
      
      return filteredCategories;
    },

    /**
     * Process category data for all components
     */
    async processCategoryData(categoryData) {
      console.log("=== Processing Category Data ===");
      console.log("Processing", categoryData.length, "categories");
      
     // 1. Process for Top Categories List (top 5) - SORTED BY HIGHEST SALES
    this.topItems = categoryData
      .sort((a, b) => {
        // Get sales amount for category A
        const salesA = a.total_sales || 
                      a.total_net_sales || 
                      a.total_amount || 
                      a.revenue || 
                      a.sales || 0;
        
        // Get sales amount for category B
        const salesB = b.total_sales || 
                      b.total_net_sales || 
                      b.total_amount || 
                      b.revenue || 
                      b.sales || 0;
        
        // Sort in descending order (highest first)
        return salesB - salesA;
      })
      .slice(0, 5) // Take top 5 after sorting
      .map((category, index) => {
        console.log(`Processing top category ${index}:`, category);
        
        return {
          name: category.category_name || 
                category.name || 
                category.item_name || 
                `Category ${index + 1}`,
          price: this.formatCurrency(
            category.total_sales || 
            category.total_net_sales || 
            category.total_amount || 
            category.revenue || 
            category.sales || 
            0
          )
        };
      });
      
      console.log("✅ Top categories processed:", this.topItems);
      
      // 2. Process for Chart Data (top 6 for better visualization)
      this.updateChartData(categoryData.slice(0, 6));
      console.log("✅ Chart data processed");
      
      // 3. Process for Category Table (all categories)
      this.categories = categoryData.map((category, index) => {
        console.log(`Processing table category ${index}:`, category);
        
        // Calculate product count from subcategories
        const productCount = category.subcategories ? category.subcategories.reduce((total, sub) => total + (sub.product_count || 0), 0) : 0;
        
         return {
            id: category._id || category.id || index,
            name: category.category_name || category.name || `Category ${index + 1}`,
            category_name: category.category_name || category.name,
            description: category.description || 'No description available',
            sub_categories: category.subcategories || category.sub_categories || [],
            total_items_sold: category.total_quantity_sold || 
                            category.total_items_sold || 
                            category.items_sold || 
                            category.quantity || 0,
            total_net_sales: category.total_sales || 
                            category.total_net_sales || 
                            category.total_amount || 
                            category.net_sales || 
                            category.revenue || 0,
            product_count: productCount // Now correctly sums subcategory product counts
          };
        });
      console.log("✅ Category table processed:", this.categories.length, "categories");
      
      // Log a sample category for debugging
      if (this.categories.length > 0) {
        console.log("Sample category for table:", this.categories[0]);
      }
    },

    /**
     * Set fallback data when API fails
     */
    setFallbackData() {
      console.log("Setting fallback data...");
      
      // Fallback top items
      this.topItems = [
        { name: 'Noodles', price: '₱15,234.21' },
        { name: 'Drinks', price: '₱5,789.50' },
        { name: 'Toppings', price: '₱4,520.75' },
        { name: 'Snacks', price: '₱3,821.25' }
      ];
      
      // Fallback chart data
      this.setDefaultChartData();
      
      // Fallback table data
      this.categories = [
        {
          id: 1,
          name: 'Noodles',
          description: 'Various noodle dishes',
          sub_categories: ['Ramen', 'Udon', 'Soba'],
          total_items_sold: 450,
          total_net_sales: 15234.21,
          product_count: 12
        },
        {
          id: 2,
          name: 'Drinks',
          description: 'Beverages and drinks',
          sub_categories: ['Hot', 'Cold', 'Alcoholic'],
          total_items_sold: 320,
          total_net_sales: 5789.50,
          product_count: 8
        },
        {
          id: 3,
          name: 'Toppings',
          description: 'Additional toppings',
          sub_categories: ['Meat', 'Vegetables', 'Sauce'],
          total_items_sold: 280,
          total_net_sales: 4520.75,
          product_count: 15
        },
        {
          id: 4,
          name: 'Snacks',
          description: 'Light snacks and appetizers',
          sub_categories: ['Sweet', 'Savory'],
          total_items_sold: 180,
          total_net_sales: 3821.25,
          product_count: 6
        }
      ];
      
      console.log("✅ Fallback data set");
    },

    /**
     * Legacy method for retry button
     */
    async getTopItems() {
      console.log("Retrying category data load...");
      await this.loadAllCategoryData();
    },

    // ================================================================
    // CHART METHODS
    // ================================================================
    
    /**
     * Update chart data with category response
     */
    updateChartData(categories) {
      console.log("Updating chart with categories:", categories);
      
      if (!categories || categories.length === 0) {
        this.setDefaultChartData();
        return;
      }
      
      const colors = this.generateChartColors(categories.length);
      
      this.chartData = {
        labels: categories.map(category => 
          category.category_name || category.name || 'Unknown Category'
        ),
        datasets: [{
          label: `Category Sales (${this.selectedFrequency})`,
          data: categories.map(category => 
            category.total_sales || category.total_net_sales || category.total_amount || 0
          ),
          backgroundColor: colors.background,
          borderColor: colors.border,
          borderWidth: 1
        }]
      };
      
      console.log("Updated chartData:", this.chartData);
    },

    /**
     * Generate colors for chart
     */
    generateChartColors(count) {
      const baseColors = [
        '#ef4444', '#3b82f6', '#eab308', '#22c55e', '#8b5cf6',
        '#f59e0b', '#10b981', '#6366f1', '#f97316', '#84cc16'
      ];
      
      const borderColors = [
        '#dc2626', '#2563eb', '#ca8a04', '#16a34a', '#7c3aed',
        '#d97706', '#059669', '#4f46e5', '#ea580c', '#65a30d'
      ];
      
      const background = [];
      const border = [];
      
      for (let i = 0; i < count; i++) {
        background.push(baseColors[i % baseColors.length]);
        border.push(borderColors[i % borderColors.length]);
      }
      
      return { background, border };
    },

    /**
     * Set default chart data
     */
    setDefaultChartData() {
      this.chartData = {
        labels: ['Noodles', 'Drinks', 'Toppings', 'Snacks'],
        datasets: [{
          label: `Category Sales (${this.selectedFrequency})`,
          data: [15234.21, 5789.50, 4520.75, 3821.25],
          backgroundColor: ['#ef4444', '#3b82f6', '#eab308', '#22c55e'],
          borderColor: ['#dc2626', '#2563eb', '#ca8a04', '#16a34a'],
          borderWidth: 1
        }]
      };
    },

    /**
     * Calculate date range based on frequency
     */
    calculateDateRange(frequency) {
      const now = new Date();
      const end_date = now.toISOString().split('T')[0]; // Today
      let start_date;
      
      switch (frequency) {
        case 'daily':
          // Last 30 days for daily view
          start_date = new Date(now.getTime() - (30 * 24 * 60 * 60 * 1000))
            .toISOString().split('T')[0];
          break;
          
        case 'weekly':
          // Last 12 weeks for weekly view
          start_date = new Date(now.getTime() - (12 * 7 * 24 * 60 * 60 * 1000))
            .toISOString().split('T')[0];
          break;
          
        case 'monthly':
          // Last 12 months for monthly view
          const monthsAgo = new Date(now);
          monthsAgo.setMonth(monthsAgo.getMonth() - 12);
          start_date = monthsAgo.toISOString().split('T')[0];
          break;
          
        case 'yearly':
          // Last 5 years for yearly view
          const yearsAgo = new Date(now);
          yearsAgo.setFullYear(yearsAgo.getFullYear() - 5);
          start_date = yearsAgo.toISOString().split('T')[0];
          break;
          
        default:
          // Default to last 3 months
          const defaultDate = new Date(now);
          defaultDate.setMonth(defaultDate.getMonth() - 3);
          start_date = defaultDate.toISOString().split('T')[0];
      }
      
      return { start_date, end_date };
    },

    /**
     * Handle frequency change - UPDATED: Only affects chart
     */
    async onFrequencyChange() {
      console.log("Frequency changed to:", this.selectedFrequency);
      
      // Show loading state for chart only
      this.loadingChart = true;
      
      try {
        // Calculate new date range
        const dateRange = this.calculateDateRange(this.selectedFrequency);
        this.currentDateRange = dateRange;
        
        console.log("Updating chart only for frequency:", this.selectedFrequency);
        
        // Call API with date parameters for chart data only
        const requestParams = {
          start_date: dateRange.start_date,
          end_date: dateRange.end_date,
          frequency: this.selectedFrequency
        };
        
        let response;
        try {
          response = await CategoryService.CategoryData(requestParams);
        } catch (apiError) {
          console.warn("API doesn't support date filtering, using base call");
          response = await CategoryService.CategoryData();
        }
        
        // Extract and filter data for chart only
        let categoryData = this.extractCategoryData(response);
        
        if (categoryData && categoryData.length > 0) {
          // Apply client-side filtering if needed
          if (!response?.date_filter_applied) {
            categoryData = this.filterCategoriesByDate(categoryData, dateRange);
          }
          
          // Update ONLY the chart (NOT top items or table)
          this.updateChartData(categoryData.slice(0, 6));
          
          console.log("✅ Chart updated for frequency:", this.selectedFrequency);
        } else {
          // Update chart label at minimum
          if (this.chartData.datasets[0]) {
            this.chartData.datasets[0].label = `Category Sales (${this.selectedFrequency})`;
          }
        }
        
      } catch (error) {
        console.error("❌ Error updating chart for frequency change:", error);
        // Just update the label if reload fails
        if (this.chartData.datasets[0]) {
          this.chartData.datasets[0].label = `Category Sales (${this.selectedFrequency})`;
        }
      } finally {
        this.loadingChart = false;
      }
    },

    /**
     * Update only top items and chart (separate from table)
     */
    updateTopItemsAndChart(categoryData) {
      console.log("=== Updating Top Items and Chart Only ===");
      
      // 1. Update Top Categories List (top 5) with period data
      this.topItems = categoryData.slice(0, 5).map((category, index) => ({
        name: category.category_name || 
              category.name || 
              category.item_name || 
              `Category ${index + 1}`,
        price: this.formatCurrency(
          category.total_sales || 
          category.total_net_sales || 
          category.total_amount || 
          category.revenue || 
          category.sales || 
          0
        )
      }));
      
      console.log("✅ Top items updated for period:", this.topItems);
      
      // 2. Update Chart Data with period data
      this.updateChartData(categoryData.slice(0, 6));
      console.log("✅ Chart updated for period");
      
      // Note: Table data remains unchanged - shows all categories
    },

    /**
     * Refresh all data
     */
    async refreshData() {
      console.log("Refreshing all category data...");
      await this.loadAllCategoryData();
    },

    // ================================================================
    // FORMATTING METHODS
    // ================================================================
    
    /**
     * Format currency amount
     */
    formatCurrency(amount) {
      let numericAmount = amount;
      
      if (typeof amount === 'string') {
        numericAmount = parseFloat(amount);
      }
      
      if (typeof numericAmount !== 'number' || isNaN(numericAmount)) {
        numericAmount = 0;
      }
      
      return `₱${numericAmount.toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })}`;
    },

    /**
     * Format number with commas
     */
    formatNumber(number) {
      let numericValue = number;
      
      if (typeof number === 'string') {
        numericValue = parseFloat(number);
      }
      
      if (typeof numericValue !== 'number' || isNaN(numericValue)) {
        return '0';
      }
      
      return numericValue.toLocaleString('en-US');
    },

    /**
     * Format sub-categories for display
     */
    formatSubCategories(subCategories) {
      if (!subCategories || !Array.isArray(subCategories)) {
        return 'None';
      }
      
      if (subCategories.length === 0) {
        return 'None';
      }
      
      // Handle subcategories with name property vs simple strings
      const categoryNames = subCategories.map(sub => {
        if (typeof sub === 'object' && sub.name) {
          return sub.name;
        }
        return sub.toString();
      });
      
      if (categoryNames.length <= 3) {
        return categoryNames.join(', ');
      }
      
      return `${categoryNames.slice(0, 3).join(', ')} +${categoryNames.length - 3} more`;
    },

    // ============ AUTO-REFRESH SYSTEM ============
    toggleAutoRefresh() {
      if (this.autoRefreshEnabled) {
        this.autoRefreshEnabled = false
        this.stopAutoRefresh()
        console.log('Auto-refresh disabled by user')
      } else {
        this.autoRefreshEnabled = true
        this.startAutoRefresh()
        console.log('Auto-refresh enabled by user')
      }
    },
  
    startAutoRefresh() {
      this.stopAutoRefresh() // Clear any existing timers
      
      // Start countdown
      this.countdown = this.autoRefreshInterval / 1000
      this.countdownTimer = setInterval(() => {
        this.countdown--
        if (this.countdown <= 0) {
          this.countdown = this.autoRefreshInterval / 1000
        }
      }, 1000)
      
      // Start auto-refresh timer
      this.autoRefreshTimer = setInterval(() => {
        this.loadAllCategoryData() // Use your existing refresh method
      }, this.autoRefreshInterval)
      
      console.log(`Auto-refresh started (${this.autoRefreshInterval / 1000}s interval)`)
    },
  
    stopAutoRefresh() {
      if (this.autoRefreshTimer) {
        clearInterval(this.autoRefreshTimer)
        this.autoRefreshTimer = null
      }
      
      if (this.countdownTimer) {
        clearInterval(this.countdownTimer)
        this.countdownTimer = null
      }
      
      console.log('Auto-refresh stopped')
    },

    // Emergency reconnect method
    async emergencyReconnect() {
      console.log('Emergency reconnect initiated')
      this.consecutiveErrors = 0
      this.connectionLost = false
      await this.loadAllCategoryData()
      
      if (!this.autoRefreshEnabled) {
        this.autoRefreshEnabled = true
        this.startAutoRefresh()
      }
    },

    // Connection status methods
    getConnectionStatus() {
      if (this.connectionLost) return 'connection-lost'
      if (this.consecutiveErrors > 0) return 'connection-unstable'
      if (this.lastSuccessfulLoad && (Date.now() - this.lastSuccessfulLoad < 60000)) return 'connection-good'
      return 'connection-unknown'
    },

    getConnectionIcon() {
      switch (this.getConnectionStatus()) {
        case 'connection-good': return 'bi bi-wifi text-success'
        case 'connection-unstable': return 'bi bi-wifi-1 text-warning'
        case 'connection-lost': return 'bi bi-wifi-off text-danger'
        default: return 'bi bi-wifi text-muted'
      }
    },

    getConnectionText() {
      switch (this.getConnectionStatus()) {
        case 'connection-good': return 'Connected'
        case 'connection-unstable': return 'Unstable'
        case 'connection-lost': return 'Connection Lost'
        default: return 'Connecting...'
      }
    }
  }
}
</script>

<style scoped>
/* ====================================================================== */
/* MAIN LAYOUT */
/* ====================================================================== */
.SBC-page {
  padding: 0;
  width: 100%;
  max-width: 1600px;
  margin: 0 auto;
}

.TopContainer {
  width: 100%;
  height: 400px;
  display: grid;
  grid-template-columns: 1fr 2px 1fr;
  gap: 20px;
  align-items: start;
  margin-top: 20px;
}

.divider {
  width: 2px;
  height: 100%;
  background-color: #e5e7eb;
  justify-self: center;
}

/* ====================================================================== */
/* TOP CATEGORIES SECTION */
/* ====================================================================== */
.LCL1 {
  display: flex;
  align-items: baseline;
  gap: 250px;
}

.LCL1 h1, .LCL1 h3 {
  margin: 0;
}

.LCL1 h3 {
  color: grey;
  font-size: 20px;
}

.LCL1 h1 {
  color: black;
  font-size: 29px;
  font-weight: bold;
}

.LC-SBC h1 {
  font-weight: bold;
}

.LCL2 {
  list-style-type: none;
  padding-left: 0;
  margin-top: 10px;
}

.LCL2 li {
  color: black;
  height: 30px;
  margin-bottom: 20px;
}

.list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: black;
  margin-bottom: 8px;
  height: 30px;
  padding: 0 10px;
}

.item-name {
  font-weight: 500;
}

.item-price {
  font-weight: bold;
}

/* ====================================================================== */
/* CHART SECTION */
/* ====================================================================== */
.RC-SBC {
  color: black;
}

.RC-SBC h1 {
  font-weight: bold;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.chart-header h1 {
  font-size: 30px;
}

.frequency-dropdown {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background-color: white;
  font-size: 14px;
  color: #6b7280;
  cursor: pointer;
}

.frequency-dropdown:focus {
  outline: none;
  border-color: #3b82f6;
}

.chart-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 150px;
  width: 500px;
  height: 100%;
}

.chart-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  width: 100%;
}

.chart-loading p {
  margin-top: 10px;
  color: #6b7280;
}

/* ====================================================================== */
/* CATEGORY ANALYSIS SECTION */
/* ====================================================================== */
.BottomContainer {
  color: black;
  width: 100%;
  margin-top: 40px;
}

.transaction-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e5e7eb;
}

.header-left h1 {
  margin: 0 0 4px 0;
  font-weight: bold;
}

.date-range-info {
  color: #6b7280;
  font-size: 13px;
}

.date-range-info i {
  margin-right: 4px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.header-actions .btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  padding: 8px 16px;
  border-radius: 6px;
  font-weight: 500;
  transition: all 0.2s;
}

.header-actions .btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* ====================================================================== */
/* TABLE STYLES */
/* ====================================================================== */
.table-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.table {
  margin: 0;
  width: 100%;
}

.table thead th {
  background-color: #567cdc;
  font-weight: 600;
  color: white;
  border-bottom: 2px solid #e5e7eb;
  padding: 12px;
}

.table tbody td {
  padding: 12px;
  vertical-align: middle;
  border-bottom: 1px solid #f3f4f6;
}

.table tbody tr:hover {
  background-color: #f9fafb;
}

.category-name {
  font-weight: 600;
  color: #374151;
}

.category-description {
  color: #6b7280;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sub-categories {
  font-size: 13px;
  color: #6b7280;
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.items-sold, .product-count {
  text-align: center;
  font-weight: 500;
}

.net-sales {
  text-align: right;
}

.total-amount {
  font-weight: bold;
  color: #059669;
}

/* ====================================================================== */
/* LOADING AND EMPTY STATES */
/* ====================================================================== */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.loading-state p {
  margin-top: 16px;
  color: #6b7280;
}

.loading-state-small {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  text-align: center;
}

.loading-state-small p {
  margin-top: 8px;
  color: #6b7280;
}

.spinner-border-sm {
  width: 20px;
  height: 20px;
  border: 2px solid #e5e7eb;
  border-top: 2px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.spinner-border {
  width: 40px;
  height: 40px;
  border: 3px solid #e5e7eb;
  border-top: 3px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.empty-state p {
  margin: 16px 0;
  color: #6b7280;
  font-size: 16px;
}

.empty-state-small {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  text-align: center;
}

.empty-state-small p {
  margin: 8px 0;
  color: #6b7280;
}

/* ====================================================================== */
/* BUTTON STYLES */
/* ====================================================================== */
.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background-color: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #2563eb;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
}

.text-muted {
  color: #6b7280 !important;
}

/* ====================================================================== */
/* RESPONSIVE DESIGN */
/* ====================================================================== */
@media (max-width: 768px) {
  .TopContainer {
    grid-template-columns: 1fr;
    height: auto;
  }
  
  .divider {
    display: none;
  }
  
  .LCL1 {
    gap: 20px;
    flex-direction: column;
    align-items: flex-start;
  }
  
  .chart-container {
    width: 100%;
    height: 300px;
  }
  
  .transaction-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
  
  .header-actions {
    width: 100%;
    justify-content: flex-end;
  }
  
  .table-container {
    overflow-x: auto;
  }
  
  .table {
    min-width: 800px;
  }
  
  .category-description {
    max-width: 150px;
  }
  
  .sub-categories {
    max-width: 120px;
  }
}

@media (max-width: 480px) {
  .LCL1 {
    gap: 10px;
  }
  
  .chart-header h1 {
    font-size: 24px;
  }
  
  .table {
    min-width: 600px;
  }
  
  .btn {
    padding: 6px 12px;
    font-size: 13px;
  }
  
  .header-left h1 {
    font-size: 24px;
  }
  
  .date-range-info {
    font-size: 12px;
  }
}

/* Auto-refresh status indicator */
.auto-refresh-status {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: #f0fdf4;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  border: 1px solid #bbf7d0;
  min-width: 280px;
}

.status-text {
  font-size: 0.875rem;
  color: #16a34a;
  font-weight: 500;
  flex: 1;
}

/* Connection indicator */
.connection-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.connection-good {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: #16a34a;
}

.connection-unstable {
  background: #fefce8;
  border: 1px solid #fde047;
  color: #ca8a04;
}

.connection-lost {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
}

.connection-unknown {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  color: #64748b;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.8125rem;
  border-radius: 0.25rem;
}

.btn-outline-secondary {
  color: #6c757d;
  border: 1px solid #6c757d;
  background-color: transparent;
}

.btn-outline-secondary:hover:not(:disabled) {
  color: #fff;
  background-color: #6c757d;
  border-color: #6c757d;
}

.btn-outline-success {
  color: #10b981;
  border: 1px solid #10b981;
  background-color: transparent;
}

.btn-outline-success:hover:not(:disabled) {
  color: #fff;
  background-color: #10b981;
  border-color: #10b981;
}

/* Spinning icon animation */
.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .auto-refresh-status {
    flex-direction: column;
    text-align: center;
    gap: 0.25rem;
    min-width: auto;
  }

  .connection-indicator {
    order: -1;
  }
}

</style>