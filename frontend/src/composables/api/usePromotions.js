// composables/promotions/usePromotions.js
import { ref, computed } from 'vue'
import promotionApiService from '@/services/apiPromotions'
import { useToast } from '@/composables/ui/useToast'

export function usePromotions() {
  const { success: showSuccess, error: showError } = useToast()
  
  // State
  const promotions = ref([])
  const loading = ref(false)
  const error = ref(null)
  const selectedPromotions = ref([]) // ✅ Added for selection management
  
  const pagination = ref({
    current_page: 1,
    total_pages: 1,
    total_items: 0,
    items_per_page: 20
  })
  
  const filters = ref({
    discountType: 'all',
    status: 'all'
  })
  
  const searchQuery = ref('')

  // ✅ EXISTING METHOD - Preserved as-is
  const fetchActivePromotions = async () => {
    loading.value = true
    error.value = null
    try {
      console.log('📦 Fetching active promotions...')
      const response = await promotionApiService.getAllPromotions()
      console.log('📦 Fetched promotions response:', response)
      
      if (response.success && response.promotions) {
        // Filter only active promotions
        const now = new Date()
        promotions.value = response.promotions.filter(p => {
          const isActive = p.status === 'active'
          const startDate = new Date(p.start_date)
          const endDate = new Date(p.end_date)
          const isInDateRange = now >= startDate && now <= endDate
          
          return isActive && isInDateRange
        })
        console.log('✅ Active promotions:', promotions.value)
      } else {
        promotions.value = []
        console.warn('⚠️ No promotions found in response')
      }
      
      return promotions.value
    } catch (err) {
      console.error('❌ Error fetching promotions:', err)
      error.value = err.message
      promotions.value = []
      showError('Failed to load promotions')
      return []
    } finally {
      loading.value = false
    }
  }

  // ✅ NEW METHOD - For admin panel with filters
  const fetchPromotions = async () => {
    try {
      loading.value = true
      error.value = null
      
      const params = {
        page: pagination.value.current_page,
        limit: pagination.value.items_per_page
      }
      
      if (filters.value.discountType !== 'all') {
        params.discount_type = filters.value.discountType
      }
      if (filters.value.status !== 'all') {
        params.status = filters.value.status
      }
      if (searchQuery.value.trim()) {
        params.search_query = searchQuery.value.trim()
      }
      
      console.log('📦 Fetching promotions with params:', params)
      const response = await promotionApiService.getAllPromotions(params)
      console.log('📦 Response:', response)
      
      if (response.success) {
        promotions.value = response.promotions || []
        pagination.value = response.pagination || pagination.value
        console.log('✅ Loaded promotions:', promotions.value.length)
      } else {
        error.value = response.message || 'Failed to load promotions'
        showError(error.value)
      }
    } catch (err) {
      console.error('❌ Error fetching promotions:', err)
      error.value = err.message
      showError('Failed to load promotions')
    } finally {
      loading.value = false
    }
  }

  // ✅ DELETE OPERATIONS
  const deletePromotion = async (promotionId) => {
    try {
      console.log('🗑️ Deleting promotion:', promotionId)
      const result = await promotionApiService.deletePromotion(promotionId)
      console.log('✅ Delete result:', result)
      return result
    } catch (err) {
      console.error('❌ Error deleting promotion:', err)
      throw err
    }
  }

  const deleteMultiplePromotions = async (promotionIds) => {
    try {
      console.log('🗑️ Deleting multiple promotions:', promotionIds)
      const result = await promotionApiService.deleteMultiplePromotions(promotionIds)
      console.log('✅ Bulk delete result:', result)
      return result
    } catch (err) {
      console.error('❌ Error deleting multiple promotions:', err)
      throw err
    }
  }

  // ✅ ACTIVATION/DEACTIVATION OPERATIONS
  const activatePromotion = async (promotionId) => {
    try {
      console.log('▶️ Activating promotion:', promotionId)
      const result = await promotionApiService.activatePromotion(promotionId)
      console.log('✅ Activation result:', result)
      return result
    } catch (err) {
      console.error('❌ Error activating promotion:', err)
      throw err
    }
  }

  const deactivatePromotion = async (promotionId) => {
    try {
      console.log('⏸️ Deactivating promotion:', promotionId)
      const result = await promotionApiService.deactivatePromotion(promotionId)
      console.log('✅ Deactivation result:', result)
      return result
    } catch (err) {
      console.error('❌ Error deactivating promotion:', err)
      throw err
    }
  }

  // ✅ FILTER & SEARCH MANAGEMENT
  const setFilters = (newFilters) => {
    filters.value = { ...filters.value, ...newFilters }
    pagination.value.current_page = 1 // Reset to first page
  }

  const setSearchQuery = (query) => {
    searchQuery.value = query
    pagination.value.current_page = 1 // Reset to first page
  }

  const setPage = (page) => {
    pagination.value.current_page = page
  }

  const clearSelection = () => {
    selectedPromotions.value = []
  }

  // ✅ EXISTING METHODS - Preserved as-is
    const getApplicablePromotion = (product) => {
    if (!product || !promotions.value.length) {
        console.log('🔍 No product or no promotions available')
        return null
    }

    // ✅ ADD THIS: Check what the product actually has
    console.log('🔍 Product being checked:', {
        product_name: product.product_name,
        category_id: product.category_id,
        category_name: product.category_name,
        full_product: product
    })

    const now = new Date()

    const applicablePromo = promotions.value.find(promo => {
        console.log('🔍 Checking promotion:', promo.promotion_name, {
        status: promo.status,
        target_type: promo.target_type,
        target_ids: promo.target_ids,
        product_category_id: product.category_id
        })

        // Check if promotion is active and within date range
        const startDate = new Date(promo.start_date)
        const endDate = new Date(promo.end_date)
        
        if (promo.status !== 'active' || now < startDate || now > endDate) {
        console.log('❌ Promotion not active or outside date range')
        return false
        }

        // Check if promotion applies to this product
        if (promo.target_type === 'all') {
        console.log('✅ Promotion applies to all products')
        return true
        }

        if (promo.target_type === 'categories' && promo.target_ids) {
        const applies = promo.target_ids.includes(product.category_id)
        console.log(`${applies ? '✅' : '❌'} Category match:`, {
            target_ids: promo.target_ids,
            product_category_id: product.category_id,
            applies
        })
        return applies
        }

        console.log('❌ Promotion does not apply')
        return false
    })

    if (applicablePromo) {
        console.log('🎉 Found applicable promotion:', applicablePromo.promotion_name)
    } else {
        console.log('ℹ️ No applicable promotion found for this product')
    }

    return applicablePromo
    }

  const calculateDiscountedPrice = (originalPrice, promotion) => {
    if (!promotion || !originalPrice) return originalPrice

    console.log('💰 Calculating discount:', {
      originalPrice,
      type: promotion.discount_type,
      value: promotion.discount_value
    })

    let discounted = originalPrice

    if (promotion.discount_type === 'percentage') {
      discounted = originalPrice * (1 - promotion.discount_value / 100)
    } else if (promotion.discount_type === 'fixed_amount') {
      discounted = Math.max(0, originalPrice - promotion.discount_value)
    }

    console.log('💰 Discounted price:', discounted)
    return discounted
  }

  const formatDiscount = (promotion) => {
    if (!promotion) return ''
    
    if (promotion.discount_type === 'percentage') {
      return `${promotion.discount_value}% OFF`
    }
    if (promotion.discount_type === 'fixed_amount') {
      return `₱${promotion.discount_value} OFF`
    }
    if (promotion.discount_type === 'buy_x_get_y') {
      return 'BOGO'
    }
    return ''
  }

  // ✅ Computed
  const hasSelectedPromotions = computed(() => selectedPromotions.value.length > 0)

  return {
    // State
    promotions,
    loading,
    error,
    pagination,
    filters,
    searchQuery,
    selectedPromotions,
    
    // Computed
    hasSelectedPromotions,
    
    // Methods - Admin Panel (NEW)
    fetchPromotions,
    deletePromotion,
    deleteMultiplePromotions,
    activatePromotion,
    deactivatePromotion,
    setFilters,
    setSearchQuery,
    setPage,
    clearSelection,
    
    // Methods - Customer-facing (EXISTING - Preserved)
    fetchActivePromotions,
    getApplicablePromotion,
    calculateDiscountedPrice,
    formatDiscount
  }
}