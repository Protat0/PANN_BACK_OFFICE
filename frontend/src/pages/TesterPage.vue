<template>
  <div class="container-fluid pt-4 pb-4">
    <div class="card card-theme">
      <div class="card-header">
        <h4 class="mb-0 text-primary">🧪 Product Data Test</h4>
      </div>
      
      <div class="card-body">
        <!-- Loading State -->
        <div v-if="loading" class="text-center py-4">
          <div class="spinner-border text-accent" role="status"></div>
          <p class="mt-2">Fetching product data...</p>
        </div>

        <!-- Error Display -->
        <div v-if="error" class="alert alert-danger">
          <strong>❌ Error:</strong> {{ error }}
        </div>

        <!-- Product Display -->
        <div v-if="product && !loading">
          <h5>📦 Product Details:</h5>
          <div class="row">
            <div class="col-md-6">
              <p><strong>Name:</strong> {{ product.product_name }}</p>
              <p><strong>SKU:</strong> {{ product.SKU }}</p>
              <p><strong>Category ID:</strong> <code>{{ product.category_id }}</code></p>
              <p><strong>Category Name:</strong> 
                <span :class="product.category_name ? 'text-success' : 'text-warning'">
                  {{ product.category_name || 'NOT ENRICHED' }}
                </span>
              </p>
            </div>
            <div class="col-md-6">
              <p><strong>Stock:</strong> {{ product.stock }}</p>
              <p><strong>Price:</strong> ₱{{ product.selling_price }}</p>
              <p><strong>Status:</strong> {{ product.status }}</p>
            </div>
          </div>
          
          <hr>
          <h6>🔍 Raw JSON:</h6>
          <pre class="bg-light p-3 rounded small">{{ JSON.stringify(product, null, 2) }}</pre>
        </div>

        <!-- Categories Display -->
        <div v-if="categories.length > 0 && !loading" class="mt-4">
          <h5>🏷️ Available Categories ({{ categories.length }}):</h5>
          <div class="row">
            <div v-for="category in categories" :key="category._id" class="col-md-4 mb-2">
              <div class="p-2 border rounded">
                <strong>{{ category.category_name }}</strong><br>
                <small class="text-muted">{{ category._id }}</small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import productsApiService from '@/services/apiProducts.js'
import categoryApiService from '@/services/apiCategory.js'
import { api } from '@/services/api.js'

export default {
  name: 'TesterPage',
  setup() {
    const loading = ref(true)
    const error = ref(null)
    const product = ref(null)
    const categories = ref([])
    
    const fetchTestData = async () => {
      try {
        loading.value = true
        console.log('🔍 Starting test data fetch...')
        
        // Step 1: Test different category endpoints
        console.log('📋 Testing category endpoints...')
        try {
          // Test 1: Try getAllCategories method
          console.log('🧪 Test 1: Trying getAllCategories...')
          if (categoryApiService.getAllCategories) {
            categories.value = await categoryApiService.getAllCategories()
            console.log('✅ getAllCategories worked:', categories.value.length, 'categories')
          } else {
            console.log('❌ getAllCategories method not found')
          }
          
          // Test 2: Try CategoryData as fallback
          if (categories.value.length === 0) {
            console.log('🧪 Test 2: Trying CategoryData fallback...')
            const categoryResponse = await categoryApiService.CategoryData()
            console.log('📋 CategoryData response:', categoryResponse)
            
            if (Array.isArray(categoryResponse)) {
              categories.value = categoryResponse
            } else if (categoryResponse.categories) {
              categories.value = categoryResponse.categories
            } else {
              categories.value = categoryResponse || []
            }
            console.log('✅ CategoryData result:', categories.value.length, 'categories')
          }
          
          // Test 3: Direct API call as last resort
          if (categories.value.length === 0) {
            console.log('🧪 Test 3: Trying direct API call...')
            const directResponse = await api.get('/category/')
            console.log('📋 Direct API response:', directResponse.data)
            categories.value = directResponse.data || []
          }
          
        } catch (categoryError) {
          console.error('❌ All category fetch methods failed:', categoryError)
          categories.value = []
        }
        
        // Step 2: Fetch products
        console.log('📦 Fetching products...')
        const productsResponse = await productsApiService.getProducts()
        console.log('📦 Products API response structure:', {
          hasResults: !!productsResponse.results,
          isArray: Array.isArray(productsResponse),
          hasProducts: !!productsResponse.products,
          keys: Object.keys(productsResponse)
        })
        
        let products = []
        if (productsResponse.results) {
          products = productsResponse.results
        } else if (Array.isArray(productsResponse)) {
          products = productsResponse
        } else {
          products = productsResponse.products || []
        }
        
        console.log(`📦 Found ${products.length} products`)
        
        if (products.length > 0) {
          // Get the first product
          product.value = products[0]
          console.log('🎯 Selected product for testing:', {
            name: product.value.product_name,
            id: product.value._id,
            category_id: product.value.category_id,
            has_category_name: !!product.value.category_name
          })
          
          // Step 3: Manual enrichment test
          console.log('🔄 Testing manual category enrichment...')
          if (product.value.category_id && categories.value.length > 0) {
            console.log('🔍 Looking for category ID:', product.value.category_id)
            console.log('🔍 Available categories:', categories.value.map(c => ({
              id: c._id,
              name: c.category_name
            })))
            
            const matchingCategory = categories.value.find(cat => cat._id === product.value.category_id)
            if (matchingCategory) {
              product.value.category_name = matchingCategory.category_name
              console.log('✅ Successfully enriched with category name:', matchingCategory.category_name)
            } else {
              console.log('❌ No matching category found!')
              console.log('   Product category_id:', product.value.category_id, typeof product.value.category_id)
              console.log('   Available category IDs:', categories.value.map(c => `${c._id} (${typeof c._id})`))
            }
          } else {
            console.log('⚠️ Cannot enrich: missing category_id or no categories available')
          }
          
          // Step 4: Test the enrichProductsWithCategoryInfo method
          console.log('🧪 Testing enrichProductsWithCategoryInfo method...')
          try {
            const enrichedProducts = await productsApiService.enrichProductsWithCategoryInfo([product.value])
            console.log('✅ enrichProductsWithCategoryInfo result:', enrichedProducts[0])
            if (enrichedProducts[0]?.category_name) {
              product.value = enrichedProducts[0]
            }
          } catch (enrichError) {
            console.log('❌ enrichProductsWithCategoryInfo failed:', enrichError.message)
          }
          
        } else {
          console.log('❌ No products found')
        }
        
      } catch (err) {
        console.error('❌ Test fetch error:', err)
        error.value = err.message
      } finally {
        loading.value = false
      }
    }
    
    onMounted(() => {
      fetchTestData()
    })
    
    return {
      loading,
      error,
      product,
      categories
    }
  }
}
</script>

<style scoped>
.card {
  max-width: 1200px;
  margin: 0 auto;
}

pre {
  max-height: 300px;
  overflow-y: auto;
  font-size: 12px;
}

.text-success {
  color: #28a745 !important;
}

.text-warning {
  color: #ffc107 !important;
}
</style>