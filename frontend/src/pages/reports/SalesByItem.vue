<template>
  <div class="SBI-page">
    <div class="TopContainer">
      <div class="LC-SBI">
        <div class="LCL1">
          <h1>Top Five Items</h1>
          <h3>Net Sales</h3>
        </div>
        <ul class="LCL2">
          <li v-for="(item, index) in topItems" :key="index" class="list-item">
            <span class="item-name" style="font-weight:bold; font-size: 25px;">{{ item.name }}</span>
            <span class="item-price" style="color:green; font-size: 15px;">{{ item.price }}</span>
          </li>
        </ul>
      </div>
      
      <div class="divider"></div>
      
      <div class="RC-SBI">
        <div class="chart-header">
          <h1>Sales Chart</h1>
          <select v-model="selectedFrequency" class="frequency-dropdown">
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
            <option value="yearly">Yearly</option>
          </select>
        </div>
        <div class="chart-container">
          <BarChart :chartData="chartData" :selectedFrequency="selectedFrequency" />
        </div>
      </div>
    </div>
    <div class="BottomContainer">
      <div class="transaction-header">
        <h1>Transaction History</h1>
        <div class="header-actions">
          <button class="btn btn-primary" @click="importData">
            <i class="bi bi-upload"></i> Import
          </button>
          <button class="btn btn-success" @click="exportData">
            <i class="bi bi-download"></i> Export
          </button>
          <button class="btn btn-warning" @click="refreshData" :disabled="loading">
            <i class="bi bi-arrow-clockwise"></i> {{ loading ? 'Loading...' : 'Refresh' }}
          </button>
        </div>
      </div>
      
      <table class="table table-striped">
        <thead>
          <tr>
            <th scope="col">ID</th>
            <th scope="col">Items</th>
            <th scope="col">Customer</th>
            <th scope="col">Timestamp</th>
            <th scope="col">Payment Method</th>
            <th scope="col">Sale Type</th>
            <th scope="col">Total</th>
            <th scope="col">Actions</th>
          </tr>
        </thead>
        <tbody class="table-group-divider">
          <tr v-for="transaction in transactions" :key="transaction.id">
            <th scope="row">{{ transaction.id }}</th>
            <td>{{ transaction.items }}</td>
            <td>{{ transaction.customer }}</td>
            <td>{{ transaction.timestamp }}</td>
            <td>{{ transaction.paymentMethod }}</td>
            <td>{{ transaction.saleType }}</td>
            <td class="text-success fw-bold">{{ transaction.total }}</td>
            <td>
              <button class="btn btn-sm btn-outline-primary">View</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import BarChart from '@/components/BarChart.vue';

export default {
  name: 'SalesByItem',
  components: {
    BarChart  // Register the component here
  },
  data() {
    return {
      loading: false,
      selectedFrequency: 'monthly',
      topItems: [
        { name: 'Noodles', price: '₱15,234.21' },
        { name: 'Drinks', price: '₱5,789.50' },
        { name: 'Toppings', price: '₱4,520.75' },
        { name: 'Snacks', price: '₱3,821.25' }
      ],
      chartData: {
        labels: ['Noodles', 'Drinks', 'Toppings', 'Snacks'],
        datasets: [{
          label: 'Sales Amount',
          data: [15234.21, 5789.50, 4520.75, 3821.25],
          backgroundColor: ['#ef4444', '#3b82f6', '#eab308', '#22c55e'],
          borderColor: ['#dc2626', '#2563eb', '#ca8a04', '#16a34a'],
          borderWidth: 1
        }]
      },
      transactions: [
        {
          id: 1,
          items: 'Chicken Noodles, Coke',
          customer: 'John Doe',
          timestamp: '2024-01-15 14:30',
          paymentMethod: 'Cash',
          saleType: 'Dine-in',
          total: '₱250.00'
        },
        {
          id: 2,
          items: 'Beef Noodles, Sprite',
          customer: 'Jane Smith',
          timestamp: '2024-01-15 15:45',
          paymentMethod: 'Card',
          saleType: 'Takeout',
          total: '₱320.00'
        },
        {
          id: 3,
          items: 'Vegetable Noodles',
          customer: 'Mike Johnson',
          timestamp: '2024-01-15 16:20',
          paymentMethod: 'GCash',
          saleType: 'Delivery',
          total: '₱180.00'
        }
      ]
    };
  },
  methods: {
    importData() {
      console.log('Import data functionality');
      // Add your import logic here
    },
    exportData() {
      console.log('Export data functionality');
      // Add your export logic here
    },
    refreshData() {
      this.loading = true;
      console.log('Refresh data functionality');
      // Simulate loading
      setTimeout(() => {
        this.loading = false;
      }, 1000);
    }
  }
}
</script>

<style scoped>
.SBI-page{
  padding: 0;
  width: 100%;
  max-width: 1600px;
  margin: 0 auto;
}

.TopContainer{
  width: 100%;
  height: 400px;
  display: grid;
  grid-template-columns: 1fr 2px 1fr; /* Left column, divider, right column */
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

.LCL1{
  display: flex;
  align-items: baseline; /* Aligns text baselines */
  gap: 250px; /* Space between h1 and h2 */
}

.LCL1 h1, .LCL1 h3{
  margin: 0; /* Removes default margins */
}

.LCL1 h3{
  color: grey;
  font-size: 20px;
}

.LCL1 h1{
  color: black;
  font-size: 30px;
  font-weight: bold;
}

.LC-SBI h1{ /* Fixed selector - removed the dot */
  font-weight: bold;
}

.RC-SBI{
  color: black;
}

.RC-SBI h1{ /* Fixed selector - removed the dot */
  font-weight: bold;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.chart-header h1{
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
  width: 500px;   /* Set desired width */
  height: 100%;
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

.BottomContainer{
  height: 250px;
  color: black;
  width: 100%;
}

.transaction-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.transaction-header h1 {
  margin: 0;
  font-weight: bold;
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
 
}
</style>