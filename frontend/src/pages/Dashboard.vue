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
        :value="totalProfit"
        value-color="primary"
        subtitle="From the last month"
        border-color="primary"
        border-position="all"
        shadow="md"
        class="profit-card"
      >
        <template #header>
          <div class="card-header-with-change">
            <span class="change-badge positive">+24%</span>
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
        :value="totalProducts"
        value-color="success"
        subtitle="Updated: May 02, 2025"
        border-color="success"
        border-position="all"
        shadow="md"
      >
        <template #header>
          <div class="card-header-with-change">
            <span class="change-badge positive">+24%</span>
          </div>
        </template>
      </CardTemplate>
      
      <!-- Monthly Income Card -->
      <CardTemplate
        size="custom"
        width="100%"
        :height="140"
        :padding="16"
        title="Monthly Income"
        :value="monthlyIncome"
        value-color="secondary"
        subtitle="Updated: May 02, 2025"
        border-color="secondary"
        border-position="all"
        shadow="md"
      >
        <template #header>
          <div class="card-header-with-change">
            <span class="change-badge positive">+15%</span>
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
      
      <!-- Total Orders Card -->
      <CardTemplate
        size="custom"
        width="100%"
        :height="140"
        :padding="16"
        title="Total Orders"
        :value="totalOrders"
        value-color="error"
        subtitle="Updated: May 02, 2025"
        border-color="error"
        border-position="all"
        shadow="md"
      >
        <template #header>
          <div class="card-header-with-change">
            <span class="change-badge positive">+14%</span>
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
          title="Product Sale"
          subtitle="Sales performance by category"
          border-color="neutral"
          border-position="all"
          shadow="md"
        >
          <template #header>
            <div class="chart-header-controls">
              <select v-model="selectedFrequency" @change="updateChart" class="frequency-select">
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

export default {
  name: 'Dashboard',
  components: {
    CardTemplate,
    SalesChart
  },
  data() {
    return {
      targetProgress: 78,
      // Raw data values
      rawData: {
        totalProfit: 78452.23,
        totalProducts: 56,
        monthlyIncome: 120042,
        totalSold: 12490,
        totalOrders: 123,
        targetSales: 50000
      }
    }
  },
  computed: {
    // Formatted values for display
    totalProfit() {
      return formatCurrency(this.rawData.totalProfit)
    },
    totalProducts() {
      return formatNumber(this.rawData.totalProducts)
    },
    monthlyIncome() {
      return formatCurrency(this.rawData.monthlyIncome)
    },
    totalSold() {
      return formatNumber(this.rawData.totalSold)
    },
    totalOrders() {
      return formatNumber(this.rawData.totalOrders)
    },
    targetSales() {
      return formatCurrency(this.rawData.targetSales)
    }
  },
  methods: {
    handleTargetSalesClick() {
      console.log('Target sales button clicked')
    },
    updateChart() {
      console.log('Updating chart for frequency:', this.selectedFrequency)
      // Update chart data based on frequency
      if (this.chart) {
        // Sample data changes based on frequency
        let newData = []
        switch(this.selectedFrequency) {
          case 'daily':
            this.chart.data.labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
            newData = [
              [45, 42, 38, 50, 48],
              [35, 32, 28, 40, 38], 
              [25, 22, 18, 30, 28],
              [15, 12, 8, 20, 18]
            ]
            break
          case 'weekly':
            this.chart.data.labels = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
            newData = [
              [180, 170, 160, 200],
              [140, 130, 120, 160],
              [100, 90, 80, 120],
              [60, 50, 40, 80]
            ]
            break
          case 'yearly':
            this.chart.data.labels = ['2021', '2022', '2023', '2024']
            newData = [
              [1200, 1400, 1600, 1800],
              [900, 1100, 1300, 1500],
              [600, 800, 1000, 1200],
              [300, 500, 700, 900]
            ]
            break
          default: // monthly
            this.chart.data.labels = ['JAN', 'FEB', 'MAR', 'APR']
            newData = [
              [300, 280, 250, 350],
              [220, 200, 180, 240],
              [170, 160, 150, 190],
              [130, 120, 110, 140]
            ]
        }
        
        // Update datasets
        this.chart.data.datasets.forEach((dataset, index) => {
          dataset.data = newData[index]
        })
        
        this.chart.update()
      }
    },
    async initChart() {
      // Import Chart.js dynamically
      try {
        const { Chart, registerables } = await import('chart.js')
        Chart.register(...registerables)
        
        const ctx = this.$refs.chartCanvas.getContext('2d')
        
        this.chart = new Chart(ctx, {
          type: 'bar',
          data: this.chartData,
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
                  display: false
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
                  color: '#f3f4f6'
                },
                ticks: {
                  font: {
                    size: 11
                  },
                  color: '#6b7280'
                }
              }
            },
            elements: {
              bar: {
                borderRadius: 4,
                borderSkipped: false
              }
            }
          }
        })
      } catch (error) {
        console.error('Failed to load Chart.js:', error)
        // Fallback: show a simple text message
        this.$refs.chartCanvas.style.display = 'none'
        const fallback = document.createElement('div')
        fallback.innerHTML = `
          <div style="text-align: center; padding: 2rem; color: #6b7280;">
            <p>Chart.js not available. Install chart.js to display charts:</p>
            <code>npm install chart.js</code>
            <br><br>
            <div style="background: #f3f4f6; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
              Sample Data:<br>
              Noodles: 300, 280, 250, 350<br>
              Toppings: 220, 200, 180, 240<br>
              Snacks: 170, 160, 150, 190<br>
              Drinks: 130, 120, 110, 140
            </div>
          </div>
        `
        this.$refs.chartCanvas.parentNode.appendChild(fallback)
      }
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