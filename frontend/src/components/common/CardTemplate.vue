<template>
  <div 
    :class="cardClasses"
    @click="handleClick"
  >
    <!-- Card Header (optional) -->
    <div v-if="$slots.header" class="card-header">
      <slot name="header"></slot>
    </div>

    <!-- Card Body -->
    <div class="card-body">
      <!-- Title -->
      <h6 v-if="title" :class="titleClasses">{{ title }}</h6>
      
      <!-- Main Content -->
      <slot name="content">
        <div v-if="content" v-html="content"></div>
      </slot>
      
      <!-- Value Display -->
      <div v-if="value !== null && value !== undefined" :class="valueClasses">
        {{ formattedValue }}
      </div>
      
      <!-- Subtitle/Description -->
      <small v-if="subtitle" :class="subtitleClasses">{{ subtitle }}</small>
    </div>

    <!-- Card Footer (optional) -->
    <div v-if="$slots.footer" class="card-footer">
      <slot name="footer"></slot>
    </div>

    <!-- Loading Overlay -->
    <div v-if="loading" class="card-loading-overlay">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CardTemplate',
  props: {
    // Size variants
    size: {
      type: String,
      default: 'md',
      validator: (value) => ['mini', 'xs', 'compact', 'sm', 'md', 'lg', 'xl', 'xxl'].includes(value)
    },
    
    // Border color variants
    borderColor: {
      type: String,
      default: 'none',
      validator: (value) => [
        'none', 'primary', 'secondary', 'success', 'info', 'warning', 
        'danger', 'error', 'tertiary', 'neutral'
      ].includes(value)
    },
    
    // Border position
    borderPosition: {
      type: String,
      default: 'start',
      validator: (value) => ['start', 'end', 'top', 'bottom', 'all'].includes(value)
    },
    
    // Content props
    title: {
      type: String,
      default: null
    },
    
    subtitle: {
      type: String,
      default: null
    },
    
    content: {
      type: String,
      default: null
    },
    
    value: {
      type: [String, Number],
      default: null
    },
    
    // Styling props
    clickable: {
      type: Boolean,
      default: false
    },
    
    loading: {
      type: Boolean,
      default: false
    },
    
    shadow: {
      type: String,
      default: 'sm',
      validator: (value) => ['none', 'sm', 'md', 'lg'].includes(value)
    },
    
    // Value formatting
    valueType: {
      type: String,
      default: 'text',
      validator: (value) => ['text', 'number', 'currency', 'percentage'].includes(value)
    },
    
    valueColor: {
      type: String,
      default: 'primary',
      validator: (value) => [
        'primary', 'secondary', 'success', 'info', 'warning', 
        'danger', 'error', 'tertiary', 'neutral'
      ].includes(value)
    }
  },
  
  emits: ['click'],
  
  computed: {
    cardClasses() {
      const classes = ['card', 'card-template']
      
      // Size classes
      classes.push(`card-${this.size}`)
      
      // Border classes
      if (this.borderColor !== 'none') {
        if (this.borderPosition === 'all') {
          classes.push(`border-${this.borderColor}`)
        } else {
          classes.push(`border-${this.borderPosition}`)
          classes.push(`border-${this.borderColor}`)
        }
        
        // Add border width for visibility
        if (this.borderPosition !== 'all') {
          classes.push('border-4')
        }
      }
      
      // Shadow classes
      if (this.shadow !== 'none') {
        classes.push(`shadow-${this.shadow}`)
      }
      
      // Interactive classes
      if (this.clickable) {
        classes.push('card-clickable')
      }
      
      // Loading state
      if (this.loading) {
        classes.push('card-loading')
      }
      
      return classes
    },
    
    titleClasses() {
      const classes = ['card-title', 'text-tertiary-dark', 'mb-2']
      
      // Size-based title classes
      if (this.size === 'mini') {
        classes.push('small', 'fw-semibold')
      } else if (this.size === 'xs') {
        classes.push('small', 'fw-semibold')
      } else if (this.size === 'compact') {
        classes.push('h6', 'mb-1')
      } else if (this.size === 'sm') {
        classes.push('h6')
      } else if (this.size === 'lg') {
        classes.push('h5')
      } else if (this.size === 'xl') {
        classes.push('h4')
      } else if (this.size === 'xxl') {
        classes.push('h3')
      } else {
        classes.push('h6')
      }
      
      return classes
    },
    
    valueClasses() {
      const classes = ['card-value', 'fw-bold', 'mb-1']
      
      // Color classes
      classes.push(`text-${this.valueColor}`)
      
      // Size-based value classes
      if (this.size === 'mini') {
        classes.push('h6', 'mb-0')
      } else if (this.size === 'xs') {
        classes.push('h5', 'mb-0')
      } else if (this.size === 'compact') {
        classes.push('h4', 'mb-1')
      } else if (this.size === 'sm') {
        classes.push('h6')
      } else if (this.size === 'lg') {
        classes.push('h1')
      } else if (this.size === 'xl') {
        classes.push('display-6')
      } else if (this.size === 'xxl') {
        classes.push('display-4')
      } else {
        classes.push('h2')
      }
      
      return classes
    },
    
    subtitleClasses() {
      return ['card-subtitle', 'text-tertiary-medium']
    },
    
    formattedValue() {
      if (this.value === null || this.value === undefined) return ''
      
      switch (this.valueType) {
        case 'currency':
          return `₱${parseFloat(this.value).toFixed(2)}`
        case 'percentage':
          return `${this.value}%`
        case 'number':
          return parseFloat(this.value).toLocaleString()
        default:
          return this.value
      }
    }
  },
  
  methods: {
    handleClick(event) {
      if (this.clickable && !this.loading) {
        this.$emit('click', event)
      }
    }
  }
}
</script>

<style scoped>
/* ==========================================================================
   CARD TEMPLATE COMPONENT
   Reusable card component with size and border variants
   ========================================================================== */

.card-template {
  position: relative;
  transition: all 0.2s ease;
  background-color: white;
  border-radius: 0.75rem;
}

/* ==========================================================================
   SIZE VARIANTS
   ========================================================================== */
.card-mini .card-body {
  padding: 0.5rem 0.75rem;
}

.card-xs .card-body {
  padding: 0.625rem 0.875rem;
}

.card-compact .card-body {
  padding: 0.75rem 1rem;
}

.card-sm .card-body {
  padding: 0.75rem;
}

.card-md .card-body {
  padding: 1.25rem;
}

.card-lg .card-body {
  padding: 1.5rem;
}

.card-xl .card-body {
  padding: 2rem;
}

.card-xxl .card-body {
  padding: 2.5rem;
}

/* ==========================================================================
   COMPACT SIZE TYPOGRAPHY ADJUSTMENTS
   ========================================================================== */

.card-mini .card-title {
  font-size: 0.75rem;
  line-height: 1.2;
  margin-bottom: 0.25rem !important;
}

.card-mini .card-value {
  font-size: 1rem;
  line-height: 1.1;
  margin-bottom: 0 !important;
}

.card-mini .card-subtitle {
  font-size: 0.6875rem;
  margin-bottom: 0 !important;
}

.card-xs .card-title {
  font-size: 0.8125rem;
  line-height: 1.2;
  margin-bottom: 0.375rem !important;
}

.card-xs .card-value {
  font-size: 1.125rem;
  line-height: 1.1;
  margin-bottom: 0 !important;
}

.card-xs .card-subtitle {
  font-size: 0.75rem;
  margin-bottom: 0 !important;
}

.card-compact .card-title {
  font-size: 0.875rem;
  line-height: 1.3;
  margin-bottom: 0.5rem !important;
}

.card-compact .card-value {
  font-size: 1.5rem;
  line-height: 1.1;
  margin-bottom: 0.25rem !important;
}

.card-compact .card-subtitle {
  font-size: 0.8125rem;
  margin-bottom: 0 !important;
}

/* ==========================================================================
   BORDER COLOR VARIANTS
   Using colors.css variables
   ========================================================================== */

.border-primary {
  border-color: var(--primary) !important;
}

.border-secondary {
  border-color: var(--secondary) !important;
}

.border-success {
  border-color: var(--success) !important;
}

.border-info {
  border-color: var(--info) !important;
}

.border-warning {
  border-color: var(--warning, #ffc107) !important;
}

.border-danger,
.border-error {
  border-color: var(--error) !important;
}

.border-tertiary {
  border-color: var(--tertiary) !important;
}

.border-neutral {
  border-color: var(--neutral) !important;
}

/* ==========================================================================
   VALUE COLOR VARIANTS
   ========================================================================== */

.text-primary {
  color: var(--primary) !important;
}

.text-secondary {
  color: var(--secondary) !important;
}

.text-success {
  color: var(--success) !important;
}

.text-info {
  color: var(--info) !important;
}

.text-warning {
  color: var(--warning, #ffc107) !important;
}

.text-danger,
.text-error {
  color: var(--error) !important;
}

.text-tertiary {
  color: var(--tertiary) !important;
}

.text-neutral {
  color: var(--neutral-dark) !important;
}

/* ==========================================================================
   INTERACTIVE STATES
   ========================================================================== */

.card-clickable {
  cursor: pointer;
}

.card-clickable:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px 0 rgba(0, 0, 0, 0.15) !important;
}

.card-clickable:active {
  transform: translateY(-1px);
}

/* ==========================================================================
   LOADING STATE
   ========================================================================== */

.card-loading {
  pointer-events: none;
  opacity: 0.8;
}

.card-loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(255, 255, 255, 0.8);
  border-radius: inherit;
  z-index: 10;
}

/* ==========================================================================
   SHADOW VARIANTS
   ========================================================================== */

.shadow-sm {
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05) !important;
}

.shadow-md {
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06) !important;
}

.shadow-lg {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06) !important;
}

/* ==========================================================================
   CUSTOM TEXT COLORS USING COLORS.CSS VARIABLES
   ========================================================================== */

.text-tertiary-dark {
  color: var(--tertiary-dark) !important;
}

.text-tertiary-medium {
  color: var(--tertiary-medium) !important;
}

/* ==========================================================================
   RESPONSIVE ADJUSTMENTS
   ========================================================================== */

@media (max-width: 768px) {
  .card-xl .card-body {
    padding: 1.5rem;
  }
  
  .card-xxl .card-body {
    padding: 1.75rem;
  }
  
  .card-lg .card-body {
    padding: 1.25rem;
  }
  
  .card-md .card-body {
    padding: 1rem;
  }
  
  .card-sm .card-body {
    padding: 0.75rem;
  }

    .card-mini .card-body {
    padding: 0.375rem 0.5rem;
  }
  
  .card-xs .card-body {
    padding: 0.5rem 0.625rem;
  }
  
  .card-compact .card-body {
    padding: 0.625rem 0.75rem;
  }
}

/* ==========================================================================
   ACCESSIBILITY ENHANCEMENTS
   ========================================================================== */

.card-clickable:focus {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}

@media (prefers-reduced-motion: reduce) {
  .card-template,
  .card-clickable {
    transition: none;
  }
  
  .card-clickable:hover {
    transform: none;
  }
}
</style>