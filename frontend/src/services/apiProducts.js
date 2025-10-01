// services/apiProducts.js - UPDATED VERSION WITH CATEGORY SERVICE REFERENCE
import { api } from './api.js';
import categoryApiService from './apiCategory.js'; // Import category service

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

  async getCategoryStats() {
    try {
      const response = await api.get('/category/stats/') 
      return this.handleResponse(response)
    } catch (error) {
      console.error('Error fetching category stats:', error)
      this.handleError(error)
    }
  }

  // PRODUCT CRUD OPERATIONS
  
  /**
   * Get all products with optional query parameters
   * @param {Object} params - Query parameters (page, limit, search, category, include_deleted, etc.)
   * @returns {Promise<Object>} Products list with pagination info
   */
  async getProducts(filters = {}) {
    try {
      const response = await api.get('/products/', { params: filters });
      return this.handleResponse(response); // Make sure this returns the correct structure
    } catch (error) {
      this.handleError(error);
    }
  }

  /**
   * Get a specific product by ID
   * @param {string} productId - Product ID
   * @param {boolean} includeDeleted - Whether to include soft-deleted products
   * @returns {Promise<Object>} Product details
   */
  async getProduct(productId, includeDeleted = false) {
    try {
      const params = includeDeleted ? { include_deleted: true } : {};
      const response = await api.get(`/products/${productId}`, { params });
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  /**
   * Get a product by SKU
   * @param {string} sku - Product SKU
   * @param {boolean} includeDeleted - Whether to include soft-deleted products
   * @returns {Promise<Object>} Product details
   */
  async getProductBySku(sku, includeDeleted = false) {
    try {
      const params = includeDeleted ? { include_deleted: true } : {};
      const response = await api.get(`/products/sku/${sku}`, { params });
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
      const response = await api.patch(`/products/${productId}/update/`, productData);
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  /**
   * Delete a product (soft delete by default)
   * @param {string} productId - Product ID
   * @param {boolean} hardDelete - Whether to permanently delete (hard delete)
   * @returns {Promise<void>}
   */
  async deleteProduct(productId, hardDelete = false) {
    try {
      const params = hardDelete ? { hard_delete: 'true' } : {};
      const response = await api.delete(`/products/${productId}/`, { params });
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  /**
   * Restore a soft-deleted product
   * @param {string} productId - Product ID
   * @returns {Promise<Object>} Restored product
   */
  async restoreProduct(productId) {
    try {
      const response = await api.post(`/products/${productId}/restore/`);
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  /**
   * Get all soft-deleted products
   * @returns {Promise<Array>} Deleted products
   */
  async getDeletedProducts() {
    try {
      const response = await api.get('/products/deleted/');
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
   * Bulk update stock for multiple products - FIXED URL
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
   * Get stock history for a product - FIXED URL
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

  // TEMPLATE DOWNLOAD METHODS - UPDATED TO USE CSV PRIMARILY

  /**
   * Download import template for client-side generation - SIMPLIFIED VERSION
   * @param {string} fileType - Template format ('csv' or 'xlsx')
   * @returns {void} Downloads template file directly
   */
  downloadImportTemplateClient(fileType = 'csv') {
    try {
      console.log('Generating client-side import template:', fileType);
      
      // Define template headers matching backend expectations
      const templateHeaders = [
        'product_name',
        'SKU', 
        'category',
        'supplier',
        'stock',
        'low_stock_threshold',
        'cost_price',
        'selling_price',
        'tax_percentage',
        'unit',
        'expiry_date'
      ];

      if (fileType.toLowerCase() === 'csv') {
        this._downloadSimpleCSVTemplate(templateHeaders);
      } else if (fileType.toLowerCase() === 'xlsx') {
        this._downloadSimpleExcelTemplate(templateHeaders);
      } else {
        throw new Error(`Unsupported file type: ${fileType}`);
      }
      
      console.log('Template download initiated successfully');
    } catch (error) {
      console.error('Error downloading template:', error);
      this.handleError(error);
    }
  }

  /**
   * Simple CSV template without sample data
   * @param {Array<string>} headers - Column headers
   * @private
   */
  _downloadSimpleCSVTemplate(headers) {
    try {
      // Create simple CSV content with just headers and empty rows
      const csvRows = [
        // Headers row
        headers.join(','),
        
        // Empty rows for user input (no defaults)
        ...Array(20).fill().map(() => 
          headers.map(() => '').join(',')
        )
      ];

      // Join all rows
      const csvContent = csvRows.join('\n');

      // Create and download the file with UTF-8 BOM for Excel compatibility
      const BOM = '\uFEFF';
      const blob = new Blob([BOM + csvContent], { 
        type: 'text/csv;charset=utf-8;' 
      });
      
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);
      link.setAttribute('href', url);
      link.setAttribute('download', 'product_import_template.csv');
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
      console.log('Simple CSV template downloaded successfully');
    } catch (error) {
      console.error('Error creating simple CSV template:', error);
      throw error;
    }
  }

  /**
   * Simple Excel template
   * @param {Array<string>} headers - Column headers
   * @private
   */
  _downloadSimpleExcelTemplate(headers) {
    try {
      if (typeof window !== 'undefined' && window.XLSX) {
        const worksheetData = [
          headers,
          ...Array(20).fill().map(() => new Array(headers.length).fill(''))
        ];
        
        const worksheet = window.XLSX.utils.aoa_to_sheet(worksheetData);
        
        // Set column widths
        worksheet['!cols'] = [
          { wch: 25 }, // product_name
          { wch: 15 }, // SKU
          { wch: 12 }, // category
          { wch: 15 }, // supplier
          { wch: 8 },  // stock
          { wch: 18 }, // low_stock_threshold
          { wch: 12 }, // cost_price
          { wch: 12 }, // selling_price
          { wch: 15 }, // tax_percentage
          { wch: 8 },  // unit
          { wch: 12 }  // expiry_date
        ];
        
        const workbook = window.XLSX.utils.book_new();
        window.XLSX.utils.book_append_sheet(workbook, worksheet, 'Products');
        
        window.XLSX.writeFile(workbook, 'product_import_template.xlsx');
        
      } else {
        // Fallback to CSV if XLSX not available
        this._downloadSimpleCSVTemplate(headers);
      }
    } catch (error) {
      console.error('Excel template creation failed, using CSV:', error);
      this._downloadSimpleCSVTemplate(headers);
    }
  }

  /**
   * Adjust stock for sale - NEW METHOD
   * @param {string} productId - Product ID
   * @param {number} quantitySold - Quantity sold
   * @returns {Promise<Object>} Updated stock info
   */
  async adjustStockForSale(productId, quantitySold) {
    try {
      const response = await api.post(`/products/${productId}/stock/adjust/`, {
        quantity_sold: parseInt(quantitySold)
      });
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  /**
   * Restock product from supplier - NEW METHOD
   * @param {string} productId - Product ID
   * @param {number} quantityReceived - Quantity received
   * @param {Object} supplierInfo - Supplier information
   * @returns {Promise<Object>} Updated stock info
   */
  async restockProduct(productId, quantityReceived, supplierInfo = null) {
    try {
      const payload = {
        quantity_received: parseInt(quantityReceived)
      };
      
      if (supplierInfo) {
        payload.supplier_info = supplierInfo;
      }
      
      const response = await api.post(`/products/${productId}/restock/`, payload);
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
   * Get products by category - USES CATEGORY SERVICE
   * @param {string} categoryId - Category ID
   * @param {Object} params - Additional query parameters
   * @returns {Promise<Object>} Products in category
   */
  async getProductsByCategory(categoryId, params = {}) {
    try {
      // First verify category exists and is active using category service
      const category = await categoryApiService.getCategoryById(categoryId);
      if (!category || category.status !== 'active') {
        throw new Error('Category not found or inactive');
      }

      // Now get products for this category
      const response = await api.get(`/products/category/${categoryId}/`, { params });
      const productsData = this.handleResponse(response);

      // Enhance with category info
      return {
        ...productsData,
        category_info: {
          id: category._id,
          name: category.category_name,
          description: category.description,
          status: category.status
        }
      };
    } catch (error) {
      this.handleError(error);
    }
  }

  /**
   * Get products by subcategory - NEW METHOD USING CATEGORY SERVICE
   * @param {string} categoryId - Category ID
   * @param {string} subcategoryName - Subcategory name
   * @param {Object} params - Additional query parameters
   * @returns {Promise<Array>} Products in subcategory
   */
  async getProductsBySubcategory(categoryId, subcategoryName, params = {}) {
    try {
      // Use category service to get subcategories
      const subcategories = await categoryApiService.getSubcategories(categoryId);
      
      // Verify subcategory exists
      const subcategory = subcategories.find(sub => sub.name === subcategoryName);
      if (!subcategory) {
        throw new Error(`Subcategory '${subcategoryName}' not found in category`);
      }

      // Get products and filter by subcategory
      const response = await api.get(`/products/category/${categoryId}/`, { 
        params: { ...params, subcategory: subcategoryName } 
      });
      
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  /**
   * Update product's subcategory - NEW METHOD USING CATEGORY SERVICE
   * @param {string} productId - Product ID
   * @param {string} categoryId - Target category ID
   * @param {string} subcategoryName - Target subcategory name
   * @returns {Promise<Object>} Updated product
   */
  async updateProductSubcategory(productId, categoryId, subcategoryName) {
    try {
      // Use category service's ProductSubcategoryService functionality
      const response = await api.put(`/products/${productId}/subcategory/`, {
        category_id: categoryId,
        subcategory: subcategoryName
      });
      
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  /**
   * Move product to uncategorized - NEW METHOD
   * @param {string} productId - Product ID
   * @returns {Promise<Object>} Updated product
   */
  async moveProductToUncategorized(productId) {
    try {
      const response = await api.post(`/products/${productId}/move-to-uncategorized/`);
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

  // BULK OPERATIONS - COMPLETELY FIXED

  /**
   * Bulk create products - FINAL FIXED VERSION
   * @param {Array<Object>} productsData - Array of product data
   * @param {Object} options - Additional options (validation_only, etc.)
   * @returns {Promise<Object>} Bulk creation result
   */
  async bulkCreateProducts(productsData, options = {}) {
    try {
      console.log('=== BULK CREATE DEBUG START ===');
      console.log('Input products count:', productsData.length);
      console.log('Sample product (first):', productsData[0]);
      console.log('URL being called:', '/products/bulk-create/');
      
      // CRITICAL FIX: Based on your backend views, it expects { products: [...] }
      const payload = { 
        products: productsData
      };
      
      // Add validation option if requested
      if (options.validate_only) {
        payload.validate_only = options.validate_only;
      }
      
      console.log('Final payload structure:', {
        hasProducts: 'products' in payload,
        productsCount: payload.products.length,
        validateOnly: payload.validate_only || false
      });
      
      console.log('Making POST request...');
      const response = await api.post('/products/bulk-create/', payload);
      
      console.log('=== RESPONSE RECEIVED ===');
      console.log('Status:', response.status);
      console.log('Response data:', response.data);
      console.log('=== BULK CREATE DEBUG END ===');
      
      return this.handleResponse(response);
    } catch (error) {
      console.error('=== BULK CREATE ERROR ===');
      console.error('HTTP Status:', error.response?.status);
      console.error('Error data:', error.response?.data);
      console.error('Request URL:', error.config?.url);
      console.error('Request method:', error.config?.method);
      
      // Try to parse the request data to see what we actually sent
      try {
        const requestData = error.config?.data;
        if (typeof requestData === 'string') {
          console.error('Request payload:', JSON.parse(requestData));
        } else {
          console.error('Request payload:', requestData);
        }
      } catch (parseError) {
        console.error('Could not parse request data');
      }
      
      console.error('Full error object:', error);
      console.error('=== END ERROR DEBUG ===');
      
      this.handleError(error);
    }
  }

  /**
   * Validate bulk products without creating them - LOCAL VALIDATION
   * @param {Array<Object>} productsData - Array of product data
   * @returns {Promise<Object>} Validation result
   */
  async validateBulkProducts(productsData) {
    try {
      // Local validation since backend endpoint might not exist
      const validationErrors = [];
      
      // Get all categories for validation
      const categories = await categoryApiService.getAllCategories();
      const categoryNames = categories.map(c => c.category_name.toLowerCase());
      const categoryIds = categories.map(c => c._id);
      
      productsData.forEach((product, index) => {
        // Required fields validation
        if (!product.product_name || product.product_name.trim() === '') {
          validationErrors.push({
            index,
            field: 'product_name',
            error: 'Product name is required'
          });
        }
        
        // Category validation using category service data
        if (product.category) {
          const categoryLower = product.category.toLowerCase();
          const isValidCategoryName = categoryNames.includes(categoryLower);
          const isValidCategoryId = categoryIds.includes(product.category);
          
          if (!isValidCategoryName && !isValidCategoryId) {
            validationErrors.push({
              index,
              field: 'category',
              error: `Invalid category: ${product.category}`
            });
          }
        }
        
        // Numeric validation
        if (product.stock && isNaN(parseInt(product.stock))) {
          validationErrors.push({
            index,
            field: 'stock',
            error: 'Stock must be a number'
          });
        }
        
        if (product.cost_price && isNaN(parseFloat(product.cost_price))) {
          validationErrors.push({
            index,
            field: 'cost_price',
            error: 'Cost price must be a number'
          });
        }
        
        if (product.selling_price && isNaN(parseFloat(product.selling_price))) {
          validationErrors.push({
            index,
            field: 'selling_price',
            error: 'Selling price must be a number'
          });
        }
        
        // Business logic validation
        if (product.cost_price && product.selling_price && 
            parseFloat(product.cost_price) >= parseFloat(product.selling_price)) {
          validationErrors.push({
            index,
            field: 'selling_price',
            error: 'Selling price must be higher than cost price'
          });
        }
      });
      
      return {
        validation_only: true,
        total_products: productsData.length,
        valid_products: productsData.length - validationErrors.length,
        validation_errors: validationErrors
      };
    } catch (error) {
      this.handleError(error);
    }
  }

  // IMPORT/EXPORT OPERATIONS - FIXED URLS

  /**
   * Export products data - FIXED URL
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
   * Import products from file - FIXED URL
   * @param {File} file - CSV or Excel file
   * @param {Object} options - Import options (validate_only, etc.)
   * @returns {Promise<Object>} Import result
   */
  async importProducts(file, options = {}) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      // Add options to form data
      Object.keys(options).forEach(key => {
        formData.append(key, options[key]);
      });

      console.log('Uploading file for import:', file.name);
      
      const response = await api.post('/products/import/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          console.log(`Upload progress: ${percentCompleted}%`);
        }
      });
      
      return this.handleResponse(response);
    } catch (error) {
      console.error('Import error:', error.response?.data || error.message);
      this.handleError(error);
    }
  }

  /**
   * Download import template - FIXED URL
   * @param {string} format - Template format ('csv' or 'xlsx')
   * @returns {Promise<Blob>} Template file
   */
  async downloadImportTemplate(format = 'csv') {
    try {
      const response = await api.get('/products/import/template/', { 
        params: { format },
        responseType: 'blob'
      });
      
      return response.data;
    } catch (error) {
      this.handleError(error);
    }
  }

  // SYNCHRONIZATION METHODS - NEW

  /**
   * Sync products between local and cloud - NEW METHOD
   * @param {string} direction - 'to_cloud' or 'to_local'
   * @param {Array} products - Products to sync (for to_cloud)
   * @returns {Promise<Object>} Sync result
   */
  async syncProducts(direction = 'to_cloud', products = []) {
    try {
      const payload = {
        direction,
        ...(direction === 'to_cloud' && { products })
      };
      
      const response = await api.post('/products/sync/', payload);
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  /**
   * Get unsynced products - NEW METHOD
   * @param {string} source - 'local' or 'cloud'
   * @returns {Promise<Array>} Unsynced products
   */
  async getUnsyncedProducts(source = 'local') {
    try {
      const response = await api.get('/products/sync/unsynced/', {
        params: { source }
      });
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  /**
   * Get/Update sync status for a product - NEW METHOD
   * @param {string} productId - Product ID
   * @param {Object} updateData - Update data (optional)
   * @returns {Promise<Object>} Sync status
   */
  async syncStatus(productId, updateData = null) {
    try {
      if (updateData) {
        // Update sync status
        const response = await api.put(`/products/${productId}/sync/status/`, updateData);
        return this.handleResponse(response);
      } else {
        // Get sync status
        const response = await api.get(`/products/${productId}/sync/status/`);
        return this.handleResponse(response);
      }
    } catch (error) {
      this.handleError(error);
    }
  }

  // UTILITY METHODS

  /**
   * Check if product exists by SKU
   * @param {string} sku - Product SKU
   * @param {boolean} includeDeleted - Whether to include soft-deleted products
   * @returns {Promise<boolean>} Whether product exists
   */
  async productExistsBySku(sku, includeDeleted = false) {
    try {
      await this.getProductBySku(sku, includeDeleted);
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
      return product.stock || 0;
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

  /**
   * Check if product is deleted
   * @param {string} productId - Product ID
   * @returns {Promise<boolean>} Whether product is soft-deleted
   */
  async isProductDeleted(productId) {
    try {
      const product = await this.getProduct(productId, true); // Include deleted
      return product.isDeleted === true;
    } catch (error) {
      if (error.message.includes('404') || error.message.includes('Not Found')) {
        return false; // Product doesn't exist at all
      }
      throw error;
    }
  }

  // BATCH PROCESSING HELPERS

/**
  * Process products in batches to avoid overwhelming the server
  * @param {Array<Object>} products - Array of products to process
  * @param {Function} processFn - Function to process each batch
  * @param {number} batchSize - Size of each batch (default: 20)
  * @returns {Promise<Array>} Array of batch results
  */
 async processBatches(products, processFn, batchSize = 20) {
   const results = [];
   
   for (let i = 0; i < products.length; i += batchSize) {
     const batch = products.slice(i, i + batchSize);
     
     try {
       console.log(`Processing batch ${Math.floor(i/batchSize) + 1}/${Math.ceil(products.length/batchSize)}`);
       const batchResult = await processFn(batch);
       results.push({
         batchIndex: Math.floor(i/batchSize),
         success: true,
         result: batchResult
       });
       
       // Add small delay between batches to avoid overwhelming server
       await new Promise(resolve => setTimeout(resolve, 250));
       
     } catch (error) {
       console.error(`Error in batch ${Math.floor(i/batchSize) + 1}:`, error);
       results.push({
         batchIndex: Math.floor(i/batchSize),
         success: false,
         error: error.message
       });
     }
   }
   
   return results;
 }

 /**
  * Create products in batches - FIXED METHOD
  * @param {Array<Object>} products - Array of products to create
  * @param {number} batchSize - Size of each batch
  * @returns {Promise<Object>} Batch creation results
  */
 async createProductsInBatches(products, batchSize = 15) {
   const batchResults = await this.processBatches(
     products, 
     (batch) => this.bulkCreateProducts(batch),
     batchSize
   );
   
   // Aggregate results
   const successfulBatches = batchResults.filter(r => r.success);
   const totalSuccessful = successfulBatches
     .reduce((sum, r) => sum + (r.result?.results?.total_successful || 0), 0);
     
   const totalFailed = successfulBatches
     .reduce((sum, r) => sum + (r.result?.results?.total_failed || 0), 0);
   
   return {
     total_batches: batchResults.length,
     successful_batches: successfulBatches.length,
     failed_batches: batchResults.filter(r => !r.success).length,
     total_successful: totalSuccessful,
     total_failed: totalFailed,
     batch_details: batchResults
   };
 }

 // CATEGORY-RELATED HELPER METHODS (Using Category Service)

 /**
  * Get all categories for product assignment
  * @returns {Promise<Array>} Active categories
  */
 async getAvailableCategories() {
   try {
     // Use category service to get active categories
     return await categoryApiService.getActiveCategories();
   } catch (error) {
     console.error('Error fetching available categories:', error);
     return [];
   }
 }

 /**
  * Get subcategories for a specific category
  * @param {string} categoryId - Category ID
  * @returns {Promise<Array>} Subcategories
  */
 async getAvailableSubcategories(categoryId) {
   try {
     // Use category service to get subcategories
     return await categoryApiService.getSubcategories(categoryId);
   } catch (error) {
     console.error('Error fetching subcategories:', error);
     return [];
   }
 }

 /**
  * Validate category and subcategory before product creation/update
  * @param {string} categoryId - Category ID
  * @param {string} subcategoryName - Subcategory name (optional)
  * @returns {Promise<Object>} Validation result
  */
 async validateCategoryAssignment(categoryId, subcategoryName = null) {
   try {
     // Check if category exists and is active
     const category = await categoryApiService.getCategoryById(categoryId);
     if (!category) {
       return {
         isValid: false,
         error: 'Category not found'
       };
     }
     
     if (category.status !== 'active') {
       return {
         isValid: false,
         error: 'Category is not active'
       };
     }
     
     // If subcategory is specified, validate it exists
     if (subcategoryName) {
       const subcategories = await categoryApiService.getSubcategories(categoryId);
       const subcategoryExists = subcategories.some(sub => sub.name === subcategoryName);
       
       if (!subcategoryExists) {
         return {
           isValid: false,
           error: `Subcategory '${subcategoryName}' not found in category '${category.category_name}'`
         };
       }
     }
     
     return {
       isValid: true,
       category: category,
       subcategory: subcategoryName
     };
   } catch (error) {
     return {
       isValid: false,
       error: error.message || 'Category validation failed'
     };
   }
 }

 /**
  * Get category name by ID (helper for display purposes)
  * @param {string} categoryId - Category ID
  * @returns {Promise<string>} Category name
  */
 async getCategoryName(categoryId) {
   try {
     const category = await categoryApiService.getCategoryById(categoryId);
     return category ? category.category_name : 'Unknown Category';
   } catch (error) {
     console.error('Error fetching category name:', error);
     return 'Unknown Category';
   }
 }

 /**
  * Enrich products with category information
  * @param {Array<Object>} products - Array of products
  * @returns {Promise<Array>} Products with category details
  */
 async enrichProductsWithCategoryInfo(products) {
   try {
     // Get all categories once to avoid multiple API calls
     const allCategories = await categoryApiService.getAllCategories();
     const categoryMap = new Map(allCategories.map(cat => [cat._id, cat]));
     
     // Enrich each product with category info
     return products.map(product => {
       const category = categoryMap.get(product.category_id);
       return {
         ...product,
         category_name: category ? category.category_name : 'Unknown',
         category_status: category ? category.status : 'unknown',
         category_description: category ? category.description : ''
       };
     });
   } catch (error) {
     console.error('Error enriching products with category info:', error);
     // Return products without enrichment if error occurs
     return products;
   }
 }

 /**
  * Get products grouped by category
  * @param {Object} params - Query parameters
  * @returns {Promise<Object>} Products grouped by category
  */
 async getProductsGroupedByCategory(params = {}) {
   try {
     // Get all products
     const productsResponse = await this.getProducts(params);
     const products = productsResponse.data || productsResponse.products || [];
     
     // Get all categories
     const categories = await categoryApiService.getAllCategories();
     
     // Group products by category
     const grouped = {};
     
     // Initialize groups for each category
     categories.forEach(category => {
       grouped[category._id] = {
         category_id: category._id,
         category_name: category.category_name,
         category_description: category.description,
         category_status: category.status,
         products: [],
         product_count: 0
       };
     });
     
     // Add "Uncategorized" group
     grouped['uncategorized'] = {
       category_id: 'uncategorized',
       category_name: 'Uncategorized',
       category_description: 'Products without category assignment',
       category_status: 'active',
       products: [],
       product_count: 0
     };
     
     // Assign products to groups
     products.forEach(product => {
       const categoryId = product.category_id || 'uncategorized';
       if (grouped[categoryId]) {
         grouped[categoryId].products.push(product);
         grouped[categoryId].product_count++;
       } else {
         // If category doesn't exist in our list, add to uncategorized
         grouped['uncategorized'].products.push(product);
         grouped['uncategorized'].product_count++;
       }
     });
     
     // Convert to array and filter out empty categories if needed
     const groupedArray = Object.values(grouped);
     
     return {
       total_categories: groupedArray.length,
       total_products: products.length,
       groups: groupedArray,
       pagination: productsResponse.pagination || null
     };
   } catch (error) {
     this.handleError(error);
   }
 }
}

// Create and export singleton instance
const productsApiService = new ProductsApiService();

export default productsApiService;