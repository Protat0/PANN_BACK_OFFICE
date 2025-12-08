# Frontend Tests

This directory contains all frontend testing files for the POS system.

## 📁 Directory Structure

```
tests/
├── README.md                 # This file
├── unit/                     # Unit tests (planned)
├── integration/              # Integration tests (planned)
└── performance/              # Performance tests (planned)
```

## 🧪 Current Test Setup

### Test Framework
- **Framework:** Vitest
- **Config:** `vitest.config.js` (in frontend root)
- **Component Tests:** Located in `src/components/__tests__/`

### Running Tests

```bash
# Run all tests
npm run test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage
```

## 📋 Test Coverage Areas

### Current Coverage
- ✅ Component tests in `src/components/__tests__/`
  - HelloWorld.spec.js (sample test)

### Recommended Test Coverage

#### 1. Unit Tests
- **Composables:**
  - `src/composables/api/useProducts.js`
  - `src/composables/api/useSales.js`
  - `src/composables/api/useCustomers.js`
  
- **Services:**
  - `src/services/apiProducts.js`
  - `src/services/apiReports.js`
  - `src/services/apiSalesByItem.js`

- **Utilities:**
  - `src/helpers/currencyHelpers.js`
  - `src/helpers/dateHelpers.js`

#### 2. Component Tests
- **Pages:**
  - Dashboard.vue
  - Products.vue
  - Sales.vue
  - Reports.vue

- **Components:**
  - ProductCard.vue
  - SalesTable.vue
  - Charts/

#### 3. Integration Tests
- **API Integration:**
  - Product CRUD operations
  - Sales creation and retrieval
  - Dashboard data loading
  - Report generation

#### 4. Performance Tests
- **Load Time Tests:**
  - Dashboard initial load
  - Product list pagination
  - Large dataset rendering
  
- **Memory Tests:**
  - Image loading optimization
  - Data caching effectiveness
  - Memory leak detection

## 🎯 Testing Best Practices

### 1. Test Naming Convention
```javascript
describe('ComponentName', () => {
  describe('methodName', () => {
    it('should do something specific', () => {
      // Test implementation
    })
  })
})
```

### 2. Arrange-Act-Assert Pattern
```javascript
it('should calculate total correctly', () => {
  // Arrange
  const items = [{ price: 10 }, { price: 20 }]
  
  // Act
  const total = calculateTotal(items)
  
  // Assert
  expect(total).toBe(30)
})
```

### 3. Mock External Dependencies
```javascript
import { vi } from 'vitest'

vi.mock('@/services/apiProducts', () => ({
  getAllProducts: vi.fn(() => Promise.resolve({ data: [] }))
}))
```

## 🔍 Performance Testing

### Dashboard Load Test
Backend simulation test verifies Dashboard queries:
- **File:** `backend/test_dashboard_simulation.py`
- **What it tests:**
  - Product fetching with/without images
  - Sales display queries
  - Profit calculations
  - Top products aggregation
  - Recent transactions

### Results
- **With Images:** 34.1 seconds
- **Without Images:** 11.3 seconds
- **Speedup:** 3.0x faster

## 📚 Related Documentation

- **Performance Optimization:** `frontend/docs/PERFORMANCE_OPTIMIZATION.md`
- **Backend Tests:** `backend/test_dashboard_simulation.py`
- **Test Results:** `FINAL_TEST_SUMMARY.md` (root)

## 🚀 Future Test Plans

### Phase 1: Essential Tests
- [ ] Unit tests for composables
- [ ] API service tests
- [ ] Dashboard component test
- [ ] Product CRUD integration tests

### Phase 2: Comprehensive Coverage
- [ ] All page components
- [ ] Form validation tests
- [ ] Error handling tests
- [ ] Loading state tests

### Phase 3: Advanced Testing
- [ ] E2E tests with Playwright
- [ ] Visual regression tests
- [ ] Performance benchmarks
- [ ] Accessibility tests

## 🛠️ Tools & Resources

### Testing Libraries
- **Vitest:** https://vitest.dev/
- **Vue Test Utils:** https://test-utils.vuejs.org/
- **Testing Library:** https://testing-library.com/

### Recommended Reading
- [Vue Testing Handbook](https://lmiller1990.github.io/vue-testing-handbook/)
- [JavaScript Testing Best Practices](https://github.com/goldbergyoni/javascript-testing-best-practices)
- [Vitest Documentation](https://vitest.dev/guide/)

---

**Note:** This test structure is prepared for future expansion. As the application grows, organize tests by feature or module for better maintainability.
