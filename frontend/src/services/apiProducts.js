// services/apiProducts.js
import { api } from './api.js';

class ProductsApiService {
  // Helper method to handle responses
  handleResponse(response) {
    return response.data;
  }

  // Helper method to handle errors
  handleError(error) {
    const message = error.response?.data?.error || 
                   error.response?.data?.message || 
                   error.message || 
                   'An unexpected error occurred';
    throw new Error(message);
  }

  // PRODUCT CRUD OPERATIONS
  
  /**
   * Get all products with optional query parameters
   * @param {Object} params - Query parameters (page, limit, search, category, etc.)
   * @returns {Promise<Object>} Products list with pagination info
   */
  async getProducts(params = {}) {
    try {
      console.log('Making API call to get products...', params);
      const response = await api.get('/products/', { params });
      console.log('Products API response:', response);
      return this.handleResponse(response);
    } catch (error) {
      console.error('Error in getProducts:', error);
      this.handleError(error);
    }
  }

  /**
   * Get a specific product by ID
   * @param {string} productId - Product ID
   * @returns {Promise<Object>} Product details
   */
  async getProduct(productId) {
    try {
      const response = await api.get(`/products/${productId}/`);
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  /**
   * Get a product by SKU
   * @param {string} sku - Product SKU
   * @returns {Promise<Object>} Product details
   */
  async getProductBySku(sku) {
    try {
      const response = await api.get(`/products/sku/${sku}/`);
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  /**
   * Create a new product
   * @param {Object} productData - Product data
   * @returns {Promise<Object>} Created product
   */
  async createProduct(productData) {
    try {
      const response = await api.post('/products/', productData);
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  /**
   * Update an existing product
   * @param {string} productId - Product ID
   * @param {Object} productData - Updated product data
   * @returns {Promise<Object>} Updated product
   */
  async updateProduct(productId, productData) {
    try {
      const response = await api.put(`/products/${productId}/`, productData);
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  /**
   * Partially update a product
   * @param {string} productId - Product ID
   * @param {Object} productData - Partial product data
   * @returns {Promise<Object>} Updated product
   */
  async patchProduct(productId, productData) {
    try {
      const response = await api.patch(`/products/${productId}/`, productData);
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  /**
   * Delete a product
   * @param {string} productId - Product ID
   * @returns {Promise<void>}
   */
  async deleteProduct(productId) {
    try {
      const response = await api.delete(`/products/${productId}/`);
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  /**
   * Bulk delete products
   * @param {Array<string>} productIds - Array of product IDs
   * @returns {Promise<Object>} Deletion result
   */
  async bulkDeleteProducts(productIds) {
    try {
      const response = await api.delete('/products/', { 
        data: { product_ids: productIds } 
      });
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  // STOCK MANAGEMENT - FIXED METHODS

  /**
   * Update product stock - FIXED VERSION
   * @param {string} productId - Product ID
   * @param {Object} stockData - Stock update data (quantity, operation_type, reason, etc.)
   * @returns {Promise<Object>} Updated stock info
   */
  async updateProductStock(productId, stockData) {
    try {
      // Transform data to match backend expectations
      const payload = {
        operation_type: stockData.operation_type || 'set',
        quantity: stockData.quantity || stockData.stock || 0,
        reason: stockData.reason || 'Manual adjustment'
      };

      console.log('Sending stock update payload:', payload);
      console.log('To URL:', `/products/${productId}/stock/`);
      
      // Use PUT method to match your backend view
      const response = await api.put(`/products/${productId}/stock/`, payload);
      return this.handleResponse(response);
    } catch (error) {
      console.error('Stock update error:', error.response?.data || error.message);
      this.handleError(error);
    }
  }

  /**
   * Add stock to product
   * @param {string} productId - Product ID
   * @param {number} quantity - Quantity to add
   * @param {string} reason - Reason for stock addition
   * @returns {Promise<Object>} Updated stock info
   */
  async addStock(productId, quantity, reason = 'Manual adjustment') {
    return this.updateProductStock(productId, {
      quantity: parseInt(quantity),
      operation_type: 'add',
      reason
    });
  }

  /**
   * Remove stock from product
   * @param {string} productId - Product ID
   * @param {number} quantity - Quantity to remove
   * @param {string} reason - Reason for stock removal
   * @returns {Promise<Object>} Updated stock info
   */
  async removeStock(productId, quantity, reason = 'Manual adjustment') {
    return this.updateProductStock(productId, {
      quantity: parseInt(quantity),
      operation_type: 'remove',
      reason
    });
  }

  /**
   * Set exact stock quantity
   * @param {string} productId - Product ID
   * @param {number} quantity - New stock quantity
   * @param {string} reason - Reason for stock adjustment
   * @returns {Promise<Object>} Updated stock info
   */
  async setStock(productId, quantity, reason = 'Stock correction') {
    return this.updateProductStock(productId, {
      quantity: parseInt(quantity),
      operation_type: 'set',
      reason
    });
  }

  /**
   * Bulk update stock for multiple products - NEW METHOD
   * @param {Array<Object>} stockUpdates - Array of stock updates
   * @returns {Promise<Object>} Bulk update result
   */
  async bulkUpdateStock(stockUpdates) {
    try {
      const response = await api.post('/products/stock/bulk-update/', {
        updates: stockUpdates
      });
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  /**
   * Get stock history for a product - NEW METHOD
   * @param {string} productId - Product ID
   * @returns {Promise<Object>} Stock history
   */
  async getStockHistory(productId) {
    try {
      const response = await api.get(`/products/${productId}/stock/history/`);
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  // REPORTS AND ANALYTICS

  /**
   * Get low stock products
   * @param {Object} params - Query parameters (threshold, branch_id, etc.)
   * @returns {Promise<Array>} Low stock products
   */
  async getLowStockProducts(params = {}) {
    try {
      const response = await api.get('/products/reports/low-stock/', { params });
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  /**
   * Get expiring products
   * @param {Object} params - Query parameters (days_ahead, branch_id, etc.)
   * @returns {Promise<Array>} Expiring products
   */
  async getExpiringProducts(params = {}) {
    try {
      const response = await api.get('/products/reports/expiring/', { params });
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  /**
   * Get products by category
   * @param {string} categoryId - Category ID
   * @param {Object} params - Additional query parameters
   * @returns {Promise<Object>} Products in category
   */
  async getProductsByCategory(categoryId, params = {}) {
    try {
      const response = await api.get('/products/', { 
        params: { ...params, category: categoryId } 
      });
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  /**
   * Search products
   * @param {string} query - Search query
   * @param {Object} params - Additional search parameters
   * @returns {Promise<Object>} Search results
   */
  async searchProducts(query, params = {}) {
    try {
      const response = await api.get('/products/', { 
        params: { ...params, search: query } 
      });
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  // BULK OPERATIONS

  /**
   * Bulk create products
   * @param {Array<Object>} productsData - Array of product data
   * @returns {Promise<Object>} Bulk creation result
   */
  async bulkCreateProducts(productsData) {
    try {
      const response = await api.post('/products/bulk/', { products: productsData });
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  /**
   * Bulk update products
   * @param {Array<Object>} productsData - Array of product updates
   * @returns {Promise<Object>} Bulk update result
   */
  async bulkUpdateProducts(productsData) {
    try {
      const response = await api.put('/products/bulk/', { products: productsData });
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  /**
   * Export products data
   * @param {Object} params - Export parameters (format, filters, etc.)
   * @returns {Promise<Blob>} Exported file
   */
  async exportProducts(params = {}) {
    try {
      const response = await api.get('/products/export/', { 
        params,
        responseType: 'blob'
      });
      return response.data;
    } catch (error) {
      this.handleError(error);
    }
  }

  /**
   * Import products from file
   * @param {File} file - CSV or Excel file
   * @param {Object} options - Import options
   * @returns {Promise<Object>} Import result
   */
  async importProducts(file, options = {}) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      Object.keys(options).forEach(key => {
        formData.append(key, options[key]);
      });

      const response = await api.post('/products/import/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  // BARCODE OPERATIONS

  /**
   * Generate barcode for product
   * @param {string} productId - Product ID
   * @param {Object} options - Barcode generation options
   * @returns {Promise<Object>} Barcode data
   */
  async generateBarcode(productId, options = {}) {
    try {
      const response = await api.post(`/products/${productId}/barcode/`, options);
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  /**
   * Update product barcode
   * @param {string} productId - Product ID
   * @param {string} barcode - New barcode
   * @returns {Promise<Object>} Updated product
   */
  async updateBarcode(productId, barcode) {
    return this.patchProduct(productId, { barcode });
  }

  // UTILITY METHODS

  /**
   * Check if product exists by SKU
   * @param {string} sku - Product SKU
   * @returns {Promise<boolean>} Whether product exists
   */
  async productExistsBySku(sku) {
    try {
      await this.getProductBySku(sku);
      return true;
    } catch (error) {
      if (error.message.includes('404') || error.message.includes('Not Found')) {
        return false;
      }
      throw error;
    }
  }

  /**
   * Get product stock level
   * @param {string} productId - Product ID
   * @returns {Promise<number>} Current stock level
   */
  async getProductStock(productId) {
    try {
      const product = await this.getProduct(productId);
      return product.stock || 0; // Fixed property name
    } catch (error) {
      this.handleError(error);
    }
  }

  /**
   * Check if product is in stock
   * @param {string} productId - Product ID
   * @param {number} requiredQuantity - Required quantity (default: 1)
   * @returns {Promise<boolean>} Whether product is in stock
   */
  async isInStock(productId, requiredQuantity = 1) {
    try {
      const stockLevel = await this.getProductStock(productId);
      return stockLevel >= requiredQuantity;
    } catch (error) {
      this.handleError(error);
    }
  }
}

// Create and export singleton instance
const productsApiService = new ProductsApiService();

export default productsApiService;