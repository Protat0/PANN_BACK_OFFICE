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
      const response = await promotionApiService.getAllPromotions()

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

      const response = await promotionApiService.getAllPromotions(params)

      if (response.success) {
        promotions.value = response.promotions || []
        pagination.value = response.pagination || pagination.value
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
      const result = await promotionApiService.deletePromotion(promotionId)
      return result
    } catch (err) {
      console.error('❌ Error deleting promotion:', err)
      throw err
    }
  }

  const deleteMultiplePromotions = async (promotionIds) => {
    try {
      const result = await promotionApiService.deleteMultiplePromotions(promotionIds)
      return result
    } catch (err) {
      console.error('❌ Error deleting multiple promotions:', err)
      throw err
    }
  }

  // ✅ ACTIVATION/DEACTIVATION OPERATIONS
  const activatePromotion = async (promotionId) => {
    try {
      const result = await promotionApiService.activatePromotion(promotionId)
      return result
    } catch (err) {
      console.error('❌ Error activating promotion:', err)
      throw err
    }
  }

  const deactivatePromotion = async (promotionId) => {
    try {
      const result = await promotionApiService.deactivatePromotion(promotionId)
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
        return null
    }

    const now = new Date()

    const applicablePromo = promotions.value.find(promo => {
        // Check if promotion is active and within date range
        const startDate = new Date(promo.start_date)
        const endDate = new Date(promo.end_date)

        if (promo.status !== 'active' || now < startDate || now > endDate) {
        return false
        }

        // Check if promotion applies to this product
        if (promo.target_type === 'all') {
        return true
        }

        if (promo.target_type === 'categories' && promo.target_ids) {
        const applies = promo.target_ids.includes(product.category_id)
        return applies
        }

        return false
    })

    return applicablePromo
    }

  const calculateDiscountedPrice = (originalPrice, promotion) => {
    if (!promotion || !originalPrice) return originalPrice

    let discounted = originalPrice

    if (promotion.discount_type === 'percentage') {
      discounted = originalPrice * (1 - promotion.discount_value / 100)
    } else if (promotion.discount_type === 'fixed_amount') {
      discounted = Math.max(0, originalPrice - promotion.discount_value)
    }

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