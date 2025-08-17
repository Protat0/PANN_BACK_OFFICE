<template>
  <div class="promotions-page">
  <!-- Main Content -->
   <h1 class="page-title">Promotion Management</h1>   
  <div class="container-fluid py-4">
    
    <!-- Loading State (outside action-bar) -->
    <div v-if="loading" class="text-center py-4">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2 text-muted">Loading promotions...</p>
    </div>

    <!-- Error State (outside action-bar) -->
    <div v-if="error" class="alert alert-danger" role="alert">
      {{ error }}
      <button @click="loadPromotions" class="btn btn-sm btn-outline-danger ms-2">
        Retry
      </button>
    </div>

    <!-- Action Bar and Filters (only show when not loading) -->
    <div v-if="!loading" class="action-bar-container mb-3">
      <div class="action-row">
        <!-- Left Side: Main Actions (Always visible when no selection) -->
        <div v-if="selectedPromotions.length === 0" class="d-flex gap-2">
          <!-- Add Promo Button -->
          <button 
            class="btn btn-add btn-sm btn-with-icon"
            @click="handleSinglePromo"
          >
            <Plus :size="14" />
            ADD PROMO
          </button>

          <button 
            class="btn btn-outline-secondary btn-sm"
            @click="exportData"
          >
            EXPORT
          </button>
        </div>
         <div class="auto-refresh-status">
          <i class="bi bi-arrow-repeat text-success" :class="{ 'spinning': loading }"></i>
          <span class="status-text">
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
        <!-- Selection Actions (Visible when items are selected) -->
        <div v-if="selectedPromotions.length > 0" class="d-flex gap-2">
          <button 
            class="btn btn-delete btn-sm btn-with-icon"
            @click="deleteSelected"
          >
            <Trash2 :size="14" />
            DELETE ({{ selectedPromotions.length }})
          </button>
        </div>

        <!-- Right Side: Search and Filters -->
        <div class="filters-section d-flex align-items-center gap-2">
          <!-- Search Toggle -->
          <button 
            class="btn btn-secondary btn-sm search-toggle-btn"
            @click="toggleSearchMode"
            :class="{ 'active': searchMode }"
          >
            <Search :size="16" />
          </button>

          <!-- Filter Dropdowns (Hidden when search is active) -->
          <template v-if="!searchMode">
            <div class="filter-group">
              <label class="filter-label">Discount Type</label>
              <select 
                class="form-select form-select-sm" 
                v-model="discountTypeFilter" 
                @change="applyFilters"
              >
                <option value="all">All types</option>
                <option value="percentage">Percentage</option>
                <option value="fixed">Fixed Amount</option>
                <option value="buy_one_get_one">BOGO</option>
              </select>
            </div>

            <div class="filter-group">
              <label class="filter-label">Status</label>
              <select 
                class="form-select form-select-sm" 
                v-model="statusFilter" 
                @change="applyFilters"
              >
                <option value="all">All status</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="expired">Expired</option>
                <option value="scheduled">Scheduled</option>
                <option value="deleted">Deleted Items</option>  
              </select>
            </div>
          </template>

          <!-- Search Bar (Visible when search mode is active) -->
          <div v-if="searchMode" class="search-container">
            <div class="position-relative">
              <input 
                ref="searchInput"
                v-model="searchFilter" 
                @input="applyFilters"
                type="text" 
                class="form-control form-control-sm search-input"
                placeholder="Search promotions..."
              />
              <button 
                class="btn btn-sm btn-link position-absolute end-0 top-50 translate-middle-y"
                @click="clearSearch"
                style="border: none; padding: 0.25rem;"
              >
                <X :size="16" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Data Table (only show when not loading) -->
    <div v-if="!loading" class="row">
      <div class="col-12">
        <!-- Promotions Table -->
        <DataTable
          :total-items="totalPromotions"
          :current-page="currentPage"
          :items-per-page="itemsPerPage"
          @page-changed="handlePageChange"
        >
          <template #header>
            <tr>
              <th class="text-center" style="width: 50px;">
                <div class="form-check">
                  <input 
                    class="form-check-input" 
                    type="checkbox" 
                    :checked="isAllSelected"
                    :indeterminate="isIndeterminate"
                    @change="toggleSelectAll"
                  >
                </div>
              </th>
              <th>Promotion Name</th>
              <th>Discount Type</th>
              <th>Discount Value</th>
              <th>Start Date</th>
              <th>End Date</th>
              <th>Status</th>
              <th>Last Updated</th>
              <th class="text-center" style="width: 120px;">Actions</th>
            </tr>
          </template>

          <template #body>
            <tr 
              v-for="promotion in paginatedPromotions" 
              :key="promotion._id"
              :class="{ 'table-primary': selectedPromotions.includes(promotion._id) }"
            >
              <td class="text-center">
                <div class="form-check">
                  <input 
                    class="form-check-input" 
                    type="checkbox" 
                    :value="promotion._id"
                    v-model="selectedPromotions"
                  >
                </div>
              </td>
              <td>
                <div class="fw-medium text-tertiary-dark">{{ promotion.promotion_name }}</div>
              </td>
              <td>
                <span class="badge" :class="getDiscountTypeBadgeClass(promotion.discount_type)">
                  {{ formatDiscountType(promotion.discount_type) }}
                </span>
              </td>
              <td class="text-tertiary-dark">
                {{ formatDiscountValue(promotion.discount_value, promotion.discount_type) }}
              </td>
              <td class="text-tertiary-medium">
                {{ formatDate(promotion.start_date) }}
              </td>
              <td class="text-tertiary-medium">
                {{ formatDate(promotion.end_date) }}
              </td>
              <td>
                <!-- ✅ FIXED: Use isDeleted consistently -->
                <span class="badge" :class="promotion.isDeleted === true ? 'bg-dark text-white' : getStatusBadgeClass(promotion.status)">
                  {{ promotion.isDeleted === true ? 'Deleted' : formatStatus(promotion.status) }}
                </span>
              </td>
              <td class="text-tertiary-medium">
                {{ formatDateTime(promotion.last_updated) }}
              </td>
              <td class="text-center">
                <div class="d-flex justify-content-center gap-1">
                  <!-- ✅ FIXED: Check isDeleted consistently -->
                  <template v-if="promotion.status === 'deleted' || promotion.isDeleted === true">
                    <!-- Actions for deleted items -->
                    <button 
                      class="btn btn-outline-success action-btn"
                      @click="restorePromotion(promotion)"
                      title="Restore"
                    >
                      ↻
                    </button>
                    <button 
                      class="btn btn-outline-danger action-btn"
                      @click="hardDeletePromotion(promotion)"
                      title="Delete Permanently"
                    >
                      ⚠
                    </button>
                  </template>
                  
                  <!-- Actions for active items -->
                  <template v-else>
                    <button 
                      class="btn btn-outline-primary action-btn action-btn-view"
                      @click="viewPromotion(promotion)"
                      title="View Details"
                    >
                      <Eye :size="12" />
                    </button>
                    <button 
                      class="btn btn-outline-secondary action-btn action-btn-edit"
                      @click="editPromotion(promotion)"
                      title="Edit"
                    >
                      <Edit :size="12" />
                    </button>
                    <button 
                      class="btn btn-outline-danger action-btn action-btn-delete"
                      @click="deletePromotion(promotion)"
                      title="Delete"
                    >
                      <Trash2 :size="12" />
                    </button>
                  </template>
                </div>
              </td>
            </tr>

            <!-- Empty State -->
            <tr v-if="!loading && filteredPromotions.length === 0">
              <td colspan="9" class="text-center py-5">
                <div class="text-tertiary-medium">
                  <Package :size="48" class="mb-3 opacity-50" />
                  <div>No promotions found</div>
                  <small v-if="statusFilter === 'deleted'">No deleted promotions to display</small>
                  <small v-else>Start by creating your first promotional campaign</small>
                </div>
              </td>
            </tr>
          </template>
        </DataTable>
      </div>
    </div>

    <!-- Add Promo Modal -->
    <AddPromoModal 
      ref="addPromoModal" 
      :product-categories="productCategories"
      @promotion-saved="onPromotionSaved"
      @promotion-updated="onPromotionUpdated"
    />
  </div>
</div>
</template>

<script>
import DataTable from '@/components/common/TableTemplate.vue'
import AddPromoModal from '@/components/promotions/AddPromoModal.vue'
import apiPromotion from '@/services/apiPromotions' 
import categoryApiService from '@/services/apiCategory'

export default {
  name: 'Promotions',
  components: {
    DataTable,
    AddPromoModal
  },
  data() {
    return {
      promotions: [],
      filteredPromotions: [],
      selectedPromotions: [],
      currentPage: 1,
      itemsPerPage: 10,
      productCategories: [],

      // UI State
      searchMode: false,
      loading: false,
      error: null,
      
      //Refreshing State
      autoRefreshEnabled: true,
      autoRefreshInterval: 30000, // 30 seconds
      baseRefreshInterval: 30000,
      autoRefreshTimer: null,
      countdown: 30,
      countdownTimer: null,
      
      
      // Filters
      discountTypeFilter: 'all',
      statusFilter: 'all',
      searchFilter: ''
    }
  },
  computed: {
    totalPromotions() {
      return this.filteredPromotions.length
    },
    paginatedPromotions() {
      const start = (this.currentPage - 1) * this.itemsPerPage
      const end = start + this.itemsPerPage
      return this.filteredPromotions.slice(start, end)
    },
    isAllSelected() {
      return this.selectedPromotions.length === this.paginatedPromotions.length && this.paginatedPromotions.length > 0
    },
    isIndeterminate() {
      return this.selectedPromotions.length > 0 && this.selectedPromotions.length < this.paginatedPromotions.length
    }
  },
  
  async mounted() {
    await Promise.all([
      this.loadPromotions(),
      this.loadProductCategories(),
    ]);
    if (this.autoRefreshEnabled) {
          this.startAutoRefresh()
        }
  },
  
  methods: {
    async loadPromotions() {
      try {
        this.loading = true;
        this.error = null;
        
        // Always load ALL promotions (including deleted) and filter on frontend
        const params = {
          include_deleted: true
        };
        
        // console.log('🔍 === LOAD PROMOTIONS DEBUG ===');
        // console.log('🔍 API params being sent:', params);
        // console.log('🔍 Current status filter:', this.statusFilter);
        
        const response = await apiPromotion.PromotionData(params);
        
        // console.log('🔍 Raw API response:', response);
        // console.log('🔍 Response type:', typeof response);
        // console.log('🔍 Response length:', response?.length);
        
        // Check if we're getting all promotions
        // if (response && response.length >= 5) {
        //   console.log('✅ SUCCESS: Getting all promotions including deleted ones!');
        // } else {
        //   console.log('⚠️ WARNING: Expected promotions, got:', response?.length);
        // }
        
        this.promotions = response || [];
        // console.log('🔍 Promotions assigned to component:', this.promotions.length);
        
        if (this.promotions.length > 0) {
          // console.log('🔍 All promotions received:');
          
          // Show all promotions with their delete status
          // this.promotions.forEach((promo, index) => {
          //   const isDeleted = promo.isDeleted === true;
          //   console.log(`${index + 1}. "${promo.promotion_name}" - isDeleted: ${promo.isDeleted} (${isDeleted ? 'DELETED' : 'ACTIVE'})`);
          // });
          
          // Count deleted vs active
          const deletedCount = this.promotions.filter(p => p.isDeleted === true).length;
          const activeCount = this.promotions.length - deletedCount;
          
          // console.log(`🔍 Final counts - Active: ${activeCount}, Deleted: ${deletedCount}, Total: ${this.promotions.length}`);
        }
        
        // console.log('🔍 About to apply filters...');
        this.applyFilters();
        // console.log('🔍 === END LOAD PROMOTIONS DEBUG ===');

      } catch (error) {
        this.error = 'Failed to load promotions: ' + error.message;
        console.error('❌ Error in loadPromotions:', error);
      } finally {
        this.loading = false;
      }
    },

    async loadProductCategories() {
      try {
        // TEMPORARY: Skip API call since categories DB is empty
        console.log('Using fallback categories (DB is empty)');
        
        // TODO: Uncomment when categories are added to database
        // const response = await categoryApiService.CategoryData();
        // const categories = response.data || response.categories || response;
        
        // Use fallback categories for now
        this.productCategories = [
          { value: 'all', label: 'All Products' },
          { value: 'noodles', label: 'Noodles' },
          { value: 'drinks', label: 'Drinks' },
          { value: 'toppings', label: 'Toppings' },
          { value: 'snacks', label: 'Snacks' }
        ];
        
        console.log('Product categories loaded (fallback):', this.productCategories);
        
      } catch (error) {
        console.error('Error loading product categories:', error);
        // Fallback is already set above
      }
    },

     toggleAutoRefresh() {
      if (this.autoRefreshEnabled) {
        this.autoRefreshEnabled = false
        this.stopAutoRefresh()
        console.log('Auto-refresh disabled by user')
      } else {
        this.autoRefreshEnabled = true
        this.startAutoRefresh()
        console.log('Auto-refresh enabled by user')
      }
    },
    startAutoRefresh() {
      this.stopAutoRefresh() // Clear any existing timers
      
      // Start countdown
      this.countdown = this.autoRefreshInterval / 1000
      this.countdownTimer = setInterval(() => {
        this.countdown--
        if (this.countdown <= 0) {
          this.countdown = this.autoRefreshInterval / 1000
        }
      }, 1000)
      
      // Start auto-refresh timer - FIXED: call refreshData instead of fetchUsers
      this.autoRefreshTimer = setInterval(() => {
        this.refreshData() // Changed from this.fetchUsers(true)
      }, this.autoRefreshInterval)
      
      console.log(`Auto-refresh started (${this.autoRefreshInterval / 1000}s interval)`)
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
      
      console.log('Auto-refresh stopped')
    },

    // ============ ENHANCED REFRESH SYSTEM ============
    // Replace the refreshData method with this corrected version:
    async refreshData() {
      console.log('=== COMPREHENSIVE PROMOTIONS DATA REFRESH INITIATED ===')
      
      this.error = null
      
      const currentSelections = [...this.selectedPromotions]
      const currentFilters = {
        discountType: this.discountTypeFilter,
        status: this.statusFilter,
        search: this.searchFilter
      }
      
      console.log('Preserving current state:', {
        selections: currentSelections,
        filters: currentFilters
      })
      
      try {
        // Refresh promotions data
        await this.loadPromotions()
        
        // Restore promotion selections (only those that still exist)
        this.selectedPromotions = currentSelections.filter(promotionId => 
          this.promotions.some(promotion => promotion._id === promotionId)
        )
        
        // Restore filters
        this.discountTypeFilter = currentFilters.discountType
        this.statusFilter = currentFilters.status
        this.searchFilter = currentFilters.search
        
        this.applyFilters()
        
        this.$toast?.success(`Promotions data refreshed successfully. ${this.promotions.length} promotions loaded.`)
        
        console.log('✅ Comprehensive refresh completed successfully')
        console.log('Final state:', {
          totalPromotions: this.promotions.length,
          filteredPromotions: this.filteredPromotions.length,
          selectedPromotions: this.selectedPromotions.length
        })
        
      } catch (error) {
        console.error('❌ Comprehensive refresh failed:', error)
        this.error = 'Failed to refresh promotions data: ' + error.message
      }
    },

    handleSinglePromo() {
      if (this.$refs.addPromoModal && this.$refs.addPromoModal.openAdd) {
        this.$refs.addPromoModal.openAdd();
        
      } else {
        if (this.$refs.addPromoModal && this.$refs.addPromoModal.open) {
          this.$refs.addPromoModal.open();
          location.reload(); 
        }
      }
    },

    async onPromotionSaved(promotionData) {
      try {
        // console.log('🔍 Saving promotion with data:', promotionData);
        const response = await apiPromotion.AddPromotionData(promotionData);
        // console.log('🔍 Save response:', response);
        
        this.promotions.push(response);
        this.applyFilters();
        this.$toast?.success('Promotion created successfully!');
        this.$refs.addPromoModal.onOperationSuccess();
        location.reload();
      } catch (error) {
        this.$refs.addPromoModal.error = 'Failed to create promotion: ' + error.message;
        this.$refs.addPromoModal.loading = false;
        console.error('❌ Error creating promotion:', error);
      }
    },

    async onPromotionUpdated(promotionData) {
      try {
        const response = await apiPromotion.UpdatePromotionData({
          id: promotionData.promotion_id,
          promotion_name: promotionData.promotion_name,
          discount_type: promotionData.discount_type,
          discount_value: promotionData.discount_value,
          applicable_products: promotionData.applicable_products || [],
          start_date: promotionData.start_date,
          end_date: promotionData.end_date,
          status: promotionData.status || 'active'
        });
        
        await this.loadPromotions();
        
        this.$toast?.success('Promotion updated successfully!');
        this.$refs.addPromoModal.onOperationSuccess();
        
      } catch (error) {
        this.$refs.addPromoModal.error = 'Failed to update promotion: ' + error.message;
        this.$refs.addPromoModal.loading = false;
        console.error('Error updating promotion:', error);
      }
    },

    // ✅ FIXED: Delete method using isDeleted consistently
    async deletePromotion(promotion) {
      try {
        const promotionId = promotion._id;
        const promotionName = promotion.promotion_name;
        
        if (!promotionId) {
          this.error = 'Unable to delete promotion - invalid ID';
          return;
        }

        const confirmed = confirm(`Are you sure you want to delete "${promotionName}"?\n\nThis will move it to deleted items (can be restored later).`);
        if (!confirmed) return;

        this.loading = true;
        
        await apiPromotion.SoftDeletePromotion({
          id: promotionId,
          promotion_name: promotionName
        });

        // Update local state
        const index = this.promotions.findIndex(p => p._id === promotionId);
        
        if (index !== -1) {
          this.promotions[index].status = 'deleted';
          this.promotions[index].isDeleted = true;
        }

        this.applyFilters();
        this.selectedPromotions = this.selectedPromotions.filter(id => id !== promotionId);
        this.$toast?.success('Promotion deleted successfully!');

      } catch (error) {
        this.error = 'Failed to delete promotion: ' + error.message;
        console.error('❌ Error deleting promotion:', error);
        this.$toast?.error('Failed to delete promotion');
      } finally {
        this.loading = false;
      }
    },

    async deleteSelected() {
      if (this.selectedPromotions.length === 0) return;
      
      try {
        const confirmed = confirm(`Are you sure you want to delete ${this.selectedPromotions.length} promotion(s)?\n\nThey will be moved to deleted items (can be restored later).`);
        if (!confirmed) return;

        this.loading = true;

        const deletePromises = this.selectedPromotions.map(async (promotionId) => {
          const promotion = this.promotions.find(p => p._id === promotionId);
          return apiPromotion.SoftDeletePromotion({
            id: promotionId,
            promotion_name: promotion?.promotion_name || 'Unknown'
          });
        });

        await Promise.all(deletePromises);

        this.selectedPromotions.forEach(promotionId => {
          const index = this.promotions.findIndex(p => p._id === promotionId);
          if (index !== -1) {
            this.promotions[index].status = 'deleted';
            this.promotions[index].isDeleted = true;
          }
        });
        
        const deletedCount = this.selectedPromotions.length;
        this.selectedPromotions = [];
        this.applyFilters();
        this.$toast?.success(`${deletedCount} promotion(s) deleted successfully!`);
      } catch (error) {
        this.error = 'Failed to delete promotions: ' + error.message;
        console.error('Error deleting promotions:', error);
        this.$toast?.error('Failed to delete some promotions');
      } finally {
        this.loading = false;
      }
    },

    async hardDeletePromotion(promotion) {
      try {
        const promotionId = promotion._id;
        const promotionName = promotion.promotion_name;

        const confirmed = confirm(`⚠️ PERMANENT DELETE WARNING ⚠️\n\nAre you sure you want to PERMANENTLY delete "${promotionName}"?\n\nThis action CANNOT be undone!`);
        if (!confirmed) return;

        const doubleConfirmed = confirm(`This is your FINAL WARNING!\n\nPermanently delete "${promotionName}"?\n\nType 'DELETE' in the next prompt to confirm.`);
        if (!doubleConfirmed) return;

        const userInput = prompt('Type "DELETE" to confirm permanent deletion:');
        if (userInput !== 'DELETE') {
          alert('Deletion cancelled - text did not match.');
          return;
        }

        this.loading = true;

        await apiPromotion.HardDeletePromotion({
          id: promotionId,
          promotion_name: promotionName
        });

        const index = this.promotions.findIndex(p => p._id === promotionId);
        if (index !== -1) {
          this.promotions.splice(index, 1);
        }

        this.applyFilters();
        this.selectedPromotions = this.selectedPromotions.filter(id => id !== promotionId);
        this.$toast?.success('Promotion permanently deleted!');
      } catch (error) {
        this.error = 'Failed to permanently delete promotion: ' + error.message;
        console.error('Error hard deleting promotion:', error);
        this.$toast?.error('Failed to permanently delete promotion');
      } finally {
        this.loading = false;
      }
    },

    // ✅ FIXED: Restore method using isDeleted consistently
    async restorePromotion(promotion) {
      try {
        const promotionId = promotion._id;
        const promotionName = promotion.promotion_name;

        const confirmed = confirm(`Restore "${promotionName}"?`);
        if (!confirmed) return;

        this.loading = true;

        await apiPromotion.RestorePromotion({
          id: promotionId,
          promotion_name: promotionName
        });

        const index = this.promotions.findIndex(p => p._id === promotionId);
        if (index !== -1) {
          this.promotions[index].status = 'active';
          this.promotions[index].isDeleted = false;
        }

        this.applyFilters();
        this.$toast?.success('Promotion restored successfully!');
      } catch (error) {
        this.error = 'Failed to restore promotion: ' + error.message;
        console.error('Error restoring promotion:', error);
        this.$toast?.error('Failed to restore promotion');
      } finally {
        this.loading = false;
      }
    },

    exportData() {
      try {
        // console.log('🔍 Exporting promotions data...');
        
        // Use filteredPromotions to export only what user is currently viewing
        const dataToExport = this.filteredPromotions.length > 0 ? this.filteredPromotions : this.promotions;
        
        if (dataToExport.length === 0) {
          this.$toast?.warning('No data to export');
          return;
        }
        
        // Define CSV headers
        const headers = [
          'Promotion ID',
          'Promotion Name', 
          'Discount Type',
          'Discount Value',
          'Start Date',
          'End Date',
          'Status',
          'Is Deleted',
          'Date Created',
          'Last Updated',
          'Applicable Products'
        ];
        
        // Convert data to CSV format
        const csvRows = [
          headers.join(','), // Header row
          ...dataToExport.map(promotion => [
            `"${promotion._id}"`,
            `"${promotion.promotion_name || ''}"`,
            `"${this.formatDiscountType(promotion.discount_type)}"`,
            `"${this.formatDiscountValue(promotion.discount_value, promotion.discount_type)}"`,
            `"${this.formatDate(promotion.start_date)}"`,
            `"${this.formatDate(promotion.end_date)}"`,
            `"${promotion.isDeleted ? 'Deleted' : this.formatStatus(promotion.status)}"`,
            `"${promotion.isDeleted ? 'Yes' : 'No'}"`,
            `"${this.formatDateTime(promotion.date_created)}"`,
            `"${this.formatDateTime(promotion.last_updated)}"`,
            `"${(promotion.applicable_products || []).join('; ')}"`
          ].join(','))
        ];
        
        // Create CSV content
        const csvContent = csvRows.join('\n');
        
        // Create and trigger download
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        
        if (link.download !== undefined) {
          const url = URL.createObjectURL(blob);
          link.setAttribute('href', url);
          
          // Generate filename with current date and filter info
          const now = new Date();
          const timestamp = now.toISOString().slice(0, 10); // YYYY-MM-DD
          const filterInfo = this.statusFilter !== 'all' ? `_${this.statusFilter}` : '';
          const filename = `promotions_export${filterInfo}_${timestamp}.csv`;
          
          link.setAttribute('download', filename);
          link.style.visibility = 'hidden';
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          
          // console.log(`✅ Successfully exported ${dataToExport.length} promotions to ${filename}`);
          this.$toast?.success(`Exported ${dataToExport.length} promotions to ${filename}`);
        } else {
          // Fallback for older browsers
          const url = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csvContent);
          window.open(url);
          
          this.$toast?.success(`Exported ${dataToExport.length} promotions`);
        }
        
      } catch (error) {
        console.error('❌ Error exporting data:', error);
        this.$toast?.error('Failed to export data: ' + error.message);
      }
    },

    toggleSearchMode() {
      this.searchMode = !this.searchMode
      
      if (this.searchMode) {
        this.$nextTick(() => {
          if (this.$refs.searchInput) {
            this.$refs.searchInput.focus()
          }
        })
      } else {
        this.searchFilter = ''
        this.applyFilters()
      }
    },

    clearSearch() {
      this.searchFilter = ''
      this.searchMode = false
      this.applyFilters()
    },

    applyFilters() {
      // console.log('🔍 === APPLY FILTERS DEBUG ===');
      // console.log('🔍 Total promotions loaded:', this.promotions.length);
      // console.log('🔍 Status filter:', this.statusFilter);
      
      let filtered = [...this.promotions];

      // Log each promotion's delete status
      // console.log('🔍 Promotion delete status check:');
      // this.promotions.forEach((promo, index) => {
      //   console.log(`${index + 1}. "${promo.promotion_name}":`, {
      //     _id: promo._id,
      //     status: promo.status,
      //     isDeleted: promo.isDeleted,
      //     isDeleted_type: typeof promo.isDeleted,
      //     isDeleted_strict_true: promo.isDeleted === true,
      //     deleted_at: promo.deleted_at
      //   });
      // });

      // Helper function to check if promotion is deleted
      const isDeleted = (promo) => {
        const deleted = promo.isDeleted === true || promo.status === 'deleted';
        // console.log(`🔍 isDeleted check for "${promo.promotion_name}": ${deleted} (isDeleted: ${promo.isDeleted}, status: ${promo.status})`);
        return deleted;
      };

      if (this.discountTypeFilter !== 'all') {
        // console.log('🔍 Applying discount type filter:', this.discountTypeFilter);
        filtered = filtered.filter(promo => promo.discount_type === this.discountTypeFilter);
        // console.log('🔍 After discount type filter:', filtered.length);
      }

      if (this.statusFilter !== 'all') {
        // console.log('🔍 Applying status filter:', this.statusFilter);
        
        if (this.statusFilter === 'deleted') {
          // Show only soft-deleted items
          // console.log('🔍 Filtering for deleted items...');
          
          filtered = filtered.filter(promo => {
            const deleted = isDeleted(promo);
            return deleted;
          });
          
          // console.log(`🔍 Found ${filtered.length} deleted promotions after filter`);
          // console.log('🔍 Deleted promotions found:', filtered.map(p => ({
          //   name: p.promotion_name,
          //   isDeleted: p.isDeleted,
          //   status: p.status
          // })));
          
        } else {
          // Show only non-deleted items with specific status
          // console.log('🔍 Filtering for active items with status:', this.statusFilter);
          filtered = filtered.filter(promo => 
            !isDeleted(promo) && promo.status === this.statusFilter
          );
          // console.log('🔍 After active status filter:', filtered.length);
        }
      } else {
        // For "all", exclude deleted items
        // console.log('🔍 Filtering out deleted items (showing all active)');
        const beforeCount = filtered.length;
        filtered = filtered.filter(promo => !isDeleted(promo));
        // console.log(`🔍 Excluded ${beforeCount - filtered.length} deleted items, showing ${filtered.length} active`);
      }

      if (this.searchFilter.trim()) {
        const search = this.searchFilter.toLowerCase();
        // console.log('🔍 Applying search filter:', search);
        const beforeSearch = filtered.length;
        filtered = filtered.filter(promo => 
          promo.promotion_name?.toLowerCase().includes(search) ||
          promo._id?.toLowerCase().includes(search)
        );
        // console.log(`🔍 Search reduced from ${beforeSearch} to ${filtered.length} items`);
      }

      // console.log('🔍 Final filtered count:', filtered.length);
      // console.log('🔍 Final filtered promotions:', filtered.map(p => p.promotion_name));
      // console.log('🔍 === END APPLY FILTERS DEBUG ===');

      this.currentPage = 1;
      this.selectedPromotions = [];
      this.filteredPromotions = filtered;
    },

    clearFilters() {
      this.discountTypeFilter = 'all'
      this.statusFilter = 'all'
      this.searchFilter = ''
      this.searchMode = false
      this.applyFilters()
    },

    handlePageChange(page) {
      this.currentPage = page
    },

    toggleSelectAll() {
      if (this.isAllSelected) {
        this.selectedPromotions = []
      } else {
        this.selectedPromotions = this.paginatedPromotions.map(p => p._id)
      }
    },

    formatDiscountType(type) {
      const types = {
        'percentage': 'Percentage',
        'fixed': 'Fixed Amount',
        'buy_one_get_one': 'BOGO'
      }
      return types[type] || type
    },

    formatDiscountValue(value, type) {
      if (type === 'percentage') {
        return `${value}%`
      } else if (type === 'fixed') {
        return `₱${value}`
      }
      return value
    },

    formatStatus(status) {
      const statuses = {
        'active': 'Active',
        'inactive': 'Inactive',
        'expired': 'Expired',
        'scheduled': 'Scheduled',
        'deleted': 'Deleted'
      }
      return statuses[status] || status
    },

    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    },

    formatDateTime(dateString) {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },

    getDiscountTypeBadgeClass(type) {
      const classes = {
        'percentage': 'bg-primary text-white',
        'fixed': 'bg-success text-white',
        'buy_one_get_one': 'bg-info text-white'
      }
      return classes[type] || 'bg-secondary text-white'
    },

    getStatusBadgeClass(status) {
      const classes = {
        'active': 'bg-success text-white',
        'inactive': 'bg-secondary text-white',
        'expired': 'bg-danger text-white',
        'scheduled': 'bg-warning text-dark',
        'deleted': 'bg-dark text-white'
      }
      return classes[status] || 'bg-secondary text-white'
    },

    viewPromotion(promotion) {
      if (this.$refs.addPromoModal && this.$refs.addPromoModal.openView) {
        this.$refs.addPromoModal.openView(promotion)
      }
    },

    editPromotion(promotion) {
      if (this.$refs.addPromoModal && this.$refs.addPromoModal.openEdit) {
        this.$refs.addPromoModal.openEdit(promotion);
      } else {
        if (this.$refs.addPromoModal && this.$refs.addPromoModal.open) {
          this.$refs.addPromoModal.open(promotion, 'edit');
        }
      }
    },
    beforeDestroy() {
      // Clean up timers when component is destroyed
      this.stopAutoRefresh()
    }
  }
}
</script>

<style scoped>
.promotions-page {
  min-height: 100vh;
  background-color: var(--neutral-light);
  padding: 1rem;
}

/* Action Bar Styles */
.action-bar-container {
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  overflow: hidden;
  padding: 1rem;
  margin-bottom: 1rem;
}

/* Header Row - Separate from action controls */
.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  gap: 1rem;
}

.page-title {
  font-size: 2rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
  flex-shrink: 0;
}

/* Auto-refresh and Connection Status Container */
.status-container {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

/* Auto-refresh status indicator */
.auto-refresh-status {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: #f0fdf4;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  border: 1px solid #bbf7d0;
  min-width: 200px;
  flex-shrink: 0;
}

.status-text {
  font-size: 0.875rem;
  color: #16a34a;
  font-weight: 500;
  flex: 1;
  white-space: nowrap;
}

/* Connection indicator */
.connection-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  flex-shrink: 0;
}

.connection-good {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: #16a34a;
}

.connection-unstable {
  background: #fefce8;
  border: 1px solid #fde047;
  color: #ca8a04;
}

.connection-lost {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
}

.connection-unknown {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  color: #64748b;
}

/* Action Row Layout */
.action-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

/* Filters Section */
.filters-section {
  display: flex;
  align-items: end;
  gap: 1rem;
  flex-shrink: 0;
}

/* Action Buttons Section */
.action-buttons {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

/* Filter Groups */
.filter-group {
  min-width: 140px;
}

.filter-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--tertiary-medium);
  margin-bottom: 0.25rem;
  display: block;
}

/* Search Container */
.search-container {
  min-width: 300px;
  max-width: 400px;
  flex: 1;
}

.search-input {
  padding-right: 2.5rem;
  height: calc(1.5em + 0.75rem + 2px);
}

.search-container .position-relative .btn {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Search Toggle Button */
.search-toggle-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  flex-shrink: 0;
}

/* Button States */
.btn.active {
  background-color: var(--primary);
  border-color: var(--primary);
  color: white;
}

/* Form controls focus states */
.form-select:focus,
.form-control:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 0.2rem rgba(115, 146, 226, 0.25);
}

.action-btn {
  width: 32px;
  height: 32px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.375rem;
  transition: all 0.2s ease;
  font-size: 14px;
  font-weight: bold;
}

.btn-outline-success:hover {
  background-color: #198754;
  border-color: #198754;
  color: white;
}

.btn-outline-danger:hover {
  background-color: #dc3545;
  border-color: #dc3545;
  color: white;
}

/* Status badge for deleted items */
.badge.bg-dark {
  background-color: #495057 !important;
}

/* Ensure consistent spacing for action buttons */
.d-flex.gap-1 {
  gap: 0.25rem !important;
}

/* Responsive Design */
@media (max-width: 1200px) {
  .auto-refresh-status {
    min-width: 180px;
  }
  
  .status-text {
    font-size: 0.8125rem;
  }
  
  .search-container {
    min-width: 250px;
  }
}

@media (max-width: 992px) {
  .header-row {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  
  .status-container {
    justify-content: center;
  }
  
  .action-row {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  
  .filters-section {
    justify-content: space-between;
    flex-wrap: wrap;
  }
  
  .action-buttons {
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .promotions-page {
    padding: 0.5rem;
  }
  
  .action-bar-container {
    padding: 0.75rem;
  }
  
  .page-title {
    font-size: 1.5rem;
    text-align: center;
  }
  
  .status-container {
    flex-direction: column;
    align-items: stretch;
  }
  
  .auto-refresh-status {
    min-width: auto;
    justify-content: center;
  }
  
  .connection-indicator {
    justify-content: center;
  }
  
  .filters-section {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .filter-group {
    min-width: auto;
  }
  
  .search-container {
    min-width: auto;
  }
  
  .action-buttons {
    flex-wrap: wrap;
    justify-content: center;
  }
}

@media (max-width: 576px) {
  .header-row {
    gap: 0.75rem;
  }
  
  .action-row {
    gap: 0.75rem;
  }
  
  .page-title {
    font-size: 1.25rem;
  }
  
  .auto-refresh-status {
    padding: 0.5rem 0.75rem;
    flex-direction: column;
    text-align: center;
    gap: 0.25rem;
  }
  
  .connection-indicator {
    padding: 0.5rem 0.75rem;
  }
  
  .status-text {
    font-size: 0.8125rem;
  }
}
</style>