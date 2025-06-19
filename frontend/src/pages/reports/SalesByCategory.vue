<template>
  <div class="SBC-page">
    <div class="TopContainer">
      <div class="LC-SBC">
        <div class="LCL1">
          <h1>Top 5 Categories</h1>
          <h3>Net Sales</h3>
        </div>
        <ul class="LCL2">
          <li v-for="(item, index) in topItems" :key="index" class="list-item">
            <span class="item-name">{{ item.name }}</span>
            <span class="item-price">{{ item.price }}</span>
          </li>
        </ul>

      </div>
      <div class="RC-SBC">
        <h1>Sales Chart</h1>
      </div>
    </div>
    <div class="BottomContainer">
      <h1>Transaction History</h1>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SalesByCategory',
  data() {
    return {
      topItems: [
        { name: 'Noodles', price: '₱1200' },
        { name: 'Drinks', price: '₱800' },
        { name: 'Toppings', price: '₱600' },
        { name: 'Snacks', price: '₱450' }
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
  height: 250px;
  display: grid;
  grid-template-columns: 1fr 1fr; /* This creates two equal columns */
  gap: 20px; /* Optional: adds space between columns */
}

.LCL1{
  display: flex;
  align-items: baseline; /* Aligns text baselines */
  gap: 200px; /* Space between h1 and h2 */
}

.LCL1 h1, .LCL1 h3{
  margin: 0; /* Removes default margins */
}

.LCL1 h3{
  color: grey;
}

.LCL1 h1{
  color: black;
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

.LCL2 {
   list-style-type: none;
  padding-left: 0;
  margin-top: 10px;
}

.LCL2 li {
  color: black;
  margin-bottom: 4px;
  height: 30px;
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