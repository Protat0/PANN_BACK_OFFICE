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
                      <div class="col-8">
                        <input 
                          type="text" 
                          class="form-control form-control-sm" 
                          v-model="subCategory.name"
                          placeholder="Sub-category name"
                        />
                      </div>
                      <div class="col-2">
                        <input 
                          type="text" 
                          class="form-control form-control-sm" 
                          v-model="subCategory.description"
                          placeholder="Description (optional)"
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
                <p class="text-tertiary-medium mb-0 small">
                  Note: A default "None" subcategory will be automatically created.
                </p>
              </div>
            </div>

            <!-- Category Image Upload (Optional) -->
            <div class="mb-3">
                <label class="form-label text-tertiary-dark fw-semibold">
                  Category Image
                </label>
                
                <!-- Image Preview (if exists) -->
                <div v-if="imagePreview" class="mb-3">
                  <div class="image-preview-container bg-neutral-light rounded p-3 text-center">
                    <img 
                      :src="imagePreview" 
                      alt="Category preview" 
                      class="img-fluid rounded mb-2" 
                      style="max-height: 120px;" 
                    />
                    <br>
                    <small v-if="hasExistingImage" class="text-muted">Current image</small>
                    <small v-else class="text-success">New image selected</small>
                    <br>
                    <button 
                      type="button" 
                      class="btn btn-outline-danger btn-xs mt-2"
                      @click="removeImage"
                    >
                      <Trash2 :size="12" class="me-1" />
                      Remove Image
                    </button>
                  </div>
                </div>
                
                <!-- File Input (always visible) -->
                <div class="category-image-upload">
                  <div class="image-upload-container bg-neutral-light rounded p-4 text-center">
                    <Package :size="32" class="text-tertiary-medium mb-2" />
                    <p class="text-tertiary-medium mb-2">
                      {{ imagePreview ? 'Change image' : 'Upload category image' }}
                    </p>
                    <input 
                      type="file" 
                      class="form-control" 
                      accept="image/*"
                      @change="handleImageUpload"
                      ref="imageInput"
                      :key="'imageInput-' + (isEditMode ? editingCategoryId : 'new')"
                    />
                    <small class="text-muted mt-2 d-block">
                      Maximum file size: 5MB. Supported formats: JPEG, PNG, GIF, WebP
                    </small>
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
            :disabled="!isFormValid || isLoading"
          >
            <div v-if="isLoading" class="spinner-border spinner-border-sm me-2" role="status"></div>
            <Save v-else :size="14" />
            {{ isEditMode ? 'Update Category' : 'Create Category' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useCategories } from '@/composables/api/useCategories'

export default {
  name: 'AddCategoryModal',
  setup() {
    const {
      createCategory,
      updateCategory,
      loading,
      validateCategoryData
    } = useCategories()

    return {
      createCategory,
      updateCategory,
      loading,
      validateCategoryData
    }
  },
  
  data() {
    return {
      isEditMode: false,
      editingCategoryId: null,
      isLoading: false,
      formData: {
        category_name: '',
        description: '',
        status: 'active',
        sub_categories: []
      },
      imagePreview: null,
      selectedImageFile: null, 
      hasExistingImage: false
    }
  },
  
  computed: {
    isFormValid() {
      const validation = this.validateCategoryData(this.formData)
      return validation.isValid && !this.isLoading
    }
  },
  
  methods: {
    addSubCategory() {
      this.formData.sub_categories.push({
        name: '',
        description: ''
      })
    },
    
    removeSubCategory(index) {
      this.formData.sub_categories.splice(index, 1)
    },
    
    handleImageUpload(event) {
      const file = event.target.files[0]
      if (!file) {
        return
      }

      // Store the actual file
      this.selectedImageFile = file

      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        console.error('File too large:', file.size)
        alert('Image size should be less than 5MB')
        this.clearImageData()
        return
      }

      // Validate file type
      const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
      if (!validTypes.includes(file.type)) {
        console.error('Invalid file type:', file.type)
        alert('Please select a valid image file (JPEG, PNG, GIF, WebP)')
        this.clearImageData()
        return
      }

      const reader = new FileReader()

      reader.onload = (e) => {
        this.imagePreview = e.target.result
        this.hasExistingImage = false // This is a new upload
      }

      reader.onerror = (e) => {
        console.error('FileReader error:', e)
        alert('Error reading the image file')
        this.clearImageData()
      }

      reader.readAsDataURL(file)
    },

    removeImage() {
      this.clearImageData()
    },
    
    clearImageData() {
      this.imagePreview = null
      this.selectedImageFile = null
      this.hasExistingImage = false
    },
    
    async handleSubmit() {
      if (!this.isFormValid || this.isLoading) return
      
      this.isLoading = true
      
      try {
        // Validate form data using composable
        const validation = this.validateCategoryData(this.formData)
        if (!validation.isValid) {
          alert('Please fix the following errors:\n' + validation.errors.join('\n'))
          return
        }

        // Prepare the category data for the refactored structure
        const categoryData = {
          category_name: this.formData.category_name.trim(),
          description: this.formData.description.trim(),
          status: this.formData.status,
          sub_categories: this.formData.sub_categories
            .filter(sub => sub.name.trim() !== '')
            .map(sub => ({
              name: sub.name.trim(),
              description: sub.description?.trim() || ''
            }))
        }
        
        // Handle image data
        if (this.selectedImageFile && this.imagePreview) {
          // New image uploaded
          categoryData.image_filename = this.selectedImageFile.name
          categoryData.image_size = this.selectedImageFile.size
          categoryData.image_type = this.selectedImageFile.type
          categoryData.image_url = this.imagePreview
          categoryData.image_uploaded_at = new Date().toISOString()
        }
        else if (this.hasExistingImage && this.imagePreview) {
          // Existing image kept (in edit mode) - don't modify image fields
        }
        else if (this.isEditMode && !this.imagePreview) {
          // Image was removed in edit mode
          categoryData.image_url = null
          categoryData.image_filename = null
          categoryData.image_size = null
          categoryData.image_type = null
          categoryData.image_uploaded_at = null
        }
        
        // Call the appropriate composable method
        if (this.isEditMode) {
          await this.updateCategory(this.editingCategoryId, categoryData)
          this.$emit('category-updated', { 
            _id: this.editingCategoryId, 
            ...categoryData 
          })
        } else {
          const newCategory = await this.createCategory(categoryData)
          this.$emit('category-added', newCategory.category)
        }
        
        this.resetForm()
        this.closeModal()
        
      } catch (error) {
        console.error('Error in handleSubmit:', error)
        const action = this.isEditMode ? 'update' : 'create'
        alert(`Failed to ${action} category. Please try again.\n\nError: ${error.message || 'Unknown error'}`)
      } finally {
        this.isLoading = false
      }
    },

    openAddMode() {
      this.isEditMode = false
      this.editingCategoryId = null
      this.resetForm()

      this.$nextTick(() => {
        this.showModal()
      })
    },

    openEditMode(categoryData) {
      this.isEditMode = true
      this.editingCategoryId = categoryData._id || categoryData.id

      // Populate form with existing data
      this.formData = {
        category_name: categoryData.category_name || '',
        description: categoryData.description || '',
        status: categoryData.status || 'active',
        sub_categories: this.processSubCategories(categoryData.sub_categories || [])
      }

      // Handle existing image
      if (categoryData.image_url) {
        this.imagePreview = categoryData.image_url
        this.hasExistingImage = true
        this.selectedImageFile = null
      } else {
        this.clearImageData()
      }

      this.showModal()
    },
    
    processSubCategories(subCategories) {
      if (!Array.isArray(subCategories)) return []
      
      return subCategories
        .filter(sub => sub.name !== 'None') // Filter out the default "None" subcategory
        .map(sub => {
          if (typeof sub === 'string') {
            return { name: sub, description: '' }
          } else if (sub && typeof sub === 'object') {
            return {
              name: sub.name || '',
              description: sub.description || ''
            }
          }
          return { name: '', description: '' }
        })
    },

    showModal() {
      const modalElement = document.getElementById('addCategoryModal')
      if (modalElement) {
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
    
    closeModal() {
      try {
        const modal = bootstrap.Modal.getInstance(document.getElementById('addCategoryModal'))
        if (modal) {
          modal.hide()
        }
      } catch (error) {
        console.error('Error closing modal:', error)
      }
    },
    
    resetForm() {
      this.isEditMode = false
      this.editingCategoryId = null
      this.isLoading = false
      this.formData = {
        category_name: '',
        description: '',
        status: 'active',
        sub_categories: []
      }
      this.clearImageData()
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

/* Loading spinner */
.spinner-border-sm {
  width: 0.875rem;
  height: 0.875rem;
}
</style>