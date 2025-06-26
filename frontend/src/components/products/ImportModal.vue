<template>
  <div 
    class="modal fade" 
    id="importModal" 
    tabindex="-1" 
    aria-labelledby="importModalLabel" 
    aria-hidden="true"
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
                :disabled="isDownloading"
              >
                <FileSpreadsheet :size="14" />
                Download CSV Template
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
                :disabled="isUploading"
              >
              <div class="form-text" style="color: var(--tertiary-medium);">
                Supported formats: CSV, Excel (.xlsx, .xls)
              </div>
            </div>

            <!-- Selected File Info -->
            <div v-if="selectedFile" class="alert alert-success border-0" style="background-color: var(--success-light); color: var(--success-dark);">
              <Check :size="16" class="me-2" />
              <strong>Selected:</strong> {{ selectedFile.name }} 
              <small>({{ formatFileSize(selectedFile.size) }})</small>
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
              >
              <label class="form-check-label" for="validateOnly" style="color: var(--tertiary-medium);">
                Validate only (don't import, just check for errors)
              </label>
            </div>
            
            <div class="form-check">
              <input 
                class="form-check-input" 
                type="checkbox" 
                id="skipDuplicates"
                v-model="skipDuplicates"
                :disabled="validateOnly"
              >
              <label class="form-check-label" for="skipDuplicates" style="color: var(--tertiary-medium);">
                Skip duplicate products
              </label>
            </div>
          </div>

          <!-- Progress Bar -->
          <div v-if="isUploading" class="mb-3">
            <div class="d-flex justify-content-between align-items-center mb-2">
              <small style="color: var(--tertiary-medium);">{{ uploadStatus }}</small>
              <small style="color: var(--tertiary-medium);">{{ uploadProgress }}%</small>
            </div>
            <div class="progress">
              <div 
                class="progress-bar" 
                role="progressbar" 
                :style="{ 
                  width: uploadProgress + '%',
                  backgroundColor: uploadProgress === 100 ? 'var(--success)' : 'var(--primary)'
                }"
                :aria-valuenow="uploadProgress" 
                aria-valuemin="0" 
                aria-valuemax="100"
              ></div>
            </div>
          </div>

          <!-- Results Section -->
          <div v-if="importResults" class="mt-4">
            <h6 class="mb-3" style="color: var(--tertiary-dark);">
              Import Results
            </h6>
            
            <!-- Success Results -->
            <div v-if="importResults.success" class="alert alert-success border-0" style="background-color: var(--success-light); color: var(--success-dark);">
              <CheckCircle :size="16" class="me-2" />
              <strong>Import completed successfully!</strong>
              <ul class="mb-0 mt-2">
                <li>Total processed: {{ importResults.totalProcessed || 0 }}</li>
                <li>Successfully imported: {{ importResults.totalSuccessful || 0 }}</li>
                <li v-if="importResults.totalFailed > 0">Failed: {{ importResults.totalFailed }}</li>
              </ul>
            </div>

            <!-- Error Results -->
            <div v-if="!importResults.success" class="alert alert-danger border-0" style="background-color: var(--error-light); color: var(--error-dark);">
              <AlertTriangle :size="16" class="me-2" />
              <strong>Import failed:</strong> {{ importResults.error }}
            </div>

            <!-- Validation Results -->
            <div v-if="importResults.validationErrors && importResults.validationErrors.length > 0" class="mt-3">
              <div class="alert alert-warning border-0" style="background-color: var(--neutral-light); color: var(--tertiary-dark);">
                <AlertTriangle :size="16" class="me-2" />
                <strong>Validation Issues Found:</strong>
                <div class="mt-2" style="max-height: 200px; overflow-y: auto;">
                  <ul class="mb-0">
                    <li v-for="error in importResults.validationErrors.slice(0, 10)" :key="error.index">
                      Row {{ error.index + 2 }}: {{ error.error }}
                    </li>
                    <li v-if="importResults.validationErrors.length > 10" class="text-muted">
                      ... and {{ importResults.validationErrors.length - 10 }} more issues
                    </li>
                  </ul>
                </div>
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
            :disabled="isUploading"
          >
            Cancel
          </button>
          
          <button 
            type="button" 
            class="btn btn-submit btn-sm btn-with-icon-sm"
            @click="handleImport"
            :disabled="!selectedFile || isUploading"
            :class="{ 'btn-loading': isUploading }"
          >
            <Upload v-if="!isUploading" :size="14" />
            {{ isUploading ? 'Importing...' : (validateOnly ? 'Validate File' : 'Import Products') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import productsApiService from '@/services/apiProducts.js'

export default {
  name: 'ImportModal',
  emits: ['import-completed', 'import-failed'],
  setup(props, { emit }) {
    // Reactive state
    const selectedFile = ref(null)
    const validateOnly = ref(false)
    const skipDuplicates = ref(true)
    const isDownloading = ref(false)
    const isUploading = ref(false)
    const uploadProgress = ref(0)
    const uploadStatus = ref('')
    const importResults = ref(null)
    const fileInput = ref(null)

    // Methods
    const downloadTemplate = async (fileType) => {
      try {
        isDownloading.value = true
        await productsApiService.downloadImportTemplateClient(fileType)
      } catch (error) {
        console.error('Error downloading template:', error)
        // You could show a toast notification here
      } finally {
        isDownloading.value = false
      }
    }

    const onFileSelected = (event) => {
      const file = event.target.files[0]
      if (file) {
        selectedFile.value = file
        importResults.value = null // Clear previous results
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
      importResults.value = null
      uploadProgress.value = 0
      uploadStatus.value = ''
      if (fileInput.value) {
        fileInput.value.value = ''
      }
    }

    const handleImport = async () => {
      if (!selectedFile.value) return

      try {
        isUploading.value = true
        uploadProgress.value = 0
        uploadStatus.value = 'Preparing file...'

        const options = {
          validate_only: validateOnly.value,
          skip_duplicates: skipDuplicates.value
        }

        // Simulate progress for better UX
        const progressInterval = setInterval(() => {
          if (uploadProgress.value < 90) {
            uploadProgress.value += 10
            updateStatusMessage()
          }
        }, 200)

        const result = await productsApiService.importProducts(selectedFile.value, options)

        clearInterval(progressInterval)
        uploadProgress.value = 100
        uploadStatus.value = 'Import completed!'

        importResults.value = {
          success: true,
          ...result
        }

        emit('import-completed', result)

      } catch (error) {
        uploadProgress.value = 0
        uploadStatus.value = 'Import failed'
        
        importResults.value = {
          success: false,
          error: error.message || 'An unexpected error occurred'
        }

        emit('import-failed', error)
      } finally {
        isUploading.value = false
      }
    }

    const updateStatusMessage = () => {
      const progress = uploadProgress.value
      if (progress < 30) {
        uploadStatus.value = 'Uploading file...'
      } else if (progress < 60) {
        uploadStatus.value = 'Processing data...'
      } else if (progress < 90) {
        uploadStatus.value = validateOnly.value ? 'Validating products...' : 'Creating products...'
      } else {
        uploadStatus.value = 'Finalizing...'
      }
    }

    return {
      // State
      selectedFile,
      validateOnly,
      skipDuplicates,
      isDownloading,
      isUploading,
      uploadProgress,
      uploadStatus,
      importResults,
      fileInput,

      // Methods
      downloadTemplate,
      onFileSelected,
      formatFileSize,
      resetForm,
      handleImport
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
  height: 8px;
  background-color: var(--neutral-light);
  border-radius: 4px;
}

.progress-bar {
  border-radius: 4px;
  transition: width 0.3s ease;
}

/* Alert customizations */
.alert {
  border-radius: 8px;
}

/* File input styling */
.form-control[type="file"] {
  padding: 0.5rem;
}

/* Scrollable validation errors */
.alert ul {
  margin-bottom: 0;
}

.alert li {
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
}
</style>