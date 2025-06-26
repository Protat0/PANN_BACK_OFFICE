<template>
  <div class="SBC-page">
    <div class="TopContainer">
      <div class="LC-SBC">
        <div class="LCL1">
          <h1 >Top Categories</h1>
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
      
      <div class="RC-SBC">
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
          <PieChartView :chartData="chartData" :selectedFrequency="selectedFrequency" />
        </div>
      </div>
    </div>
    <div class="BottomContainer">
      <h1>Transaction History</h1>
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
          <tr v-for="transaction in transactions" :key="transaction.id">
            <th scope="row">{{ transaction.id }}</th>
            <td>{{ transaction.items }}</td>
            <td>{{ transaction.customer }}</td>
            <td>{{ transaction.timestamp }}</td>
            <td>{{ transaction.paymentMethod }}</td>
            <td>{{ transaction.saleType }}</td>
            <td class="text-success fw-bold">{{ transaction.total }}</td>
            <td>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>

import PieChartView from '@/components/PieChartView.vue';
import 'bootstrap/dist/css/bootstrap.min.css'

// Import Bootstrap JS (optional, for interactive components)
import 'bootstrap/dist/js/bootstrap.bundle.min.js'


export default {
  name: 'SalesByCategory',
  components: {
    PieChartView
  },
  data() {
    return {
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
        },
        {
          id: 2,
          items: 'Beef Noodles, Sprite',
          customer: 'Jane Smith',
          timestamp: '2024-01-15 15:45',
          paymentMethod: 'Card',
          saleType: 'Takeout',
        },
        {
          id: 3,
          items: 'Vegetable Noodles',
          customer: 'Mike Johnson',
          timestamp: '2024-01-15 16:20',
          paymentMethod: 'GCash',
          saleType: 'Delivery',
        }
      ]
    };
  }
}
</script>

<style scoped>
.SBC-page{
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
}

.LC-SBC{
  
}

.LC-SBC h1{ /* Fixed selector - removed the dot */
  font-weight: bold;
}

.RC-SBC{
  color: black;
}

.RC-SBC h1{ /* Fixed selector - removed the dot */
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
</style>