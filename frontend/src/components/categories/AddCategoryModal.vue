<template>
  <!-- Modal -->
  <div class="modal fade" id="addCategoryModal" tabindex="-1" aria-labelledby="addCategoryModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <!-- Modal Header -->
        <div class="modal-header">
          <h5 class="modal-title text-primary-dark fw-bold" id="addCategoryModalLabel">
            <Package :size="20" class="me-2" />
            {{ isEditMode ? 'Edit Category' : 'Add New Category' }}
          </h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>

        <!-- Modal Body -->
        <div class="modal-body">
          <form @submit.prevent="handleSubmit">
            <!-- Category Name -->
            <div class="mb-3">
              <label for="categoryName" class="form-label text-tertiary-dark fw-semibold">
                Category Name <span class="text-danger">*</span>
              </label>
              <input 
                type="text" 
                class="form-control" 
                id="categoryName"
                v-model="formData.category_name"
                placeholder="Enter category name (e.g., Noodles)"
                required
              />
              <div class="form-text text-tertiary-medium">
                This will be the main category name displayed to users
              </div>
            </div>

            <!-- Description -->
            <div class="mb-3">
              <label for="description" class="form-label text-tertiary-dark fw-semibold">
                Description
              </label>
              <textarea 
                class="form-control" 
                id="description"
                v-model="formData.description"
                rows="3"
                placeholder="Enter category description (e.g., Different Types of Noodles for the business)"
              ></textarea>
              <div class="form-text text-tertiary-medium">
                Optional description to explain what products belong in this category
              </div>
            </div>

            <!-- Status -->
            <div class="mb-3">
              <label for="status" class="form-label text-tertiary-dark fw-semibold">
                Status <span class="text-danger">*</span>
              </label>
              <select 
                class="form-select" 
                id="status"
                v-model="formData.status"
                required
              >
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
              </select>
              <div class="form-text text-tertiary-medium">
                Active categories will be visible to users
              </div>
            </div>

            <!-- Sub-Categories Section -->
            <div class="mb-4">
              <div class="d-flex justify-content-between align-items-center mb-3">
                <label class="form-label text-tertiary-dark fw-semibold mb-0">
                  Sub-Categories
                </label>
                <button 
                  type="button" 
                  class="btn btn-add btn-sm btn-with-icon-sm"
                  @click="addSubCategory"
                >
                  <Plus :size="14" />
                  Add Sub-Category
                </button>
              </div>
              
              <!-- Sub-Category List -->
              <div v-if="formData.sub_categories.length > 0" class="sub-categories-list">
                <div 
                  v-for="(subCategory, index) in formData.sub_categories" 
                  :key="index"
                  class="sub-category-item card mb-2"
                >
                  <div class="card-body py-2">
                    <div class="row g-2 align-items-center">
                      <div class="col-10">
                        <input 
                          type="text" 
                          class="form-control form-control-sm" 
                          v-model="subCategory.name"
                          placeholder="Sub-category name"
                        />
                      </div>
                      <div class="col-2 text-end">
                        <button 
                          type="button" 
                          class="btn btn-delete btn-xs btn-icon-only"
                          @click="removeSubCategory(index)"
                        >
                          <Trash2 :size="12" />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Empty State -->
              <div v-else class="text-center py-3 bg-neutral-light rounded">
                <Package :size="24" class="text-tertiary-medium mb-2" />
                <p class="text-tertiary-medium mb-0 small">
                  No sub-categories added yet. Click "Add Sub-Category" to create one.
                </p>
              </div>
            </div>

            <!-- Category Image Upload (Optional) -->
            <div class="mb-3">
              <label class="form-label text-tertiary-dark fw-semibold">
                Category Image
              </label>
              <div class="category-image-upload">
                <div class="image-preview-container bg-neutral-light rounded p-4 text-center">
                  <div v-if="!imagePreview" class="image-placeholder">
                    <Package :size="48" class="text-tertiary-medium mb-2" />
                    <p class="text-tertiary-medium mb-2">Upload category image</p>
                    <input 
                      type="file" 
                      class="form-control" 
                      accept="image/*"
                      @change="handleImageUpload"
                      ref="imageInput"
                    />
                  </div>
                  <div v-else class="image-preview">
                    <img :src="imagePreview" alt="Category preview" class="img-fluid rounded mb-2" style="max-height: 120px;" />
                    <br>
                    <button 
                      type="button" 
                      class="btn btn-cancel btn-xs"
                      @click="removeImage"
                    >
                      Remove Image
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </form>
        </div>

        <!-- Modal Footer -->
        <div class="modal-footer">
          <button type="button" class="btn btn-cancel btn-sm" data-bs-dismiss="modal">
            Cancel
          </button>
          <button 
            type="button" 
            class="btn btn-save btn-sm btn-with-icon-sm"
            @click="handleSubmit"
            :disabled="!isFormValid"
          >
            <Save :size="14" />
            {{ isEditMode ? 'Update Category' : 'Create Category' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { 
  Package,
  Plus,
  Trash2,
  Save
} from 'lucide-vue-next'

export default {
  name: 'AddCategoryModal',
  components: {
    Package,
    Plus,
    Trash2,
    Save
  },
  data() {
    return {
      isEditMode: false,
      editingCategoryId: null,
      formData: {
        category_name: '',
        description: '',
        status: 'active',
        sub_categories: []
      },
      imagePreview: null
    }
  },
  computed: {
    isFormValid() {
      return this.formData.category_name.trim() !== '' && this.formData.status !== ''
    }
  },
  methods: {
    addSubCategory() {
      this.formData.sub_categories.push({
        name: ''
      })
    },
    
    removeSubCategory(index) {
      this.formData.sub_categories.splice(index, 1)
    },
    
    handleImageUpload(event) {
      const file = event.target.files[0]
      if (file) {
        const reader = new FileReader()
        reader.onload = (e) => {
          this.imagePreview = e.target.result
        }
        reader.readAsDataURL(file)
      }
    },
    
    removeImage() {
      this.imagePreview = null
      if (this.$refs.imageInput) {
        this.$refs.imageInput.value = ''
      }
    },
    
    handleSubmit() {
      if (!this.isFormValid) return
      
      // Prepare the data structure based on the collection
      const categoryData = {
        category_name: this.formData.category_name,
        description: this.formData.description,
        status: this.formData.status,
        last_updated: new Date().toISOString(),
        sub_categories: this.formData.sub_categories.filter(sub => sub.name.trim() !== '')
      }
      
      // Add date_created only for new categories
      if (!this.isEditMode) {
        categoryData.date_created = new Date().toISOString()
      }
      
      console.log(`${this.isEditMode ? 'Update' : 'Create'} category data:`, categoryData)
      
      if (this.isEditMode) {
        // TODO: Integrate with update API
        // Example: await categoriesApi.updateCategory(this.editingCategoryId, categoryData)
        console.log('Updating category with ID:', this.editingCategoryId)
        alert('Category updated successfully!')
      } else {
        // TODO: Integrate with create API
        // Example: await categoriesApi.createCategory(categoryData)
        alert('Category created successfully!')
      }
      
      this.resetForm()
      this.closeModal()
    },
    
    // Method to open modal in add mode
    openAddMode() {
      console.log('openAddMode called')
      this.isEditMode = false
      this.editingCategoryId = null
      this.resetForm()
      
      // Try to show modal with a slight delay to ensure DOM is ready
      this.$nextTick(() => {
        this.showModal()
      })
    },
    
    // Method to open modal in edit mode
    openEditMode(categoryData) {
      this.isEditMode = true
      this.editingCategoryId = categoryData._id || categoryData.id
      
      // Populate form with existing data
      this.formData = {
        category_name: categoryData.category_name || '',
        description: categoryData.description || '',
        status: categoryData.status || 'active',
        sub_categories: categoryData.sub_categories ? [...categoryData.sub_categories] : []
      }
      
      // Handle existing image if available
      if (categoryData.image_url) {
        this.imagePreview = categoryData.image_url
      }
      
      this.showModal()
    },
    
    // Show modal
    showModal() {
      const modalElement = document.getElementById('addCategoryModal')
      if (modalElement) {
        // Check if Bootstrap is available
        if (typeof bootstrap !== 'undefined') {
          const modal = new bootstrap.Modal(modalElement)
          modal.show()
        } else {
          console.error('Bootstrap is not available')
        }
      } else {
        console.error('Modal element not found')
      }
    },
    
    // Close modal
    closeModal() {
      const modal = bootstrap.Modal.getInstance(document.getElementById('addCategoryModal'))
      if (modal) {
        modal.hide()
      }
    },
    
    resetForm() {
      this.isEditMode = false
      this.editingCategoryId = null
      this.formData = {
        category_name: '',
        description: '',
        status: 'active',
        sub_categories: []
      }
      this.imagePreview = null
      if (this.$refs.imageInput) {
        this.$refs.imageInput.value = ''
      }
    }
  }
}
</script>

<style scoped>
.text-primary-dark {
  color: var(--primary-dark) !important;
}

.text-tertiary-dark {
  color: var(--tertiary-dark) !important;
}

.text-tertiary-medium {
  color: var(--tertiary-medium) !important;
}

.bg-neutral-light {
  background-color: var(--neutral-light) !important;
}

/* Modal styling */
.modal-content {
  border-radius: 0.75rem;
  border: 1px solid var(--neutral);
}

.modal-header {
  border-bottom: 1px solid var(--neutral-light);
  background-color: var(--neutral-light);
}

.modal-footer {
  border-top: 1px solid var(--neutral-light);
  background-color: var(--neutral-light);
}

/* Form styling */
.form-control:focus,
.form-select:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 0.2rem rgba(115, 146, 226, 0.25);
}

/* Sub-category items */
.sub-category-item {
  border: 1px solid var(--neutral-light);
  border-radius: 0.5rem;
}

.sub-category-item .card-body {
  background-color: var(--neutral-light);
}

/* Image upload styling */
.category-image-upload {
  border: 2px dashed var(--neutral);
  border-radius: 0.75rem;
  transition: border-color 0.3s ease;
}

.category-image-upload:hover {
  border-color: var(--primary);
}

.image-preview-container {
  min-height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Button disabled state */
.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>