<template>
  <div class="bulk-entry-page">
    <!-- Header with Navigation -->
    <div class="page-header">
      <div class="breadcrumb">
        <router-link to="/products" class="breadcrumb-link">Products</router-link>
        <span class="breadcrumb-separator">></span>
        <span class="breadcrumb-current">Add Products (Bulk)</span>
      </div>
      
      <div class="header-actions">
        <button 
          class="btn btn-secondary" 
          @click="openBarcodeScanner"
          :disabled="loading"
        >
          <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 7V5a2 2 0 0 1 2-2h2m0 0h8m-8 0v2m8-2v2m0-2h2a2 2 0 0 1 2 2v2M7 21H5a2 2 0 0 1-2-2v-2m14 0v2a2 2 0 0 1-2 2h-2"/>
            <line x1="7" y1="8" x2="7" y2="12"/>
            <line x1="10" y1="8" x2="10" y2="16"/>
            <line x1="13" y1="8" x2="13" y2="12"/>
            <line x1="16" y1="8" x2="16" y2="16"/>
          </svg>
          Scan Barcode
        </button>
        
        <button 
          class="btn btn-primary" 
          @click="saveProducts" 
          :disabled="loading || !hasValidProducts"
        >
          <svg v-if="loading" class="btn-icon spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 12a9 9 0 11-6.219-8.56"/>
          </svg>
          <svg v-else class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
            <polyline points="17,21 17,13 7,13 7,21"/>
            <polyline points="7,3 7,8 15,8"/>
          </svg>
          {{ loading ? 'Saving...' : 'Save Products' }}
        </button>
      </div>
    </div>

    <!-- Progress Indicator -->
    <div v-if="products.length > 0" class="progress-section">
      <div class="progress-info">
        <span class="product-count">{{ products.length }} Products Added</span>
        <span class="valid-count">{{ validProducts }} Valid • {{ invalidProducts }} Invalid</span>
      </div>
      <div class="progress-bar">
        <div 
          class="progress-fill" 
          :style="{ width: `${progressPercentage}%` }"
        ></div>
      </div>
    </div>

    <!-- Success/Error Messages -->
    <div v-if="successMessage" class="message success-message">
      <svg class="message-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="20,6 9,17 4,12"/>
      </svg>
      {{ successMessage }}
    </div>
    
    <div v-if="errorMessage" class="message error-message">
      <svg class="message-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"/>
        <line x1="15" y1="9" x2="9" y2="15"/>
        <line x1="9" y1="9" x2="15" y2="15"/>
      </svg>
      {{ errorMessage }}
    </div>

    <!-- Bulk Entry Table -->
    <div class="table-container">
      <div class="table-header">
        <h2 class="table-title">Add Products in Bulk</h2>
        <div class="table-actions">
          <button 
            class="btn btn-success btn-sm" 
            @click="addNewRow"
            :disabled="loading"
          >
            <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="12" y1="5" x2="12" y2="19"/>
              <line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
            Add Row
          </button>
          
          <button 
            v-if="products.length > 0"
            class="btn btn-error btn-sm" 
            @click="clearAll"
            :disabled="loading"
          >
            <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="3,6 5,6 21,6"/>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
            </svg>
            Clear All
          </button>
        </div>
      </div>

      <div class="table-wrapper">
        <table class="bulk-entry-table">
          <thead>
            <tr>
              <th class="row-number-col">#</th>
              <th class="image-col">Image</th>
              <th class="name-col">Name <span class="required">*</span></th>
              <th class="sku-col">SKU <span class="required">*</span></th>
              <th class="category-col">Category <span class="required">*</span></th>
              <th class="cost-col">Cost Price <span class="required">*</span></th>
              <th class="markup-col">Mark up % <span class="required">*</span></th>
              <th class="selling-col">Selling Price <span class="required">*</span></th>
              <th class="stock-col">Stock</th>
              <th class="actions-col">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="products.length === 0" class="empty-row">
              <td colspan="10" class="empty-state">
                <div class="empty-content">
                  <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                    <line x1="9" y1="12" x2="15" y2="12"/>
                    <line x1="12" y1="9" x2="12" y2="15"/>
                  </svg>
                  <p>No products added yet</p>
                  <button class="btn btn-primary btn-sm" @click="addNewRow">
                    Add First Product
                  </button>
                </div>
              </td>
            </tr>
            
            <tr 
              v-for="(product, index) in products" 
              :key="product.id"
              :class="{ 'invalid-row': !isProductValid(product) }"
            >
              <td class="row-number">{{ index + 1 }}</td>
              
              <!-- Image Upload -->
              <td class="image-cell">
                <div class="image-upload">
                  <input 
                    type="file" 
                    :id="`image-${product.id}`"
                    @change="handleImageUpload(index, $event)"
                    accept="image/*"
                    class="image-input"
                  />
                  <label :for="`image-${product.id}`" class="image-label">
                    <img 
                      v-if="product.image_preview" 
                      :src="product.image_preview" 
                      alt="Product"
                      class="product-image"
                    />
                    <div v-else class="image-placeholder">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                        <circle cx="8.5" cy="8.5" r="1.5"/>
                        <polyline points="21,15 16,10 5,21"/>
                      </svg>
                    </div>
                  </label>
                </div>
              </td>
              
              <!-- Product Name -->
              <td class="name-cell">
                <input 
                  v-model="product.product_name"
                  type="text"
                  placeholder="Product name"
                  class="table-input"
                  @input="calculateSellingPrice(index)"
                />
              </td>
              
              <!-- SKU -->
              <td class="sku-cell">
                <input 
                  v-model="product.SKU"
                  type="text"
                  placeholder="Auto-generated"
                  class="table-input sku-input"
                  @blur="validateSKU(index)"
                />
                <div v-if="product.sku_error" class="field-error">{{ product.sku_error }}</div>
              </td>
              
              <!-- Category -->
              <td class="category-cell">
                <select 
                  v-model="product.category_id"
                  class="table-select"
                >
                  <option value="">Select category</option>
                  <option value="noodles">Noodles</option>
                  <option value="drinks">Drinks</option>
                  <option value="toppings">Toppings</option>
                </select>
              </td>
              
              <!-- Cost Price -->
              <td class="cost-cell">
                <input 
                  v-model.number="product.cost_price"
                  type="number"
                  step="0.01"
                  min="0"
                  placeholder="0.00"
                  class="table-input price-input"
                  @input="calculateSellingPrice(index)"
                />
              </td>
              
              <!-- Markup Percentage -->
              <td class="markup-cell">
                <input 
                  v-model.number="product.markup_percentage"
                  type="number"
                  min="0"
                  max="1000"
                  placeholder="25"
                  class="table-input markup-input"
                  @input="calculateSellingPrice(index)"
                />
                <span class="markup-suffix">%</span>
              </td>
              
              <!-- Selling Price -->
              <td class="selling-cell">
                <input 
                  v-model.number="product.selling_price"
                  type="number"
                  step="0.01"
                  min="0"
                  placeholder="0.00"
                  class="table-input price-input"
                  @input="calculateMarkup(index)"
                />
              </td>
              
              <!-- Stock -->
              <td class="stock-cell">
                <input 
                  v-model.number="product.stock"
                  type="number"
                  min="0"
                  placeholder="0"
                  class="table-input stock-input"
                />
              </td>
              
              <!-- Actions -->
              <td class="actions-cell">
                <button 
                  class="action-btn duplicate-btn" 
                  @click="duplicateRow(index)"
                  title="Duplicate Row"
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                  </svg>
                </button>
                
                <button 
                  class="action-btn delete-btn" 
                  @click="removeRow(index)"
                  title="Remove Row"
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="3,6 5,6 21,6"/>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                    <line x1="10" y1="11" x2="10" y2="17"/>
                    <line x1="14" y1="11" x2="14" y2="17"/>
                  </svg>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Barcode Scanner Modal -->
    <BarcodeScanner
      :show="showBarcodeModal"
      @close="closeBarcodeScanner"
      @scanned="handleBarcodeScanned"
    />

    <!-- Notification Modal -->
    <NotificationModal
      :show="showNotificationModal"
      :type="notificationData.type"
      :title="notificationData.title"
      :message="notificationData.message"
      :details="notificationData.details"
      @close="closeNotificationModal"
      @confirm="handleNotificationConfirm"
      @retry="handleNotificationRetry"
    />
  </div>
</template>

<script>
import productsApiService from '../../services/apiProducts.js'
import BarcodeScanner from '../../components/products/BarcodeScanner.vue'
import NotificationModal from '../../components/common/NotificationModal.vue'

export default {
  name: 'ProductBulkEntry',
  components: {
    BarcodeScanner,
    NotificationModal
  },
  data() {
    return {
      products: [],
      loading: false,
      successMessage: null,
      errorMessage: null,
      showBarcodeModal: false,
      nextId: 1,
      showNotificationModal: false,
      notificationData: {
        type: 'success',
        title: '',
        message: '',
        details: null
      }
    }
  },
  computed: {
    hasValidProducts() {
      return this.products.some(product => this.isProductValid(product))
    },
    
    validProducts() {
      return this.products.filter(product => this.isProductValid(product)).length
    },
    
    invalidProducts() {
      return this.products.length - this.validProducts
    },
    
    progressPercentage() {
      if (this.products.length === 0) return 0
      return Math.round((this.validProducts / this.products.length) * 100)
    }
  },
  mounted() {
    // Start with one empty row
    this.addNewRow()
  },
  methods: {
    addNewRow() {
      const newProduct = {
        id: this.nextId++,
        product_name: '',
        SKU: '',
        category_id: '',
        cost_price: null,
        selling_price: null,
        markup_percentage: 25,
        stock: 0,
        unit: 'piece',
        status: 'active',
        image_preview: null,
        image_file: null,
        sku_error: null
      }
      
      this.products.push(newProduct)
    },
    
    removeRow(index) {
      if (this.products.length > 1) {
        this.products.splice(index, 1)
      }
    },
    
    duplicateRow(index) {
      const original = this.products[index]
      const duplicate = {
        ...original,
        id: this.nextId++,
        product_name: original.product_name ? `${original.product_name} (Copy)` : '',
        SKU: '', // Clear SKU to avoid duplicates
        sku_error: null
      }
      
      this.products.splice(index + 1, 0, duplicate)
    },
    
    clearAll() {
      const confirmed = confirm('Are you sure you want to clear all products? This action cannot be undone.')
      if (confirmed) {
        this.products = []
        this.addNewRow()
        this.clearMessages()
      }
    },

    isProductValid(product) {
      const nameValid = product.product_name && 
                      product.product_name.trim().length > 0
      
      const priceValid = product.cost_price && 
                        product.cost_price > 0 && 
                        !isNaN(product.cost_price)
      
      return !!(nameValid && priceValid && !product.sku_error)
    },
    
    calculateSellingPrice(index) {
      const product = this.products[index]
      if (product.cost_price && product.markup_percentage) {
        const markup = product.cost_price * (product.markup_percentage / 100)
        product.selling_price = parseFloat((product.cost_price + markup).toFixed(2))
      }
    },
    
    calculateMarkup(index) {
      const product = this.products[index]
      if (product.cost_price && product.selling_price && product.cost_price > 0) {
        const markup = ((product.selling_price - product.cost_price) / product.cost_price) * 100
        product.markup_percentage = parseFloat(markup.toFixed(2))
      }
    },
    
    async validateSKU(index) {
      const product = this.products[index]
      if (!product.SKU) {
        product.sku_error = null
        return
      }
      
      try {
        // Check for duplicates in current list
        const duplicates = this.products.filter((p, i) => 
          i !== index && p.SKU === product.SKU
        )
        
        if (duplicates.length > 0) {
          product.sku_error = 'Duplicate SKU in list'
          return
        }
        
        // Check if SKU exists in database
        const exists = await productsApiService.productExistsBySku(product.SKU)
        if (exists) {
          product.sku_error = 'SKU already exists'
        } else {
          product.sku_error = null
        }
      } catch (error) {
        console.error('Error validating SKU:', error)
        product.sku_error = null
      }
    },
    
    handleImageUpload(index, event) {
      const file = event.target.files[0]
      if (file) {
        // Validate file type
        if (!file.type.startsWith('image/')) {
          this.showError('Please select a valid image file')
          return
        }
        
        // Validate file size (max 5MB)
        if (file.size > 5 * 1024 * 1024) {
          this.showError('Image size must be less than 5MB')
          return
        }
        
        const product = this.products[index]
        product.image_file = file
        
        // Create preview
        const reader = new FileReader()
        reader.onload = (e) => {
          product.image_preview = e.target.result
        }
        reader.readAsDataURL(file)
      }
    },
    
    openBarcodeScanner() {
      this.showBarcodeModal = true
    },
    
    closeBarcodeScanner() {
      this.showBarcodeModal = false
    },
    
    handleBarcodeScanned(barcodeData) {
      // Find an empty row or add a new one
      let targetIndex = this.products.findIndex(p => !p.product_name)
      if (targetIndex === -1) {
        this.addNewRow()
        targetIndex = this.products.length - 1
      }
      
      // Populate the row with scanned data
      const product = this.products[targetIndex]
      product.SKU = barcodeData.code
      product.product_name = barcodeData.product_name || ''
      
      // If we have additional product data from the barcode
      if (barcodeData.cost_price) product.cost_price = barcodeData.cost_price
      if (barcodeData.category_id) product.category_id = barcodeData.category_id
      
      this.closeBarcodeScanner()
      this.showSuccess('Product added from barcode scan')
    },
    

    async saveProducts() {
      console.log('=== SAVE PRODUCTS CALLED ===')
      console.log('Valid products:', this.hasValidProducts)
      console.log('Products to save:', this.products.filter(product => this.isProductValid(product)))
      
      if (!this.hasValidProducts) {
        this.showError('Please add at least one valid product')
        return
      }
      
      this.loading = true
      this.clearMessages()
      
      try {
        // Filter only valid products
        const validProducts = this.products.filter(product => this.isProductValid(product))
        
        // Clean data preparation
        const productsData = validProducts.map(product => {
          const data = {
            product_name: product.product_name?.trim(),
            cost_price: parseFloat(product.cost_price),
            selling_price: parseFloat(product.selling_price),
            stock: parseInt(product.stock) || 0,
            unit: product.unit || 'piece',
            status: product.status || 'active',
            low_stock_threshold: Math.max(1, Math.floor((product.stock || 0) * 0.1)),
            is_taxable: true
          }
          
          // Only add these fields if they have actual values
          if (product.SKU && product.SKU.trim()) {
            data.SKU = product.SKU.trim()
          }
          
          if (product.category_id && product.category_id !== '') {
            data.category_id = product.category_id
          }
          
          return data
        })
        
        // Final validation before sending
        console.log('=== FINAL VALIDATION BEFORE API ===')
        const hasInvalidData = productsData.some((product, index) => {
          const nameInvalid = !product.product_name || 
                            typeof product.product_name !== 'string' || 
                            product.product_name.trim() === ''
          
          const priceInvalid = !product.cost_price || 
                              isNaN(product.cost_price) || 
                              product.cost_price <= 0
          
          if (nameInvalid) {
            console.error(`Product ${index + 1} has invalid name:`, product.product_name)
          }
          if (priceInvalid) {
            console.error(`Product ${index + 1} has invalid price:`, product.cost_price)
          }
          
          return nameInvalid || priceInvalid
        })
        
        if (hasInvalidData) {
          this.showError('Some products have invalid data. Check console for details.')
          return
        }
        
        console.log('Sending products data:', productsData)
        
        // Call the API
        const result = await productsApiService.bulkCreateProducts(productsData)
        
        console.log('Full API Response:', result)
        console.log('Response data:', result.data)
        
        // Fixed response parsing - handle both wrapped and direct response
        let successfulCount = 0
        let failedCount = 0
        let responseData = null
        
        // Check if response is wrapped in .data or direct
        responseData = result.data || result
        
        console.log('Parsed response data:', responseData)
        console.log('Response message:', responseData?.message)
        console.log('Response results:', responseData?.results)
        
        // Parse response based on actual structure
        if (responseData) {
          // Check if we have results array
          if (responseData.results && Array.isArray(responseData.results)) {
            console.log('Found results array, parsing individual results...')
            responseData.results.forEach((item, index) => {
              console.log(`Result ${index}:`, item)
              // Since API says "completed", assume success unless there's explicit error
              if (!item.error && !item.failed) {
                successfulCount++
              } else {
                failedCount++
              }
            })
          } 
          // If message indicates completion, assume all successful
          else if (responseData.message && responseData.message.includes('completed')) {
            console.log('No results array, but message indicates completion. Assuming all successful.')
            successfulCount = validProducts.length
          }
          // Handle other possible success indicators
          else if (responseData.success || responseData.status === 'success') {
            console.log('Response indicates success, assuming all products successful.')
            successfulCount = validProducts.length
          }
        }
        
        // Fallback: if we got a 200 response but no clear success indicators
        if (successfulCount === 0 && failedCount === 0) {
          console.log('No clear success/failure indicators, but got 200 response. Assuming success.')
          successfulCount = validProducts.length
        }
        
        console.log('Final calculated counts - Success:', successfulCount, 'Failed:', failedCount)
        
        // Show success notification if we have any successful creates
        if (successfulCount > 0) {
          console.log('✅ Triggering success notification...')
          
          // Set notification data
          this.notificationData = {
            type: 'success',
            title: 'Products Created Successfully!',
            message: `${successfulCount} product${successfulCount > 1 ? 's have' : ' has'} been created successfully.`,
            details: {
              successful: successfulCount,
              failed: failedCount
            }
          }
          
          // Show the modal
          this.showNotificationModal = true
          
          console.log('✅ Notification modal visible:', this.showNotificationModal)
          console.log('✅ Notification data:', this.notificationData)
          
        } else {
          console.error('❌ No success detected despite 200 response')
          this.showError('Products may have been created but response was unclear. Please check your inventory.')
        }
        
        // Handle failures
        if (failedCount > 0) {
          console.warn('⚠️ Some products failed to create')
          setTimeout(() => {
            this.showError(`${failedCount} products failed to create. Check console for details.`)
          }, 100)
        }
        
      } catch (error) {
        console.error('💥 Error saving products:', error)
        console.error('💥 Error details:', error.response?.data)
        
        // Better error handling
        let errorMessage = 'Failed to save products'
        
        if (error.response?.data?.error) {
          errorMessage = error.response.data.error
        } else if (error.response?.data?.message) {
          errorMessage = error.response.data.message
        } else if (error.message) {
          errorMessage = error.message
        }
        
        this.notificationData = {
          type: 'error',
          title: 'Failed to Create Products',
          message: errorMessage,
          details: null
        }
        this.showNotificationModal = true
        
      } finally {
        this.loading = false
      }
    },
        
    showSuccess(message) {
      this.successMessage = message
      this.errorMessage = null
      setTimeout(() => {
        this.successMessage = null
      }, 5000)
    },
    
    showError(message) {
      this.errorMessage = message
      this.successMessage = null
      setTimeout(() => {
        this.errorMessage = null
      }, 5000)
    },
    
    clearMessages() {
      this.successMessage = null
      this.errorMessage = null
    },

    closeNotificationModal() {
      this.showNotificationModal = false
    },

    handleNotificationConfirm() {
      // Reset table for adding more products
      this.products = []
      this.nextId = 1  // Reset the ID counter too
      this.addNewRow()
      this.clearMessages()  // Clear any residual messages
      this.showNotificationModal = false
      
      console.log('Table reset, new products array:', this.products)
    },

    handleNotificationRetry() {
      // Just close modal, keep current data
      this.showNotificationModal = false
    }
  }
}
</script>

<style scoped>
.bulk-entry-page {
  padding: 1.5rem;
  max-width: 100%;
  margin: 0 auto;
  background-color: var(--neutral-light);
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--tertiary-medium);
  font-size: 0.875rem;
}

.breadcrumb-link {
  color: var(--tertiary-medium);
  text-decoration: none;
  transition: color 0.2s ease;
}

.breadcrumb-link:hover {
  color: var(--primary);
}

.breadcrumb-separator {
  color: var(--tertiary-medium);
}

.breadcrumb-current {
  color: var(--primary);
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.25rem;
  border-radius: 0.5rem;
  border: none;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.875rem;
  white-space: nowrap;
}

.btn-icon {
  width: 16px;
  height: 16px;
}

.btn-primary {
  background-color: var(--primary);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: var(--primary-dark);
}

.btn-secondary {
  background-color: var(--neutral-medium);
  color: var(--tertiary-dark);
}

.btn-secondary:hover:not(:disabled) {
  background-color: var(--neutral-dark);
}

.btn-info {
  background-color: var(--info);
  color: white;
}

.btn-info:hover:not(:disabled) {
  background-color: var(--info-dark);
}

.btn-success {
  background-color: var(--success);
  color: white;
}

.btn-success:hover:not(:disabled) {
  background-color: var(--success-dark);
}

.btn-error {
  background-color: var(--error);
  color: white;
}

.btn-error:hover:not(:disabled) {
  background-color: var(--error-dark);
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.8125rem;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.progress-section {
  background: white;
  padding: 1rem 1.5rem;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  margin-bottom: 1.5rem;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.product-count {
  font-weight: 600;
  color: var(--tertiary-dark);
  font-size: 1rem;
}

.valid-count {
  font-size: 0.875rem;
  color: var(--tertiary-medium);
}

.progress-bar {
  width: 100%;
  height: 8px;
  background-color: var(--neutral-light);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--success), var(--primary));
  transition: width 0.3s ease;
}

.message {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  border-radius: 0.5rem;
  margin-bottom: 1.5rem;
  font-weight: 500;
}

.message-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.success-message {
  background-color: var(--success-light);
  border: 1px solid var(--success);
  color: var(--success-dark);
}

.error-message {
  background-color: var(--error-light);
  border: 1px solid var(--error);
  color: var(--error-dark);
}

.table-container {
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  overflow: hidden;
  border: 1px solid var(--neutral-medium);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid var(--neutral-medium);
  background-color: white;
}

.table-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--tertiary-dark);
  margin: 0;
}

.table-actions {
  display: flex;
  gap: 0.75rem;
}

.table-wrapper {
  overflow-x: auto;
  max-height: 70vh;
}

.bulk-entry-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 1200px;
}

.bulk-entry-table th {
  background-color: var(--neutral-light);
  padding: 1rem 0.75rem;
  text-align: left;
  font-weight: 600;
  color: var(--tertiary-dark);
  border-bottom: 2px solid var(--neutral-medium);
  font-size: 0.875rem;
  white-space: nowrap;
  position: sticky;
  top: 0;
  z-index: 10;
}

.bulk-entry-table td {
  padding: 0.75rem;
  border-bottom: 1px solid var(--neutral);
  vertical-align: middle;
}

.bulk-entry-table tr:hover {
  background-color: var(--neutral-light);
}

.invalid-row {
  background-color: rgba(235, 105, 102, 0.1) !important;
  border-left: 3px solid var(--error);
}

.invalid-row:hover {
  background-color: rgba(235, 105, 102, 0.15) !important;
}

.required {
  color: var(--error);
  font-weight: 500;
}

/* Column Widths */
.row-number-col { width: 50px; }
.image-col { width: 80px; }
.name-col { width: 200px; }
.sku-col { width: 120px; }
.category-col { width: 130px; }
.cost-col { width: 120px; }
.markup-col { width: 100px; }
.selling-col { width: 120px; }
.stock-col { width: 100px; }
.actions-col { width: 100px; }

.row-number {
  font-weight: 500;
  color: var(--tertiary-medium);
  text-align: center;
}

/* Image Upload */
.image-upload {
  position: relative;
  width: 50px;
  height: 50px;
}

.image-input {
  display: none;
}

.image-label {
  display: block;
  width: 100%;
  height: 100%;
  cursor: pointer;
  border-radius: 0.375rem;
  overflow: hidden;
  border: 2px dashed var(--neutral);
  transition: border-color 0.2s ease;
}

.image-label:hover {
  border-color: var(--primary);
}

.product-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  background-color: var(--neutral-light);
  color: var(--tertiary-medium);
}

.image-placeholder svg {
  width: 20px;
  height: 20px;
}

/* Form Inputs */
.table-input,
.table-select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--neutral-medium);
  border-radius: 0.375rem;
  font-size: 0.875rem;
  background: white;
  color: var(--tertiary-dark);
  transition: border-color 0.2s ease;
}

.table-input:focus,
.table-select:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(115, 146, 226, 0.1);
}

.table-input.invalid {
  border-color: var(--error);
  background-color: var(--error-light);
}

.table-input.invalid:focus {
  box-shadow: 0 0 0 3px rgba(229, 57, 53, 0.1);
}

.sku-input {
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
  font-size: 0.8125rem;
}

.price-input,
.stock-input {
  text-align: right;
}

.markup-cell {
  position: relative;
}

.markup-suffix {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--tertiary-medium);
  font-size: 0.875rem;
  pointer-events: none;
}

.markup-input {
  padding-right: 1.5rem;
}

.field-error {
  font-size: 0.75rem;
  color: var(--error);
  margin-top: 0.25rem;
  font-weight: 500;
}

/* Action Buttons */
.actions-cell {
  text-align: center;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: 1px solid;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.15s ease;
  background-color: transparent;
  margin: 0 0.125rem;
}

.action-btn svg {
  width: 16px;
  height: 16px;
  stroke-width: 1.5;
}

.duplicate-btn {
  color: var(--info);
  border-color: var(--info);
}

.duplicate-btn:hover {
  background-color: var(--info-light);
  color: var(--info-dark);
}

.delete-btn {
  color: var(--error);
  border-color: var(--error);
}

.delete-btn:hover {
  background-color: var(--error-light);
  color: var(--error-dark);
}

/* Empty State */
.empty-row td {
  padding: 3rem;
  text-align: center;
}

.empty-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  color: var(--tertiary-medium);
}

.empty-icon {
  width: 48px;
  height: 48px;
  color: var(--tertiary-medium);
}

.empty-content p {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 500;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .bulk-entry-page {
    padding: 1rem;
  }
  
  .page-header {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  
  .breadcrumb {
    justify-content: center;
  }
  
  .header-actions {
    justify-content: center;
  }
  
  .table-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .table-actions {
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .btn {
    padding: 0.5rem 1rem;
    font-size: 0.8125rem;
  }
  
  .btn-icon {
    width: 14px;
    height: 14px;
  }
  
  .header-actions {
    flex-direction: column;
  }
  
  .table-wrapper {
    border-radius: 0;
    margin: 0 -1rem;
  }
  
  .bulk-entry-table {
    min-width: 800px;
  }
  
  .bulk-entry-table th,
  .bulk-entry-table td {
    padding: 0.5rem;
  }
  
  .progress-section {
    margin: 0 -1rem 1.5rem;
    border-radius: 0;
  }
}

/* Print Styles */
@media print {
  .page-header,
  .progress-section,
  .message,
  .table-actions,
  .actions-col,
  .actions-cell {
    display: none;
  }
  
  .bulk-entry-page {
    padding: 0;
    background: white;
  }
  
  .table-container {
    box-shadow: none;
    border: 1px solid #000;
  }
  
  .bulk-entry-table th,
  .bulk-entry-table td {
    border: 1px solid #000;
    padding: 0.5rem;
  }
}

/* Light Theme (Default) */
.bulk-entry-page {
  background-color: var(--neutral-light);
  color: var(--tertiary-dark);
}

.table-container,
.progress-section {
  background-color: white;
  border-color: var(--neutral-medium);
}

.bulk-entry-table th {
  background-color: var(--neutral-light);
  color: var(--tertiary-dark);
}

.table-input,
.table-select {
  background-color: white;
  border-color: var(--neutral-medium);
  color: var(--tertiary-dark);
}

/* Animation for new rows */
@keyframes slideInRow {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.bulk-entry-table tbody tr {
  animation: slideInRow 0.3s ease;
}

/* Focus management for accessibility */
.table-input:focus,
.table-select:focus,
.action-btn:focus {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}

/* Loading state for table */
.bulk-entry-table.loading {
  opacity: 0.7;
  pointer-events: none;
}

/* Validation success state */
.table-input.valid {
  border-color: var(--success);
}

.table-input.valid:focus {
  box-shadow: 0 0 0 3px rgba(94, 180, 136, 0.1);
}
</style>