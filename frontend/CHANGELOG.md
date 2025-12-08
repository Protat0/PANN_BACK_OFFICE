# Frontend Changelog

All notable changes to the frontend will be documented in this file.

---

## [1.0.1] - December 8, 2025

### 🎯 Performance Optimizations

#### Changed
- **CRITICAL FIX:** Added `exclude_images: true` to profit calculation in `useSales.js`
  - **Impact:** Profit calculation now **10x faster** (15-20s → 2-3s)
  - **Data Reduction:** 99% less data transfer (2.5GB → 25MB)
  - **Location:** `src/composables/api/useSales.js` line 171

#### Performance Results
- Dashboard load time: **34s → 11.3s** (3.0x faster)
- Product list load: **15.5s → 1.4s** (11.2x faster)
- Profit widget: **15-20s → 2-3s** (10x faster)
- Top products query: **1.1s → 0.4s** (2.8x faster)

### 📁 Project Organization

#### Added
- `docs/` - New documentation folder
  - `README.md` - Documentation index
  - `PERFORMANCE_OPTIMIZATION.md` - Complete performance guide
  - `QUICK_REFERENCE.md` - Developer quick reference
  
- `tests/` - New test folder structure
  - `README.md` - Testing guide and best practices

#### Changed
- Enhanced `README.md` with better structure and links
- Added comprehensive documentation for developers

---

## [1.0.0] - November 2025

### 🎉 Initial Release

#### Added
- Vue 3 + Vite frontend application
- Dashboard with real-time widgets
- Product management system
- Sales tracking and reports
- Dark/Light theme support
- Responsive design (mobile, tablet, desktop)

#### Features
- **Dashboard Widgets:**
  - Total Profit (all-time)
  - Total Products count
  - Monthly Revenue
  - Top Performing Month
  - Recent Transactions (auto-refresh)
  - Top Products (with date filter)

- **Product Management:**
  - CRUD operations
  - Image upload (base64)
  - Category filtering
  - Search functionality
  - Pagination support

- **Sales & Reports:**
  - Sales by item view
  - Top selling products
  - Sales by period (daily/weekly/monthly)
  - Profit calculations
  - Transaction history

- **UI/UX:**
  - Modern card-based layout
  - Smooth animations
  - Loading states
  - Error handling
  - Toast notifications

---

## Migration Guide

### Upgrading to 1.0.1

#### Required Changes
1. **Update useSales.js**
   ```javascript
   // OLD (line 171)
   const response = await apiProductsService.getAllProducts({ limit: 10000 })
   
   // NEW (line 171-175)
   const response = await apiProductsService.getAllProducts({ 
     limit: 10000,
     exclude_images: true 
   })
   ```

2. **Clear Browser Cache**
   - Have users clear cache or hard refresh (Ctrl+Shift+R)
   - This ensures new optimized code is loaded

3. **Verify Backend Support**
   - Ensure backend supports `exclude_images` parameter
   - Backend file: `app/services/product_service.py`

#### Testing After Upgrade
1. Open Dashboard
2. Check DevTools → Network tab
3. Verify `/products/` requests have `exclude_images=true`
4. Confirm dashboard loads in < 15 seconds
5. Verify no console errors

---

## Performance History

| Version | Dashboard Load | Data Transfer | Status |
|---------|----------------|---------------|--------|
| 1.0.0 | 34.1s | 2.5GB | ⚠️ Slow |
| 1.0.1 | 11.3s | 25MB | ✅ Optimized |

---

## Upcoming Features

### Planned for 1.1.0
- [ ] Dedicated `/products/cost-prices/` endpoint
- [ ] Product cost price caching in localStorage
- [ ] Progressive widget loading
- [ ] Offline support with Service Workers
- [ ] Image migration to Cloudinary

### Planned for 1.2.0
- [ ] Advanced search filters
- [ ] Bulk product operations
- [ ] Export reports to PDF/Excel
- [ ] Real-time notifications
- [ ] Customer management integration

---

## Breaking Changes

### None in 1.0.1
The optimization is backward compatible. Old code will still work but will be slower.

---

## Bug Fixes

### 1.0.1
- Fixed: Dashboard timeout errors on slow connections
- Fixed: Large data transfers causing browser memory issues
- Fixed: Profit calculation taking 15-20 seconds

---

## Technical Debt

### Addressed in 1.0.1
- ✅ Removed unnecessary image data from API responses
- ✅ Optimized profit calculation data fetching
- ✅ Added proper documentation structure

### Remaining
- ⚠️ Product images still stored as base64 in MongoDB (consider Cloudinary)
- ⚠️ No caching for product cost prices
- ⚠️ Fetching up to 10,000 products for cost calculation (should use dedicated endpoint)

---

## Dependencies

### Core
- Vue 3.4+
- Vite 5.0+
- Vue Router 4.0+
- Axios 1.6+

### UI & Icons
- Lucide Vue Next 0.x

### Development
- Vitest 1.0+
- ESLint 8.x
- Prettier 3.x

---

**Maintained By:** Development Team  
**Last Updated:** December 8, 2025
