<template>
  <div class="dashboard">
    <!-- KPI Cards Grid - First 5 cards -->
    <div class="kpi-grid">
      <KpiCard
        title="Total Profit"
        :value="totalProfit"
        :subtitle="`Updated: ${currentDate}`"
        variant="profit"
        class="profit-card"
      />
      
      <KpiCard
        title="Total Products"
        :value="totalProducts"
        :subtitle="`Updated: ${currentDate}`"
        variant="products"
      />
      
      <KpiCard
        title="Monthly Income"
        :value="formatCurrency(monthlyProfit)"
        :subtitle="`Updated: ${currentMonth}`"
        variant="income"
      />
      
      <KpiCard
        title="Total Sold"
        :value="totalSold"
        :subtitle="`Updated: ${currentDate}`"
        variant="sold"
      />
      
      <KpiCard
        title="Total Orders"
        :value="totalOrders"
        :subtitle="`Updated: ${currentDate}`"
        variant="orders"
      />
    </div>

    <!-- Bottom Section: Chart + Target Sales -->
    <div class="bottom-section">
      <div class="chart-container">
        <div class="chart-section">
          <div class="chart-header">
            <h3>Category Sales Analysis</h3>
            <select v-model="selectedFrequency" @change="onFrequencyChange" class="frequency-dropdown">
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
              <option value="yearly">Yearly</option>
            </select>
          </div>
          
          <!-- Loading state -->
          <div v-if="loadingChart" class="chart-loading">
            <div class="spinner"></div>
            <p>Loading chart data...</p>
          </div>
          
          <!-- Stacked Groups Chart -->
          <StackedGroupsBarChart 
            v-else
            :chartData="stackedGroupsChartData" 
            :selectedFrequency="selectedFrequency"
            size="medium"
            title=""  
            :showLegend="true"
          />
        </div>
      </div>
      
      <div class="target-sales-container">
        <KpiCard
          title="Target Sales"
          value="₱50,000.00"
          subtitle="The target sales are computed from the minimum cost required to trigger a new purchase order"
          variant="target"
          :subtitle="`Updated: ${currentDate}`"
          :show-progress="true"
          :progress-percentage="78"
          :show-button="true"
          button-text="See More"
          @button-click="handleTargetSalesClick"
        />
      </div>
    </div>
  </div>
</template>

<script>
import KpiCard from '../components/dashboard/KpiCard.vue'
import dashboardApiService from '@/services/apiDashboard'
import CategoryService from '@/services/apiCategory' // ✅ ADDED: Missing import
import StackedGroupsBarChart from '../components/common/StackedBarChart.vue' // ✅ FIXED: Correct import

export default {
  name: 'Dashboard',
  components: {
    KpiCard,
    StackedGroupsBarChart // ✅ FIXED: Correct component name
  },
  data() {
    return {
      totalProfit: '₱0.00',
      loading: false,
      error: null,
      totalOrders: 0,
      totalProducts: 0,
      totalSold: 0,
      monthlyProfit: 0,
      selectedFrequency: 'monthly',
      loadingChart: false,
      stackedGroupsChartData: {
        labels: ['Noodles', 'Drinks', 'Toppings', 'Snacks', 'Desserts'],
        datasets: []
      }
    }
  },
  async mounted() {
    await this.getTotalProfit()
    await this.getTotalOrders()
    await this.getTotalProducts()
    await this.getTotalSold()
    await this.getMonthlyProfit()
    await this.loadStackedGroupsData()
    await this.setDefaultStackedGroupsData()
  },
  computed: {
    currentDate() {
      const now = new Date()
      return now.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short', 
        day: '2-digit'
      })
    },
    currentMonth() {
      const now = new Date()
      return now.toLocaleDateString('en-US', {
        month: 'long', 
      })
    },
  },
  methods: {
    handleTargetSalesClick() {
      console.log('Target sales button clicked')
    },

    async getTotalProfit() {
      try {
        this.loading = true
        this.error = null
        const Profit = await dashboardApiService.getTotalProfits()
        this.totalProfit = this.formatCurrency(Profit)
      } catch (error) {
        console.error('Error fetching total profit:', error)
        this.error = 'Failed to load total profit'
        this.totalProfit = '₱0.00'
      } finally {
        this.loading = false
      }
    },

    async getTotalOrders() {
      try {
        this.loading = true
        this.error = null
        const Orders = await dashboardApiService.getTotalOrders()
        this.totalOrders = Orders
      } catch (error) {
        console.error('Error fetching total Orders:', error)
        this.error = 'Failed to load total Orders'
        this.totalOrders = '0'
      } finally {
        this.loading = false
      }
    },

    async getTotalProducts() {
      try {
        this.loading = true
        this.error = null
        const Products = await dashboardApiService.getTotalProducts()
        this.totalProducts = Products
      } catch (error) {
        console.error('Error fetching total Products:', error)
        this.error = 'Failed to load total Products'
        this.totalProducts = '0'
      } finally {
        this.loading = false
      }
    },

    async getTotalSold() {
      try {
        this.loading = true
        this.error = null
        const Sold = await dashboardApiService.getTotalSold()
        this.totalSold = Sold
      } catch (error) {
        console.error('Error fetching total Sold:', error)
        this.error = 'Failed to load total Sold'
        this.totalSold = '0'
      } finally {
        this.loading = false
      }
    },

    async getMonthlyProfit() {
      try {
        this.loading = true
        this.error = null
        const monthly = await dashboardApiService.getMonthlyProfit()
        this.monthlyProfit = monthly
      } catch (error) {
        console.error('Error fetching monthly profit:', error)
        this.error = 'Failed to load monthly profit'
        this.monthlyProfit = 0
      } finally {
        this.loading = false
      }
    },
    
    formatCurrency(amount) {
      if (typeof amount === 'string' && amount.includes('₱')) {
        return amount
      }
      
      const numericAmount = parseFloat(amount) || 0
      return `₱${numericAmount.toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })}`
    },

    async loadStackedGroupsData() {
      try {
        this.loadingChart = true
        
        const response = await CategoryService.CategoryData()
        const categoryData = this.extractCategoryData(response)
        
        if (categoryData && categoryData.length > 0) {
          this.createStackedGroupsData(categoryData)
        } else {
          this.setDefaultStackedGroupsData()
        }
        
      } catch (error) {
        console.error("Error loading stacked groups data:", error)
        this.setDefaultStackedGroupsData()
      } finally {
        this.loadingChart = false
      }
    },

   async setDefaultStackedGroupsData() {
      try {
        const response = await CategoryService.CategoryData()
        
        console.log("API Response for chart:", response)
        
        // Extract categories from response
        let categories = []
        if (response?.data?.categories && Array.isArray(response.data.categories)) {
          categories = response.data.categories
        } else if (response?.categories && Array.isArray(response.categories)) {
          categories = response.categories
        } else {
          console.warn("No categories found in response, using fallback data")
          this.setFallbackChartData()
          return
        }
        
        // Get category names (labels)
        const labels = categories.map(category => category.category_name)
        
        // Get total sales data
        const salesData = categories.map(category => category.total_sales || 0)
        
        // Get total quantity data  
        const quantityData = categories.map(category => category.total_quantity || 0)
        
        // Count subcategories for each category
        const subcategoryCount = categories.map(category => {
          if (category.subcategories && Array.isArray(category.subcategories)) {
            return category.subcategories.length
          }
          return 0
        })
        
        // Count products for each category
        const productCount = categories.map(category => {
          if (category.sub_categories && Array.isArray(category.sub_categories)) {
            return category.sub_categories.reduce((total, subcat) => {
              if (subcat.products && Array.isArray(subcat.products)) {
                return total + subcat.products.length
              }
              return total
            }, 0)
          }
          return 0
        })
        
        console.log("Processed data:", {
          labels,
          salesData,
          quantityData, 
          subcategoryCount,
          productCount
        })
        
        this.stackedGroupsChartData = {
          labels: labels,
          datasets: [
            {
              label: 'Total Sales (₱)',
              data: salesData,
              backgroundColor: '#3b82f6',
              borderColor: '#2563eb',
              borderWidth: 1,
              stack: 'Current'
            },
            {
              label: 'Quantity Sold',
              data: quantityData.map(qty => qty * 10),
              backgroundColor: '#60a5fa',
              borderColor: '#3b82f6',
              borderWidth: 1,
              stack: 'Previous'
            },
      
            {
              label: 'Target Sales',
              data: quantityData.map(sales => sales * 1.5), // 150% of current sales as target
              backgroundColor: '#f59e0b',
              borderColor: '#d97706',
              borderWidth: 1,
              stack: 'Target'
            }
          ]
        }
        
        console.log("Final chart data:", this.stackedGroupsChartData)
        
      } catch (error) {
        console.error("Error fetching chart data:", error)
        this.setFallbackChartData()
      }
    },

    async onFrequencyChange() {
      console.log("Frequency changed to:", this.selectedFrequency)
      await this.loadStackedGroupsData()
    },

    extractCategoryData(response) {
      let categoryData = []
      
      if (response?.data?.data && Array.isArray(response.data.data)) {
        categoryData = response.data.data
      } else if (response?.data?.items && Array.isArray(response.data.items)) {
        categoryData = response.data.items
      } else if (Array.isArray(response?.data)) {
        categoryData = response.data
      } else if (Array.isArray(response)) {
        categoryData = response
      }
      
      return categoryData
    }
  }
}
</script>

<style scoped>
.dashboard {
  padding: 0;
  width: 100%;
  max-width: 1600px;
  margin: 0 auto;
}

.kpi-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  grid-template-rows: repeat(2, 1fr);
  gap: 1.5rem;
  margin-bottom: 2rem;
  width: 100%;
  min-height: 280px;
}

.kpi-grid .profit-card {
  grid-row: 1 / 3;
  grid-column: 1;
}

.kpi-grid .kpi-card:nth-child(2) {
  grid-row: 1;
  grid-column: 2;
}

.kpi-grid .kpi-card:nth-child(3) {
  grid-row: 1;
  grid-column: 3;
}

.kpi-grid .kpi-card:nth-child(4) {
  grid-row: 2;
  grid-column: 2;
}

.kpi-grid .kpi-card:nth-child(5) {
  grid-row: 2;
  grid-column: 3;
}

.bottom-section {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1.5rem;
  width: 100%;
  align-items: stretch;
}

.chart-container {
  width: 100%;
  height: 100%;
}

.chart-section {
  padding: 1.5rem;
  background: #f9fafb;
  border-radius: 8px;
  height: 100%;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.chart-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #374151;
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

.chart-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
}

.spinner {
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

.target-sales-container {
  width: 100%;
  height: 100%;
  display: flex;
}

.target-sales-container .kpi-card {
  flex: 1;
  min-height: 100%;
}

/* Responsive Design */
@media (max-width: 1200px) {
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
    grid-template-rows: repeat(3, 1fr);
    gap: 1.25rem;
  }
  
  .kpi-grid .profit-card {
    grid-row: 1 / 3;
    grid-column: 1;
  }
  
  .kpi-grid .kpi-card:nth-child(2) {
    grid-row: 1;
    grid-column: 2;
  }
  
  .kpi-grid .kpi-card:nth-child(3) {
    grid-row: 2;
    grid-column: 2;
  }
  
  .kpi-grid .kpi-card:nth-child(4) {
    grid-row: 3;
    grid-column: 1;
  }
  
  .kpi-grid .kpi-card:nth-child(5) {
    grid-row: 3;
    grid-column: 2;
  }
  
  .bottom-section {
    grid-template-columns: 1fr;
    gap: 1.25rem;
  }
}

@media (max-width: 900px) {
  .kpi-grid {
    grid-template-columns: 1fr;
    grid-template-rows: repeat(5, auto);
    gap: 1rem;
    min-height: auto;
  }
  
  .kpi-grid .profit-card,
  .kpi-grid .kpi-card:nth-child(2),
  .kpi-grid .kpi-card:nth-child(3),
  .kpi-grid .kpi-card:nth-child(4),
  .kpi-grid .kpi-card:nth-child(5) {
    grid-row: auto;
    grid-column: 1;
  }
  
  .bottom-section {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
}

@media (max-width: 768px) {
  .kpi-grid {
    gap: 1rem;
    margin-bottom: 1.5rem;
  }
}
</style>