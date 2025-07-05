import { api } from './api.js';

class CategoryApiService {
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
   * @param {Object} params - Query parameters (page, limit, search, category, include_deleted, etc.)
   * @returns {Promise<Object>} Products list with pagination info
   */
 
  async CategoryData(params = {}) {
    try {
        console.log("This API call is getting all Category");
        const response = await api.get('/category/dataview', { params });
        
        // Return the data from the response
        return response.data;
        
    } catch (error) {
        console.error("Error fetching all category data:", error);
        throw error; // Re-throw so calling code can handle it
    }
  }

    async AddCategoryData(params = {}) {
        try {
            console.log(`This API call is making a new category called ${params.category_name}`);
            
            // Prepare the category data payload
            const categoryData = {
                category_name: params.category_name,
                description: params.description || '',
                status: params.status || 'active',
                sub_categories: params.sub_categories || []
            };
            
            console.log('Sending category data:', categoryData);
            
            // Send POST request with the category data
            const response = await api.post('/category/', categoryData);
            
            console.log('Category created successfully:', response.data);
            return response.data;
            
        } catch (error) {
            console.error(`Error creating category ${params.category_name}:`, error);
            throw error; // Re-throw so calling code can handle it
        }
    }

 async FindCategoryData(params = {}) {
    try {
        console.log(`This API call is getting ${params.id} Category`);
        const response = await api.get(`/category/${params.id}`);
        
        // Return the data from the response
        return response.data;
        
    } catch (error) {
        console.error(`Error fetching specific category ${params.id} data:`, error);
        throw error; // Re-throw so calling code can handle it
    }
  }

    async FindProdcategory(params = {}) {
        try {
            console.log(`This API call will fetch the products under the category`);
            const response = await api.get(`/category/${params.id}`);
            
            // Build a map of product name to subcategory info
            const productToSubcategory = {};
            const product_list = [];
            
            for (const subcategory of response.data.category.sub_categories) {
                for (const productName of subcategory.products) {
                    // Map each product name to its subcategory
                    productToSubcategory[productName] = {
                        name: subcategory.name,
                        id: subcategory._id || subcategory.name
                    };
                    product_list.push(productName);
                }
            }
            
            console.log('Product names from category:', product_list);
            console.log('Product to subcategory mapping:', productToSubcategory);
            
            // Get all products from the products API
            const prod_response = await api.get("/products/");
            console.log('All products from API:', prod_response.data);
            
            // Filter products and add subcategory information
            let complete_list = [];
            for (const product of prod_response.data) {
                // Check if this product's name exists in our category's product list
                if (product_list.includes(product.product_name)) {
                    // Get the subcategory info for this product
                    const subcategoryInfo = productToSubcategory[product.product_name];
                    
                    // Add the product with subcategory information
                    complete_list.push({
                        ...product,
                        subcategory: subcategoryInfo.name,
                        subcategory_name: subcategoryInfo.name,
                        subcategory_id: subcategoryInfo.id
                    });
                }
            }
            
            console.log('Filtered products with subcategory info:', complete_list);
            
            // Return the enhanced products
            return complete_list;
            
        } catch (error) {
            console.error(`Error fetching Product List`, error);
            throw error;
        }
    }

  async CategoryPageData(params = {}) {
      try{
        console.log("This API call is getting all the Different Category");
        const response = await api.get('/category');

        return response.data;

      }catch (error) {
          console.error("Error fetching all category data:", error);
          throw error; // Re-throw so calling code can handle it
      }
  }

  async ExportCategoryData(params = {}) {
        try {
            console.log('Exporting category data with params:', params);
            
            // Prepare query parameters
            const queryParams = {
                format: params.format || 'csv',
                include_sales_data: params.include_sales_data !== false, // Default to true
                ...params.date_filter && { 
                    start_date: params.date_filter.start_date,
                    end_date: params.date_filter.end_date,
                    frequency: params.date_filter.frequency || 'monthly'
                }
            };
            
            // Remove undefined values
            Object.keys(queryParams).forEach(key => 
                queryParams[key] === undefined && delete queryParams[key]
            );
            
            console.log('Sending export request with params:', queryParams);
            
            const response = await api.get('/category/export', {
                params: queryParams,
                responseType: params.format === 'json' ? 'json' : 'blob' // Handle different response types
            });
            
            return response.data;
            
        } catch (error) {
            console.error('Error exporting category data:', error);
            throw error;
        }
    }

    // Alternative method for direct download
    async DownloadCategoryExport(params = {}) {
        try {
            console.log('Downloading category export with params:', params);
            
            const queryParams = {
                format: params.format || 'csv',
                include_sales_data: params.include_sales_data !== false,
                download: true, // Add download flag
                ...params.date_filter && { 
                    start_date: params.date_filter.start_date,
                    end_date: params.date_filter.end_date,
                    frequency: params.date_filter.frequency || 'monthly'
                }
            };
            
            // Clean up undefined values
            Object.keys(queryParams).forEach(key => 
                queryParams[key] === undefined && delete queryParams[key]
            );
            
            const response = await api.get('/category/export', {
                params: queryParams,
                responseType: 'blob' // Always blob for downloads
            });
            
            // Create download link
            const blob = new Blob([response.data], { 
                type: params.format === 'json' ? 'application/json' : 'text/csv' 
            });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `categories_export_${new Date().toISOString().split('T')[0]}.${params.format || 'csv'}`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            return { success: true, message: 'Download completed' };
            
        } catch (error) {
            console.error('Error downloading category export:', error);
            throw error;
        }
    }

    // Get export statistics
    async GetExportStats() {
        try {
            console.log('Fetching export statistics...');
            const response = await api.get('/category/export/stats');
            return response.data;
        } catch (error) {
            console.error('Error fetching export stats:', error);
            throw error;
        }
    }

}

const categoryApiService = new CategoryApiService();
export default categoryApiService;

// Also export the class if needed for multiple instances
export { CategoryApiService };