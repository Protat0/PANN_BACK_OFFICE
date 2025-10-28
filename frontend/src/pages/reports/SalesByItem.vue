<template>
  <div class="page-container">
    <!-- ========================================== -->
    <!-- TOP SECTION: Analytics & Chart -->
    <!-- ========================================== -->
    <div class="content-container d-grid gap-3 mb-4" style="grid-template-columns: 1fr 2px 1fr; align-items: start;">
      <!-- Left: Top Five Items List -->
      <div class="surface-card rounded p-3">
        <div class="d-flex justify-content-between align-items-baseline mb-3">
          <h1 class="text-primary mb-0">Top Five Items</h1>
          <h3 class="text-secondary mb-0">Net Sales</h3>
        </div>
         
        <!-- Loading state for top items -->
        <div v-if="loadingTopItems" class="text-center py-4">
          <div class="spinner-border text-accent" role="status">
            <span class="visually-hidden">Loading top items...</span>
          </div>
          <p class="text-tertiary mt-2">Loading top items...</p>
        </div>
        
        <!-- Top items list -->
        <ul v-else-if="topItems && topItems.length > 0" class="list-unstyled">
          <li v-for="(item, index) in topItems" :key="index" class="d-flex justify-content-between align-items-center py-2 border-bottom">
            <span class="text-primary fw-bold fs-4">{{ item.name }}</span>
            <span class="text-success fw-bold">{{ item.price }}</span>
          </li>
        </ul>
        
        <!-- Empty state for top items -->
        <div v-else class="empty-state-small">
          <p>No top items data available</p>
          <button @click="loadAllData" class="btn btn-sm btn-primary">Retry Loading</button>
        </div>
      </div>
      
      <div class="divider-theme"></div>
      
      <!-- Right: Sales Chart -->
      <div class="RC-SBI">
        <div class="chart-header">
          <h1>Sales Chart</h1>
          <select v-model="selectedFrequency" @change="onFrequencyChange" class="frequency-dropdown">
            <option value="daily">Daily <!--(Last 30 Days) --></option>
            <option value="weekly">Weekly <!--(Last 12 Weeks)--></option>
            <option value="monthly">Monthly (Last 12 Months)</option>
            <option value="yearly">Yearly (Last 3 Years)</option>
          </select>
        </div>
        <div class="chart-container">
          <div v-if="loadingChart" class="chart-loading">
            <div class="spinner-border text-primary"></div>
            <p>Loading chart data...</p>
          </div>
          <BarChart v-else :chartData="chartData" :selectedFrequency="selectedFrequency" />
        </div>
      </div>
    </div>
    
    <!-- ========================================== -->
    <!-- BOTTOM SECTION: Sales by Item Table -->
    <!-- ========================================== -->
    <div class="content-container">
      <!-- Header with Action Buttons -->
      <div class="transaction-header">
        <div class="header-left">
          <h1>Sales by Item</h1>
          
        </div>
        <div class="header-actions">
          <!-- Auto-refresh status and controls -->
          <div class="surface-secondary d-flex align-items-center gap-2 px-3 py-2 rounded">
            <i class="bi bi-arrow-repeat text-success" :class="{ 'spinning': salesByItemLoading }"></i>
            <span class="text-success fw-medium">
              <span v-if="autoRefreshEnabled">Updates in {{ countdown }}s</span>
              <span v-else>Auto-refresh disabled</span>
            </span>
            
            <!-- Toggle button -->
            <button 
              class="btn btn-sm"
              :class="autoRefreshEnabled ? 'btn-outline-secondary' : 'btn-outline-success'"
              @click="toggleAutoRefresh"
            >
              {{ autoRefreshEnabled ? 'Disable' : 'Enable' }}
            </button>
          </div>
          
          <!-- Connection health indicator -->
          <div class="px-3 py-2 rounded" :class="getConnectionStatus()">
            <i :class="getConnectionIcon()"></i>
            <span class="ms-2">{{ getConnectionText() }}</span>
          </div>
          
          <!-- Emergency Refresh - Only show if error or connection lost -->
          <button 
            v-if="error || connectionLost" 
            class="btn btn-warning btn-sm" 
            @click="emergencyReconnect"
            :disabled="salesByItemLoading"
          >
            <i class="bi bi-arrow-clockwise" :class="{ 'spinning': salesByItemLoading }"></i>
            {{ salesByItemLoading ? 'Reconnecting...' : 'Reconnect' }}
          </button>

          <button class="btn btn-primary btn-sm" @click="importData" :disabled="salesByItemLoading || importing">
            <i class="bi bi-upload"></i> {{ importing ? 'Importing...' : 'Import' }}
          </button>
          <button class="btn btn-success btn-sm" @click="exportData" :disabled="salesByItemLoading || exporting">
            <i class="bi bi-download"></i> {{ exporting ? 'Exporting...' : 'Export' }}
          </button>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="salesByItemLoading" class="surface-card text-center py-5 rounded">
        <div class="spinner-border text-accent" role="status">
          <span class="visually-hidden">Loading sales data...</span>
        </div>
        <p class="text-tertiary mt-2">Loading sales data...</p>
      </div>
      
      <!-- Sales by Item Table -->
      <div v-else class="surface-card rounded overflow-hidden">
        <table class="table table-striped mb-0">
          <thead class="surface-secondary">
            <tr>
              <th scope="col" class="text-primary">Product ID</th>
              <th scope="col" class="text-primary">Product Name</th>
              <th scope="col" class="text-primary">Category</th>
              <th scope="col" class="text-center text-primary">Stock</th>
              <th scope="col" class="text-center text-primary">Items Sold</th>
              <th scope="col" class="text-primary">Total Sales</th>
              <th scope="col" class="text-primary">Unit Price</th>
              <th scope="col" class="text-center text-primary">Actions</th>
            </tr>
          </thead>
          <tbody class="table-group-divider">
            <tr v-for="item in salesByItemRows" :key="item.id">
              <td class="font-monospace text-tertiary" :title="item.id">
                {{ item.id }}
              </td>
              <td class="text-primary">
                <span class="d-block text-truncate" :title="item.product" style="max-width: 200px;">
                  {{ item.product.length > 30 ? item.product.substring(0, 30) + '...' : item.product }}
                </span>
              </td>
              <td>
                <span class="badge bg-secondary">{{ item.category }}</span>
              </td>
              <td class="stock-column">
                <span :class="{'low-stock': item.stock < 10, 'critical-stock': item.stock < 5}">
                  {{ item.stock }} {{ item.unit }}
                </span>
              </td>
              <td class="text-center fw-medium">
                {{ item.items_sold }}
              </td>
              <td class="text-end">
                <span class="text-success fw-bold">{{ formatCurrency(item.total_sales) }}</span>
              </td>
              <td class="text-end fw-bold">
                {{ formatCurrency(item.selling_price) }}
              </td>
              <td class="text-center">
                  <button 
                    class="btn btn-outline-primary btn-sm" 
                    @click="viewProductDetails(item)"
                    title="View Product Details"
                  >
                    <Eye/>
                  </button>
              </td>
            </tr>
          </tbody>
        </table>
        
        <!-- Empty State -->
        <div v-if="salesByItemRows.length === 0 && !salesByItemLoading" class="empty-state">
          <i class="bi bi-receipt" style="font-size: 3rem; color: #6b7280;"></i>
          <p>No sales data found for the selected time period</p>
          <button class="btn btn-primary" @click="loadAllData">
            <i class="bi bi-arrow-clockwise"></i> Refresh Data
          </button>
        </div>
        
        <!-- Pagination for Sales by Item Table -->
        <div v-if="showSalesByItemPagination" class="surface-secondary p-3 border-top">
          <div class="d-flex justify-content-end align-items-center mb-3">
            <div class="d-flex flex-column align-items-end gap-2">
              <span class="text-tertiary small">
                Showing {{ ((salesByItemPagination.current_page - 1) * salesByItemPagination.page_size) + 1 }} 
                to {{ Math.min(salesByItemPagination.current_page * salesByItemPagination.page_size, salesByItemPagination.total_records) }} 
                of {{ salesByItemPagination.total_records }} products
              </span>
              
              <div class="d-flex align-items-center gap-2">
                <label for="salesPageSize" class="text-primary small mb-0">Per page:</label>
                <select 
                  id="salesPageSize"
                  :value="salesByItemPagination.page_size" 
                  @change="changeSalesByItemPageSize(Number($event.target.value))"
                  :disabled="salesByItemLoading"
                  class="form-select form-select-sm"
                >
                  <option value="10">10</option>
                  <option value="25">25</option>
                  <option value="50">50</option>
                  <option value="100">100</option>
                </select>
              </div>
            </div>
          </div>

          <nav aria-label="Sales by item pagination">
            <ul class="pagination pagination-sm justify-content-center mb-0">
              <li class="page-item" :class="{ disabled: !salesByItemPagination.has_prev || salesByItemLoading }">
                <button 
                  class="page-link" 
                  @click="goToSalesByItemPage(salesByItemPagination.current_page - 1)"
                  :disabled="!salesByItemPagination.has_prev || salesByItemLoading"
                  aria-label="Previous page"
                >
                  <i class="bi bi-chevron-left">‹</i>
                </button>
              </li>

              <li 
                v-for="page in getSalesByItemVisiblePages" 
                :key="page"
                class="page-item" 
                :class="{ active: page === salesByItemPagination.current_page }"
              >
                <button 
                  class="page-link" 
                  @click="goToSalesByItemPage(page)"
                  :disabled="salesByItemLoading"
                >
                  {{ page }}
                </button>
              </li>

              <li class="page-item" :class="{ disabled: !salesByItemPagination.has_next || salesByItemLoading }">
                <button 
                  class="page-link" 
                  @click="goToSalesByItemPage(salesByItemPagination.current_page + 1)"
                  :disabled="!salesByItemPagination.has_next || salesByItemLoading"
                  aria-label="Next page"
                >
                  <i class="bi bi-chevron-right">›</i>
                </button>
              </li>
            </ul>
          </nav>
        </div>
      </div>
    </div>

    <!-- ========================================== -->
    <!-- MODALS -->
    <!-- ========================================== -->
    
    <!-- Import Progress Modal -->
    <div v-if="showImportProgressModal" class="modal-overlay-theme position-fixed" @click="closeImportProgressModal">
      <div class="modal-theme rounded" @click.stop>
        <div class="modal-header border-bottom">
          <h3 class="text-primary mb-0">{{ importStep === 'uploading' ? 'Uploading CSV File' : 'Processing Import' }}</h3>
          <button class="btn-close" @click="closeImportProgressModal" :disabled="importing">&times;</button>
        </div>
        <div class="modal-body p-4">
          <div class="mb-4">
            <div class="d-flex justify-content-between align-items-center mb-2">
              <span class="text-primary">{{ importStatusText }}</span>
              <span class="text-accent fw-bold">{{ Math.round(importProgress) }}%</span>
            </div>
            <div class="progress">
              <div class="progress-bar" role="progressbar" :style="{ width: importProgress + '%' }"></div>
            </div>
          </div>
          
          <div v-if="importResult">
            <h4 class="text-primary">Import Results</h4>
            <div class="d-flex flex-column gap-2 mb-3">
              <div class="surface-secondary p-2 rounded d-flex justify-content-between">
                <span class="text-success">✅ Successful:</span>
                <span class="fw-bold">{{ importResult.summary?.successful || 0 }}</span>
              </div>
              <div v-if="importResult.summary?.failed > 0" class="surface-secondary p-2 rounded d-flex justify-content-between">
                <span class="text-error">❌ Failed:</span>
                <span class="fw-bold">{{ importResult.summary?.failed || 0 }}</span>
              </div>
              <div class="surface-secondary p-2 rounded d-flex justify-content-between">
                <span class="text-primary">📊 Success Rate:</span>
                <span class="fw-bold">{{ importResult.summary?.success_rate || 0 }}%</span>
              </div>
            </div>
            
            <div v-if="importResult.warnings && importResult.warnings.length > 0">
              <h5 class="text-status-warning">⚠️ Warnings</h5>
              <ul class="list-unstyled">
                <li v-for="warning in importResult.warnings" :key="warning.type" class="text-status-warning p-2 border-start border-warning border-3 mb-1">
                  {{ warning.message }}
                </li>
              </ul>
            </div>
          </div>
          
          <div v-if="importError" class="alert alert-danger">
            <h4 class="alert-heading text-error">❌ Import Failed</h4>
            <p class="mb-0">{{ importError }}</p>
          </div>
        </div>
        <div class="modal-footer border-top d-flex justify-content-end gap-2 p-3">
          <button v-if="!importing" class="btn btn-secondary" @click="closeImportProgressModal">
            Close
          </button>
          <button v-if="importResult && !importing" class="btn btn-primary" @click="closeImportProgressModal">
            Done
          </button>
        </div>
      </div>
    </div>

    <!-- Product Details Modal -->
    <div v-if="showProductModal" class="modal-overlay-theme position-fixed" @click="closeProductModal">
      <div class="modal-theme rounded" @click.stop>
        <div class="modal-header border-bottom">
          <h2 class="text-primary mb-0">Product Details</h2>
          <button class="btn-close" @click="closeProductModal">&times;</button>
        </div>
        
        <div class="modal-body p-4">
          <div v-if="selectedProductData" class="d-flex flex-column gap-4">
            <div class="surface-secondary border rounded p-3">
              <h4 class="text-primary mb-3">Product Information</h4>
              <div class="d-flex justify-content-between align-items-center py-2 border-bottom">
                <strong class="text-primary">Product ID:</strong> 
                <span class="text-tertiary font-monospace">{{ selectedProductData.id }}</span>
              </div>
              <div class="d-flex justify-content-between align-items-center py-2 border-bottom">
                <strong class="text-primary">Product Name:</strong> 
                <span class="text-primary">{{ selectedProductData.name }}</span>
              </div>
              <div class="d-flex justify-content-between align-items-center py-2 border-bottom">
                <strong class="text-primary">SKU:</strong> 
                <span class="text-tertiary">{{ selectedProductData.sku }}</span>
              </div>
              <div class="d-flex justify-content-between align-items-center py-2">
                <strong class="text-primary">Category:</strong> 
                <span class="text-primary">{{ selectedProductData.category }}</span>
              </div>
            </div>

            <div class="surface-secondary border rounded p-3">
              <h4 class="text-primary mb-3">Inventory & Sales</h4>
              <div class="d-flex justify-content-between align-items-center py-2 border-bottom">
                <strong class="text-primary">Stock:</strong> 
                <span class="text-primary fw-medium">{{ selectedProductData.stock }} {{ selectedProductData.unit }}</span>
              </div>
              <div class="d-flex justify-content-between align-items-center py-2 border-bottom">
                <strong class="text-primary">Items Sold:</strong> 
                <span class="text-primary fw-medium">{{ selectedProductData.items_sold }}</span>
              </div>
              <div class="d-flex justify-content-between align-items-center py-2 border-bottom">
                <strong class="text-primary">Unit Price:</strong> 
                <span class="text-primary fw-bold">{{ selectedProductData.selling_price }}</span>
              </div>
              <div class="d-flex justify-content-between align-items-center py-2 border-bottom">
                <strong class="text-primary">Total Sales:</strong> 
                <span class="text-success fw-bold fs-5">{{ selectedProductData.total_sales }}</span>
              </div>
              <div class="d-flex justify-content-between align-items-center py-2">
                <strong class="text-primary">Taxable:</strong> 
                <span class="text-primary">{{ selectedProductData.is_taxable }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="modal-footer border-top d-flex justify-content-end p-3">
          <button class="btn btn-secondary" @click="closeProductModal">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import BarChart from '@/components/BarChart.vue';
import { useSales } from '@/composables/api/useSales.js';

export default {
  name: 'SalesByItem',
  components: {
    BarChart
  },
  
  data() {
    return {
      // Loading states
      loadingTopItems: false,
      loadingChart: false,
      
      // Sales by Item data
      salesByItemRows: [],
      allSalesByItemRows: [],
      salesByItemLoading: false,
      salesByItemError: null,
      
      // Sales by Item Pagination
      salesByItemPagination: {
        current_page: 1,
        page_size: 10,
        total_records: 0,
        total_pages: 0,
        has_next: false,
        has_prev: false
      },
      
      // Product Details Modal
      showProductModal: false,
      selectedProductData: null,
      
      // Chart and analytics
      selectedFrequency: 'monthly',
      currentDateRange: null,
      topItems: [],
      chartData: {
        labels: ['Loading...'],
        datasets: [{
          label: 'Sales Amount',
          data: [0],
          backgroundColor: ['#e5e7eb'],
          borderColor: ['#d1d5db'],
          borderWidth: 1
        }]
      },

      autoRefreshEnabled: true,
      autoRefreshInterval: 30000,
      autoRefreshTimer: null,
      countdown: 30,
      countdownTimer: null,
      
      // Connection health tracking
      connectionLost: false,
      consecutiveErrors: 0,
      lastSuccessfulLoad: null,
      error: null,
    };
  },
  
  computed: {
    showSalesByItemPagination() {
      return this.salesByItemPagination.total_pages > 1;
    },
    
    getSalesByItemVisiblePages() {
      const current = this.salesByItemPagination.current_page;
      const total = this.salesByItemPagination.total_pages;
      const delta = 2;
      
      if (total <= 7) {
        return Array.from({ length: total }, (_, i) => i + 1);
      }
      
      let start = Math.max(1, current - delta);
      let end = Math.min(total, current + delta);
      
      if (current <= delta + 1) {
        end = Math.min(total, 2 * delta + 2);
      }
      if (current >= total - delta) {
        start = Math.max(1, total - 2 * delta - 1);
      }
      
      const pages = [];
      for (let i = start; i <= end; i++) {
        pages.push(i);
      }
      
      return pages;
    },

    dateRangeDisplay() {
      if (!this.currentDateRange) return 'Select date range';
      const start = new Date(this.currentDateRange.start_date);
      const end = new Date(this.currentDateRange.end_date);
      const opts = { year: 'numeric', month: 'short', day: 'numeric' };
      return `${start.toLocaleDateString('en-US', opts)} - ${end.toLocaleDateString('en-US', opts)}`;
    }
  },
  
  async mounted() {
    await this.loadAllData();
    
    if (this.autoRefreshEnabled) {
      this.startAutoRefresh();
    }
  },

  beforeUnmount() {
    this.stopAutoRefresh();
  },
  
  methods: {
    // ================================================================
    // CORE DATA LOADING METHODS
    // ================================================================
    
    async loadAllData() {
      try {
        await Promise.all([
          this.getTopItems(),
          this.getTopChartItems(),
          this.loadSalesByItemTable()
        ]);
      } catch (error) {
        console.error('Error loading all data:', error);
      }
    },

    async getTopItems() {
      try {
        this.loadingTopItems = true;
        
        const dateRange = this.calculateDateRange(this.selectedFrequency);
        
        const response = await salesDisplayService.getSalesByItem(
          dateRange.start_date, 
          dateRange.end_date
        );

        let items = [];
        
        if (Array.isArray(response)) {
          items = response;
        } else if (response?.data && Array.isArray(response.data)) {
          items = response.data;
        }

        if (items && items.length > 0) {
          const sortedItems = items
            .sort((a, b) => (b.total_sales || 0) - (a.total_sales || 0))
            .slice(0, 5);

          this.topItems = sortedItems.map((item) => ({
            name: item.product_name || 'Unknown Product',
            price: this.formatCurrency(item.total_sales || 0)
          }));
        } else {
          this.topItems = [
            { name: 'No data available', price: '₱0.00' }
          ];
        }
        
        this.connectionLost = false;
        this.consecutiveErrors = 0;
        this.lastSuccessfulLoad = Date.now();
        this.error = null;
        
      } catch (error) {
        console.error("❌ Error loading top items:", error);
        
        this.consecutiveErrors++;
        this.error = `Failed to load top items: ${error.message}`;

        if (this.consecutiveErrors >= 3) {
          this.connectionLost = true;
        }

        this.topItems = [{ name: 'Error loading data', price: '₱0.00' }];
      } finally {
        this.loadingTopItems = false;
      }
    },

    async getTopChartItems() {
      try {
        this.loadingChart = true;
        const dateRange = this.calculateDateRange(this.selectedFrequency);
        
        const response = await salesDisplayService.getSalesByItem(
          dateRange.start_date, 
          dateRange.end_date
        );

        let items = [];
        
        if (Array.isArray(response)) {
          items = response;
        } else if (response?.data && Array.isArray(response.data)) {
          items = response.data;
        }

        if (items && items.length > 0) {
          const sortedItems = items
            .sort((a, b) => (b.total_sales || 0) - (a.total_sales || 0))
            .slice(0, 10);

          const chartItems = sortedItems.map(item => ({
            item_name: item.product_name || 'Unknown Product',
            total_amount: item.total_sales || 0
          }));

          this.updateChartData(chartItems);

          this.connectionLost = false;
          this.consecutiveErrors = 0;
          this.lastSuccessfulLoad = Date.now();
          this.error = null;

        } else {
          this.setDefaultChartData();
        }
        
      } catch (error) {
        console.error("❌ Error in getTopChartItems:", error);
        
        this.consecutiveErrors++;
        this.error = `Failed to load chart data: ${error.message}`;

        if (this.consecutiveErrors >= 3) {
          this.connectionLost = true;
        }

        this.setDefaultChartData();
      } finally {
        this.loadingChart = false;
      }
    },

    async loadSalesByItemTable() {
      try {
        this.salesByItemLoading = true;
        this.salesByItemError = null;
        
        const dateRange = this.calculateDateRange(this.selectedFrequency);
        this.currentDateRange = dateRange;
        
        if (!this.validateDateRange(dateRange.start_date, dateRange.end_date)) {
          this.salesByItemError = 'Invalid date range: start date cannot be after end date';
          this.allSalesByItemRows = [];
          this.salesByItemRows = [];
          return;
        }
        
        console.log('📊 Fetching sales data with date range:', dateRange);
        console.log('📅 Frequency:', this.selectedFrequency);
        
        const response = await salesDisplayService.getSalesByItem(
          dateRange.start_date, 
          dateRange.end_date,
          false
        );

        console.log('📦 Raw API response:', response);
        
        let data = [];
        
        if (Array.isArray(response)) {
          data = response;
        } else if (response?.data && Array.isArray(response.data)) {
          data = response.data;
        } else if (response?.results && Array.isArray(response.results)) {
          data = response.results;
        } else {
          console.warn('⚠️ Unexpected API response format:', response);
          data = [];
        }

        console.log('📈 Processed data for table:', data);

        this.allSalesByItemRows = data
          .filter(item => item && typeof item === 'object')
          .sort((a, b) => {
            const salesA = parseFloat(a.total_sales) || 0;
            const salesB = parseFloat(b.total_sales) || 0;
            return salesB - salesA;
          })
          .map(item => ({
            id: item.product_id || item.id || 'N/A',
            product: item.product_name || item.name || item.product || 'Unknown Product',
            category: item.category_name || item.category || 'Uncategorized',
            stock: parseInt(item.stock) || 0,
            items_sold: parseInt(item.items_sold) || 0,
            total_sales: parseFloat(item.total_sales) || 0,
            selling_price: parseFloat(item.selling_price) || 0,
            unit: item.unit || 'unit',
            sku: item.sku || 'N/A',
            is_taxable: Boolean(item.is_taxable)
          }));

        this.salesByItemPagination.current_page = 1;
        this.updateSalesByItemPageData();

        console.log('🎯 Final table rows:', this.salesByItemRows);
        console.log('📄 Pagination info:', this.salesByItemPagination);

        this.connectionLost = false;
        this.consecutiveErrors = 0;
        this.lastSuccessfulLoad = Date.now();
        this.error = null;

      } catch (error) {
        console.error('❌ loadSalesByItemTable error:', error);
        
        this.consecutiveErrors++;
        this.salesByItemError = this.getErrorMessage(error);

        if (this.consecutiveErrors >= 3) {
          this.connectionLost = true;
        }

        this.allSalesByItemRows = [];
        this.salesByItemRows = [];
        this.salesByItemPagination.current_page = 1;
        this.updateSalesByItemPageData();
        
      } finally {
        this.salesByItemLoading = false;
      }
    },

    // ================================================================
    // DATE FILTERING METHODS - FIXED
    // ================================================================
    
    calculateDateRange(frequency) {
      const now = new Date();
      const end_date = this.formatDateForAPI(now);
      let start_date;
      
      switch (frequency) {
        case 'daily':
          // Last 30 days
          const dailyDate = new Date(now);
          dailyDate.setDate(dailyDate.getDate() - 30);
          start_date = this.formatDateForAPI(dailyDate);
          break;
        case 'weekly':
          // Last 12 weeks
          const weeklyDate = new Date(now);
          weeklyDate.setDate(weeklyDate.getDate() - (12 * 7));
          start_date = this.formatDateForAPI(weeklyDate);
          break;
        case 'monthly':
          // Last 12 months
          const monthlyDate = new Date(now);
          monthlyDate.setMonth(monthlyDate.getMonth() - 12);
          start_date = this.formatDateForAPI(monthlyDate);
          break;
        case 'yearly':
          // Last 3 years
          const yearlyDate = new Date(now);
          yearlyDate.setFullYear(yearlyDate.getFullYear() - 3);
          start_date = this.formatDateForAPI(yearlyDate);
          break;
        default:
          // Default to last 30 days
          const defaultDate = new Date(now);
          defaultDate.setDate(defaultDate.getDate() - 30);
          start_date = this.formatDateForAPI(defaultDate);
      }
      
      console.log(`📅 ${frequency} date range:`, { start_date, end_date });
      
      return { start_date, end_date };
    },

    formatDateForAPI(date) {
      if (!(date instanceof Date)) {
        date = new Date(date);
      }
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    },

    validateDateRange(startDate, endDate) {
      if (!startDate || !endDate) return true;
      
      const start = new Date(startDate);
      const end = new Date(endDate);
      
      return start <= end;
    },

    getErrorMessage(error) {
      if (error.response?.status === 400) {
        return 'Invalid date range or parameters. Please try a different time period.';
      } else if (error.response?.status === 404) {
        return 'Sales data not found for the selected period.';
      } else if (error.response?.status === 500) {
        return 'Server error. Please try again later.';
      } else if (error.message?.includes('Network Error') || error.message?.includes('Failed to fetch')) {
        return 'Network connection failed. Please check your internet connection.';
      } else {
        return error.message || 'Failed to load sales data. Please try again.';
      }
    },

    // ================================================================
    // CHART METHODS - FIXED
    // ================================================================
    
    updateChartData(items) {
      const colors = this.generateChartColors(items.length);
      
      this.chartData = {
        labels: items.map(item => {
          const name = item.item_name || 'Unknown Item';
          return name.length > 20 ? name.substring(0, 20) + '...' : name;
        }),
        datasets: [{
          label: `Sales Amount (${this.selectedFrequency})`,
          data: items.map(item => item.total_amount || 0),
          backgroundColor: colors.background,
          borderColor: colors.border,
          borderWidth: 1
        }]
      };
    },

    generateChartColors(count) {
      const baseColors = [
        '#ef4444', '#3b82f6', '#eab308', '#22c55e', '#8b5cf6',
        '#f59e0b', '#10b981', '#6366f1', '#f97316', '#84cc16'
      ];
      
      const borderColors = [
        '#dc2626', '#2563eb', '#ca8a04', '#16a34a', '#7c3aed',
        '#d97706', '#059669', '#4f46e5', '#ea580c', '#65a30d'
      ];
      
      const background = [];
      const border = [];
      
      for (let i = 0; i < count; i++) {
        background.push(baseColors[i % baseColors.length]);
        border.push(borderColors[i % borderColors.length]);
      }
      
      return { background, border };
    },

    setDefaultChartData() {
      this.chartData = {
        labels: ['No Data Available'],
        datasets: [{
          label: 'Sales Amount',
          data: [0],
          backgroundColor: ['#e5e7eb'],
          borderColor: ['#d1d5db'],
          borderWidth: 1
        }]
      };
    },

    async onFrequencyChange() {
      if (this.showProductModal) {
        return;
      }

      await this.loadAllData();
    },

    // ================================================================
    // PAGINATION METHODS
    // ================================================================
    
    updateSalesByItemPageData() {
      const startIndex = (this.salesByItemPagination.current_page - 1) * this.salesByItemPagination.page_size;
      const endIndex = startIndex + this.salesByItemPagination.page_size;
      
      this.salesByItemRows = this.allSalesByItemRows.slice(startIndex, endIndex);
      
      this.salesByItemPagination.total_records = this.allSalesByItemRows.length;
      this.salesByItemPagination.total_pages = Math.ceil(this.allSalesByItemRows.length / this.salesByItemPagination.page_size);
      this.salesByItemPagination.has_prev = this.salesByItemPagination.current_page > 1;
      this.salesByItemPagination.has_next = this.salesByItemPagination.current_page < this.salesByItemPagination.total_pages;
    },
    
    goToSalesByItemPage(page) {
      if (this.showProductModal) {
        return;
      }
      
      if (page >= 1 && page <= this.salesByItemPagination.total_pages) {
        this.salesByItemPagination.current_page = page;
        this.updateSalesByItemPageData();
      }
    },

    changeSalesByItemPageSize(newPageSize) {
      if (this.showProductModal) {
        return;
      }
      
      this.salesByItemPagination.page_size = newPageSize;
      this.salesByItemPagination.current_page = 1;
      this.updateSalesByItemPageData();
    },

    // ================================================================
    // MODAL METHODS
    // ================================================================
    
    viewProductDetails(product) {
      try {
        this.selectedProductData = {
          id: product.id,
          name: product.product,
          category: product.category,
          stock: product.stock,
          unit: product.unit,
          items_sold: product.items_sold,
          total_sales: this.formatCurrency(product.total_sales),
          selling_price: this.formatCurrency(product.selling_price),
          sku: product.sku || 'N/A',
          is_taxable: product.is_taxable ? 'Yes' : 'No'
        };
        
        this.showProductModal = true;
      } catch (error) {
        console.error('Error in viewProductDetails:', error);
        this.showError('Failed to display product details');
      }
    },

    closeProductModal() {
      this.showProductModal = false;
      this.selectedProductData = null;
    },

    // ================================================================
    // FORMATTING METHODS
    // ================================================================
    
    formatCurrency(amount) {
      let numericAmount = amount;
      
      if (typeof amount === 'string') {
        numericAmount = parseFloat(amount);
      }
      
      if (typeof numericAmount !== 'number' || isNaN(numericAmount)) {
        numericAmount = 0;
      }
      
      return `₱${numericAmount.toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })}`;
    },

    // ================================================================
    // UTILITY METHODS
    // ================================================================
    
    showSuccess(message) {
      alert(message);
    },

    showError(message) {
      console.error('Error:', message);
      alert(message);
    },

    async refreshData() {
      if (this.showProductModal) {
        return;
      }

      try {
        this.error = null;
        await this.loadAllData();
        this.connectionLost = false;
        this.consecutiveErrors = 0;
        this.lastSuccessfulLoad = Date.now();
      } catch (error) {
        console.error('Error refreshing data:', error);
        this.consecutiveErrors++;
        this.error = `Failed to refresh data: ${error.message}`;

        if (this.consecutiveErrors >= 3) {
          this.connectionLost = true;
        }
      }
    },

    toggleAutoRefresh() {
      if (this.autoRefreshEnabled) {
        this.autoRefreshEnabled = false
        this.stopAutoRefresh()
      } else {
        this.autoRefreshEnabled = true
        this.startAutoRefresh()
      }
    },
    
    startAutoRefresh() {
      this.stopAutoRefresh()
      
      this.countdown = this.autoRefreshInterval / 1000
      this.countdownTimer = setInterval(() => {
        this.countdown--
        if (this.countdown <= 0) {
          this.countdown = this.autoRefreshInterval / 1000
        }
      }, 1000)
      
      this.autoRefreshTimer = setInterval(() => {
        this.refreshData()
      }, this.autoRefreshInterval)
    },

    stopAutoRefresh() {
      if (this.autoRefreshTimer) {
        clearInterval(this.autoRefreshTimer)
        this.autoRefreshTimer = null
      }

      if (this.countdownTimer) {
        clearInterval(this.countdownTimer)
        this.countdownTimer = null
      }
    },

    async emergencyReconnect() {
      this.consecutiveErrors = 0
      this.connectionLost = false
      this.error = null
      await this.refreshData()

      if (!this.autoRefreshEnabled) {
        this.autoRefreshEnabled = true
        this.startAutoRefresh()
      }
    },

    getConnectionStatus() {
      if (this.connectionLost) return 'connection-lost'
      if (this.consecutiveErrors > 0) return 'connection-unstable'
      if (this.lastSuccessfulLoad && (Date.now() - this.lastSuccessfulLoad < 60000)) return 'connection-good'
      return 'connection-unknown'
    },

    getConnectionIcon() {
      switch (this.getConnectionStatus()) {
        case 'connection-good': return 'bi bi-wifi text-success'
        case 'connection-unstable': return 'bi bi-wifi-1 text-warning'
        case 'connection-lost': return 'bi bi-wifi-off text-danger'
        default: return 'bi bi-wifi text-muted'
      }
    },

    getConnectionText() {
      switch (this.getConnectionStatus()) {
        case 'connection-good': return 'Connected'
        case 'connection-unstable': return 'Unstable'
        case 'connection-lost': return 'Connection Lost'
        default: return 'Connecting...'
      }
    }
  }
}
</script>

<style scoped>
/* ====================================================================== */
/* LAYOUT OVERRIDES FOR SEMANTIC CLASSES */
/* ====================================================================== */

/* Ensure proper grid layout for top section */
.content-container.d-grid {
  height: auto;
  min-height: 400px;
}

/* Custom divider styling */
.divider-theme {
  width: 2px;
  height: 100%;
  justify-self: center;
}

/* ====================================================================== */
/* CONNECTION STATUS OVERRIDES */
/* ====================================================================== */

/* Connection status semantic overrides */
.connection-good {
  background: var(--status-success-bg);
  border: 1px solid var(--status-success);
  color: var(--status-success);
}

.connection-unstable {
  background: var(--status-warning-bg);
  border: 1px solid var(--status-warning);
  color: var(--status-warning);
}

.connection-lost {
  background: var(--status-error-bg);
  border: 1px solid var(--status-error);
  color: var(--status-error);
}

.connection-unknown {
  background: var(--surface-secondary);
  border: 1px solid var(--border-secondary);
  color: var(--text-tertiary);
}

/* ====================================================================== */
/* SPINNING ICON ANIMATION */
/* ====================================================================== */
.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* ====================================================================== */
/* RESPONSIVE ADJUSTMENTS */
/* ====================================================================== */
@media (max-width: 768px) {
  .content-container.d-grid {
    grid-template-columns: 1fr !important;
  }
  
  .divider-theme {
    display: none;
  }
}

.low-stock {
  color: #dc2626;
  font-weight: bold;
}

.product-column {
  font-weight: 500;
}

.category-column .badge {
  font-size: 11px;
}

.stock-column, .sold-column {
  text-align: center;
  font-weight: 500;
}

.sales-column {
  text-align: right;
  font-weight: bold;
}

.product-column {
  max-width: 200px;
}

.product-column span {
  display: inline-block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100%;
  cursor: help;
}

/* Low stock warning */
.low-stock {
  color: #dc2626;
  font-weight: bold;
}

/* Center align stock and sold columns */
.stock-column, .sold-column {
  text-align: center;
  font-weight: 500;
}

/* Right align sales and price columns */
.sales-column, .price-column {
  text-align: right;
  font-weight: bold;
}

/* Action buttons */
.actions-column {
  text-align: center;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 5px;
}

.action-buttons .btn-sm {
  padding: 4px 8px;
  font-size: 12px;
}

.critical-stock {
  color: #dc2626;
  font-weight: bold;
  background-color: #fef2f2;
  padding: 2px 6px;
  border-radius: 4px;
}

.low-stock {
  color: #d97706;
  font-weight: bold;
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.date-range-info {
  color: #6b7280;
  font-size: 13px;
}

.date-range-info i {
  margin-right: 4px;
}

</style>