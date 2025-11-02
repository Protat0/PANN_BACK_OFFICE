// composables/useDropdown.js
import { ref, onMounted, onBeforeUnmount } from 'vue'

export function useDropdown() {
  const showDropdown = ref(false)
  const dropdownRef = ref(null)

  const toggleDropdown = (event) => {
    event.stopPropagation()
    showDropdown.value = !showDropdown.value
  }

  const closeDropdown = () => {
    showDropdown.value = false
  }

  const handleClickOutside = (event) => {
    if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
      showDropdown.value = false
    }
  }

  onMounted(() => {
    document.addEventListener('click', handleClickOutside)
  })

  onBeforeUnmount(() => {
    document.removeEventListener('click', handleClickOutside)
  })

  return {
    showDropdown,
    dropdownRef,
    toggleDropdown,
    closeDropdown
  }
}