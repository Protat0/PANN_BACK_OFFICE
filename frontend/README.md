# PANN POS - Frontend

Vue 3 + Vite frontend for the PANN Point of Sale system.

---

## 🚀 Quick Start

### Project Setup
```sh
npm install
```

### Development
```sh
npm run dev
```
Server runs on `http://localhost:5173`

### Production Build
```sh
npm run build
npm run preview  # Preview production build
```

---

## 📚 Documentation

- **[Full Documentation](./docs/)** - Complete frontend documentation
- **[Performance Optimization](./docs/PERFORMANCE_OPTIMIZATION.md)** - Dashboard optimization guide (99% data reduction!)
- **[Quick Reference](./docs/QUICK_REFERENCE.md)** - Quick tips and common patterns
- **[Test Documentation](./tests/)** - Testing guide and structure

---

## 🏗️ Tech Stack

- **Framework:** Vue 3 (Composition API)
- **Build Tool:** Vite 5
- **Styling:** CSS3 with CSS Variables
- **HTTP Client:** Axios
- **Testing:** Vitest + Vue Test Utils
- **Icons:** Lucide Vue Next

---

## 📁 Project Structure

```
frontend/
├── src/
│   ├── assets/          # Static assets
│   ├── components/      # Reusable components
│   │   ├── common/      # Common UI components
│   │   └── __tests__/   # Component tests
│   ├── composables/     # Vue composables
│   │   └── api/         # API composables (useProducts, useSales, etc.)
│   ├── helpers/         # Utility functions
│   ├── pages/           # Page components
│   ├── router/          # Vue Router
│   ├── services/        # API services
│   └── theme/           # Theme configuration
├── docs/                # 📚 Documentation
├── tests/               # 🧪 Test files
└── public/              # Public static files
```

---

## 🎯 Key Features

- ✅ **Dashboard** - Real-time sales monitoring
- ✅ **Product Management** - CRUD with image support
- ✅ **Sales Tracking** - Transaction history and analytics
- ✅ **Reports** - Top products, sales by period, profit analysis
- ✅ **Dark/Light Theme** - Persistent theme selection
- ✅ **Responsive Design** - Mobile, tablet, desktop support
- ✅ **Performance Optimized** - 3x faster with image exclusion

---

## 🧪 Testing

### Run All Tests
```sh
npm run test
```

### Watch Mode
```sh
npm run test:watch
```

### Coverage Report
```sh
npm run test:coverage
```

---

## 🔧 Development Tools

### Linting
```sh
npm run lint        # Check code style
npm run lint:fix    # Auto-fix issues
```

### Recommended IDE Setup
- **Editor:** [VSCode](https://code.visualstudio.com/)
- **Extensions:**
  - [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (Vue Language Features)
  - [ESLint](https://marketplace.visualstudio.com/items?itemName=dbaeumer.vscode-eslint)
  - [Prettier](https://marketplace.visualstudio.com/items?itemName=esbenp.prettier-vscode)

**Note:** Disable Vetur if you have it installed (conflicts with Volar)

---

## ⚡ Performance Tips

### 1. Always Exclude Images for Lists
```javascript
// ✅ CORRECT
const products = await getAllProducts({ exclude_images: true })

// ❌ WRONG - Downloads 2.5GB for 10,000 products!
const products = await getAllProducts({ limit: 10000 })
```

### 2. Key Optimization
The Dashboard was optimized from **34 seconds → 11 seconds** by:
- Excluding images from list queries
- Optimizing profit calculation
- Reducing data transfer by 99%

**See:** `docs/PERFORMANCE_OPTIMIZATION.md` for full details

---

## 📦 Build Configuration

### Vite Configuration
See [Vite Configuration Reference](https://vite.dev/config/)

Custom aliases:
- `@/` → `src/`
- `@components/` → `src/components/`
- `@services/` → `src/services/`

---

## 🔌 API Integration

### Backend URL
Configure in `src/services/api.js`:
```javascript
const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
```

### Environment Variables
Create `.env.local`:
```
VITE_API_URL=http://localhost:8000
```

---

## 🐛 Troubleshooting

### Slow Dashboard Load
**Problem:** Dashboard takes 30+ seconds

**Solution:** Verify `exclude_images: true` in:
- `src/composables/api/useSales.js` (line 171)
- Network tab → check query parameters

### Build Errors
```sh
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf node_modules/.vite
npm run dev
```

---

## 📖 Additional Resources

- **Vue 3 Docs:** https://vuejs.org/
- **Vite Docs:** https://vitejs.dev/
- **Vitest Docs:** https://vitest.dev/
- **Vue Router:** https://router.vuejs.org/

---

## 🤝 Contributing

1. Follow ESLint rules
2. Write tests for new features
3. Update documentation
4. Use clear commit messages
5. Test performance impact

---

## 📈 Performance Benchmarks

**After Optimization:**
- Dashboard Load: **11.3s** (was 34s)
- Product List: **1.4s** (was 15.5s)
- Data Transfer: **25MB** (was 2.5GB)
- Overall Speedup: **3.0x**

---

**Last Updated:** December 8, 2025  
**Version:** 1.0.0
