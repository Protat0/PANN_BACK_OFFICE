<template>
  <div 
    class="modal fade" 
    id="importModal" 
    tabindex="-1" 
    aria-labelledby="importModalLabel" 
    aria-hidden="true"
    @hidden.bs.modal="onModalHidden"
    @shown.bs.modal="onModalShown"
  >
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <!-- Modal Header -->
        <div class="modal-header">
          <h5 class="modal-title" id="importModalLabel">
            <Upload :size="20" class="me-2" style="color: var(--primary);" />
            Import Products
          </h5>
          <button 
            type="button" 
            class="btn-close" 
            data-bs-dismiss="modal" 
            aria-label="Close"
          ></button>
        </div>

        <!-- Modal Body -->
        <div class="modal-body">
          <!-- Download Template Section -->
          <div class="mb-4">
            <h6 class="mb-3" style="color: var(--tertiary-dark);">
              Step 1: Download Template
            </h6>
            <div class="alert alert-info border-0" style="background-color: var(--info-light); color: var(--info-dark);">
              <AlertTriangle :size="16" class="me-2" />
              Download the template file to see the required format and column headers.
            </div>
            
            <div class="d-flex gap-2 flex-wrap">
              <button 
                type="button" 
                class="btn btn-export btn-sm btn-with-icon-sm"
                @click="downloadTemplate('csv')"
                :disabled="isDownloading || loading"
              >
                <FileSpreadsheet :size="14" />
                {{ isDownloading ? 'Downloading...' : 'Download CSV Template' }}
              </button>
              
              <button 
                type="button" 
                class="btn btn-export btn-sm btn-with-icon-sm"
                @click="downloadTemplate('xlsx')"
                :disabled="isDownloading || loading"
              >
                <FileSpreadsheet :size="14" />
                {{ isDownloading ? 'Downloading...' : 'Download Excel Template' }}
              </button>
            </div>
          </div>

          <!-- File Upload Section -->
          <div class="mb-4">
            <h6 class="mb-3" style="color: var(--tertiary-dark);">
              Step 2: Upload Your File
            </h6>
            
            <!-- File Input -->
            <div class="mb-3">
              <label for="importFile" class="form-label" style="color: var(--tertiary-medium);">
                Select CSV or Excel file
              </label>
              <input 
                type="file" 
                class="form-control" 
                id="importFile"
                ref="fileInput"
                @change="onFileSelected"
                accept=".csv,.xlsx,.xls"
                :disabled="isUploading || loading"
              >
              <div class="form-text" style="color: var(--tertiary-medium);">
                Supported formats: CSV, Excel (.xlsx, .xls) • Max file size: 10MB
              </div>
            </div>

            <!-- Selected File Info -->
            <div v-if="selectedFile" class="alert alert-success border-0" style="background-color: var(--success-light); color: var(--success-dark);">
              <Check :size="16" class="me-2" />
              <strong>Selected:</strong> {{ selectedFile.name }} 
              <small>({{ formatFileSize(selectedFile.size) }})</small>
            </div>

            <!-- File Validation Errors -->
            <div v-if="fileValidationError" class="alert alert-danger border-0" style="background-color: var(--error-light); color: var(--error-dark);">
              <AlertTriangle :size="16" class="me-2" />
              {{ fileValidationError }}
            </div>
          </div>

          <!-- Import Options -->
          <div class="mb-4">
            <h6 class="mb-3" style="color: var(--tertiary-dark);">
              Step 3: Import Options
            </h6>
            
            <div class="form-check mb-2">
              <input 
                class="form-check-input" 
                type="checkbox" 
                id="validateOnly"
                v-model="validateOnly"
                :disabled="loading"
              >
              <label class="form-check-label" for="validateOnly" style="color: var(--tertiary-medium);">
                Validate only (don't import, just check for errors)
              </label>
              <small class="form-text d-block mt-1" style="color: var(--tertiary-medium);">
                Use this option to check your file for errors before doing the actual import
              </small>
            </div>
            
            <div class="form-check mb-2">
              <input 
                class="form-check-input" 
                type="checkbox" 
                id="skipDuplicates"
                v-model="skipDuplicates"
                :disabled="validateOnly || loading"
              >
              <label class="form-check-label" for="skipDuplicates" style="color: var(--tertiary-medium);">
                Skip duplicate products (based on SKU)
              </label>
              <small class="form-text d-block mt-1" style="color: var(--tertiary-medium);">
                Products with existing SKUs will be skipped instead of causing errors
              </small>
            </div>

            <div class="form-check">
              <input 
                class="form-check-input" 
                type="checkbox" 
                id="updateExisting"
                v-model="updateExisting"
                :disabled="validateOnly || skipDuplicates || loading"
              >
              <label class="form-check-label" for="updateExisting" style="color: var(--tertiary-medium);">
                Update existing products
              </label>
              <small class="form-text d-block mt-1" style="color: var(--tertiary-medium);">
                Update products that already exist (based on SKU) instead of creating duplicates
              </small>
            </div>
          </div>

          <!-- Category Validation Info -->
          <div v-if="categories.length > 0" class="mb-4">
            <div class="alert alert-info border-0" style="background-color: var(--info-light); color: var(--info-dark);">
              <AlertTriangle :size="16" class="me-2" />
              <strong>Available Categories:</strong> 
              <span class="ms-2">{{ categories.map(c => c.category_name).join(', ') }}</span>
            </div>
          </div>

          <!-- Progress Bar -->
          <div v-if="isUploading || loading" class="mb-3">
            <div class="d-flex justify-content-between align-items-center mb-2">
              <small style="color: var(--tertiary-medium);">{{ uploadStatus }}</small>
              <small v-if="!loading" style="color: var(--tertiary-medium);">{{ uploadProgress }}%</small>
            </div>
            <div class="progress">
              <div 
                class="progress-bar" 
                role="progressbar" 
                :style="{ 
                  width: loading ? '100%' : uploadProgress + '%',
                  backgroundColor: uploadProgress === 100 ? 'var(--success)' : 'var(--primary)'
                }"
                :class="{ 'progress-bar-striped progress-bar-animated': loading }"
                :aria-valuenow="loading ? 100 : uploadProgress" 
                aria-valuemin="0" 
                aria-valuemax="100"
              ></div>
            </div>
          </div>

          <!-- Error Messages from useProducts -->
          <div v-if="error" class="alert alert-danger border-0" style="background-color: var(--error-light); color: var(--error-dark);">
            <AlertTriangle :size="16" class="me-2" />
            <strong>Error:</strong> {{ error }}
          </div>

          <!-- Success Message from useProducts -->
          <div v-if="successMessage && !importResults" class="alert alert-success border-0" style="background-color: var(--success-light); color: var(--success-dark);">
            <CheckCircle :size="16" class="me-2" />
            {{ successMessage }}
          </div>

          <!-- Results Section -->
          <div v-if="importResults" class="mt-4">
            <h6 class="mb-3" style="color: var(--tertiary-dark);">
              Import Results
            </h6>
            
            <!-- Success Results -->
            <div v-if="importResults.success" class="alert alert-success border-0" style="background-color: var(--success-light); color: var(--success-dark);">
              <CheckCircle :size="16" class="me-2" />
              <strong>{{ validateOnly ? 'Validation completed!' : 'Import completed successfully!' }}</strong>
              <ul class="mb-0 mt-2">
                <li>Total processed: {{ importResults.totalProcessed || 0 }}</li>
                <li v-if="!validateOnly">Successfully imported: {{ importResults.totalSuccessful || 0 }}</li>
                <li v-if="!validateOnly && importResults.totalSkipped > 0">Skipped (duplicates): {{ importResults.totalSkipped }}</li>
                <li v-if="importResults.totalFailed && importResults.totalFailed > 0">Failed: {{ importResults.totalFailed }}</li>
              </ul>
            </div>

            <!-- Error Results -->
            <div v-if="!importResults.success" class="alert alert-danger border-0" style="background-color: var(--error-light); color: var(--error-dark);">
              <AlertTriangle :size="16" class="me-2" />
              <strong>{{ validateOnly ? 'Validation failed:' : 'Import failed:' }}</strong> {{ importResults.error }}
              <ul v-if="importResults.totalProcessed > 0" class="mb-0 mt-2">
                <li>Total processed: {{ importResults.totalProcessed || 0 }}</li>
                <li v-if="!validateOnly">Successfully imported: {{ importResults.totalSuccessful || 0 }}</li>
                <li>Failed: {{ importResults.totalFailed || 0 }}</li>
              </ul>
            </div>

            <!-- Validation Results -->
            <div v-if="importResults.validationErrors && importResults.validationErrors.length > 0" class="mt-3">
              <div class="alert alert-warning border-0" style="background-color: var(--neutral-light); color: var(--tertiary-dark);">
                <AlertTriangle :size="16" class="me-2" />
                <strong>{{ validateOnly ? 'Validation Issues Found:' : 'Issues Found During Import:' }}</strong>
                <div class="mt-2" style="max-height: 200px; overflow-y: auto;">
                  <ul class="mb-0">
                    <li v-for="(error, index) in importResults.validationErrors.slice(0, 20)" :key="index">
                      Row {{ (error.row || error.index || index) + 1 }}: {{ error.error || error.message }}
                      <small v-if="error.field" class="text-muted d-block">Field: {{ error.field }}</small>
                    </li>
                    <li v-if="importResults.validationErrors.length > 20" class="text-muted">
                      ... and {{ importResults.validationErrors.length - 20 }} more issues
                    </li>
                  </ul>
                </div>
                <div v-if="!validateOnly && importResults.validationErrors.length > 0" class="mt-2">
                  <small class="text-muted">
                    💡 Try running validation first to see all issues before importing
                  </small>
                </div>
              </div>
            </div>

            <!-- Success Actions -->
            <div v-if="importResults.success && !validateOnly" class="mt-3">
              <div class="d-flex gap-2 flex-wrap">
                <button 
                  type="button" 
                  class="btn btn-export btn-sm"
                  @click="refreshProductList"
                  :disabled="loading"
                >
                  <RefreshCw :size="14" />
                  Refresh Product List
                </button>
                
                <button 
                  type="button" 
                  class="btn btn-view btn-sm"
                  @click="viewImportedProducts"
                  :disabled="loading"
                >
                  <Eye :size="14" />
                  View Imported Products
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Modal Footer -->
        <div class="modal-footer">
          <button 
            type="button" 
            class="btn btn-cancel btn-sm"
            data-bs-dismiss="modal"
            :disabled="isUploading || loading"
          >
            {{ (importResults?.success && !validateOnly) ? 'Close' : 'Cancel' }}
          </button>
          
          <button 
            v-if="!importResults?.success || validateOnly"
            type="button" 
            class="btn btn-submit btn-sm btn-with-icon-sm"
            @click="handleImport"
            :disabled="!canImport"
            :class="{ 'btn-loading': isUploading || loading }"
          >
            <Upload v-if="!isUploading && !loading" :size="14" />
            {{ getImportButtonText }}
          </button>

          <button 
            v-if="importResults?.success && !validateOnly"
            type="button" 
            class="btn btn-add btn-sm btn-with-icon-sm"
            @click="startNewImport"
          >
            <Plus :size="14" />
            Import Another File
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useProducts } from '@/composables/ui/products/useProducts'
import productsApiService from '@/services/apiProducts.js'

export default {
  name: 'ImportModal',
  emits: ['import-completed', 'import-failed', 'refresh-products'],
  
  setup(props, { emit }) {
    // Use the products composable for consistency
    const {
      categories,
      loading,
      error,
      successMessage,
      fetchCategories,
      handleImportSuccess,
      handleImportError,
      refreshData
    } = useProducts()

    // Local reactive state
    const selectedFile = ref(null)
    const validateOnly = ref(false)
    const skipDuplicates = ref(true)
    const updateExisting = ref(false)
    const isDownloading = ref(false)
    const isUploading = ref(false)
    const uploadProgress = ref(0)
    const uploadStatus = ref('')
    const importResults = ref(null)
    const fileInput = ref(null)
    const lastImportWasSuccessful = ref(false)
    const fileValidationError = ref(null)

    // Computed properties
    const canImport = computed(() => {
      return selectedFile.value && 
             !isUploading.value && 
             !loading.value && 
             !fileValidationError.value
    })

    const getImportButtonText = computed(() => {
      if (isUploading.value || loading.value) {
        return validateOnly.value ? 'Validating...' : 'Importing...'
      }
      return validateOnly.value ? 'Validate File' : 'Import Products'
    })

    // Methods
    const downloadTemplate = async (fileType) => {
      try {
        isDownloading.value = true
        uploadStatus.value = `Downloading ${fileType.toUpperCase()} template...`
        
        // Use the updated API service method
        await productsApiService.downloadImportTemplateClient(fileType)
        
        uploadStatus.value = 'Template downloaded successfully!'
        setTimeout(() => {
          uploadStatus.value = ''
        }, 2000)
        
      } catch (error) {
        console.error('Error downloading template:', error)
        uploadStatus.value = 'Failed to download template'
        setTimeout(() => {
          uploadStatus.value = ''
        }, 3000)
      } finally {
        isDownloading.value = false
      }
    }

    const validateFile = (file) => {
      // Reset validation error
      fileValidationError.value = null

      // Check file size (10MB limit)
      const maxSize = 10 * 1024 * 1024 // 10MB
      if (file.size > maxSize) {
        fileValidationError.value = `File size (${formatFileSize(file.size)}) exceeds the 10MB limit`
        return false
      }

      // Check file type
      const allowedTypes = [
        'text/csv',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      ]
      
      const fileExtension = file.name.toLowerCase().split('.').pop()
      const allowedExtensions = ['csv', 'xlsx', 'xls']

      if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(fileExtension)) {
        fileValidationError.value = 'Invalid file type. Please select a CSV or Excel file'
        return false
      }

      return true
    }

    const onFileSelected = (event) => {
      const file = event.target.files[0]
      if (file && validateFile(file)) {
        selectedFile.value = file
        importResults.value = null // Clear previous results
      } else if (file) {
        selectedFile.value = null
        // fileValidationError.value is already set by validateFile
      }
    }

    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }

    const resetForm = () => {
      selectedFile.value = null
      validateOnly.value = false
      skipDuplicates.value = true
      updateExisting.value = false
      importResults.value = null
      uploadProgress.value = 0
      uploadStatus.value = ''
      isUploading.value = false
      isDownloading.value = false
      lastImportWasSuccessful.value = false
      fileValidationError.value = null
      
      if (fileInput.value) {
        fileInput.value.value = ''
      }
    }

    const startNewImport = () => {
      resetForm()
    }

    const handleImport = async () => {
      if (!selectedFile.value || !canImport.value) return

      try {
        isUploading.value = true
        uploadProgress.value = 0
        uploadStatus.value = 'Preparing file...'

        // UPDATED: Enhanced options based on new API capabilities
        const options = {
          validate_only: validateOnly.value,
          skip_duplicates: skipDuplicates.value,
          update_existing: updateExisting.value,
          create_history: true, // CRITICAL: Ensure product history is created
          batch_size: 50 // Process in batches for better performance
        }

        // Enhanced progress simulation
        const progressInterval = setInterval(() => {
          if (uploadProgress.value < 85) {
            uploadProgress.value += Math.random() * 15
            updateStatusMessage()
          }
        }, 300)

        console.log('Starting import with options:', options)
        
        const result = await productsApiService.importProducts(selectedFile.value, options)
        
        clearInterval(progressInterval)
        uploadProgress.value = 100

        console.log('Import API response:', result)

        // UPDATED: Enhanced result parsing based on new API response format
        const processedResult = parseImportResult(result)

        if (processedResult.success) {
          uploadStatus.value = validateOnly.value ? 'Validation completed!' : 'Import completed!'
          importResults.value = processedResult
          lastImportWasSuccessful.value = !validateOnly.value

          // Use useProducts success handler for consistency
          if (!validateOnly.value) {
            handleImportSuccess(result)
            emit('import-completed', result)
          }
        } else {
          uploadStatus.value = validateOnly.value ? 'Validation failed' : 'Import completed with issues'
          uploadProgress.value = 0
          importResults.value = processedResult
          lastImportWasSuccessful.value = false

          // Use useProducts error handler for consistency
          handleImportError({ message: processedResult.error, details: result })
          emit('import-failed', { message: processedResult.error, details: result })
        }

      } catch (error) {
        console.error('Import error:', error)
        uploadProgress.value = 0
        uploadStatus.value = validateOnly.value ? 'Validation failed' : 'Import failed'
        
        const errorMessage = error.response?.data?.error || 
                           error.response?.data?.message || 
                           error.message || 
                           'An unexpected error occurred'

        importResults.value = {
          success: false,
          error: errorMessage,
          totalProcessed: 0,
          totalSuccessful: 0,
          totalFailed: 0,
          validationErrors: []
        }

        lastImportWasSuccessful.value = false
        
        // Use useProducts error handler
        handleImportError(error)
        emit('import-failed', error)
      } finally {
        isUploading.value = false
      }
    }

    // UPDATED: Enhanced result parsing for different API response formats
    const parseImportResult = (result) => {
      if (!result) {
        return {
          success: false,
          error: 'No response from server',
          totalProcessed: 0,
          totalSuccessful: 0,
          totalFailed: 0,
          validationErrors: []
        }
      }

      // Handle different response structures
      const data = result.results || result

      const totalProcessed = data.total_processed || data.totalProcessed || 0
      const totalSuccessful = data.total_successful || data.totalSuccessful || 0
      const totalFailed = data.total_failed || data.totalFailed || 0
      const totalSkipped = data.total_skipped || data.totalSkipped || 0
      const validationErrors = data.validation_errors || data.validationErrors || []

      // Determine success based on multiple criteria
      const isSuccess = validateOnly.value ? 
        (totalProcessed > 0 && validationErrors.length === 0) :
        (totalSuccessful > 0 && (totalFailed === 0 || totalSuccessful > totalFailed))

      return {
        success: isSuccess,
        error: data.error || data.message || (isSuccess ? '' : 'Import validation failed'),
        totalProcessed,
        totalSuccessful,
        totalFailed,
        totalSkipped,
        validationErrors
      }
    }

    const updateStatusMessage = () => {
      const progress = uploadProgress.value
      if (progress < 20) {
        uploadStatus.value = 'Uploading file...'
      } else if (progress < 40) {
        uploadStatus.value = 'Processing data...'
      } else if (progress < 60) {
        uploadStatus.value = 'Validating categories...'
      } else if (progress < 80) {
        uploadStatus.value = validateOnly.value ? 'Validating products...' : 'Creating products...'
      } else {
        uploadStatus.value = 'Finalizing...'
      }
    }

    const refreshProductList = async () => {
      try {
        await refreshData()
        emit('refresh-products')
        uploadStatus.value = 'Product list refreshed!'
        setTimeout(() => {
          uploadStatus.value = ''
        }, 2000)
      } catch (error) {
        console.error('Error refreshing products:', error)
        uploadStatus.value = 'Failed to refresh product list'
      }
    }

    const viewImportedProducts = () => {
      // Close modal and emit event to navigate to products with filter
      const modal = bootstrap.Modal.getInstance(document.getElementById('importModal'))
      if (modal) {
        modal.hide()
      }
      
      // You could emit an event to filter products by recent imports
      emit('view-imported-products', importResults.value)
    }

    // Modal event handlers
    const onModalShown = () => {
      // Fetch categories when modal opens for validation
      if (categories.value.length === 0) {
        fetchCategories()
      }

      // Reset form when modal is opened if last import was successful
      if (lastImportWasSuccessful.value) {
        resetForm()
      }
    }

    const onModalHidden = () => {
      // Optional: Clear any temporary states
      uploadStatus.value = ''
    }

    // Bootstrap modal event listeners setup
    let modalElement = null

    onMounted(() => {
      modalElement = document.getElementById('importModal')
      if (modalElement) {
        modalElement.addEventListener('shown.bs.modal', onModalShown)
        modalElement.addEventListener('hidden.bs.modal', onModalHidden)
      }

      // Fetch categories on component mount
      if (categories.value.length === 0) {
        fetchCategories()
      }
    })

    onUnmounted(() => {
      if (modalElement) {
        modalElement.removeEventListener('shown.bs.modal', onModalShown)
        modalElement.removeEventListener('hidden.bs.modal', onModalHidden)
      }
    })

    return {
      // From useProducts
      categories,
      loading,
      error,
      successMessage,

      // Local state
      selectedFile,
      validateOnly,
      skipDuplicates,
      updateExisting,
      isDownloading,
      isUploading,
      uploadProgress,
      uploadStatus,
      importResults,
      fileInput,
      fileValidationError,

      // Computed
      canImport,
      getImportButtonText,

      // Methods
      downloadTemplate,
      onFileSelected,
      formatFileSize,
      resetForm,
      startNewImport,
      handleImport,
      refreshProductList,
      viewImportedProducts,
      onModalShown,
      onModalHidden
    }
  }
}
</script>

<style scoped>
/* Custom styles for better visual hierarchy */
.modal-header {
  border-bottom: 1px solid var(--neutral-medium);
}

.modal-footer {
  border-top: 1px solid var(--neutral-medium);
}

.form-control:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 0.2rem rgba(115, 146, 226, 0.25);
}

.form-check-input:checked {
  background-color: var(--primary);
  border-color: var(--primary);
}

.progress {
  height: 10px;
  background-color: var(--neutral-light);
  border-radius: 5px;
  overflow: hidden;
}

.progress-bar {
  border-radius: 5px;
  transition: width 0.3s ease;
}

.progress-bar-striped {
  background-image: linear-gradient(45deg, rgba(255, 255, 255, 0.15) 25%, transparent 25%, transparent 50%, rgba(255, 255, 255, 0.15) 50%, rgba(255, 255, 255, 0.15) 75%, transparent 75%, transparent);
  background-size: 1rem 1rem;
}

.progress-bar-animated {
  animation: progress-bar-stripes 1s linear infinite;
}

@keyframes progress-bar-stripes {
  0% {
    background-position-x: 1rem;
  }
}

/* Alert customizations */
.alert {
  border-radius: 8px;
}

/* File input styling */
.form-control[type="file"] {
  padding: 0.5rem;
}

.form-control[type="file"]:focus {
  box-shadow: 0 0 0 0.2rem rgba(115, 146, 226, 0.25);
}

/* Scrollable validation errors */
.alert ul {
  margin-bottom: 0;
}

.alert li {
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
}

/* Enhanced button states */
.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Form text styling */
.form-text {
  font-size: 0.8125rem;
}

/* Checkbox and label improvements */
.form-check {
  padding-left: 1.5em;
}

.form-check-input {
  margin-top: 0.15em;
}

.form-check-label {
  line-height: 1.4;
}

/* Loading state for buttons */
.btn-loading {
  position: relative;
  color: transparent !important;
}

.btn-loading::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 1rem;
  height: 1rem;
  border: 2px solid currentColor;
  border-radius: 50%;
  border-top-color: transparent;
  animation: btn-spin 0.8s linear infinite;
}

@keyframes btn-spin {
  to {
    transform: translate(-50%, -50%) rotate(360deg);
  }
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .modal-lg {
    max-width: 95%;
    margin: 1rem auto;
  }
  
  .d-flex.gap-2 {
    flex-direction: column;
  }
  
  .d-flex.gap-2 .btn {
    width: 100%;
  }
}
</style>