# Quick Reference Guide - Frontend Optimization

**Quick checklist for developers working on the PANN POS frontend.**

---

## ⚡ Performance Rules

### 1. ALWAYS Exclude Images for Lists
```javascript
// ✅ CORRECT: Exclude images when fetching products for lists/dashboards
const response = await apiProductsService.getAllProducts({ 
  limit: 100,
  exclude_images: true 
})

// ❌ WRONG: Fetching images for list views
const response = await apiProductsService.getAllProducts({ limit: 100 })
```

### 2. Only Fetch Images When Needed
```javascript
// ✅ CORRECT: Fetch images only for detail view
const product = await apiProductsService.getProductById(id)  // Includes image

// ✅ CORRECT: Fetch multiple products without images
const products = await apiProductsService.getAllProducts({ 
  exclude_images: true 
})
```

### 3. Cache Product Cost Prices
```javascript
// ✅ CORRECT: Use cached cost prices
const costPrice = getProductCostPrice(productId)  // From cache

// ❌ WRONG: Fetching all products every time
const products = await getAllProducts()
const costPrice = products.find(p => p.id === productId).cost_price
```

---

## 🎯 Common Operations

### Fetching Products for Dashboard
```javascript
// Use the composable
const { products, fetchProducts } = useProducts()

await fetchProducts({ 
  page: 1, 
  limit: 100,
  exclude_images: true  // ← Don't forget this!
})
```

### Calculating Profit
```javascript
// From useSales composable - now optimized
const { totalProfit, loadTotalProfitAllTime } = useSales()

await loadTotalProfitAllTime()  // Now uses exclude_images: true
console.log(totalProfit.value)
```

### Loading Dashboard Data
```javascript
// Dashboard.vue - loads all widgets
async mounted() {
  await Promise.all([
    this.loadProductsData(),    // Excludes images
    this.loadSalesData()        // Excludes images in profit calc
  ])
  await this.loadRecentTransactions()
  await this.loadTopProducts()
}
```

---

## 🐛 Debugging Performance Issues

### Check Network Tab
1. Open Browser DevTools → Network tab
2. Filter by "Fetch/XHR"
3. Look for `/products/` requests
4. Click on request → Preview/Response
5. **Verify:** `exclude_images=true` in query params
6. **Verify:** Response size is small (< 1MB for 100 products)

### Check Response Size
```javascript
// Should be ~2.5KB per product (without images)
// NOT 250KB per product (with base64 images)

// With 100 products:
// ✅ Expected: ~250KB total
// ❌ Problem: ~25MB total
```

### Common Mistakes

#### ❌ Mistake #1: Forgetting exclude_images
```javascript
// This downloads 2.5GB for 10,000 products!
const response = await apiProductsService.getAllProducts({ limit: 10000 })
```

**Fix:**
```javascript
const response = await apiProductsService.getAllProducts({ 
  limit: 10000,
  exclude_images: true 
})
```

#### ❌ Mistake #2: Fetching All Products for One Field
```javascript
// Bad: Fetching all products just to get one cost_price
const allProducts = await getAllProducts()
const costPrice = allProducts.find(p => p.id === id).cost_price
```

**Fix:**
```javascript
// Good: Use cache or dedicated endpoint
const costPrice = getProductCostPrice(id)  // From cache
```

#### ❌ Mistake #3: No Loading States
```javascript
// Bad: No feedback during slow operations
async loadData() {
  const data = await fetchData()
}
```

**Fix:**
```javascript
// Good: Show loading state
async loadData() {
  this.loading = true
  try {
    const data = await fetchData()
  } finally {
    this.loading = false
  }
}
```

---

## 📏 Size Benchmarks

### Product Document Sizes
- **With base64 image:** ~250KB per product
- **Without image:** ~2.5KB per product
- **Ratio:** 100:1 reduction

### Dashboard Load Benchmarks
- **With images:** 34 seconds, 2.5GB transfer
- **Without images:** 11 seconds, 25MB transfer
- **Improvement:** 3x faster, 99% less data

### Widget Load Times (Target)
- Total Products: < 2s
- Total Profit: < 3s
- Monthly Revenue: < 1s
- Recent Transactions: < 2s
- Top Products: < 2s

---

## 🔧 Backend Query Parameters

### Products Endpoint
```
GET /products/?exclude_images=true&page=1&limit=100
```

**Parameters:**
- `exclude_images` (boolean): Exclude image fields from response
- `page` (int): Page number for pagination
- `limit` (int): Items per page
- `search` (string): Search query
- `category_id` (string): Filter by category

### Sales Endpoints
```
GET /sales/recent/?limit=20
GET /sales-report/by-period/?start_date=2024-10-01&end_date=2024-12-08&period=monthly
GET /reports/top-chart-item/?limit=10&start_date=2024-10-01&end_date=2024-12-08
```

---

## 🚀 Deployment Checklist

### Before Deploying
- [ ] Verify `exclude_images: true` in `useSales.js` (line 171)
- [ ] Test Dashboard load time (should be < 15s)
- [ ] Check Network tab for large payloads
- [ ] Run `npm run build` successfully
- [ ] No console errors in production build

### After Deploying
- [ ] Clear browser cache on client machines
- [ ] Test Dashboard performance
- [ ] Monitor backend logs for optimization messages
- [ ] Verify no timeout errors
- [ ] Check user feedback

---

## 📞 Quick Help

### File Locations
- **Profit Calculation:** `frontend/src/composables/api/useSales.js` (line 171)
- **Product Service:** `frontend/src/services/apiProducts.js`
- **Dashboard Component:** `frontend/src/pages/Dashboard.vue`
- **Backend Product Service:** `backend/app/services/product_service.py`

### Key Functions
- `useProducts()` - Product composable
- `useSales()` - Sales composable
- `fetchProductCostPrices()` - Cost price fetching (optimized)
- `loadTotalProfitAllTime()` - Profit calculation (optimized)

### Related Docs
- **Full Optimization Guide:** `PERFORMANCE_OPTIMIZATION.md`
- **Testing Guide:** `../tests/README.md`
- **Backend Tests:** `../../backend/test_dashboard_simulation.py`

---

## 💡 Pro Tips

1. **Always test with production data size** - 357 products revealed our bottleneck
2. **Profile before optimizing** - Network tab showed exact problem
3. **One line can change everything** - `exclude_images: true` = 10x speedup
4. **Images are heavy** - 250KB × 10,000 = 2.5GB of waste
5. **Cache aggressively** - Don't re-fetch what you already have

---

**Remember:** When in doubt, exclude images for list views! 🎯
