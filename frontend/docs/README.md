# Frontend Documentation

This directory contains all frontend-related documentation for the PANN POS system.

---

## 📚 Available Documentation

### Performance & Optimization
- **[PERFORMANCE_OPTIMIZATION.md](./PERFORMANCE_OPTIMIZATION.md)** - Complete guide to Dashboard performance optimization, including the 99% data reduction fix

---

## 🏗️ Architecture Overview

### Tech Stack
- **Framework:** Vue 3 (Composition API)
- **Build Tool:** Vite
- **Styling:** CSS3 with CSS Variables (Dark/Light theme support)
- **State Management:** Composables (no Vuex/Pinia)
- **HTTP Client:** Axios
- **Testing:** Vitest + Vue Test Utils

### Project Structure
```
frontend/
├── src/
│   ├── assets/          # Static assets (images, fonts, etc.)
│   ├── components/      # Reusable Vue components
│   │   ├── common/      # Common UI components
│   │   └── __tests__/   # Component tests
│   ├── composables/     # Vue composables (shared logic)
│   │   └── api/         # API-related composables
│   ├── helpers/         # Utility functions
│   ├── pages/           # Page components (routes)
│   ├── router/          # Vue Router configuration
│   ├── services/        # API services
│   └── theme/           # Theme configuration
├── docs/                # Documentation (this folder)
├── tests/               # Test files
└── public/              # Public static files
```

---

## 🎨 UI/UX Guidelines

### Color System
- **Primary:** Blue (#3B82F6)
- **Secondary:** Purple (#8B5CF6)
- **Success:** Green (#10B981)
- **Error:** Red (#EF4444)
- **Warning:** Yellow (#F59E0B)
- **Info:** Cyan (#06B6D4)

### Theme Support
- ✅ Dark Mode
- ✅ Light Mode
- ✅ Auto-detect system preference
- ✅ Persistent theme selection

### Responsive Breakpoints
- **Mobile:** < 768px
- **Tablet:** 768px - 1024px
- **Desktop:** > 1024px

---

## 🔌 API Integration

### API Services Location
All API services are located in `src/services/`:
- `apiProducts.js` - Product CRUD operations
- `apiReports.js` - Sales reports and analytics
- `apiSalesByItem.js` - Sales display by item
- `api.js` - Base Axios configuration

### Composables
Composables provide reactive state management for API data:
- `useProducts()` - Product data and operations
- `useSales()` - Sales data and statistics
- `useCustomers()` - Customer management

### Example Usage
```javascript
import { useProducts } from '@/composables/api/useProducts'

const { 
  products,           // Reactive product list
  loading,            // Loading state
  error,              // Error state
  fetchProducts,      // Fetch function
  createProduct       // Create function
} = useProducts()

// Fetch products
await fetchProducts({ 
  page: 1, 
  limit: 20,
  exclude_images: true  // Performance optimization!
})
```

---

## 📊 Dashboard Components

### Main Widgets
1. **Total Profit** - All-time profit calculation
2. **Total Products** - Product count
3. **Monthly Revenue** - Current month's income
4. **Top Performing Month** - Best month of the year
5. **Total Items Sold** - Sales count
6. **Recent Transactions** - Last 20 sales (auto-refresh)
7. **Top Products** - Best-selling products with date filter

### Performance Considerations
- ✅ Images excluded from list views
- ✅ Profit calculation optimized (99% data reduction)
- ✅ Auto-refresh with smart intervals
- ✅ Progressive loading of widgets
- ✅ Error handling and retry logic

---

## 🚀 Development Workflow

### Setup
```bash
cd frontend
npm install
npm run dev
```

### Build
```bash
npm run build
npm run preview  # Preview production build
```

### Testing
```bash
npm run test              # Run tests
npm run test:watch        # Watch mode
npm run test:coverage     # Coverage report
```

### Linting
```bash
npm run lint              # Check code style
npm run lint:fix          # Auto-fix issues
```

---

## 🔧 Configuration Files

### Vite Configuration
- **File:** `vite.config.js`
- **Purpose:** Build configuration, dev server, path aliases

### Vitest Configuration
- **File:** `vitest.config.js`
- **Purpose:** Test environment setup

### ESLint Configuration
- **File:** `eslint.config.js`
- **Purpose:** Code quality and style rules

### JSConfig
- **File:** `jsconfig.json`
- **Purpose:** Path aliases for IDE support

---

## 🐛 Debugging Tips

### Vue DevTools
Install Vue DevTools browser extension for:
- Component inspection
- Vuex state (if used)
- Performance profiling
- Event tracking

### Network Debugging
Use Browser DevTools → Network tab:
- Check API request/response
- Monitor payload sizes
- Verify `exclude_images` parameter
- Measure load times

### Common Issues

#### 1. Slow Dashboard Load
**Symptoms:** Dashboard takes 30+ seconds to load

**Solution:** Verify `exclude_images: true` is passed in API calls
- Check: `useSales.js` line 171
- Check: Network tab for query parameters

#### 2. Images Not Loading
**Symptoms:** Product images show as broken

**Solution:** 
- Verify base64 encoding is correct
- Check image MIME type
- Consider Cloudinary migration

#### 3. Auto-refresh Not Working
**Symptoms:** Recent transactions don't update

**Solution:**
- Check `autoRefreshEnabled` state
- Verify no JavaScript errors in console
- Check network connectivity

---

## 📖 Best Practices

### 1. Component Design
- **Single Responsibility:** Each component should do one thing well
- **Props Down, Events Up:** Follow Vue's data flow pattern
- **Reusable:** Design for reusability from the start
- **Composable Logic:** Extract shared logic to composables

### 2. Performance
- **Lazy Loading:** Use dynamic imports for routes
- **Image Optimization:** Always use `exclude_images: true` for lists
- **Debouncing:** Debounce search inputs and frequent operations
- **Memoization:** Use `computed()` for expensive calculations

### 3. Code Style
- **Consistent Naming:** Use camelCase for variables, PascalCase for components
- **Clear Functions:** Functions should be small and focused
- **Comments:** Comment complex logic, not obvious code
- **ESLint:** Follow ESLint rules consistently

### 4. API Integration
- **Error Handling:** Always handle API errors gracefully
- **Loading States:** Show loading indicators during async operations
- **Retry Logic:** Implement retry for failed requests
- **Caching:** Cache when appropriate to reduce API calls

---

## 🔐 Security Considerations

### Authentication
- JWT tokens stored in localStorage
- Token refresh on expiry
- Auto-logout on unauthorized responses

### Data Validation
- Client-side validation for UX
- Server-side validation for security
- Sanitize user inputs

### API Security
- CORS configuration
- Rate limiting (backend)
- No sensitive data in frontend

---

## 📈 Performance Metrics

### Target Metrics
- **Dashboard Load:** < 15 seconds
- **Product List Load:** < 3 seconds
- **Search Response:** < 1 second
- **Page Navigation:** < 500ms

### Current Performance (After Optimization)
- ✅ Dashboard Load: **11.3 seconds** (from 34s)
- ✅ Product List: **1.4 seconds** (from 15.5s)
- ✅ Data Transfer: **25MB** (from 2.5GB)
- ✅ Profit Widget: **2-3 seconds** (from 15-20s)

---

## 🆘 Getting Help

### Internal Resources
- **Performance Guide:** `PERFORMANCE_OPTIMIZATION.md`
- **Test Guide:** `../tests/README.md`
- **Main README:** `../README.md`

### External Resources
- **Vue 3 Docs:** https://vuejs.org/
- **Vite Docs:** https://vitejs.dev/
- **Vitest Docs:** https://vitest.dev/

---

## 📝 Contributing

### Adding Documentation
1. Create new `.md` file in this directory
2. Use clear, descriptive titles
3. Include code examples where applicable
4. Link to related documentation
5. Update this README with new document

### Documentation Style
- Use emoji for section headers (sparingly)
- Include code examples in triple backticks
- Use tables for comparisons
- Add "Related Documentation" sections
- Keep language clear and concise

---

**Last Updated:** December 8, 2025  
**Maintained By:** Development Team
