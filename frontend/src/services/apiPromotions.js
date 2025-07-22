import { api } from './api.js';

class PromotionsApiService {
  // Helper method to handle errors
  handleError(error) {
    const message = error.response?.data?.error || 
                   error.response?.data?.message || 
                   error.message || 
                   'An unexpected error occurred';
    throw new Error(message);
  }

  /**
   * Get all promotions with optional parameters
   * @param {Object} params - Query parameters (include_deleted, etc.)
   * @returns {Promise<Object>} Promotions list
   */
  async PromotionData(params = {}) {
    try {
      console.log('🔍 PromotionData called with params:', params);
      
      // Build URL with query parameters
      let url = '/promotions/';
      
      const queryParams = new URLSearchParams();
      
      // Add include_deleted parameter
      if (params.include_deleted !== undefined) {
        queryParams.append('include_deleted', params.include_deleted.toString());
      }
      
      // Add cache buster if present
      if (params._t) {
        queryParams.append('_t', params._t.toString());
      }
      
      if (queryParams.toString()) {
        url += '?' + queryParams.toString();
      }
      
      console.log('🔍 Making API call to:', url);
      
      const response = await api.get(url);
      
      console.log('🔍 API response status:', response.status);
      console.log('🔍 API response data length:', response.data?.length);
      
      // Check for deleted promotions in the response
      if (response.data && Array.isArray(response.data)) {
        const deletedPromos = response.data.filter(p => p.isDeleted === true);
        const activePromos = response.data.filter(p => p.isDeleted !== true);
        
        console.log('🔍 Response analysis:');
        console.log(`  - Total promotions: ${response.data.length}`);
        console.log(`  - Active promotions: ${activePromos.length}`);
        console.log(`  - Deleted promotions: ${deletedPromos.length}`);
        
        if (deletedPromos.length > 0) {
          console.log('🔍 Deleted promotions found:');
          deletedPromos.forEach(p => {
            console.log(`  - "${p.promotion_name}" (${p._id})`);
          });
        }
      }
      
      return response.data;
      
    } catch (error) {
      console.error('❌ Error fetching promotion data:', error);
      this.handleError(error);
    }
  }

  async AddPromotionData(params = {}) {
    try {
      console.log('This API call is making a new promotion');
      
      const promotionData = {
        promotion_name: params.promotion_name,
        discount_type: params.discount_type,
        discount_value: params.discount_value,  
        applicable_products: params.applicable_products || [],  
        start_date: params.start_date,
        end_date: params.end_date,
        status: params.status || 'active',
      };

      const response = await api.post('/promotions/', promotionData);

      console.log('Promotion created successfully:', response.data);

      return response.data;

    } catch (error) {
      console.error(`Error creating Promotion ${params.promotion_name}:`, error);
      this.handleError(error);
    }
  }
  
  async UpdatePromotionData(params = {}) {
    try {
      console.log('This API call is updating a promotion');

      const updatePromotion = {
        promotion_name: params.promotion_name,
        discount_type: params.discount_type,
        discount_value: params.discount_value,  
        applicable_products: params.applicable_products || [],  
        start_date: params.start_date,
        end_date: params.end_date,
        status: params.status || 'active',
      };

      // Remove undefined values
      Object.keys(updatePromotion).forEach(key => {
        if (updatePromotion[key] === undefined) {
          delete updatePromotion[key];
        }
      });

      console.log('Sending updated data:', updatePromotion);
      const response = await api.put(`/promotions/${params.id}/`, updatePromotion);

      console.log('Promotion updated successfully:', response.data);
      return response.data;

    } catch (error) {
      console.error(`Error updating Promotion ${params.promotion_name}:`, error);
      this.handleError(error);
    }
  }

  async debugPromotionById(promotionId) {
    try {
      console.log(`🔍 DEBUG: Testing promotion ID: ${promotionId}`);
      
      // Test 1: Try to GET the specific promotion first
      try {
        console.log(`🔍 Step 1: GET /promotions/${promotionId}/`);
        const getResponse = await api.get(`/promotion/${promotionId}/`);
        console.log('✅ GET Success:', getResponse.data);
        return { exists: true, data: getResponse.data };
      } catch (getError) {
        console.log('❌ GET Failed:', getError.response?.status, getError.response?.data);
        
        if (getError.response?.status === 404) {
          console.log('❌ Promotion does not exist');
          return { exists: false, error: 'Promotion not found' };
        }
        
        return { exists: false, error: getError.message };
      }
      
    } catch (error) {
      console.error('❌ Debug error:', error);
      return { exists: false, error: error.message };
    }
  }

  // Updated SoftDeletePromotion with debug
  async SoftDeletePromotion(params = {}) {
    try {
      console.log('🗑️ Soft deleting promotion:', params);
      
      if (!params.id) {
        throw new Error('Promotion ID is required for deletion');
      }
      
      // SKIP THE DEBUG CHECK - the delete works fine
      console.log(`🗑️ Deleting promotion with ID: ${params.id}`);
      
      const response = await api.delete(`/promotions/${params.id}/`);
      
      console.log('✅ Promotion has been soft deleted:', response.data);
      return response.data;

    } catch (error) {
      console.error(`❌ Error soft deleting promotion ${params.promotion_name}:`, error);
      
      if (error.response?.status === 404) {
        throw new Error(`Promotion with ID ${params.id} not found. It may have already been deleted or the ID is invalid.`);
      }
      
      this.handleError(error);
    }
  }

  async HardDeletePromotion(params = {}) {
    try {
      console.log('💀 This API call is for hard deleting');
      
      if (!params.id) {
        throw new Error('Promotion ID is required for hard deletion');
      }
      
      const response = await api.delete(`/promotions/${params.id}/hard-delete/`);
      console.log('✅ Promotion has been hard deleted:', response.data);
      return response.data;

    } catch (error) {
      console.error(`❌ Error hard deleting Promotion ${params.promotion_name}:`, error);
      this.handleError(error);
    }
  }

  async RestorePromotion(params = {}) {
    try {
      console.log('🔄 This API call is for restoring');
      
      if (!params.id) {
        throw new Error('Promotion ID is required for restoration');
      }
      
      const response = await api.post(`/promotions/${params.id}/restore/`, {});
      console.log('✅ Promotion has been restored:', response.data);
      return response.data;

    } catch (error) {
      console.error(`❌ Error restoring Promotion ${params.promotion_name}:`, error);
      this.handleError(error);
    }
  }
}

// Fix the export to match the class name
const promotionsApiService = new PromotionsApiService();
export default promotionsApiService;

export { PromotionsApiService };