<template>
  <div class="search-container">
    <input
      type="text"
      :id="relationship.target"
      v-model="localSearchTerm"
      @input="onSearch"
      @keydown="handleKeyDown"
      @focus="focused = true"
      @blur="onBlur"
      placeholder="Search..."
      class="search-input"
    />
    <div v-if="focused && searchResults?.length" class="search-results">
      <div
        v-for="(item, index) in searchResults"
        :key="item.id"
        @click="onSelect(item)"
        :class="['search-item', { 'search-item-highlighted': index === highlightedIndex }]"
      >
        {{ item.label }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { Relationship } from '../stores/metadata'
import { debounce } from 'lodash-es'

const props = defineProps<{
  relationship: Relationship
  value: any
  searchTerm: string
  searchResults: any[]
}>()

const emit = defineEmits(['search', 'select'])

const localSearchTerm = ref(props.searchTerm)
const highlightedIndex = ref(-1)
const focused = ref(false)

watch(() => props.searchTerm, (val) => {
  localSearchTerm.value = val
})

watch(() => props.searchResults, () => {
  highlightedIndex.value = -1
})

const onBlur = () => {
  setTimeout(() => { focused.value = false }, 150)
}

const debouncedSearch = debounce((term: string) => {
  emit('search', term)
}, 300)

const onSearch = () => {
  debouncedSearch(localSearchTerm.value)
}

const onSelect = (item: any) => {
  emit('select', item)
  localSearchTerm.value = item.label
}

const handleKeyDown = (event: KeyboardEvent) => {
  if (!props.searchResults.length) return

  switch (event.key) {
    case 'ArrowDown':
      event.preventDefault()
      highlightedIndex.value = Math.min(highlightedIndex.value + 1, props.searchResults.length - 1)
      break
    case 'ArrowUp':
      event.preventDefault()
      highlightedIndex.value = Math.max(highlightedIndex.value - 1, 0)
      break
    case 'Enter':
      event.preventDefault()
      if (highlightedIndex.value >= 0) {
        onSelect(props.searchResults[highlightedIndex.value])
      }
      break
    case 'Escape':
      event.preventDefault()
      highlightedIndex.value = -1
      break
  }
}
</script>

<style scoped>
.search-container {
  position: relative;
  width: 100%;
}

.search-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: #4a90e2;
  box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.2);
}

.search-results {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  max-height: 200px;
  overflow-y: auto;
  z-index: 1001;
  margin-top: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.search-item {
  padding: 8px 12px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.search-item:hover,
.search-item-highlighted {
  background-color: #f5f5f5;
}

.search-item:not(:last-child) {
  border-bottom: 1px solid #eee;
}
</style> 