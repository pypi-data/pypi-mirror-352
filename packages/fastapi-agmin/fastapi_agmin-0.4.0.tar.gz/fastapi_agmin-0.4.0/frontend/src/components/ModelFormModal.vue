<template>
  <div v-if="show" class="modal">
    <div class="modal-content">
      <h2>Add New {{ modelName }}</h2>
      <form @submit.prevent="onSubmit">
        <!-- Regular columns -->
        <div v-for="(col, name) in columns" :key="name" class="form-group">
          <template v-if="!col.primary_key && !name.endsWith('_id') && name !== 'display_name_'">
            <label :for="name">{{ col.label || name }}</label>
            <textarea
              v-if="col.type === 'VARCHAR' && (name === 'description' || name === 'notes' || name === 'bio')"
              :id="name"
              v-model="localFormData[name]"
              :required="!col.nullable"
              class="form-control"
            ></textarea>
            <input
              v-else
              :type="getInputType(col.type)"
              :id="name"
              v-model="localFormData[name]"
              :required="!col.nullable"
              class="form-control"
            />
          </template>
        </div>

        <!-- Relationship fields -->
        <div v-for="(rel, name) in relationships" :key="name" class="form-group">
          <label :for="name">{{ rel.target }}</label>
          <RelationshipSearchField
            :relationship="rel"
            :value="localFormData[name]"
            :searchTerm="localSearchTerms[name] ?? ''"
            :searchResults="localSearchResults[name] ?? []"
            @search="(term) => handleSearch(name, term)"
            @select="(item) => handleSelect(name, item)"
          />
        </div>

        <div class="modal-actions">
          <button type="submit" class="btn btn-primary" :disabled="loading">Save</button>
          <button type="button" @click="onCancel" class="btn btn-secondary">Cancel</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed, onMounted, onUnmounted, watchEffect } from 'vue'
import type { Column, Relationship } from '../stores/metadata'
import { toRefs } from 'vue'
import RelationshipSearchField from './RelationshipSearchField.vue'
import axios from 'axios'
import { useMetadataStore } from '../stores/metadata'

const props = defineProps<{
  modelName: string
  columns: Record<string, Column>
  relationships: Record<string, Relationship>
  id?: number
  show: boolean
  loading?: boolean
}>()

const emit = defineEmits(['submit', 'cancel'])

const localFormData = ref<Record<string, any>>({})
const localSearchTerms = ref<Record<string, string>>({})
const localSearchResults = ref<Record<string, any[]>>({})

const metadataStore = useMetadataStore()

const handleKeyDown = (event: KeyboardEvent) => {
  if (event.key === 'Escape') {
    onCancel()
  }
}

onMounted(async () => {
  window.addEventListener('keydown', handleKeyDown)
  if (props.id) {
    try {
      const response = await axios.get(`/agmin/api/${props.modelName.toLowerCase()}/${props.id}`)
      const data = response.data
      const rels = metadataStore.getRelationships(props.modelName)
      // Flatten relationship fields in data before assigning to localFormData
      for (const [relName, rel] of Object.entries(rels)) {
        if (data[relName] && typeof data[relName] === 'object') {
          if (Array.isArray(data[relName])) {
            data[relName] = data[relName].map((v: any) => v?.id ?? v)
          } else {
            data[relName] = data[relName]?.id ?? data[relName]
          }
        }
      }
      localFormData.value = { ...data }
      // Populate search results and terms for relationship fields
      for (const [relName, rel] of Object.entries(rels)) {
        const value = localFormData.value[relName]
        if (value) {
          if (Array.isArray(value)) {
            // Fetch all related entities for many-to-many
            const results = await Promise.all(value.map((id: number) =>
              typeof id === 'number' ? axios.get(`/agmin/api/${rel.target.toLowerCase()}/${id}`).then(r => r.data) : null
            ).filter(Boolean))
            localSearchResults.value[relName] = results.map(r => ({
              id: r.id,
              label: r.display_name_ || r.name || r.title || r.id
            }))
            localSearchTerms.value[relName] = '' // Optionally join labels if you want
          } else if (typeof value === 'number') {
            // Fetch the related entity for foreign key
            const r = await axios.get(`/agmin/api/${rel.target.toLowerCase()}/${value}`).then(r => r.data)
            localSearchResults.value[relName] = [{
              id: r.id,
              label: r.display_name_ || r.name || r.title || r.id
            }]
            localSearchTerms.value[relName] = localSearchResults.value[relName][0].label
          }
        }
      }
    } catch (err) {
      localFormData.value = {}
    }
  } else {
    localFormData.value = {}
  }
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
})

watchEffect(() => {
  if (props.show) {
    for (const name in props.relationships) {
    }
  }
})

const getInputType = (type: string) => {
  const typeMap: Record<string, string> = {
    'INTEGER': 'number',
    'VARCHAR': 'text',
    'DATE': 'date',
    'BOOLEAN': 'checkbox',
    'FLOAT': 'number',
    'DECIMAL': 'number'
  }
  return typeMap[type.toUpperCase()] || 'text'
}

const handleSearch = async (fieldName: string, term: string) => {
  localSearchTerms.value[fieldName] = term
  if (term.length < 3) {
    localSearchResults.value[fieldName] = []
    return
  }
  const rel = props.relationships[fieldName]
  if (!rel) return
  try {
    const response = await axios.get(`/agmin/api/${rel.target.toLowerCase()}/search`, { params: { q: term } })
    localSearchResults.value[fieldName] = response.data
  } catch (err) {
    localSearchResults.value[fieldName] = []
  }
}

const handleSelect = (fieldName: string, item: any) => {
  localFormData.value[fieldName] = item.id
  localSearchTerms.value[fieldName] = item.label
  localSearchResults.value[fieldName] = []
}

const onSubmit = () => {
  const data = { ...localFormData.value }
  for (const [name, rel] of Object.entries(props.relationships)) {
    if (typeof data[name] === 'number') {
      data[`${name}_id`] = data[name]
      delete data[name]
    }
  }
  emit('submit', data)
}

const onCancel = () => {
  emit('cancel')
}
</script>

<style scoped>
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  overflow-y: auto;
  padding: 20px;
}

.modal-content {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  width: 800px;
  max-width: 90%;
  position: relative;
  max-height: calc(100vh - 40px);
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  overflow: hidden;
}

.form-group {
  margin-bottom: 15px;
  position: relative;
  width: 100%;
  box-sizing: border-box;
  max-width: 100%;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  width: 100%;
  box-sizing: border-box;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  max-width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
  font-size: 14px;
  margin: 0;
}

.form-group textarea {
  min-height: 100px;
  resize: vertical;
}

form {
  overflow-y: auto;
  flex: 1;
  padding-right: 0;
  width: 100%;
  box-sizing: border-box;
  max-width: 100%;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
  padding-top: 10px;
  border-top: 1px solid #eee;
  position: sticky;
  bottom: 0;
  background: white;
  width: 100%;
  box-sizing: border-box;
}

.btn {
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  border: none;
  font-weight: 500;
  transition: opacity 0.2s;
  box-sizing: border-box;
}

.btn:hover {
  opacity: 0.9;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn.btn-primary {
  background-color: #4CAF50;
  color: white;
}

.btn.btn-secondary {
  background-color: #f44336;
  color: white;
}

.search-container {
  position: relative;
  width: 100%;
  box-sizing: border-box;
  max-width: 100%;
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
  z-index: 1000;
  width: 100%;
  box-sizing: border-box;
}

.search-item {
  padding: 8px;
  cursor: pointer;
  box-sizing: border-box;
}

.search-item:hover {
  background-color: #f5f5f5;
}
</style> 