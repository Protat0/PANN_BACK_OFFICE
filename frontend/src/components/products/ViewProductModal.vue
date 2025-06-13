<template>
  <div v-if="show" class="modal-overlay" @click="handleOverlayClick">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2>Product Details</h2>
        <button class="close-btn" @click="$emit('close')">
          ✕
        </button>
      </div>

      <div v-if="product" class="product-view">
        <!-- Product Header -->
        <div class="product-header">
          <div class="product-main-info">
            <h3 class="product-name">{{ product.product_name }}</h3>
            <div class="product-badges">
              <span :class="['status-badge', `status-${product.status}`]">
                {{ formatStatus(product.status) }}
              </span>
              <span :class="['category-badge', `category-${getCategorySlug(product.category_id)}`]">
                {{ getCategoryName(product.category_id) }}
              </span>
              <span v-if="product.is_taxable" class="tax-badge">
                Taxable
              </span>
            </div>
          </div>
          <div class="product-actions">
            <button @click="$emit('edit', product)" class="btn btn-primary">
              <span class="icon">✏️</span>
              Edit Product
            </button>
          </div>
        </div>

        <!-- Product Details Grid -->
        <div class="product-details">
          <div class="details-section">
            <h4 class="section-title">Basic Information</h4>
            <div class="details-grid">
              <div class="detail-item">
                <label>Product ID</label>
                <div class="detail-value code">{{ product._id }}</div>
              </div>
              <div class="detail-item">
                <label>SKU</label>
                <div class="detail-value code">{{ product.SKU }}</div>
              </div>
              <div class="detail-item">
                <label>Barcode</label>
                <div class="detail-value code">{{ product.barcode || 'Not set' }}</div>
              </div>
              <div class="detail-item">
                <label>Unit</label>
                <div class="detail-value">{{ product.unit }}</div>
              </div>
              <div v-if="product.description" class="detail-item full-width">
                <label>Description</label>
                <div class="detail-value">{{ product.description }}</div>
              </div>
            </div>
          </div>

          <div class="details-section">
            <h4 class="section-title">Stock Information</h4>
            <div class="stock-overview">
              <div class="stock-card" :class="getStockClass(product)">
                <div class="stock-label">Current Stock</div>
                <div class="stock-value">{{ product.stock }}</div>
                <div class="stock-unit">{{ product.unit }}</div>
              </div>
              <div class="stock-card threshold">
                <div class="stock-label">Low Stock Threshold</div>
                <div class="stock-value">{{ product.low_stock_threshold }}</div>
                <div class="stock-unit">{{ product.unit }}</div>
              </div>
              <div class="stock-card status">
                <div class="stock-label">Stock Status</div>
                <div class="stock-status" :class="getStockStatusClass(product)">
                  {{ getStockStatusText(product) }}
                </div>
              </div>
            </div>
          </div>

          <div class="details-section">
            <h4 class="section-title">Pricing Information</h4>
            <div class="pricing-grid">
              <div class="price-card">
                <div class="price-label">Cost Price</div>
                <div class="price-value">₱{{ formatPrice(product.cost_price) }}</div>
              </div>
              <div class="price-card">
                <div class="price-label">Selling Price</div>
                <div class="price-value">₱{{ formatPrice(product.selling_price) }}</div>
              </div>
              <div class="price-card profit">
                <div class="price-label">Profit Margin</div>
                <div class="price-value">{{ getProfitMargin(product) }}%</div>
              </div>
              <div class="price-card profit">
                <div class="price-label">Profit per Unit</div>
                <div class="price-value">₱{{ getProfitPerUnit(product) }}</div>
              </div>
            </div>
          </div>

          <div class="details-section">
            <h4 class="section-title">Date Information</h4>
            <div class="details-grid">
              <div class="detail-item">
                <label>Date Received</label>
                <div class="detail-value">{{ formatDate(product.date_received) }}</div>
              </div>
              <div class="detail-item">
                <label>Expiry Date</label>
                <div class="detail-value" :class="getExpiryClass(product.expiry_date)">
                  {{ formatDate(product.expiry_date) }}
                  <span v-if="product.expiry_date" class="expiry-info">
                    ({{ getDaysUntilExpiry(product.expiry_date) }})
                  </span>
                </div>
              </div>
              <div class="detail-item">
                <label>Created At</label>
                <div class="detail-value">{{ formatDateTime(product.created_at) }}</div>
              </div>
              <div class="detail-item">
                <label>Last Updated</label>
                <div class="detail-value">{{ formatDateTime(product.updated_at) }}</div>
              </div>
            </div>
          </div>

          <!-- Quick Actions -->
          <div class="details-section">
            <h4 class="section-title">Quick Actions</h4>
            <div class="quick-actions">
              <button @click="$emit('restock', product)" class="action-btn restock">
                <span class="icon">📦</span>
                <div>
                  <div class="action-title">Update Stock</div>
                  <div class="action-subtitle">Add, remove, or set stock quantity</div>
                </div>
              </button>
              <button @click="toggleStatus" class="action-btn toggle">
                <span class="icon">{{ product.status === 'active' ? '🔒' : '🔓' }}</span>
                <div>
                  <div class="action-title">
                    {{ product.status === 'active' ? 'Deactivate' : 'Activate' }} Product
                  </div>
                  <div class="action-subtitle">
                    {{ product.status === 'active' ? 'Make unavailable for sale' : 'Make available for sale' }}
                  </div>
                </div>
              </button>
              <button @click="generateBarcode" class="action-btn barcode" :disabled="product.barcode">
                <span class="icon">🏷️</span>
                <div>
                  <div class="action-title">Generate Barcode</div>
                  <div class="action-subtitle">
                    {{ product.barcode ? 'Barcode already exists' : 'Create new barcode for product' }}
                  </div>
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button @click="$emit('close')" class="btn btn-secondary">
          Close
        </button>
        <button @click="$emit('edit', product)" class="btn btn-primary">
          <span class="icon">✏️</span>
          Edit Product
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ViewProductModal',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    product: {
      type: Object,
      default: null
    }
  },
  emits: ['close', 'edit', 'restock', 'toggle-status', 'generate-barcode'],
  methods: {
    handleOverlayClick() {
      this.$emit('close')
    },
    toggleStatus() {
      this.$emit('toggle-status', this.product)
    },
    generateBarcode() {
      if (!this.product.barcode) {
        this.$emit('generate-barcode', this.product)
      }
    },
    getCategoryName(categoryId) {
      const categories = {
        'noodles': 'Noodles',
        'drinks': 'Drinks',
        'toppings': 'Toppings'
      }
      return categories[categoryId] || categoryId
    },
    getCategorySlug(categoryId) {
      return categoryId?.toLowerCase().replace(/\s+/g, '-') || 'unknown'
    },
    getStockClass(product) {
      if (!product) return ''
      if (product.stock === 0) return 'stock-zero'
      if (product.stock <= product.low_stock_threshold) return 'stock-low'
      return 'stock-normal'
    },
    getStockStatusClass(product) {
      if (!product) return ''
      if (product.stock === 0) return 'status-out'
      if (product.stock <= product.low_stock_threshold) return 'status-low'
      return 'status-good'
    },
    getStockStatusText(product) {
      if (!product) return 'Unknown'
      if (product.stock === 0) return 'Out of Stock'
      if (product.stock <= product.low_stock_threshold) return 'Low Stock'
      return 'In Stock'
    },
    getExpiryClass(expiryDate) {
      if (!expiryDate) return ''
      
      const today = new Date()
      const expiry = new Date(expiryDate)
      const daysUntilExpiry = Math.ceil((expiry - today) / (1000 * 60 * 60 * 24))
      
      if (daysUntilExpiry < 0) return 'expired'
      if (daysUntilExpiry <= 7) return 'expiring-soon'
      if (daysUntilExpiry <= 30) return 'expiring-month'
      return ''
    },
    getDaysUntilExpiry(expiryDate) {
      if (!expiryDate) return ''
      
      const today = new Date()
      const expiry = new Date(expiryDate)
      const daysUntilExpiry = Math.ceil((expiry - today) / (1000 * 60 * 60 * 24))
      
      if (daysUntilExpiry < 0) return `Expired ${Math.abs(daysUntilExpiry)} days ago`
      if (daysUntilExpiry === 0) return 'Expires today'
      if (daysUntilExpiry === 1) return 'Expires tomorrow'
      return `${daysUntilExpiry} days remaining`
    },
    getProfitMargin(product) {
      if (!product || !product.selling_price || !product.cost_price) return '0.00'
      const margin = ((product.selling_price - product.cost_price) / product.selling_price * 100)
      return margin.toFixed(2)
    },
    getProfitPerUnit(product) {
      if (!product || !product.selling_price || !product.cost_price) return '0.00'
      const profit = product.selling_price - product.cost_price
      return profit.toFixed(2)
    },
    formatPrice(price) {
      return parseFloat(price || 0).toFixed(2)
    },
    formatStatus(status) {
      return status.charAt(0).toUpperCase() + status.slice(1).replace('-', ' ')
    },
    formatDate(dateString) {
      if (!dateString) return 'Not set'
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    },
    formatDateTime(dateString) {
      if (!dateString) return 'Not available'
      const date = new Date(dateString)
      return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
  },
    mounted() {
    this.handleEscape = (e) => {
        if (e.key === 'Escape' && this.show && !this.loading) {
        this.$emit('close')
        }
    }
    
    document.addEventListener('keydown', this.handleEscape)
    },

    beforeUnmount() {
    if (this.handleEscape) {
        document.removeEventListener('keydown', this.handleEscape)
    }
    }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  max-width: 900px;
  width: 95%;
  max-height: 90vh;
  overflow-y: auto;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from { 
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to { 
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #e5e7eb;
  background: #f8fafc;
  border-radius: 12px 12px 0 0;
}

.modal-header h2 {
  margin: 0;
  color: #1f2937;
  font-size: 1.5rem;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6b7280;
  padding: 0.25rem;
  border-radius: 0.375rem;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background-color: #e5e7eb;
  color: #374151;
}

.product-view {
  padding: 2rem;
}

.product-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.product-main-info {
  flex: 1;
}

.product-name {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 1rem 0;
}

.product-badges {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.status-badge,
.category-badge,
.tax-badge {
  padding: 0.375rem 0.75rem;
  border-radius: 0.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.status-badge.status-active {
  background-color: #d1fae5;
  color: #065f46;
}

.status-badge.status-inactive {
  background-color: #fee2e2;
  color: #991b1b;
}

.category-badge.category-noodles {
  background-color: #fef3c7;
  color: #92400e;
}

.category-badge.category-drinks {
  background-color: #dbeafe;
  color: #1e40af;
}

.category-badge.category-toppings {
  background-color: #e0e7ff;
  color: #5b21b6;
}

.tax-badge {
  background-color: #f3e8ff;
  color: #7c3aed;
}

.product-actions {
  margin-left: 1rem;
}

.details-section {
  margin-bottom: 2rem;
}

.section-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #374151;
  margin: 0 0 1rem 0;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #e5e7eb;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-item.full-width {
  grid-column: 1 / -1;
}

.detail-item label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.detail-value {
  font-size: 1rem;
  color: #1f2937;
  font-weight: 500;
}

.detail-value.code {
  font-family: 'Monaco', 'Menlo', monospace;
  background: #f3f4f6;
  padding: 0.5rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
}

.stock-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.stock-card {
  background: #f8fafc;
  padding: 1.5rem;
  border-radius: 0.75rem;
  text-align: center;
  border: 2px solid #e5e7eb;
  transition: all 0.2s ease;
}

.stock-card.stock-zero {
  border-color: #fca5a5;
  background: #fef2f2;
}

.stock-card.stock-low {
  border-color: #fbbf24;
  background: #fffbeb;
}

.stock-card.stock-normal {
  border-color: #86efac;
  background: #f0fdf4;
}

.stock-card.threshold {
  border-color: #a78bfa;
  background: #f5f3ff;
}

.stock-card.status {
  border-color: #60a5fa;
  background: #eff6ff;
}

.stock-label {
  font-size: 0.75rem;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.5rem;
}

.stock-value {
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
}

.stock-unit {
  font-size: 0.875rem;
  color: #6b7280;
  margin-top: 0.25rem;
}

.stock-status {
  font-size: 0.875rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 0.375rem;
  margin-top: 0.5rem;
}

.stock-status.status-good {
  background: #d1fae5;
  color: #065f46;
}

.stock-status.status-low {
  background: #fef3c7;
  color: #92400e;
}

.stock-status.status-out {
  background: #fee2e2;
  color: #991b1b;
}

.pricing-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
}

.price-card {
  background: #f8fafc;
  padding: 1.5rem;
  border-radius: 0.75rem;
  text-align: center;
  border: 2px solid #e5e7eb;
}

.price-card.profit {
  border-color: #34d399;
  background: #ecfdf5;
}

.price-label {
  font-size: 0.75rem;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.5rem;
}

.price-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
}

.expiry-info {
  font-size: 0.75rem;
  color: #6b7280;
  display: block;
  margin-top: 0.25rem;
}

.expired {
  color: #dc2626;
  font-weight: 600;
}

.expiring-soon {
  color: #ea580c;
  font-weight: 600;
}

.expiring-month {
  color: #d97706;
  font-weight: 500;
}

.quick-actions {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
}

.action-btn:hover:not(:disabled) {
  border-color: #3b82f6;
  background: #f8fafc;
  transform: translateY(-1px);
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
}

.action-btn .icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.action-title {
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.action-subtitle {
  font-size: 0.875rem;
  color: #6b7280;
}

.modal-footer {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  padding: 1.5rem 2rem;
  border-top: 1px solid #e5e7eb;
  background: #f8fafc;
  border-radius: 0 0 12px 12px;
}

.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  border: none;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-primary {
  background-color: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background-color: #2563eb;
  transform: translateY(-1px);
}

.btn-secondary {
  background-color: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-secondary:hover {
  background-color: #e5e7eb;
}

.btn .icon {
  font-size: 1rem;
}

/* Responsive Design */
@media (max-width: 768px) {
  .modal-content {
    margin: 1rem;
    max-height: calc(100vh - 2rem);
  }

  .modal-header {
    padding: 1rem 1.5rem;
  }

  .modal-header h2 {
    font-size: 1.25rem;
  }

  .product-view {
    padding: 1.5rem;
  }

  .product-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }

  .product-actions {
    margin-left: 0;
  }

  .product-name {
    font-size: 1.5rem;
  }

  .details-grid {
    grid-template-columns: 1fr;
  }

  .stock-overview {
    grid-template-columns: 1fr;
  }

  .pricing-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .modal-footer {
    padding: 1rem 1.5rem;
    flex-direction: column-reverse;
  }

  .btn {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .modal-content {
    margin: 0.5rem;
    max-height: calc(100vh - 1rem);
    border-radius: 8px;
  }

  .modal-header {
    padding: 0.75rem 1rem;
    border-radius: 8px 8px 0 0;
  }

  .product-view {
    padding: 1rem;
  }

  .pricing-grid {
    grid-template-columns: 1fr;
  }

  .product-badges {
    flex-direction: column;
    align-items: flex-start;
  }

  .modal-footer {
    padding: 0.75rem 1rem;
    border-radius: 0 0 8px 8px;
  }
}

/* Custom scrollbar */
.modal-content::-webkit-scrollbar {
  width: 8px;
}

.modal-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.modal-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.modal-content::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>