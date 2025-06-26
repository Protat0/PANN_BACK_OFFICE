<template>
  <div class="SBI-page">
    <!-- ========================================== -->
    <!-- TOP SECTION: Analytics & Chart -->
    <!-- ========================================== -->
    <div class="TopContainer">
      <!-- Left: Top Five Items List -->
      <div class="LC-SBI">
        <div class="LCL1">
          <h1>Top Five Items</h1>
          <h3>Net Sales</h3>
        </div>
         
        <!-- Loading state for top items -->
        <div v-if="loadingTopItems" class="loading-state-small">
          <div class="spinner-border-sm"></div>
          <p>Loading top items...</p>
        </div>
        
        <!-- Top items list -->
        <ul v-else-if="topItems && topItems.length > 0" class="LCL2">
          <li v-for="(item, index) in topItems" :key="index" class="list-item">
            <span class="item-name" style="font-weight:bold; font-size: 25px;">{{ item.name }}</span>
            <span class="item-price" style="color:green; font-size: 15px;">{{ item.price }}</span>
          </li>
        </ul>
        
        <!-- Empty state for top items -->
        <div v-else class="empty-state-small">
          <p>No top items data available</p>
          <button @click="getTopItems" class="btn btn-sm btn-primary">Retry Loading</button>
        </div>
      </div>
      
      <div class="divider"></div>
      
      <!-- Right: Sales Chart -->
      <div class="RC-SBI">
        <div class="chart-header">
          <h1>Sales Chart</h1>
          <select v-model="selectedFrequency" @change="onFrequencyChange" class="frequency-dropdown">
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
            <option value="yearly">Yearly</option>
          </select>
        </div>
        <div class="chart-container">
          <div v-if="loadingTopItems" class="chart-loading">
            <div class="spinner-border text-primary"></div>
            <p>Loading chart data...</p>
          </div>
          <BarChart v-else :chartData="chartData" :selectedFrequency="selectedFrequency" />
        </div>
      </div>
    </div>
    
    <!-- ========================================== -->
    <!-- BOTTOM SECTION: Transaction History -->
    <!-- ========================================== -->
    <div class="BottomContainer">
      <!-- Header with Action Buttons -->
      <div class="transaction-header">
        <h1>Transaction History</h1>
        <div class="header-actions">
          <button class="btn btn-primary" @click="importData" :disabled="loading || importing">
            <i class="bi bi-upload"></i> {{ importing ? 'Importing...' : 'Import' }}
          </button>
          <button class="btn btn-success" @click="exportData" :disabled="loading || exporting">
            <i class="bi bi-download"></i> {{ exporting ? 'Exporting...' : 'Export' }}
          </button>
          <button class="btn btn-warning" @click="refreshData" :disabled="loading">
            <i class="bi bi-arrow-clockwise"></i> {{ loading ? 'Loading...' : 'Refresh' }}
          </button>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        <div class="spinner-border text-primary"></div>
        <p>Loading transactions...</p>
      </div>
      
      <!-- Transaction Table -->
      <div v-else class="table-container">
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
            <tr v-for="transaction in transactions" :key="transaction._id">
              <td class="id-column" :title="transaction._id">
                {{ transaction._id.slice(-6) }}
              </td>
              <td class="items-column">
                <span class="items-list">
                  {{ formatItemsList(transaction.item_list) }}
                </span>
              </td>
              <td class="customer-column">
                <span :title="transaction.customer_id">
                  {{ transaction.customer_id ? transaction.customer_id.slice(-6) : 'N/A' }}
                </span>
              </td>
              <td class="timestamp-column">
                {{ formatDate(transaction.transaction_date) }}
              </td>
              <td class="payment-column">
                <span class="badge" :class="getPaymentMethodClass(transaction.payment_method)">
                  {{ formatPaymentMethod(transaction.payment_method) }}
                </span>
              </td>
              <td class="sales-type-column">
                <span class="badge" :class="getSalesTypeClass(transaction.sales_type)">
                  {{ formatSalesType(transaction.sales_type) }}
                </span>
              </td>
              <td class="total-column">
                <span class="total-amount">{{ formatCurrency(transaction.total_amount) }}</span>
              </td>
              <td class="actions-column">
                <div class="action-buttons">
                  <button 
                    class="action-btn" 
                    @click.stop="viewTransaction(transaction)" 
                    title="View Details"
                    :disabled="showTransactionModal || showImportProgressModal"
                  >
                    👁️
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        
        <!-- Empty State -->
        <div v-if="transactions.length === 0 && !loading" class="empty-state">
          <i class="bi bi-receipt" style="font-size: 3rem; color: #6b7280;"></i>
          <p>No transactions found</p>
          <button class="btn btn-primary" @click="refreshData">
            <i class="bi bi-arrow-clockwise"></i> Refresh Data
          </button>
        </div>
        
        <!-- Pagination -->
        <div v-if="showPagination" class="pagination-container">
          <div class="pagination-header">
            <div class="pagination-info-right">
              <span class="pagination-text">
                Showing {{ ((pagination.current_page - 1) * pagination.page_size) + 1 }} 
                to {{ Math.min(pagination.current_page * pagination.page_size, pagination.total_records) }} 
                of {{ pagination.total_records }} transactions
              </span>
              
              <div class="page-size-selector">
                <label for="pageSize">Per page:</label>
                <select 
                  id="pageSize"
                  :value="pagination.page_size" 
                  @change="changePageSize(Number($event.target.value))"
                  :disabled="loading"
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

          <nav aria-label="Transaction pagination">
            <ul class="pagination pagination-sm justify-content-center">
              <li class="page-item" :class="{ disabled: !pagination.has_prev || loading }">
                <button 
                  class="page-link" 
                  @click="goToPage(pagination.current_page - 1)"
                  :disabled="!pagination.has_prev || loading"
                  aria-label="Previous page"
                >
                  <i class="bi bi-chevron-left"><<</i>
                </button>
              </li>

              <li 
                v-for="page in getVisiblePages" 
                :key="page"
                class="page-item" 
                :class="{ active: page === pagination.current_page }"
              >
                <button 
                  class="page-link" 
                  @click="goToPage(page)"
                  :disabled="loading"
                >
                  {{ page }}
                </button>
              </li>

              <li class="page-item" :class="{ disabled: !pagination.has_next || loading }">
                <button 
                  class="page-link" 
                  @click="goToPage(pagination.current_page + 1)"
                  :disabled="!pagination.has_next || loading"
                  aria-label="Next page"
                >
                  <i class="bi bi-chevron-right">>></i>
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
    
    <!-- Import Progress Modal - RENAMED -->
    <div v-if="showImportProgressModal" class="modal-overlay" @click="closeImportProgressModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ importStep === 'uploading' ? 'Uploading CSV File' : 'Processing Import' }}</h3>
          <button class="modal-close" @click="closeImportProgressModal" :disabled="importing">&times;</button>
        </div>
        <div class="modal-body">
          <div class="progress-section">
            <div class="progress-info">
              <span>{{ importStatusText }}</span>
              <span class="progress-percentage">{{ Math.round(importProgress) }}%</span>
            </div>
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: importProgress + '%' }"></div>
            </div>
          </div>
          
          <div v-if="importResult" class="import-results">
            <h4>Import Results</h4>
            <div class="result-summary">
              <div class="result-item success">
                <span>✅ Successful:</span>
                <span>{{ importResult.summary?.successful || 0 }}</span>
              </div>
              <div class="result-item error" v-if="importResult.summary?.failed > 0">
                <span>❌ Failed:</span>
                <span>{{ importResult.summary?.failed || 0 }}</span>
              </div>
              <div class="result-item">
                <span>📊 Success Rate:</span>
                <span>{{ importResult.summary?.success_rate || 0 }}%</span>
              </div>
            </div>
            
            <div v-if="importResult.warnings && importResult.warnings.length > 0" class="warnings-section">
              <h5>⚠️ Warnings</h5>
              <ul class="warnings-list">
                <li v-for="warning in importResult.warnings" :key="warning.type">
                  {{ warning.message }}
                </li>
              </ul>
            </div>
          </div>
          
          <div v-if="importError" class="error-section">
            <h4>❌ Import Failed</h4>
            <p class="error-message">{{ importError }}</p>
          </div>
        </div>
        <div class="modal-footer">
          <button v-if="!importing" class="btn btn-secondary" @click="closeImportProgressModal">
            Close
          </button>
          <button v-if="importResult && !importing" class="btn btn-primary" @click="closeImportProgressModal">
            Done
          </button>
        </div>
      </div>
    </div>

    <!-- Transaction Details Modal - RENAMED -->
    <div v-if="showTransactionModal" class="modal-overlay" @click="closeTransactionModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Transaction Details</h2>
          <button class="modal-close" @click="closeTransactionModal">&times;</button>
        </div>
        
        <div class="modal-body">
          <div class="transaction-details" v-if="selectedTransactionData">
            <div class="detail-section">
              <h4>Transaction Information</h4>
              <div class="detail-row">
                <strong>Transaction ID:</strong> 
                <span class="detail-value">{{ selectedTransactionData._original?._id || 'N/A' }}</span>
              </div>
              <div class="detail-row">
                <strong>Transaction Date:</strong> 
                <span class="detail-value">{{ selectedTransactionData.latest_transaction_date }}</span>
              </div>
              <div class="detail-row">
                <strong>Customer ID:</strong> 
                <span class="detail-value">{{ selectedTransactionData._original?.customer_id || 'N/A' }}</span>
              </div>
            </div>

            <div class="detail-section">
              <h4>Items & Pricing</h4>
              <div class="detail-row">
                <strong>Items:</strong> 
                <span class="detail-value">{{ selectedTransactionData.item_name }}</span>
              </div>
              <div class="detail-row">
                <strong>Total Quantity:</strong> 
                <span class="detail-value">{{ selectedTransactionData.total_quantity }}</span>
              </div>
              <div class="detail-row">
                <strong>Unit Price:</strong> 
                <span class="detail-value">{{ selectedTransactionData.unit_price }}</span>
              </div>
              <div class="detail-row">
                <strong>Total Amount:</strong> 
                <span class="detail-value total-highlight">{{ selectedTransactionData.total_amount }}</span>
              </div>
              
              <!-- Detailed Item Breakdown -->
              <div v-if="selectedTransactionData._original?.item_list" class="item-breakdown">
                <h5>Item Details:</h5>
                <div v-for="(item, index) in selectedTransactionData._original.item_list" :key="index" class="item-detail">
                  <div class="item-row">
                    <span class="item-detail-name">{{ item.item_name }}</span>
                    <span class="item-detail-info">
                      {{ item.quantity }} × {{ formatCurrency(item.unit_price) }} = {{ formatCurrency((item.quantity || 0) * (item.unit_price || 0)) }}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <div class="detail-section">
              <h4>Payment & Sales Information</h4>
              <div class="detail-row">
                <strong>Payment Method:</strong> 
                <span class="detail-value">
                  <span class="badge" :class="getPaymentMethodClass(selectedTransactionData._original?.payment_method)">
                    {{ formatPaymentMethod(selectedTransactionData._original?.payment_method) }}
                  </span>
                </span>
              </div>
              <div class="detail-row">
                <strong>Sales Type:</strong> 
                <span class="detail-value">
                  <span class="badge" :class="getSalesTypeClass(selectedTransactionData._original?.sales_type)">
                    {{ formatSalesType(selectedTransactionData._original?.sales_type) }}
                  </span>
                </span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeTransactionModal">Close</button>
          <button class="btn btn-primary" @click="editTransaction(selectedTransactionData)">Edit Transaction</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import BarChart from '@/components/BarChart.vue';
import SalesAPIService from '@/services/apiReports.js';

export default {
  name: 'SalesByItem',
  components: {
    BarChart
  },
  
  // ====================================================================
  // COMPONENT DATA
  // ====================================================================
  data() {
    return {
      // Loading states
      loading: false,
      loadingTopItems: false,
      importing: false,
      exporting: false,
      
      // Import modal states
      showImportProgressModal: false,
      importProgress: 0,
      importStep: 'uploading', // 'uploading' or 'processing'
      importStatusText: 'Preparing upload...',
      importResult: null,
      importError: null,
      
      // Transaction view modal states - RENAMED to avoid conflicts
      showTransactionModal: false,
      selectedTransactionData: null,
      
      // Chart and analytics
      selectedFrequency: 'monthly',
      topItems: [], // Enhanced with more data
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
      
      // Transaction data with pagination
      transactions: [],
      pagination: {
        current_page: 1,
        page_size: 10,
        total_records: 0,
        total_pages: 0,
        has_next: false,
        has_prev: false
      }
    };
  },
  
  // ====================================================================
  // COMPUTED PROPERTIES
  // ====================================================================
  computed: {
    isDevelopment() {
      return process.env.NODE_ENV === 'development';
    },
    
    showPagination() {
      return this.pagination.total_pages > 1;
    },
    
    getVisiblePages() {
      const current = this.pagination.current_page;
      const total = this.pagination.total_pages;
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
    }
  },
  
  // ====================================================================
  // LIFECYCLE HOOKS
  // ====================================================================
  async mounted() {
    console.log("=== Component Mounted ===");
    console.log("SalesAPIService:", SalesAPIService);
    
    // Load data sequentially - separate calls for different purposes
    try {
      console.log("1. Loading top items list...");
      await this.getTopItems(); // For the top 5 items list only
      console.log("✅ Top items list loaded");
    } catch (error) {
      console.error("❌ Top items list failed:", error);
    }
    
    try {
      console.log("2. Loading chart data...");
      await this.getTopChartItems(); // For the chart only
      console.log("✅ Chart data loaded");
    } catch (error) {
      console.error("❌ Chart data failed:", error);
    }
    
    try {
      console.log("3. Loading transaction history...");
      await this.loadTransactionHistory();
      console.log("✅ Transaction history loaded");
    } catch (error) {
      console.error("❌ Transaction history failed:", error);
    }
  },
  
  // ====================================================================
  // METHODS
  // ====================================================================
  methods: {
    // ================================================================
    // DATA LOADING METHODS
    // ================================================================
    
    /**
     * Load top items for the list display only
     */
    async getTopItems() {
      try {
        console.log("=== Loading Top Items List Only ===");
        this.loadingTopItems = true;
        
        if (!SalesAPIService?.getTopItems) {
          throw new Error("getTopItems method not found in SalesAPIService");
        }
        
        const response = await SalesAPIService.getTopItems({ limit: 5 });
        console.log("Raw API Response:", response);
        
        let items = [];
        
        // Try different response structures
        if (response?.data?.items && Array.isArray(response.data.items)) {
          items = response.data.items;
        } else if (response?.data?.data && Array.isArray(response.data.data)) {
          items = response.data.data;
        } else if (Array.isArray(response?.data)) {
          items = response.data;
        } else if (Array.isArray(response)) {
          items = response;
        }
        
        console.log("Extracted items:", items);
        
        if (items && items.length > 0) {
          this.topItems = items.slice(0, 5).map((item, index) => ({
            name: item.item_name || item.name || item.product_name || `Item ${index + 1}`,
            price: this.formatCurrency(
              item.total_amount || item.total_sales || item.revenue || 
              item.sales || item.price || item.amount || 0
            )
          }));
          console.log("✅ Top items successfully formatted:", this.topItems);
        } else {
          this.topItems = [
            { name: 'No data available', price: '₱0.00' }
          ];
        }
      } catch (error) {
        console.error("❌ Error loading top items:", error);
        this.topItems = [{ name: 'Error loading data', price: '₱0.00' }];
      } finally {
        this.loadingTopItems = false;
      }
    },

    /**
     * Load chart data with date filtering - FIXED VERSION
     */
    async getTopChartItems() {
      try {
        console.log("=== Loading Chart Data Only ===");
        
        // Don't set loading for chart specifically, use separate flag
        const dateRange = this.calculateDateRange(this.selectedFrequency);
        console.log("Date range for", this.selectedFrequency, ":", dateRange);
        
        // Try the enhanced chart API first
        if (SalesAPIService?.getTopChartItems) {
          const requestParams = {
            limit: 10,
            start_date: dateRange.start_date,
            end_date: dateRange.end_date,
            frequency: this.selectedFrequency
          };
          
          console.log("Request params for chart:", requestParams);
          
          try {
            const response = await SalesAPIService.getTopChartItems(requestParams);
            console.log("Chart API Response:", response);
            
            let items = [];
            if (response?.success && response.data) {
              items = response.data;
            } else if (Array.isArray(response)) {
              items = response;
            }
            
            if (items && items.length > 0) {
              this.updateChartData(items.slice(0, 10));
              console.log("✅ Chart data updated successfully");
              return; // Success, exit early
            }
          } catch (chartError) {
            console.warn("Chart API failed, trying fallback:", chartError.message);
            // Don't return, fall through to fallback
          }
        }
        
        // Fallback: Use regular top items API for chart
        console.log("🔄 Using fallback: regular top items API for chart");
        if (SalesAPIService?.getTopItems) {
          try {
            const response = await SalesAPIService.getTopItems({ limit: 10 });
            console.log("Fallback API Response:", response);
            
            let items = [];
            if (response?.data?.items && Array.isArray(response.data.items)) {
              items = response.data.items;
            } else if (response?.data?.data && Array.isArray(response.data.data)) {
              items = response.data.data;
            } else if (Array.isArray(response?.data)) {
              items = response.data;
            } else if (Array.isArray(response)) {
              items = response;
            }
            
            if (items && items.length > 0) {
              // Map the regular API response to chart format
              const chartItems = items.map(item => ({
                item_name: item.item_name || item.name || 'Unknown Item',
                total_amount: item.total_amount || item.total_sales || item.revenue || 0
              }));
              
              this.updateChartData(chartItems.slice(0, 10));
              console.log("✅ Fallback chart data loaded successfully");
              return;
            }
          } catch (fallbackError) {
            console.error("❌ Fallback also failed:", fallbackError);
          }
        }
        
        // If we get here, both APIs failed
        console.warn("Both chart APIs failed, using default chart");
        this.setDefaultChartData();
        
      } catch (error) {
        console.error("❌ Error in getTopChartItems:", error);
        this.setDefaultChartData();
      }
    },

    /**
     * Load transaction history from API
     */
    async loadTransactionHistory(page = 1, pageSize = 10) {
      try {
        console.log("=== Loading Transaction History ===");
        this.loading = true;
        
        if (!SalesAPIService.getSalesItemHistory) {
          throw new Error("getSalesItemHistory method not found in SalesAPIService");
        }
        
        const response = await SalesAPIService.getSalesItemHistory({
          page: page,
          page_size: pageSize
        });
        
        if (response?.success) {
          this.transactions = response.data.data || [];
          this.pagination = response.data.pagination || {
            current_page: 1,
            page_size: 10,
            total_records: 0,
            total_pages: 0,
            has_next: false,
            has_prev: false
          };
          console.log("Loaded transactions:", this.transactions.length);
        } else {
          throw new Error(response?.message || 'Failed to load transaction history');
        }
      } catch (error) {
        console.error("Error loading transaction history:", error);
        this.showError(`Failed to load transaction history: ${error.message}`);
        this.transactions = [];
      } finally {
        this.loading = false;
      }
    },

    // ================================================================
    // CHART METHODS
    // ================================================================
    
    /**
     * Calculate date range based on frequency
     */
    calculateDateRange(frequency) {
      const now = new Date();
      const end_date = now.toISOString().split('T')[0];
      let start_date;
      
      switch (frequency) {
        case 'daily':
          start_date = new Date(now.getTime() - (7 * 24 * 60 * 60 * 1000))
            .toISOString().split('T')[0];
          break;
        case 'weekly':
          start_date = new Date(now.getTime() - (8 * 7 * 24 * 60 * 60 * 1000))
            .toISOString().split('T')[0];
          break;
        case 'monthly':
          const monthsAgo = new Date(now);
          monthsAgo.setMonth(monthsAgo.getMonth() - 12);
          start_date = monthsAgo.toISOString().split('T')[0];
          break;
        case 'yearly':
          const yearsAgo = new Date(now);
          yearsAgo.setFullYear(yearsAgo.getFullYear() - 5);
          start_date = yearsAgo.toISOString().split('T')[0];
          break;
        default:
          const defaultDate = new Date(now);
          defaultDate.setMonth(defaultDate.getMonth() - 1);
          start_date = defaultDate.toISOString().split('T')[0];
      }
      
      return { start_date, end_date };
    },

    /**
     * Update chart data with API response
     */
    updateChartData(items) {
      const colors = this.generateChartColors(items.length);
      
      this.chartData = {
        labels: items.map(item => item.item_name || 'Unknown Item'),
        datasets: [{
          label: `Sales Amount (${this.selectedFrequency})`,
          data: items.map(item => item.total_amount || 0),
          backgroundColor: colors.background,
          borderColor: colors.border,
          borderWidth: 1
        }]
      };
    },

    /**
     * Generate colors for chart items
     */
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

    /**
     * Set default chart data when no API data available
     */
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

    /**
     * Handle frequency change - FIXED to not interfere with modals
     */
    async onFrequencyChange() {
      console.log("Frequency changed to:", this.selectedFrequency);
      
      // IMPORTANT: Don't reload chart if modal is open
      if (this.showTransactionModal || this.showImportProgressModal) {
        console.log("Modal is open, deferring chart reload");
        return;
      }
      
      // Only reload chart data, not top items list
      await this.getTopChartItems();
    },

    // ================================================================
    // PAGINATION METHODS
    // ================================================================
    
    /**
     * Go to specific page - FIXED to not interfere with modals
     */
    async goToPage(page) {
      if (this.showTransactionModal || this.showImportProgressModal) {
        console.log("Modal is open, preventing page change");
        return;
      }
      
      if (page >= 1 && page <= this.pagination.total_pages) {
        await this.loadTransactionHistory(page, this.pagination.page_size);
      }
    },
    
    /**
     * Change page size - FIXED to not interfere with modals
     */
    async changePageSize(newPageSize) {
      if (this.showTransactionModal || this.showImportProgressModal) {
        console.log("Modal is open, preventing page size change");
        return;
      }
      
      await this.loadTransactionHistory(1, newPageSize);
    },
    
    /**
     * Refresh all data - FIXED to not interfere with modals
     */
    async refreshData() {
      if (this.showTransactionModal || this.showImportProgressModal) {
        console.log("Modal is open, preventing data refresh");
        return;
      }
      
      await Promise.all([
        this.loadTransactionHistory(this.pagination.current_page, this.pagination.page_size),
        this.getTopItems(),
        this.getTopChartItems()
      ]);
    },

    // ================================================================
    // MODAL METHODS - FIXED
    // ================================================================
    
    /**
     * View transaction details - FIXED to handle proper data structure
     */
    viewTransaction(transaction) {
      console.log('=== VIEW TRANSACTION DEBUG ===');
      console.log('1. Transaction received:', transaction);
      console.log('2. Item list:', transaction.item_list);
      
      try {
        // FORCE close any other modals first
        this.showImportProgressModal = false;
        this.selectedTransactionData = null;
        
        // Calculate total quantity and get unit price from item_list
        let totalQuantity = 0;
        let unitPrice = 0;
        let itemNames = [];
        
        if (transaction.item_list && Array.isArray(transaction.item_list)) {
          transaction.item_list.forEach(item => {
            if (item.quantity) {
              totalQuantity += parseFloat(item.quantity) || 0;
            }
            if (item.unit_price && unitPrice === 0) {
              // Use the first item's unit price, or you could calculate average
              unitPrice = parseFloat(item.unit_price) || 0;
            }
            if (item.item_name) {
              itemNames.push(`${item.item_name} (${item.quantity || 0})`);
            }
          });
        }
        
        console.log('3. Calculated totalQuantity:', totalQuantity);
        console.log('4. Calculated unitPrice:', unitPrice);
        console.log('5. Item names:', itemNames);
        
        // Force Vue to update the DOM
        this.$nextTick(() => {
          // Set the selected transaction with proper data mapping
          this.selectedTransactionData = {
            item_name: itemNames.length > 0 ? itemNames.join(', ') : 'No items',
            total_amount: this.formatCurrency(transaction.total_amount),
            total_quantity: totalQuantity || 'N/A',
            unit_price: unitPrice > 0 ? this.formatCurrency(unitPrice) : 'N/A',
            latest_transaction_date: this.formatDate(transaction.transaction_date),
            _original: transaction // Keep original data for reference
          };
          
          console.log('6. Final selectedTransactionData:', this.selectedTransactionData);
          
          // Show the modal
          this.showTransactionModal = true;
          console.log('7. Modal state set to:', this.showTransactionModal);
          
          // Force another update
          this.$forceUpdate();
        });
        
      } catch (error) {
        console.error('❌ Error in viewTransaction:', error);
        this.showError('Failed to display transaction details');
      }
    },
    
    /**
     * Close transaction view modal - ENHANCED
     */
    closeTransactionModal() {
      console.log('Closing transaction modal...');
      this.showTransactionModal = false;
      this.selectedTransactionData = null;
      
      // Force update to ensure DOM changes
      this.$nextTick(() => {
        console.log('Transaction modal closed, state:', this.showTransactionModal);
      });
    },
    
    /**
     * Edit transaction (placeholder)
     */
    editTransaction(transaction) {
      console.log('Edit transaction called with:', transaction);
      this.closeTransactionModal();
      
      // TODO: Implement edit functionality
      this.showSuccess('Edit functionality not implemented yet');
    },

    // ================================================================
    // IMPORT/EXPORT METHODS
    // ================================================================
    
    /**
     * Import data using CSV bulk import with progress modal
     */
    async importData() {
      try {
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = '.csv';
        fileInput.style.display = 'none';
        
        fileInput.addEventListener('change', async (event) => {
          const file = event.target.files[0];
          if (!file) return;
          
          this.showImportProgressModal = true;
          this.importing = true;
          this.importProgress = 0;
          this.importStep = 'uploading';
          this.importStatusText = 'Preparing upload...';
          this.importResult = null;
          this.importError = null;
          
          try {
            const result = await SalesAPIService.bulkImportCSV(file, (progress) => {
              this.importProgress = progress;
              this.importStatusText = `Uploading file... ${Math.round(progress)}%`;
              
              if (progress === 100) {
                this.importStep = 'processing';
                this.importStatusText = 'Processing CSV data...';
              }
            });
            
            this.importResult = result;
            this.importProgress = 100;
            this.importStatusText = 'Import completed successfully!';
            
            await this.refreshData();
            
          } catch (error) {
            console.error('Import failed:', error);
            this.importError = error.message;
            this.importProgress = 0;
            this.importStatusText = 'Import failed';
          } finally {
            this.importing = false;
            document.body.removeChild(fileInput);
          }
        });
        
        document.body.appendChild(fileInput);
        fileInput.click();
        
      } catch (error) {
        console.error('Error setting up import:', error);
        this.showError('Failed to start import process');
      }
    },
    
    /**
     * Export data to CSV
     */
    async exportData() {
      try {
        this.exporting = true;
        
        const success = await SalesAPIService.exportTransactions({});
        
        if (success) {
          this.showSuccess('Export completed successfully! Check your downloads folder.');
        } else {
          throw new Error('Export failed');
        }
        
      } catch (error) {
        console.error('Export failed:', error);
        
        if (error.message.includes('404') || error.message.includes('Not Found')) {
          this.showError('Export feature is not yet configured on the server. Please contact support.');
        } else {
          this.showError(`Export failed: ${error.message}`);
        }
      } finally {
        this.exporting = false;
      }
    },

    /**
     * Close import modal
     */
    closeImportProgressModal() {
      if (!this.importing) {
        this.showImportProgressModal = false;
        this.importProgress = 0;
        this.importResult = null;
        this.importError = null;
      }
    },

    // ================================================================
    // FORMATTING METHODS
    // ================================================================
    
    /**
     * Format items list for display - FIXED for actual data structure
     */
    formatItemsList(itemList) {
      if (!itemList || !Array.isArray(itemList)) return 'No items';
      
      return itemList
        .filter(item => item && item.item_name)
        .map(item => {
          const quantity = item.quantity ? ` (${item.quantity})` : '';
          return `${item.item_name}${quantity}`;
        })
        .join(', ') || 'No items';
    },
    
    /**
     * Format date for display
     */
    formatDate(dateString) {
      if (!dateString) return 'Unknown';
      
      try {
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return 'Invalid date';
        
        return date.toLocaleString('en-US', {
          year: 'numeric',
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        });
      } catch (error) {
        console.error('Error formatting date:', error);
        return 'Invalid date';
      }
    },
    
    /**
     * Format payment method for display
     */
    formatPaymentMethod(method) {
      if (!method) return 'Unknown';
      
      const methodMap = {
        'cash': 'Cash',
        'card': 'Card',
        'credit_card': 'Credit Card',
        'debit_card': 'Debit Card',
        'gcash': 'GCash',
        'paymaya': 'PayMaya',
        'bank_transfer': 'Bank Transfer',
        'online': 'Online Payment'
      };
      
      return methodMap[method.toLowerCase()] || 
             method.charAt(0).toUpperCase() + method.slice(1).toLowerCase();
    },
    
    /**
     * Format sales type for display
     */
    formatSalesType(type) {
      if (!type) return 'Unknown';
      
      const typeMap = {
        'dine_in': 'Dine-in',
        'takeout': 'Takeout',
        'delivery': 'Delivery',
        'online': 'Online',
        'pickup': 'Pickup'
      };
      
      return typeMap[type.toLowerCase()] || 
             type.charAt(0).toUpperCase() + type.slice(1).toLowerCase();
    },
    
    /**
     * Format currency amount
     */
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
    
    /**
     * Get CSS class for payment method badge
     */
    getPaymentMethodClass(method) {
      const classMap = {
        'cash': 'badge-success',
        'card': 'badge-primary',
        'credit_card': 'badge-primary',
        'debit_card': 'badge-info',
        'gcash': 'badge-warning',
        'paymaya': 'badge-info',
        'bank_transfer': 'badge-secondary',
        'online': 'badge-dark'
      };
      
      return classMap[method?.toLowerCase()] || 'badge-secondary';
    },
    
    /**
     * Get CSS class for sales type badge
     */
    getSalesTypeClass(type) {
      const classMap = {
        'dine_in': 'badge-success',
        'takeout': 'badge-warning',
        'delivery': 'badge-info',
        'online': 'badge-primary',
        'pickup': 'badge-secondary'
      };
      
      return classMap[type?.toLowerCase()] || 'badge-secondary';
    },

    // ================================================================
    // UTILITY METHODS
    // ================================================================
    
    /**
     * Show success message
     */
    showSuccess(message) {
      console.log('Success:', message);
      alert(message); // Replace with your notification system
    },
    
    /**
     * Show error message
     */
    showError(message) {
      console.error('Error:', message);
      alert(message); // Replace with your notification system
    }
  }
}
</script>

<style scoped>
/* ====================================================================== */
/* MAIN LAYOUT */
/* ====================================================================== */
.SBI-page {
  padding: 0;
  width: 100%;
  max-width: 1600px;
  margin: 0 auto;
}

.TopContainer {
  width: 100%;
  height: 400px;
  display: grid;
  grid-template-columns: 1fr 2px 1fr;
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

/* ====================================================================== */
/* TOP ITEMS SECTION */
/* ====================================================================== */
.LCL1 {
  display: flex;
  align-items: baseline;
  gap: 250px;
}

.LCL1 h1, .LCL1 h3 {
  margin: 0;
}

.LCL1 h3 {
  color: grey;
  font-size: 20px;
}

.LCL1 h1 {
  color: black;
  font-size: 30px;
  font-weight: bold;
}

.LC-SBI h1 {
  font-weight: bold;
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

/* ====================================================================== */
/* CHART SECTION */
/* ====================================================================== */
.RC-SBI {
  color: black;
}

.RC-SBI h1 {
  font-weight: bold;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.chart-header h1 {
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
  width: 500px;
  height: 100%;
}

.chart-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  width: 100%;
}

.chart-loading p {
  margin-top: 10px;
  color: #6b7280;
}

/* ====================================================================== */
/* TRANSACTION SECTION */
/* ====================================================================== */
.BottomContainer {
  color: black;
  width: 100%;
  margin-top: 40px;
}

.transaction-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e5e7eb;
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
  padding: 8px 16px;
  border-radius: 6px;
  font-weight: 500;
  transition: all 0.2s;
}

.header-actions .btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* ====================================================================== */
/* TABLE STYLES */
/* ====================================================================== */
.table-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.table {
  margin: 0;
  width: 100%;
}

.table thead th {
  background-color: #f8fafc;
  font-weight: 600;
  color: #374151;
  border-bottom: 2px solid #e5e7eb;
  padding: 12px;
}

.table tbody td {
  padding: 12px;
  vertical-align: middle;
  border-bottom: 1px solid #f3f4f6;
}

.table tbody tr:hover {
  background-color: #f9fafb;
}

.id-column {
  font-family: monospace;
  font-size: 12px;
  color: #6b7280;
  cursor: help;
}

.items-column {
  max-width: 200px;
}

.items-list {
  display: inline-block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100%;
}

.customer-column {
  font-family: monospace;
  font-size: 12px;
  color: #6b7280;
}

.total-amount {
  font-weight: bold;
  color: #059669;
}

.badge {
  font-size: 11px;
  padding: 4px 8px;
  border-radius: 12px;
  font-weight: 500;
  color: white;
}

.badge-success { background-color: #059669; }
.badge-primary { background-color: #3b82f6; }
.badge-info { background-color: #06b6d4; }
.badge-warning { background-color: #eab308; color: #374151; }
.badge-secondary { background-color: #6b7280; }
.badge-dark { background-color: #374151; }

.action-buttons {
  display: flex;
  gap: 5px;
}

.action-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: background-color 0.2s;
  font-size: 16px;
}

.action-btn:hover:not(:disabled) {
  background-color: #f3f4f6;
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ====================================================================== */
/* LOADING AND EMPTY STATES */
/* ====================================================================== */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.loading-state p {
  margin-top: 16px;
  color: #6b7280;
}

.loading-state-small {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  text-align: center;
}

.loading-state-small p {
  margin-top: 8px;
  color: #6b7280;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.empty-state p {
  margin: 16px 0;
  color: #6b7280;
  font-size: 16px;
}

.empty-state-small {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  text-align: center;
}

.empty-state-small p {
  margin: 8px 0;
  color: #6b7280;
}

/* ====================================================================== */
/* PAGINATION STYLES */
/* ====================================================================== */
.pagination-container {
  padding: 20px;
  border-top: 1px solid #e5e7eb;
  background-color: #f9fafb;
}

.pagination-header {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 16px;
}

.pagination-info-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
}

.pagination-text {
  color: #6b7280;
  font-size: 14px;
  text-align: right;
}

.page-size-selector {
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: flex-end;
}

.page-size-selector label {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
  white-space: nowrap;
}

.page-size-selector select {
  width: auto;
  min-width: 70px;
  padding: 4px 8px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 13px;
}

.pagination {
  margin: 0;
  display: flex;
  list-style: none;
  padding: 0;
  justify-content: center;
  margin-right: 120px;
}

.page-item {
  margin: 0 2px;
}

.page-link {
  color: #6b7280;
  border: 1px solid #d1d5db;
  padding: 6px 12px;
  text-decoration: none;
  background: white;
  cursor: pointer;
  border-radius: 4px;
  font-size: 14px;
}

.page-link:hover {
  color: #374151;
  background-color: #f3f4f6;
  border-color: #d1d5db;
}

.page-item.active .page-link {
  background-color: #3b82f6;
  border-color: #3b82f6;
  color: white;
}

.page-item.disabled .page-link {
  color: #9ca3af;
  background-color: #f9fafb;
  border-color: #e5e7eb;
  cursor: not-allowed;
}

/* ====================================================================== */
/* MODAL STYLES - ENHANCED */
/* ====================================================================== */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex !important; /* Force display */
  justify-content: center;
  align-items: center;
  z-index: 9999;
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
}

.modal-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
  z-index: 10000;
  animation: modalFadeIn 0.3s ease-out;
  
  /* Ensure modal is always visible when shown */
  opacity: 1 !important;
  visibility: visible !important;
  pointer-events: auto !important;
}

@keyframes modalFadeIn {
  from {
    opacity: 0;
    transform: scale(0.9) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
  margin: 0;
}

.modal-header h2, .modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #374151;
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #6b7280;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: background-color 0.2s;
}

.modal-close:hover {
  background-color: #f3f4f6;
}

.modal-close:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.modal-body {
  padding: 24px;
}

.modal-footer {
  padding: 16px 24px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* ====================================================================== */
/* TRANSACTION DETAILS MODAL */
/* ====================================================================== */
.transaction-details {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.detail-section {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  background-color: #f9fafb;
}

.detail-section h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 8px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f3f4f6;
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-row strong {
  min-width: 140px;
  color: #374151;
  font-weight: 500;
}

.detail-value {
  color: #6b7280;
  text-align: right;
  max-width: 60%;
  word-wrap: break-word;
}

.detail-value.total-highlight {
  color: #059669;
  font-weight: bold;
  font-size: 16px;
}

/* Item Breakdown Styles */
.item-breakdown {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e5e7eb;
}

.item-breakdown h5 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #374151;
}

.item-detail {
  margin-bottom: 8px;
}

.item-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 8px;
  background-color: #f9fafb;
  border-radius: 4px;
  border-left: 3px solid #3b82f6;
}

.item-detail-name {
  font-weight: 500;
  color: #374151;
  flex: 1;
}

.item-detail-info {
  font-size: 13px;
  color: #6b7280;
  font-family: monospace;
  text-align: right;
}

/* ====================================================================== */
/* IMPORT MODAL STYLES */
/* ====================================================================== */
.progress-section {
  margin-bottom: 24px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.progress-info span {
  font-size: 14px;
  color: #374151;
}

.progress-percentage {
  font-weight: 600;
  color: #3b82f6;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background-color: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: #3b82f6;
  border-radius: 4px;
  transition: width 0.3s ease;
  background-image: linear-gradient(
    45deg,
    rgba(255, 255, 255, 0.15) 25%,
    transparent 25%,
    transparent 50%,
    rgba(255, 255, 255, 0.15) 50%,
    rgba(255, 255, 255, 0.15) 75%,
    transparent 75%,
    transparent
  );
  background-size: 20px 20px;
  animation: progress-animation 1s linear infinite;
}

@keyframes progress-animation {
  0% {
    background-position: 0 0;
  }
  100% {
    background-position: 20px 20px;
  }
}

.import-results {
  margin-top: 20px;
}

.import-results h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #374151;
}

.result-summary {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

.result-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  border-radius: 6px;
  background-color: #f9fafb;
  font-size: 14px;
}

.result-item.success {
  background-color: #f0fdf4;
  color: #166534;
}

.result-item.error {
  background-color: #fef2f2;
  color: #dc2626;
}

.warnings-section {
  margin-top: 16px;
}

.warnings-section h5 {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: 600;
  color: #d97706;
}

.warnings-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.warnings-list li {
  padding: 8px 12px;
  background-color: #fffbeb;
  border-left: 4px solid #f59e0b;
  margin-bottom: 4px;
  font-size: 13px;
  color: #92400e;
}

.error-section {
  margin-top: 20px;
}

.error-section h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  color: #dc2626;
}

.error-message {
  padding: 12px;
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 6px;
  color: #dc2626;
  font-size: 14px;
  margin: 0;
}

/* ====================================================================== */
/* BUTTON STYLES */
/* ====================================================================== */
.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background-color: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #2563eb;
}

.btn-secondary {
  background-color: #6b7280;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #4b5563;
}

.btn-success {
  background-color: #10b981;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background-color: #059669;
}

.btn-warning {
  background-color: #f59e0b;
  color: white;
}

.btn-warning:hover:not(:disabled) {
  background-color: #d97706;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
}

/* ====================================================================== */
/* RESPONSIVE DESIGN */
/* ====================================================================== */
@media (max-width: 768px) {
  .TopContainer {
    grid-template-columns: 1fr;
    height: auto;
  }
  
  .divider {
    display: none;
  }
  
  .LCL1 {
    gap: 20px;
    flex-direction: column;
    align-items: flex-start;
  }
  
  .chart-container {
    width: 100%;
    height: 300px;
  }
  
  .transaction-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
  
  .header-actions {
    width: 100%;
    justify-content: flex-end;
  }
  
  .pagination-header {
    justify-content: center;
  }
  
  .pagination-info-right {
    align-items: center;
    text-align: center;
  }
  
  .modal-content {
    width: 95%;
    margin: 10px;
  }
  
  .detail-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
  
  .detail-value {
    max-width: 100%;
    text-align: left;
  }
}

@media (max-width: 480px) {
  .table-container {
    overflow-x: auto;
  }
  
  .table {
    min-width: 600px;
  }
  
  .modal-body {
    padding: 16px;
  }
  
  .btn {
    padding: 6px 12px;
    font-size: 13px;
  }
}
</style>