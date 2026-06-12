<template>
  <div class="skeleton-loader" :style="skeletonStyles" aria-hidden="true"></div>
</template>

<script>
export default {
  name: 'SkeletonLoader',
  props: {
    width: {
      type: [String, Number],
      default: '100%'
    },
    height: {
      type: [String, Number],
      default: '1rem'
    },
    borderRadius: {
      type: [String, Number],
      default: '0.375rem'
    }
  },
  computed: {
    skeletonStyles() {
      const formatDimension = (value) => {
        if (typeof value === 'number') return `${value}px`
        return value
      }

      return {
        width: formatDimension(this.width),
        height: formatDimension(this.height),
        borderRadius: formatDimension(this.borderRadius)
      }
    }
  }
}
</script>

<style scoped>
.skeleton-loader {
  position: relative;
  overflow: hidden;
  background-color: var(--surface-secondary);
  flex-shrink: 0;
}

.skeleton-loader::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  transform: translateX(-100%);
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.35),
    transparent
  );
  animation: skeleton-shimmer 1.4s ease-in-out infinite;
}

:root.dark-theme .skeleton-loader::after,
.dark-theme .skeleton-loader::after {
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.08),
    transparent
  );
}

@keyframes skeleton-shimmer {
  100% {
    transform: translateX(100%);
  }
}

@media (prefers-reduced-motion: reduce) {
  .skeleton-loader::after {
    animation: none;
  }
}
</style>
