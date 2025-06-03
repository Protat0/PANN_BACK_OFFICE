<template>
  <div class="dashboard">
    <!-- KPI Cards Grid - First 5 cards -->
    <div class="kpi-grid">
      <KpiCard
        title="Total Profit"
        value="₱78,452.23"
        subtitle="From the last month"
        change="+24%"
        change-type="positive"
        variant="profit"
        class="profit-card"
      />
      
      <KpiCard
        title="Total Products"
        value="56"
        subtitle="Updated: May 02, 2025"
        change="+24%"
        change-type="positive"
        variant="products"
      />
      
      <KpiCard
        title="Monthly Income"
        value="₱120,042"
        subtitle="Updated: May 02, 2025"
        change="+15%"
        change-type="positive"
        variant="income"
      />
      
      <KpiCard
        title="Total Sold"
        value="12,490"
        subtitle="Updated: May 02, 2025"
        change="+12%"
        change-type="positive"
        variant="sold"
      />
      
      <KpiCard
        title="Total Orders"
        value="123"
        subtitle="Updated: May 02, 2025"
        change="+14%"
        change-type="positive"
        variant="orders"
      />
    </div>

    <!-- Bottom Section: Target Sales + Product Sale Chart -->
    <div class="bottom-section">
      <div class="chart-container">
        <SalesChart />
      </div>
      
      <div class="target-sales-container">
        <KpiCard
          title="Target Sales"
          value="₱50,000.00"
          subtitle="The target sales are computed from the minimum cost required to trigger a new purchase order"
          variant="target"
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
import SalesChart from '../components/dashboard/SalesChart.vue'

export default {
  name: 'Dashboard',
  components: {
    KpiCard,
    SalesChart
  },
  methods: {
    handleTargetSalesClick() {
      console.log('Target sales button clicked')
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

/* Total Profit card spans 2 rows */
.kpi-grid .profit-card {
  grid-row: 1 / 3;
  grid-column: 1;
}

/* Other cards positioning */
.kpi-grid .kpi-card:nth-child(2) { /* Total Products */
  grid-row: 1;
  grid-column: 2;
}

.kpi-grid .kpi-card:nth-child(3) { /* Monthly Income */
  grid-row: 1;
  grid-column: 3;
}

.kpi-grid .kpi-card:nth-child(4) { /* Total Sold */
  grid-row: 2;
  grid-column: 2;
}

.kpi-grid .kpi-card:nth-child(5) { /* Total Orders */
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
  
  .kpi-grid .kpi-card:nth-child(2) { /* Total Products */
    grid-row: 1;
    grid-column: 2;
  }
  
  .kpi-grid .kpi-card:nth-child(3) { /* Monthly Income */
    grid-row: 2;
    grid-column: 2;
  }
  
  .kpi-grid .kpi-card:nth-child(4) { /* Total Sold */
    grid-row: 3;
    grid-column: 1;
  }
  
  .kpi-grid .kpi-card:nth-child(5) { /* Total Orders */
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
  .dashboard-header h1 {
    font-size: 1.875rem;
  }
  
  .subtitle {
    font-size: 0.95rem;
  }
  
  .kpi-grid {
    gap: 1rem;
    margin-bottom: 1.5rem;
  }
  
  .charts-section {
    margin-top: 1.5rem;
  }
}
</style>