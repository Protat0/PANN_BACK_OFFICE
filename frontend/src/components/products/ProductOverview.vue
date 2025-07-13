<template>
  <div class="overview-container">
    <!-- Left Column - Product Details (2/3 width) -->
    <div class="details-column">
      <!-- Primary Details -->
      <div class="details-card">
        <h2 class="section-title">Primary Details</h2>
        <div class="details-grid">
          <div class="detail-item">
            <label class="detail-label">Product Name</label>
            <p class="detail-value">{{ productData.name }}</p>
          </div>
          <div class="detail-item">
            <label class="detail-label">Product ID</label>
            <p class="detail-value">{{ formatProductId(productData.id) }}</p>
          </div>
          <div class="detail-item">
            <label class="detail-label">Product Category</label>
            <p class="detail-value">{{ productData.category || 'Noodles' }}</p>
          </div>
          <div class="detail-item">
            <label class="detail-label">Batch Date</label>
            <p class="detail-value">{{ formatDate(productData.batchDate) }}</p>
          </div>
          <div class="detail-item">
            <label class="detail-label">Threshold Value</label>
            <p class="detail-value">{{ productData.thresholdValue }}</p>
          </div>
        </div>
      </div>

      <!-- Supplier Details -->
      <div class="details-card">
        <h2 class="section-title">Supplier Details</h2>
        <div class="details-grid">
          <div class="detail-item">
            <label class="detail-label">Supplier Name</label>
            <p class="detail-value">{{ productData.supplier.name }}</p>
          </div>
          <div class="detail-item">
            <label class="detail-label">Contact Number</label>
            <p class="detail-value">{{ productData.supplier.contact }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Right Column - Image & Stock Info (1/3 width) -->
    <div class="sidebar-column">
      <!-- Product Image -->
      <div class="image-container">
        <img 
          :src="productData.image" 
          :alt="productData.name"
          class="product-image"
        />
      </div>

      <!-- Stock Information -->
      <div class="stock-container">
        <div class="stock-item">
          <span class="stock-label">Opening Stock</span>
          <span class="stock-value">{{ productData.stock.opening }}</span>
        </div>
        <div class="stock-item">
          <span class="stock-label">Remaining Stock</span>
          <span 
            class="stock-value" 
            :style="`color: ${getStockColor(productData.stock.remaining, productData.thresholdValue)};`"
          >
            {{ productData.stock.remaining }}
          </span>
        </div>
        <div class="stock-item">
          <span class="stock-label">On the Way</span>
          <span class="stock-value stock-info">{{ productData.stock.onTheWay }}</span>
        </div>
        <div class="stock-item">
          <span class="stock-label">Cost Price</span>
          <span class="stock-value">{{ formatPrice(productData.pricing.cost) }}</span>
        </div>
        <div class="stock-item">
          <span class="stock-label">Selling Price</span>
          <span class="stock-value">{{ formatPrice(productData.pricing.selling) }}</span>
        </div>
        <div class="stock-item">
          <span class="stock-label">Unit Type</span>
          <span class="stock-value">{{ productData.pricing.unitType }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProductOverview',
  props: {
    productData: {
      type: Object,
      required: true,
      default: () => ({
        name: '',
        id: '',
        category: '',
        batchDate: '',
        expiryDate: '',
        thresholdValue: 0,
        description: '',
        tags: [],
        supplier: {
          name: '',
          contact: '',
          email: '',
          address: ''
        },
        stock: {
          opening: 0,
          remaining: 0,
          onTheWay: 0,
          reserved: 0
        },
        pricing: {
          cost: 0,
          selling: 0,
          unitType: ''
        },
        image: ''
      })
    }
  },
  emits: ['stock-adjustment', 'reorder', 'view-history', 'image-upload'],
  methods: {
    getStockColor(remaining, threshold) {
      if (remaining <= threshold) {
        return 'var(--error)';
      } else if (remaining <= threshold * 1.5) {
        return 'var(--secondary)';
      }
      return 'var(--success)';
    },
    
    formatPrice(price) {
      if (!price) return '0.00';
      return parseFloat(price).toFixed(2);
    },
    
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      try {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit'
        });
      } catch {
        return dateString;
      }
    },
    
    formatProductId(id) {
      if (!id) return 'N/A';
      // Show the actual ID format from the image (like "00001")
      return id.length > 6 ? id.slice(-6) : id;
    },
    
    handleStockAdjustment() {
      this.$emit('stock-adjustment', this.productData);
    },
    
    handleReorder() {
      this.$emit('reorder', this.productData);
    },
    
    handleViewHistory() {
      this.$emit('view-history', this.productData);
    },
    
    handleImageUpload() {
      this.$emit('image-upload', this.productData);
    }
  }
};
</script>

<style scoped>
.overview-container {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
  max-width: 1200px;
}

.details-column {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.details-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
  padding: 1.5rem;
}

.section-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 1.5rem;
}

.details-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--tertiary-medium);
}

.detail-value {
  font-size: 1rem;
  font-weight: 500;
  color: var(--tertiary-dark);
  margin: 0;
}

.sidebar-column {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.image-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
  padding: 1.5rem;
  border: 2px dashed var(--primary-light);
  text-align: center;
}

.product-image {
  width: 100%;
  height: 150px;
  object-fit: contain;
  border-radius: 4px;
}

.stock-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.stock-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stock-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--tertiary-medium);
}

.stock-value {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--tertiary-dark);
}

.stock-info {
  color: var(--info) !important;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .overview-container {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  
  .details-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
}

@media (max-width: 768px) {
  .overview-container {
    gap: 1rem;
  }
  
  .details-card,
  .image-container,
  .stock-container {
    padding: 1rem;
  }
  
  .section-title {
    font-size: 1.125rem;
    margin-bottom: 1rem;
  }
}
</style>