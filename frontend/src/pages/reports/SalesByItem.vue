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
        <div v-else class="text-center py-4">
          <p class="text-tertiary">No top items data available</p>
          <button @click="getTopItems" class="btn btn-sm btn-primary">Retry Loading</button>
        </div>
      </div>
      
      <div class="divider-theme"></div>
      
      <!-- Right: Sales Chart -->
      <div class="surface-card rounded p-3">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <h1 class="text-primary mb-0">Sales Chart</h1>
          <select v-model="selectedFrequency" @change="onFrequencyChange" class="form-select">
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
            <option value="yearly">Yearly</option>
          </select>
        </div>
        <div class="chart-container d-flex justify-content-center align-items-center" style="height: 300px;">
          <div v-if="loadingTopItems" class="text-center">
            <div class="spinner-border text-accent" role="status">
              <span class="visually-hidden">Loading chart data...</span>
            </div>
            <p class="text-tertiary mt-2">Loading chart data...</p>
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
      <div class="header-theme d-flex justify-content-between align-items-center mb-3 p-3 rounded">
        <h1 class="text-primary mb-0">Sales by Item</h1>
        <div class="d-flex gap-2 align-items-center">
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
              <td class="text-center">
                <span :class="{'text-error fw-bold': item.stock < 10}" class="fw-medium">
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
                    <Eye />
                  </button>
              </td>
            </tr>
          </tbody>
        </table>
        
        <!-- Empty State -->
        <div v-if="salesByItemRows.length === 0 && !salesByItemLoading" class="text-center py-5">
          <i class="bi bi-receipt text-tertiary" style="font-size: 3rem;"></i>
          <p class="text-tertiary mt-3">No sales data found for the selected time period</p>
          <button class="btn btn-primary" @click="refreshData">
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
  
  setup() {
    return useSales();
  },
  
  // ====================================================================
  // All data, computed properties, and methods are now provided by useSales composable
  // ====================================================================
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

</style>