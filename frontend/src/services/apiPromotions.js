// services/apiPromotion.js - Updated with data transformation
import { api } from './api.js';

class PromotionApiService {
  handleResponse(response) {
    console.log("🔍 Handling response:", response);
    console.log("🔍 Response data:", response.data);
    
    if (!response || !response.data) {
      console.warn("⚠️ No response data");
      return {
        success: false,
        message: "No response from server"
      };
    }
    
    return response.data;
  }

  handleError(error) {
    console.error("❌ Full error object:", error);
    console.error("❌ Error response:", error.response);
    console.error("❌ Error response data:", error.response?.data);
    console.error("❌ Error response status:", error.response?.status);
    console.error("❌ Error message:", error.message);
    
    if (error.response) {
      const { data, status } = error.response;
      
      // ✅ NEW: Extract and log all error details
      let errorMessage = data.message || data.detail || `Request failed with status ${status}`;
      let errorDetails = [];
      
      // Log detailed validation errors
      if (data.errors) {
        console.error("❌ Validation errors:", data.errors);
        if (Array.isArray(data.errors)) {
          errorDetails = data.errors;
          // Join array errors into a readable message
          if (data.errors.length > 0) {
            errorMessage += '\n' + data.errors.join('\n');
          }
        }
      }
      if (data.message) {
        console.error("❌ Backend message:", data.message);
      }
      if (data.detail) {
        console.error("❌ Backend detail:", data.detail);
      }
      
      // ✅ Return proper error object with full details
      return {
        success: false,
        message: errorMessage,
        errors: errorDetails,
        status
      };
    }
    
    // ✅ Return proper error object for non-response errors
    return {
      success: false,
      message: error.message || "An unknown error occurred",
      errors: []
    };
  }

  // Data transformation methods
  transformToBackend(frontendData) {
    console.log('🔄 Transforming frontend data to backend format:', frontendData)
    
    let targetType = 'all';
    let targetIds = [];
    
    if (frontendData.affected_category) {
      if (frontendData.affected_category === 'all') {
        targetType = 'all';
        targetIds = [];
      } else {
        targetType = 'categories';
        targetIds = [frontendData.affected_category];
      }
    }

    console.log('📤 Target mapping:', {
      affected_category: frontendData.affected_category,
      target_type: targetType,
      target_ids: targetIds
    })

    // ✅ FIX: Changed formData → frontendData and formendData → frontendData
    const backendData = {
      name: frontendData.promotion_name,
      type: frontendData.discount_type,
      discount_value: parseFloat(frontendData.discount_value),
      target_type: targetType,
      target_ids: targetIds,
      start_date: frontendData.start_date,  // ✅ Fixed: was formData.end_date
      end_date: frontendData.end_date,      // ✅ Fixed: was formData.end_date
      description: frontendData.description || '',
      usage_limit: frontendData.usage_limit ? parseInt(frontendData.usage_limit) : null, // ✅ Fixed: was formendData
      status: frontendData.status
    };
    
    console.log('📦 Final backend data:', backendData)
    return backendData;
  }

  transformToFrontend(backendData) {
    console.log('🔄 Transforming backend data to frontend format:', backendData)
    
    // ✅ UPDATED: Reverse transformation for editing
    let affectedCategory = 'all';
    
    if (backendData.target_type === 'categories' && backendData.target_ids?.length > 0) {
      // Use the first target_id (which is already the real MongoDB category ID)
      affectedCategory = backendData.target_ids[0];
    }

    return {
      promotion_id: backendData.promotion_id || backendData._id,
      promotion_name: backendData.name,
      discount_type: backendData.type,
      discount_value: backendData.discount_value,
      start_date: backendData.start_date,
      end_date: backendData.end_date,
      status: backendData.status,
      is_deleted: backendData.isDeleted || false,
      last_updated: backendData.updated_at || backendData.last_updated,
      target_type: backendData.target_type,
      target_ids: backendData.target_ids || [], // ✅ ADD THIS LINE
      usage_limit: backendData.usage_limit,
      current_usage: backendData.current_usage || 0,
      description: backendData.description || '',
      affected_category: affectedCategory // ✅ Will be real MongoDB ID
    };
  }

  // PROMOTION CRUD OPERATIONS

  async getAllPromotions(params = {}) {
    try {
      console.log("Fetching all promotions with params:", params);
      
      // Transform frontend filter params to backend format
      const backendParams = { ...params };
      if (params.discount_type && params.discount_type !== 'all') {
        backendParams.type = params.discount_type;
        delete backendParams.discount_type;
      }
      
      const response = await api.get('/promotions/', { params: backendParams });
      const data = this.handleResponse(response);
      
      console.log("Response data:", data);
      console.log("Response data keys:", Object.keys(data));
      
      // Check if we have promotions to transform
      if (data.promotions && Array.isArray(data.promotions)) {
        // Transform each promotion - make sure transformToFrontend exists
        const transformedPromotions = data.promotions.map(promotion => {
          try {
            return this.transformToFrontend(promotion);
          } catch (transformError) {
            console.warn('Transform error for promotion:', promotion, transformError);
            // Return the original promotion if transform fails
            return promotion;
          }
        });
        
        return {
          success: data.success || true,
          promotions: transformedPromotions,
          pagination: data.pagination || {
            current_page: 1,
            total_pages: 1,
            total_items: data.promotions.length,
            items_per_page: params.limit || 20
          }
        };
      }
      
      // If no promotions, return empty array
      return {
        success: data.success || true,
        promotions: [],
        pagination: data.pagination || {
          current_page: 1,
          total_pages: 1,
          total_items: 0,
          items_per_page: params.limit || 20
        }
      };
    } catch (error) {
      console.error("Error fetching promotions:", error);
      this.handleError(error);
    }
  }

  async getPromotionById(promotionId) {
    try {
      console.log(`Fetching promotion with ID: ${promotionId}`);
      const response = await api.get(`/promotions/${promotionId}/`);
      const data = this.handleResponse(response);
      
      if (data.success && data.promotion) {
        return {
          success: true,
          promotion: this.transformToFrontend(data.promotion)
        };
      }
      return data;
    } catch (error) {
      console.error(`Error fetching promotion ${promotionId}:`, error);
      this.handleError(error);
    }
  }

  async createPromotion(promotionData) {
    try {
      console.log("📤 Creating new promotion with frontend data:", promotionData);
      const backendData = this.transformToBackend(promotionData);
      console.log("📦 Transformed backend data:", backendData);
      console.log("📦 Backend data stringified:", JSON.stringify(backendData, null, 2));
      
      const response = await api.post('/promotions/', backendData);
      console.log("✅ API response:", response);
      
      const data = this.handleResponse(response);
      console.log("✅ Handled response data:", data);
      
      if (data && data.promotion) {
        return {
          success: true,
          promotion: this.transformToFrontend(data.promotion),
          message: data.message || "Promotion created successfully"
        };
      }
      
      return {
        success: true,
        promotion: data,
        message: "Promotion created successfully"
      };
    } catch (error) {
      console.error("❌ Error creating promotion:", error);
      console.error("❌ Error response:", error.response?.data);
      console.error("❌ Error response errors:", error.response?.data?.errors);
      
      // ✅ FIX: Always return an object, never undefined
      const errorResult = this.handleError(error);
      return errorResult || {
        success: false,
        message: "Failed to create promotion",
        errors: []
      };
    }
  }

  async updatePromotion(promotionId, promotionData) {
    try {
      console.log(`Updating promotion ${promotionId}:`, promotionData);
      const backendData = this.transformToBackend(promotionData);
      const response = await api.put(`/promotions/${promotionId}/`, backendData);
      const data = this.handleResponse(response);
      
      if (data.success && data.promotion) {
        return {
          success: true,
          promotion: this.transformToFrontend(data.promotion),
          message: data.message
        };
      }
      return data;
    } catch (error) {
      console.error(`Error updating promotion ${promotionId}:`, error);
      this.handleError(error);
    }
  }

  async deletePromotion(promotionId) {
    try {
      console.log(`Deleting promotion with ID: ${promotionId}`);
      const response = await api.delete(`/promotions/${promotionId}/`);
      return this.handleResponse(response);
    } catch (error) {
      console.error(`Error deleting promotion ${promotionId}:`, error);
      this.handleError(error);
    }
  }

  async deleteMultiplePromotions(promotionIds) {
    try {
      console.log("Deleting multiple promotions:", promotionIds);
      const deletePromises = promotionIds.map(id => this.deletePromotion(id));
      const results = await Promise.allSettled(deletePromises);
      
      return {
        success: true,
        results: results.map((result, index) => ({
          promotion_id: promotionIds[index],
          success: result.status === 'fulfilled',
          error: result.status === 'rejected' ? result.reason.message : null
        }))
      };
    } catch (error) {
      console.error("Error in bulk delete promotions:", error);
      this.handleError(error);
    }
  }

  // SEARCH AND FILTERING
  async searchPromotions(searchQuery, filters = {}) {
    try {
      console.log("Searching promotions:", searchQuery, filters);
      const params = {
        search_query: searchQuery,
        ...filters
      };
      
      // Transform filter params
      if (filters.discount_type && filters.discount_type !== 'all') {
        params.type = filters.discount_type;
        delete params.discount_type;
      }
      
      const response = await api.get('/promotions/search/', { params });
      const data = this.handleResponse(response);
      
      return {
        success: data.success,
        promotions: data.promotions?.map(p => this.transformToFrontend(p)) || []
      };
    } catch (error) {
      console.error("Error searching promotions:", error);
      this.handleError(error);
    }
  }

  async getActivePromotions() {
    try {
      console.log("Fetching active promotions");
      const response = await api.get('/promotions/active/');
      const data = this.handleResponse(response);
      
      return {
        success: data.success,
        promotions: data.promotions?.map(p => this.transformToFrontend(p)) || []
      };
    } catch (error) {
      console.error("Error fetching active promotions:", error);
      this.handleError(error);
    }
  }

  // PROMOTION LIFECYCLE
  async activatePromotion(promotionId) {
    try {
      console.log(`Activating promotion ${promotionId}`);
      const response = await api.post(`/promotions/${promotionId}/activate/`);
      return this.handleResponse(response);
    } catch (error) {
      console.error(`Error activating promotion ${promotionId}:`, error);
      this.handleError(error);
    }
  }

  async deactivatePromotion(promotionId) {
    try {
      console.log(`Deactivating promotion ${promotionId}`);
      const response = await api.post(`/promotions/${promotionId}/deactivate/`);
      return this.handleResponse(response);
    } catch (error) {
      console.error(`Error deactivating promotion ${promotionId}:`, error);
      this.handleError(error);
    }
  }

  // EXPORT
  async exportPromotions(filters = {}, format = 'csv') {
    try {
      console.log("Exporting promotions data", { filters, format });
      
      // For now, export the current data as JSON
      // You can implement proper export endpoint later
      const data = await this.getAllPromotions(filters);
      const exportData = {
        promotions: data.promotions,
        exported_at: new Date().toISOString(),
        format: format
      };
      
      return JSON.stringify(exportData, null, 2);
    } catch (error) {
      console.error("Error exporting promotions:", error);
      this.handleError(error);
    }
  }
}

const promotionApiService = new PromotionApiService();
export default promotionApiService;