<template>
  <div class="dashboard">
    <!-- KPI Cards Grid - Using CardTemplate with custom sizes -->
    <div class="kpi-grid">
      <!-- Total Profit Card - Tall card spanning 2 rows -->
      <CardTemplate
        size="custom"
        width="100%"
        :min-height="300"
        :padding="20"
        title="Total Profit"
        :value="profitLoading ? 'Loading...' : formattedTotalProfit"
        value-color="primary"
        :subtitle="profitSubtitle"
        border-color="primary"
        border-position="all"
        shadow="md"
        class="profit-card"
      >
        <template #header>
          <div class="card-header-with-change">
            <span v-if="!profitError" class="change-badge positive">Live</span>
            <span v-else class="change-badge negative">Error</span>
          </div>
        </template>
      </CardTemplate>
      
      <!-- Total Products Card -->
      <CardTemplate
        size="custom"
        width="100%"
        :height="140"
        :padding="16"
        title="Total Products"
        :value="productsLoading ? 'Loading...' : totalProducts"
        value-color="success"
        :subtitle="productsLoading ? 'Fetching data...' : `Updated: ${lastUpdated}`"
        border-color="success"
        border-position="all"
        shadow="md"
      >
        <template #header>
          <div class="card-header-with-change">
            <span v-if="!productsError" class="change-badge positive">Live</span>
            <span v-else class="change-badge negative">Error</span>
          </div>
        </template>
      </CardTemplate>
      
      <!-- Monthly Revenue Card -->
      <CardTemplate
        size="custom"
        width="100%"
        :height="140"
        :padding="16"
        title="Monthly Revenue"
        :value="monthlyIncomeLoading ? 'Loading...' : formattedMonthlyRevenue"
        value-color="secondary"
        :subtitle="monthlyRevenueSubtitle"
        border-color="secondary"
        border-position="all"
        shadow="md"
      >
        <template #header>
          <div class="card-header-with-change">
            <span v-if="!monthlyIncomeError" class="change-badge positive">Live</span>
            <span v-else class="change-badge negative">Error</span>
          </div>
        </template>
      </CardTemplate>
      
      <!-- Total Sold Card -->
      <CardTemplate
        size="custom"
        width="100%"
        :height="140"
        :padding="16"
        title="Total Sold"
        :value="totalSold"
        value-color="info"
        subtitle="Updated: May 02, 2025"
        border-color="info"
        border-position="all"
        shadow="md"
      >
        <template #header>
          <div class="card-header-with-change">
            <span class="change-badge positive">+12%</span>
          </div>
        </template>
      </CardTemplate>
      
      <!-- Total Items Sold Card -->
      <CardTemplate
        size="custom"
        width="100%"
        :height="140"
        :padding="16"
        title="Total Items Sold"
        :value="salesStatsLoading ? 'Loading...' : totalOrders"
        value-color="error"
        :subtitle="salesDataSubtitle"
        border-color="error"
        border-position="all"
        shadow="md"
      >
        <template #header>
          <div class="card-header-with-change">
            <span v-if="!salesStatsError" class="change-badge positive">Live</span>
            <span v-else class="change-badge negative">Error</span>
          </div>
        </template>
      </CardTemplate>
    </div>

    <!-- Bottom Section: Target Sales + Product Sale Chart -->
    <div class="bottom-section">
      <div class="chart-container">
        <CardTemplate
          size="custom"
          width="100%"
          :min-height="400"
          :padding="20"
          title="Sales Trend"
          subtitle="Sales over time"
          border-color="neutral"
          border-position="all"
          shadow="md"
        >
          <template #header>
            <div class="chart-header-controls">
              <select v-model="salesSelectedFrequency" @change="onFrequencyChangeHandler" class="frequency-select">
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
                <option value="yearly">Yearly</option>
              </select>
            </div>
          </template>
          
          <template #content>
            <div class="chart-content">
              <canvas ref="chartCanvas" class="chart-canvas"></canvas>
            </div>
          </template>
        </CardTemplate>
      </div>
      
      <div class="target-sales-container">
        <CardTemplate
          size="custom"
          width="100%"
          :min-height="320"
          :padding="20"
          title="Target Sales"
          :value="targetSales"
          value-color="primary"
          subtitle="The target sales are computed from the minimum cost required to trigger a new purchase order"
          border-color="primary"
          border-position="all"
          shadow="lg"
        >
          <template #content>
            <!-- Progress Section -->
            <div class="progress-section">
              <div class="progress-bar">
                <div class="progress-fill" :style="`width: ${targetProgress}%`"></div>
              </div>
              <div class="progress-info">
                <span class="progress-percentage">{{ targetProgress }}%</span>
              </div>
            </div>
          </template>
          
          <template #footer>
            <button 
              class="btn btn-add w-100 mt-3" 
              @click="handleTargetSalesClick"
            >
              See More
            </button>
          </template>
        </CardTemplate>
      </div>
    </div>
  </div>
</template>

<script>
import CardTemplate from '../components/common/CardTemplate.vue'
import SalesChart from '../components/dashboard/SalesChart.vue'
import { formatCurrency, formatNumber } from '@/helpers/currencyHelpers'
import { useProducts } from '@/composables/api/useProducts.js'
import { useSales } from '@/composables/api/useSales.js'
import salesAPIService from '@/services/apiReports.js'

export default {
  name: 'Dashboard',
  components: {
    CardTemplate,
    SalesChart
  },
  setup() {
    const { 
      products, 
      productStats, 
      fetchProducts, 
      initializeProducts,
      loading: productsLoading, 
      error: productsError 
    } = useProducts()

    const {
      totalSalesCount,
      salesStatsLoading,
      salesStatsError,
      loadTotalSalesCount,
      loadTotalSalesCountAllTime,
      totalProfit,
      profitLoading,
      profitError,
      loadTotalProfit,
      loadTotalProfitAllTime,
      monthlyIncome,
      monthlyIncomeLoading,
      monthlyIncomeError,
      loadMonthlyIncome,
      loadCurrentMonthIncome,
      chartData: salesChartData,
      selectedFrequency: salesSelectedFrequency,
      getTopChartItems,
      onFrequencyChange,
      calculateDateRange
    } = useSales()

    return {
      products,
      productStats,
      fetchProducts,
      initializeProducts,
      productsLoading,
      productsError,
      totalSalesCount,
      salesStatsLoading,
      salesStatsError,
      loadTotalSalesCount,
      loadTotalSalesCountAllTime,
      totalProfit,
      profitLoading,
      profitError,
      loadTotalProfit,
      loadTotalProfitAllTime,
      monthlyIncome,
      monthlyIncomeLoading,
      monthlyIncomeError,
      loadMonthlyIncome,
      loadCurrentMonthIncome,
      salesChartData,
      salesSelectedFrequency,
      getTopChartItems,
      onFrequencyChange,
      calculateDateRange
    }
  },
  data() {
    return {
      targetProgress: 78,
      chart: null,
      isUpdatingChart: false, // Prevent recursion in chart updates
      isShowingAllTimeSales: false, // Track if we're showing all-time data due to no last month sales
      isShowingAllTimeProfit: false, // Track if we're showing all-time profit due to no last month profit
      currentMonthPeriod: null, // Track current month period for monthly income
      // Raw data values
      rawData: {
        totalProfit: 78452.23,
        monthlyIncome: 120042,
        totalSold: 12490,
        targetSales: 50000
      }
    }
  },
  computed: {
    // Formatted values for display
    formattedTotalProfit() {
      return formatCurrency(this.totalProfit || 0)
    },
    profitSubtitle() {
      if (this.profitLoading) {
        return 'Fetching data...'
      }
      return this.isShowingAllTimeProfit ? 'All time' : `From ${this.lastMonthPeriod}`
    },
    totalProducts() {
      // Use dynamic data from products API - check multiple sources for total count
      let count = 0
      
      // First try productStats.total (computed from products array)
      if (this.productStats?.total !== undefined) {
        count = this.productStats.total
      }
      // Fallback to direct products array length if productStats not available yet
      else if (this.products && Array.isArray(this.products)) {
        count = this.products.length
      }
      
      return formatNumber(count)
    },
    lastUpdated() {
      return new Date().toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    },
    lastMonthPeriod() {
      const now = new Date()
      const lastMonth = new Date(now.getFullYear(), now.getMonth() - 1, 1)
      return lastMonth.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long'
      })
    },
    salesDataSubtitle() {
      if (this.salesStatsLoading) {
        return 'Fetching data...'
      }
      return this.isShowingAllTimeSales ? 'All time' : `From ${this.lastMonthPeriod}`
    },
    formattedMonthlyRevenue() {
      return formatCurrency(this.monthlyIncome || 0)
    },
    monthlyRevenueSubtitle() {
      if (this.monthlyIncomeLoading) {
        return 'Fetching data...'
      }
      return this.currentMonthPeriod || 'Current month'
    },
    totalSold() {
      return formatNumber(this.rawData.totalSold)
    },
    totalOrders() {
      return formatNumber(this.totalSalesCount)
    },
    targetSales() {
      return formatCurrency(this.rawData.targetSales)
    },
    chartData() {
      // Return a default chart structure to prevent issues during initialization
      return {
        labels: ['Initializing...'],
        datasets: [{
          label: 'Sales',
          data: [0],
          borderColor: 'rgba(59, 130, 246, 1)',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          borderWidth: 3,
          fill: true,
          tension: 0.4
        }]
      }
    }
  },
  // Removed watcher to prevent recursion issues - chart updates are now handled manually
  methods: {
    handleTargetSalesClick() {
      // Target sales button clicked
    },
    /**
     * Generate time-based chart data starting from September
     */
    getTimeBasedChartData() {
      const currentDate = new Date()
      const currentYear = currentDate.getFullYear()
      
      // Get labels based on selected frequency, starting from October
      let labels = []
      
      switch(this.salesSelectedFrequency) {
          case 'daily':
          // Last 7 days
          labels = []
          for (let i = 6; i >= 0; i--) {
            const date = new Date()
            date.setDate(date.getDate() - i)
            labels.push(date.toLocaleDateString('en-US', { weekday: 'short' }))
          }
            break
          case 'weekly':
          // Last 12 weeks starting from October
          labels = []
          for (let i = 11; i >= 0; i--) {
            const weekStart = new Date(currentYear, 9, 1) // October is month 9 (0-indexed)
            weekStart.setDate(weekStart.getDate() - (i * 7))
            const weekNum = Math.ceil((weekStart.getDate()) / 7)
            labels.push(`W${weekNum}`)
          }
            break
          case 'yearly':
          // From 2024 onwards (assuming we start from current year)
          labels = []
          const startYear = currentYear - 2 // Show last 3 years
          for (let year = startYear; year <= currentYear; year++) {
            labels.push(year.toString())
          }
            break
          default: // monthly
          // From October of current year
          labels = []
          const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
          const startMonth = 9 // October (0-indexed)
          
          // Add months from October to current month, or next year if needed
          for (let i = 0; i < 12; i++) {
            const monthIndex = (startMonth + i) % 12
            const yearOffset = Math.floor((startMonth + i) / 12)
            const displayYear = currentYear + yearOffset
            labels.push(`${months[monthIndex]} ${displayYear}`)
            
            // Break if we've reached current month and it's not a full year cycle
            if (monthIndex === currentDate.getMonth() && yearOffset === 0 && i < 11) {
              break
            }
          }
      }
      
      // For now, return empty data - will be populated by real API data
      return {
        labels: labels,
        datasets: [
          {
            label: 'Sales',
            data: new Array(labels.length).fill(0), // Placeholder data
            borderColor: 'rgba(59, 130, 246, 1)',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            borderWidth: 3,
            fill: true,
            tension: 0.4,
            pointBackgroundColor: 'rgba(59, 130, 246, 1)',
            pointBorderColor: '#ffffff',
            pointBorderWidth: 2,
            pointRadius: 6,
            pointHoverRadius: 8
          }
        ]
      }
    },
    /**
     * Aggregate sales data by time period for chart display
     */
    aggregateSalesDataByTime(salesChartData, expectedLabelCount = null) {
      if (!salesChartData || !salesChartData.datasets || !salesChartData.datasets[0]) {
        // Avoid recursion by not calling getTimeBasedChartData()
        const defaultLength = expectedLabelCount || 12 // Default to 12 months
        return new Array(defaultLength).fill(0)
      }
      
      // For now, return the sales data as-is since useSales already handles aggregation
      // In the future, we could implement further aggregation here if needed
      const salesValues = salesChartData.datasets[0].data || []
      const expectedLength = expectedLabelCount || salesValues.length
      
      // If we have fewer data points than expected labels, pad with zeros
      if (salesValues.length < expectedLength) {
        return [...salesValues, ...new Array(expectedLength - salesValues.length).fill(0)]
      }
      
      // If we have more data points than expected labels, take the first N points
      return salesValues.slice(0, expectedLength)
    },
    /**
     * Load time-based sales data for the chart
     */
    async loadTimeBasedSalesData() {
      try {
        // Use the calculateDateRange from useSales composable
        const dateRange = this.calculateDateRange ? this.calculateDateRange(this.salesSelectedFrequency) : null
        
        if (dateRange) {
          // Use the same service that's available in useSales
          // For now, let's use the monthly income data we already have
          if (this.salesSelectedFrequency === 'monthly' && this.monthlyIncome) {
            return this.getMonthlyChartData()
          }
          
          // For other frequencies, we can fall back to the existing method
          return null
        }
      } catch (error) {
        console.error('Failed to load time-based sales data:', error)
        return null
      }
    },
    /**
     * Aggregate sales data by time periods for chart display
     */
    aggregateSalesByTimePeriod(salesData, frequency) {
      if (!salesData || salesData.length === 0) {
        return { labels: [], data: [] }
      }
      
      const currentDate = new Date()
      let labels = []
      let aggregatedData = []
      
      switch (frequency) {
        case 'daily':
          // Last 7 days
          labels = []
          for (let i = 6; i >= 0; i--) {
            const date = new Date()
            date.setDate(date.getDate() - i)
            labels.push(date.toLocaleDateString('en-US', { weekday: 'short' }))
          }
          // For daily, sum all sales for each day (simplified aggregation)
          aggregatedData = new Array(7).fill(0)
          const totalDaily = salesData.reduce((sum, item) => sum + (parseFloat(item.total_sales) || 0), 0)
          aggregatedData.fill(totalDaily / 7) // Distribute evenly for now
          break
          
        case 'weekly':
          // Last 12 weeks
          labels = []
          for (let i = 11; i >= 0; i--) {
            labels.push(`W${12 - i}`)
          }
          aggregatedData = new Array(12).fill(0)
          const totalWeekly = salesData.reduce((sum, item) => sum + (parseFloat(item.total_sales) || 0), 0)
          aggregatedData.fill(totalWeekly / 12) // Distribute evenly for now
          break
          
        case 'monthly':
          // From October to current month
          labels = []
          const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
          const currentYear = currentDate.getFullYear()
          const startMonth = 9 // October
          
          for (let i = 0; i < 12; i++) {
            const monthIndex = (startMonth + i) % 12
            const yearOffset = Math.floor((startMonth + i) / 12)
            const displayYear = currentYear + yearOffset
            labels.push(`${months[monthIndex]} ${displayYear}`)
            
            if (monthIndex === currentDate.getMonth() && yearOffset === 0) {
              break
            }
          }
          
          // For monthly, use actual monthly revenue if available
          aggregatedData = new Array(labels.length).fill(0)
          const totalMonthly = salesData.reduce((sum, item) => sum + (parseFloat(item.total_sales) || 0), 0)
          
          // If we have current month data, use it; otherwise distribute evenly
          if (this.monthlyIncome && this.monthlyIncome > 0) {
            aggregatedData[aggregatedData.length - 1] = this.monthlyIncome // Last month (current)
            const remainingTotal = Math.max(0, totalMonthly - this.monthlyIncome)
            const remainingMonths = Math.max(1, aggregatedData.length - 1)
            for (let i = 0; i < aggregatedData.length - 1; i++) {
              aggregatedData[i] = remainingTotal / remainingMonths
            }
          } else {
            aggregatedData.fill(totalMonthly / aggregatedData.length)
          }
          break
          
        case 'yearly':
          labels = []
          const startYear = currentDate.getFullYear() - 2
          for (let year = startYear; year <= currentDate.getFullYear(); year++) {
            labels.push(year.toString())
          }
          aggregatedData = new Array(labels.length).fill(0)
          const totalYearly = salesData.reduce((sum, item) => sum + (parseFloat(item.total_sales) || 0), 0)
          aggregatedData.fill(totalYearly / labels.length) // Distribute evenly for now
          break
          
        default:
          labels = ['No Data']
          aggregatedData = [0]
      }
      
      return { labels, data: aggregatedData }
    },
    /**
     * Get monthly chart data using the actual monthly revenue
     */
    getMonthlyChartData() {
      const currentDate = new Date()
      const currentYear = currentDate.getFullYear()
      const currentMonth = currentDate.getMonth() // 0-indexed
      const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
      
      console.log('📅 Current date info:', { currentYear, currentMonth, currentMonthName: months[currentMonth] })
      
      // Generate labels from October to current month
      let labels = []
      const startMonth = 9 // October (0-indexed)
      
      // Always start with October of current year
      if (currentMonth >= startMonth) {
        // We're in October or later - show from October to current month
        console.log(`🏷️ Adding months from ${startMonth} to ${currentMonth}`)
        for (let monthIndex = startMonth; monthIndex <= currentMonth; monthIndex++) {
          const label = `${months[monthIndex]} ${currentYear}`
          labels.push(label)
          console.log(`🏷️ Added label: ${label}`)
        }
      } else {
        // We're before October - show from October of previous year to current month
        console.log(`🏷️ Adding months from previous year October to current month`)
        // First, add remaining months from previous year (Oct, Nov, Dec)
        for (let monthIndex = startMonth; monthIndex < 12; monthIndex++) {
          const label = `${months[monthIndex]} ${currentYear - 1}`
          labels.push(label)
          console.log(`🏷️ Added previous year label: ${label}`)
        }
        // Then add months from current year up to current month
        for (let monthIndex = 0; monthIndex <= currentMonth; monthIndex++) {
          const label = `${months[monthIndex]} ${currentYear}`
          labels.push(label)
          console.log(`🏷️ Added current year label: ${label}`)
        }
      }
      
      console.log(`🏷️ Total labels generated: ${labels.length}`, labels)
      
      // Ensure we always have at least one label (fallback)
      if (labels.length === 0) {
        console.log(`🏷️ No labels generated, using fallback`)
        labels = [`Oct ${currentYear}`]
      }
      
      // Create data array with the monthly income
      const data = new Array(labels.length).fill(0)
      
      // Put the monthly income in the appropriate position
      if (this.monthlyIncome && this.monthlyIncome > 0) {
        // If we're in the current month, find its position
        const currentMonthLabel = `${months[currentMonth]} ${currentYear}`
        const currentIndex = labels.indexOf(currentMonthLabel)
        
        if (currentIndex >= 0) {
          data[currentIndex] = this.monthlyIncome
        } else {
          // Fallback: put it in the last position
          data[data.length - 1] = this.monthlyIncome
        }
      }
      
      console.log('📊 Monthly chart data generated:', { 
        labels: labels, 
        data: data, 
        monthlyIncome: this.monthlyIncome,
        labelsLength: labels.length,
        dataLength: data.length
      })
      
      return { labels, data }
    },
    /**
     * Simple method to update chart with monthly data - bypasses reactivity issues
     */
    updateChartWithMonthlyData() {
      if (!this.chart || !this.monthlyIncome) {
        console.log('📊 Chart or monthly income not available')
        return
      }
      
      try {
        // Create simple, static data for October 2025
        const currentYear = 2025
        const labels = ['Oct 2025']
        const data = [this.monthlyIncome]
        
        console.log('📊 Updating chart with simple data:', { labels, data, monthlyIncome: this.monthlyIncome })
        
        // Direct update without reactivity
        if (this.chart.data && this.chart.data.datasets && this.chart.data.datasets[0]) {
          // Clear and set new data directly
          this.chart.data.labels.length = 0
          this.chart.data.labels.push(...labels)
          this.chart.data.datasets[0].data.length = 0
          this.chart.data.datasets[0].data.push(...data)
          
          // Update chart
          this.chart.update('none')
          console.log('📊 Chart updated successfully')
        }
      } catch (error) {
        console.error('📊 Simple chart update failed:', error)
      }
    },
    
    /**
     * Load chart data only - without triggering profit calculations
     */
    async loadChartDataOnly() {
      // Prevent recursion - check flag first
      if (this.isUpdatingChart) {
        console.log('📊 Chart update already in progress, skipping')
        return
      }
      
      // Only update chart if it exists and is properly initialized
      if (!this.chart || !this.chart.data || !this.chart.data.datasets || this.chart.data.datasets.length === 0) {
        console.log('📊 Chart not ready yet, skipping data load')
        return
      }
      
      this.isUpdatingChart = true
      
      try {
        console.log('📊 Starting chart data load for frequency:', this.salesSelectedFrequency)
        
        // For monthly frequency, use the simple update method
        if (this.salesSelectedFrequency === 'monthly' && this.monthlyIncome) {
          this.updateChartWithMonthlyData()
          return
        }
        
        console.log('📊 No valid data to load for current frequency')
        
      } catch (error) {
        console.error('Failed to load chart data only:', error)
      } finally {
        // Always reset the flag after a delay to prevent rapid successive calls
        setTimeout(() => {
          this.isUpdatingChart = false
        }, 100)
      }
    },
    async updateChart() {
      // Prevent recursion by checking if already updating
      if (this.isUpdatingChart) {
        return
      }
      
      this.isUpdatingChart = true
      
      try {
        // Use the chart-only update method to avoid triggering profit calculations
        await this.loadChartDataOnly()
      } catch (error) {
        console.error('Failed to update chart:', error)
        // Fallback: update with just the labels (avoiding recursive calls)
        if (this.chart && !this.isUpdatingChart) {
          try {
            // Use monthly data directly for fallback
            if (this.salesSelectedFrequency === 'monthly') {
              const monthlyData = this.getMonthlyChartData()
              if (monthlyData && monthlyData.labels) {
                this.chart.data.labels = monthlyData.labels
                this.chart.data.datasets[0].data = monthlyData.data
                this.chart.update('none')
              }
            }
          } catch (fallbackError) {
            console.error('Fallback chart update also failed:', fallbackError)
          }
        }
      } finally {
        this.isUpdatingChart = false
      }
    },
    /**
     * Handle frequency change from the dropdown
     */
    async onFrequencyChangeHandler() {
      console.log('🔄 Frequency changed to:', this.salesSelectedFrequency)
      
      // Prevent multiple rapid changes
      if (this.isUpdatingChart) {
        return
      }
      
      try {
        // For monthly frequency, use the simple update method
        if (this.salesSelectedFrequency === 'monthly' && this.monthlyIncome) {
          this.updateChartWithMonthlyData()
        } else {
          // For other frequencies, we could implement similar simple methods
          console.log('📊 Frequency change handled, chart will be updated manually')
        }
      } catch (error) {
        console.error('Failed to handle frequency change:', error)
      }
    },
    async initChart() {
      // Import Chart.js dynamically
      try {
        const { Chart, registerables } = await import('chart.js')
        Chart.register(...registerables)
        
        const ctx = this.$refs.chartCanvas.getContext('2d')
        
        // Initialize chart with stable data structure to prevent Chart.js errors
        const initialData = {
          labels: ['Loading...'],
          datasets: [{
            label: 'Sales',
            data: [0],
            borderColor: 'rgba(59, 130, 246, 1)',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            borderWidth: 3,
            fill: true,
            tension: 0.4,
            pointBackgroundColor: 'rgba(59, 130, 246, 1)',
            pointBorderColor: '#ffffff',
            pointBorderWidth: 2,
            pointRadius: 6,
            pointHoverRadius: 8
          }]
        }
        
        this.chart = new Chart(ctx, {
          type: 'line',
          data: initialData,
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                display: true,
                position: 'bottom',
                labels: {
                  usePointStyle: true,
                  padding: 20,
                  font: {
                    size: 12
                  }
                }
              }
            },
            scales: {
              x: {
                grid: {
                  display: true,
                  color: 'rgba(0, 0, 0, 0.05)'
                },
                ticks: {
                  font: {
                    size: 11,
                    weight: 'bold'
                  },
                  color: '#6b7280'
                }
              },
              y: {
                beginAtZero: true,
                grid: {
                  color: 'rgba(0, 0, 0, 0.05)'
                },
                ticks: {
                  font: {
                    size: 11
                  },
                  color: '#6b7280',
                  callback: function(value) {
                    return '₱' + value.toLocaleString()
                  }
                }
              }
            },
            elements: {
              point: {
                hoverBackgroundColor: 'rgba(59, 130, 246, 1)',
                hoverBorderColor: '#ffffff',
                hoverBorderWidth: 3
              }
            },
            interaction: {
              intersect: false,
              mode: 'index'
            }
          }
        })
      } catch (error) {
        // Fallback: show a simple text message
        this.$refs.chartCanvas.style.display = 'none'
        const fallback = document.createElement('div')
        fallback.innerHTML = `
          <div style="text-align: center; padding: 2rem; color: #6b7280;">
            <p>Chart.js not available. Install chart.js to display charts:</p>
            <code>npm install chart.js</code>
            <br><br>
            <div style="background: #f3f4f6; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
              Sample Sales Data:<br>
              Oct: ₱1,200 | Nov: ₱1,150<br>
              Dec: ₱1,300 | Jan: ₱1,450
            </div>
          </div>
        `
        this.$refs.chartCanvas.parentNode.appendChild(fallback)
      }
    },
    async loadProductsData() {
      try {
        // Use initializeProducts for cleaner initial data loading
        await this.initializeProducts()
        console.log('Products data loaded successfully:', {
          productsCount: this.products?.length || 0,
          productStats: this.productStats
        })
      } catch (error) {
        console.error('Failed to load products data:', error)
        // Fallback to fetchProducts if initializeProducts fails
        try {
          await this.fetchProducts()
          console.log('Products data loaded via fallback method:', {
            productsCount: this.products?.length || 0,
            productStats: this.productStats
          })
        } catch (fallbackError) {
          console.error('Fallback fetchProducts also failed:', fallbackError)
          // The error is already handled by the useProducts composable
          // and will be reflected in the productsError reactive variable
        }
      }
    },
    async loadSalesData() {
      try {
        // Calculate last month's date range for reference
        const now = new Date()
        const startOfLastMonth = new Date(now.getFullYear(), now.getMonth() - 1, 1)
        const endOfLastMonth = new Date(now.getFullYear(), now.getMonth(), 0) // Last day of previous month
        
        // Format dates for API (YYYY-MM-DD format)
        const startDate = startOfLastMonth.toISOString().split('T')[0]
        const endDate = endOfLastMonth.toISOString().split('T')[0]
        
        console.log('Loading sales data - checking both last month and all-time:', { startDate, endDate })
        
        // Load the last month's sales count
        await this.loadTotalSalesCount(startDate, endDate)
        const lastMonthCount = this.totalSalesCount
        
        console.log('Last month sales count:', { 
          totalSales: lastMonthCount, 
          period: `${startDate} to ${endDate}` 
        })
        
        // Load all-time count for comparison
        console.log('🔍 Loading all-time sales count for comparison...')
        await this.loadTotalSalesCountAllTime()
        const allTimeCount = this.totalSalesCount
        
        console.log('🔍 COMPARISON:', {
          lastMonth: `${lastMonthCount} items sold (${startDate} to ${endDate})`,
          allTime: `${allTimeCount} items sold (no date filter)`,
          difference: `${allTimeCount - lastMonthCount} items sold in other periods`
        })
        
        // Use all-time count if last month shows 0, otherwise use last month
        if (lastMonthCount > 0) {
          console.log('✅ Using last month count:', lastMonthCount)
          this.totalSalesCount = lastMonthCount
          this.isShowingAllTimeSales = false
        } else {
          console.log('⚠️ Last month had no sales, using all-time count:', allTimeCount)
          this.totalSalesCount = allTimeCount
          this.isShowingAllTimeSales = true
        }
        
        // Also load profit data with the same date range
        console.log('💰 Loading profit data for same period...')
        await this.loadTotalProfit(startDate, endDate)
        const lastMonthProfit = this.totalProfit
        
        console.log('Last month profit:', lastMonthProfit)
        
        // Load all-time profit for comparison
        console.log('💰 Loading all-time profit for comparison...')
        await this.loadTotalProfitAllTime()
        const allTimeProfit = this.totalProfit
        
        console.log('💰 COMPARISON:', {
          lastMonth: `${lastMonthProfit} profit (${startDate} to ${endDate})`,
          allTime: `${allTimeProfit} profit (no date filter)`,
          difference: `${allTimeProfit - lastMonthProfit} profit in other periods`
        })
        
        // Use all-time profit if last month shows 0, otherwise use last month
        if (lastMonthProfit > 0) {
          console.log('✅ Using last month profit:', lastMonthProfit)
          // Restore the last month profit value
          this.totalProfit = lastMonthProfit
          this.isShowingAllTimeProfit = false
        } else {
          console.log('⚠️ Last month had no profit, using all-time profit:', allTimeProfit)
          // Keep the all-time profit value (already set)
          this.isShowingAllTimeProfit = true
        }
        
        // Load current month's revenue (separate from the last month date range used for sales/profit)
        console.log('💵 Loading current month revenue...')
        await this.loadCurrentMonthIncome()
        
        // Set the current month period for the subtitle
        const currentDate = new Date()
        const currentMonth = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1)
        this.currentMonthPeriod = currentMonth.toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'long'
        })
        
        console.log('✅ Monthly revenue loaded:', this.monthlyIncome, 'for', this.currentMonthPeriod)
        
      } catch (error) {
        console.error('Failed to load sales data:', error)
      }
    }
  },
  async mounted() {
    // Load products and sales data when component mounts
    await Promise.all([
      this.loadProductsData(),
      this.loadSalesData()
    ])
    
    // Initialize chart after a short delay to ensure DOM is ready
    this.$nextTick(() => {
      setTimeout(async () => {
        try {
          await this.initChart()
          console.log('📊 Chart initialized successfully')
          
          // Load chart data only after chart is properly initialized and monthly income is available
          setTimeout(() => {
            if (this.chart && this.monthlyIncome && this.salesSelectedFrequency === 'monthly') {
              console.log('📊 Loading initial chart data with simple method...')
              try {
                this.updateChartWithMonthlyData()
              } catch (error) {
                console.error('Failed to load chart data after init:', error)
              }
            }
          }, 500) // Longer delay to ensure chart is fully ready
        } catch (error) {
          console.error('Failed to initialize chart:', error)
        }
      }, 200) // Longer initial delay
    })
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
  grid-template-rows: repeat(2, 140px); /* Fixed row height */
  gap: 1.5rem;
  margin-bottom: 2rem;
  width: 100%;
}

/* Total Profit card spans 2 rows - adjust height accordingly */
.kpi-grid .profit-card {
  grid-row: 1 / 3;
  grid-column: 1;
  height: calc(280px + 1.5rem); /* Two rows + gap */
}

/* Other cards positioning */
.kpi-grid .card-template:nth-child(2) { /* Total Products */
  grid-row: 1;
  grid-column: 2;
}

.kpi-grid .card-template:nth-child(3) { /* Monthly Income */
  grid-row: 1;
  grid-column: 3;
}

.kpi-grid .card-template:nth-child(4) { /* Total Sold */
  grid-row: 2;
  grid-column: 2;
}

.kpi-grid .card-template:nth-child(5) { /* Total Orders */
  grid-row: 2;
  grid-column: 3;
}

/* Bottom section with chart and target sales side by side */
.bottom-section {
  display: grid;
  grid-template-columns: 2fr 1fr; /* Chart takes 2/3, Target Sales takes 1/3 */
  gap: 1.5rem;
  width: 100%;
  align-items: stretch; /* Ensures both items have same height */
}

.chart-container {
  width: 100%;
  height: 100%;
}

.target-sales-container {
  width: 100%;
  height: 100%;
  display: flex;
}

.target-sales-container .card-template {
  flex: 1;
  min-height: 100%;
}

/* ==========================================================================
   CUSTOM SIZE OVERRIDE FOR KPI CARDS
   CHART HEADER CONTROLS
   ========================================================================== */
.chart-header-controls {
  display: flex;
  justify-content: flex-end;
  width: 100%;
}

.frequency-select {
  padding: 0.5rem 0.75rem;
  border: 2px solid var(--border-primary);
  border-radius: 8px;
  color: var(--text-primary);
  background-color: var(--surface-primary);
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 100px;
}

.frequency-select:focus {
  outline: none;
  border-color: var(--border-accent);
  box-shadow: 0 0 0 3px rgba(160, 123, 227, 0.25);
}

.frequency-select:hover {
  border-color: var(--border-accent);
}

.card-header-with-change {
  display: flex;
  justify-content: flex-end;
  align-items: flex-start;
  width: 100%;
  margin-bottom: -8px; /* Reduce spacing */
}

.change-badge {
  padding: 0.25rem 0.5rem; /* Reduced from 0.375rem 0.75rem */
  border-radius: 6px; /* Reduced from 8px */
  font-size: 0.7rem; /* Reduced from 0.8rem */
  font-weight: 700;
  white-space: nowrap;
  border: 1px solid transparent;
  position: relative;
  z-index: 2;
}

.change-badge.positive {
  background-color: var(--success-light);
  color: var(--success-dark);
  border-color: var(--success);
}

.change-badge.negative {
  background-color: var(--error-light);
  color: var(--error-dark);
  border-color: var(--error);
}

.change-badge.neutral {
  background-color: var(--neutral-light);
  color: var(--neutral-dark);
  border-color: var(--neutral);
}

/* ==========================================================================
   PROGRESS SECTION STYLING
   ========================================================================== */
.progress-section {
  margin-top: 1.5rem;
  margin-bottom: 1rem;
}

.progress-bar {
  width: 100%;
  height: 12px;
  background-color: var(--surface-tertiary);
  border-radius: 8px;
  border: 1px solid var(--border-primary);
  overflow: hidden;
  margin-bottom: 1rem;
  position: relative;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary), var(--secondary));
  border-radius: 6px;
  transition: width 0.6s ease;
  position: relative;
}

.progress-fill::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.progress-info {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 0.5rem;
}

.progress-percentage {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--primary);
}

/* ==========================================================================
   CHART.JS CANVAS STYLING
   ========================================================================== */
.chart-content {
  display: flex;
  flex-direction: column;
  height: 300px;
  margin-top: 1rem;
}

.chart-canvas {
  width: 100% !important;
  height: 100% !important;
}

.kpi-grid .card-template .card-title {
  font-size: 0.85rem !important; /* Smaller title */
  margin-bottom: 0.75rem !important;
  line-height: 1.3 !important;
}

.kpi-grid .card-template .card-value {
  font-size: 1.5rem !important; /* Smaller value */
  margin-bottom: 0.5rem !important;
  line-height: 1.1 !important;
}

.kpi-grid .card-template .card-subtitle {
  font-size: 0.75rem !important; /* Smaller subtitle */
  line-height: 1.4 !important;
}

/* Profit card gets larger text since it has more space */
.profit-card .card-title {
  font-size: 1rem !important;
}

.profit-card .card-value {
  font-size: 2rem !important;
}

.profit-card .card-subtitle {
  font-size: 0.85rem !important;
}
/* ==========================================================================
   CARD DECORATIVE ELEMENTS
   Add subtle corner decorations similar to original KPI cards
   ========================================================================== */
.card-template {
  position: relative;
  overflow: hidden;
}

.card-template::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 50px; /* Reduced from 60px */
  height: 50px; /* Reduced from 60px */
  opacity: 0.08;
  border-radius: 0 0 0 50px; /* Adjusted radius */
  z-index: 1;
  pointer-events: none;
}

/* Color-specific decorations */
.card-template.border-primary::before {
  background: linear-gradient(135deg, var(--primary-light), var(--primary-light));
}

.card-template.border-success::before {
  background: linear-gradient(135deg, var(--success-light), var(--success-light));
}

.card-template.border-secondary::before {
  background: linear-gradient(135deg, var(--secondary-light), var(--secondary-light));
}

.card-template.border-info::before {
  background: linear-gradient(135deg, var(--info-light), var(--info-light));
}

.card-template.border-error::before {
  background: linear-gradient(135deg, var(--error-light), var(--error-light));
}

/* ==========================================================================
   RESPONSIVE DESIGN
   ========================================================================== */
@media (max-width: 1200px) {
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
    grid-template-rows: repeat(3, 140px); /* Fixed heights */
    gap: 1.25rem;
  }
  
  .kpi-grid .profit-card {
    grid-row: 1 / 3;
    grid-column: 1;
    height: calc(280px + 1.25rem); /* Adjusted for new gap */
  }
  
  .kpi-grid .card-template:nth-child(2) { /* Total Products */
    grid-row: 1;
    grid-column: 2;
  }
  
  .kpi-grid .card-template:nth-child(3) { /* Monthly Income */
    grid-row: 2;
    grid-column: 2;
  }
  
  .kpi-grid .card-template:nth-child(4) { /* Total Sold */
    grid-row: 3;
    grid-column: 1;
  }
  
  .kpi-grid .card-template:nth-child(5) { /* Total Orders */
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
    grid-template-rows: repeat(5, 160px); /* Fixed heights for mobile */
    gap: 1rem;
    min-height: auto;
  }
  
  .kpi-grid .profit-card,
  .kpi-grid .card-template:nth-child(2),
  .kpi-grid .card-template:nth-child(3),
  .kpi-grid .card-template:nth-child(4),
  .kpi-grid .card-template:nth-child(5) {
    grid-row: auto;
    grid-column: 1;
    height: 160px !important; /* Fixed height for all cards on mobile */
  }
  
  .bottom-section {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
}

@media (max-width: 768px) {
  .dashboard {
    padding: 0 0.5rem;
  }
  
  .kpi-grid {
    gap: 1rem;
    margin-bottom: 1.5rem;
  }
  
  .progress-section {
    margin-top: 1rem;
  }
  
  .change-badge {
    font-size: 0.75rem;
    padding: 0.25rem 0.5rem;
  }
  
  /* Chart responsive adjustments */
  .chart-bars {
    padding: 0 0.5rem 1rem;
    min-height: 150px;
  }
  
  .bar {
    width: 16px;
  }
  
  .chart-legend {
    grid-template-columns: repeat(2, 1fr);
    gap: 0.5rem;
  }
  
  .legend-item {
    padding: 0.375rem;
    font-size: 0.7rem;
  }
}

@media (max-width: 480px) {
  .card-header-with-change {
    justify-content: center;
    margin-bottom: 0.5rem;
  }
  
  .change-badge {
    font-size: 0.7rem;
  }
  
  .progress-bar {
    height: 10px;
  }
  
  .progress-percentage {
    font-size: 0.85rem;
  }
  
  /* Chart mobile adjustments */
  .chart-legend {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }
  
  .bar {
    width: 14px;
  }
  
  .period-label {
    font-size: 0.7rem;
  }
  
  .frequency-select {
    font-size: 0.8rem;
    padding: 0.4rem 0.6rem;
    min-width: 90px;
  }
}

/* ==========================================================================
   ENHANCED VISUAL EFFECTS
   ========================================================================== */
.card-template:hover {
  transform: translateY(-2px);
  transition: all 0.3s ease;
}

.card-template:hover::before {
  opacity: 0.12;
  transition: opacity 0.3s ease;
}

/* Button styling override for target sales */
.target-sales-container .btn {
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  border: 1px solid var(--primary);
  transition: all 0.3s ease;
}

.target-sales-container .btn:hover {
  background: linear-gradient(135deg, var(--primary-dark), var(--secondary-dark));
  border-color: var(--primary-dark);
  transform: translateY(-1px);
}
</style>