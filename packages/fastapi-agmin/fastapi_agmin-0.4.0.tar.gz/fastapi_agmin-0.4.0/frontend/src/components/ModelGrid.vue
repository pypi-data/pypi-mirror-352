<template>
  <div class="model-grid">
    <ModelGridHeader
      :modelName="modelName"
      :selectedRowsCount="selectedRows.length"
      @add="showAddModal = true"
      @delete="handleDeleteSelected"
      @refresh="fetchData"
      @header-click="goToListView"
    />

    <AgGridNamed
      :key="gridKey"
      class="ag-theme-alpine"
      :style="{ height: gridHeight }"
      :columnDefs="[...columns, ...relationships]"
      :rowData="filteredData"
      :rowSelection="'multiple'"
      :defaultColDef="{
        sortable: true,
        filter: true,
        resizable: true,
        autoHeight: true
      }"
      :rowHeight="ROW_HEIGHT/2"
      @grid-ready="onGridReady"
      @cell-value-changed="onCellValueChanged"
      @selection-changed="onSelectionChanged"
    />

    <!-- Error Toast -->
    <div v-if="errorMessage" class="error-toast">
      <span>{{ errorMessage }}</span>
      <button @click="dismissError" class="dismiss-button">×</button>
    </div>

    <!-- Add/Edit Modal -->
    <ModelFormModal
      :show="showAddModal"
      :modelName="modelName"
      :columns="metadataStore.getColumns(modelName)"
      :relationships="metadataStore.getRelationships(modelName)"
      :formData="formData"
      :loading="loading"
      @submit="handleModalSubmit"
      @cancel="showAddModal = false"
    />

    <ModelFormModal
      v-if="showEditRelatedModal && editRelatedModel && editRelatedId"
      :show="showEditRelatedModal"
      :modelName="editRelatedModel"
      :columns="metadataStore.getColumns(editRelatedModel)"
      :relationships="metadataStore.getRelationships(editRelatedModel)"
      :id="editRelatedId"
      :loading="editRelatedLoading"
      @submit="handleEditRelatedSubmit"
      @cancel="showEditRelatedModal = false"
    />

    <div v-if="editRelatedError" class="error-toast">
      <span>{{ editRelatedError }}</span>
      <button @click="editRelatedError = ''" class="dismiss-button">×</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useMetadataStore } from '../stores/metadata'
import ModelFormModal from './ModelFormModal.vue'
import ModelGridHeader from './ModelGridHeader.vue'
import { AgGridVue } from 'ag-grid-vue3'
import axios from 'axios'
import { useRouter } from 'vue-router'
import RelationshipChipCell from './RelationshipChipCell.vue'

const DISPLAY_NAME_FIELD = 'display_name_'
const ROW_HEIGHT = 75

const props = defineProps<{
  modelName: string
  parentModel?: string
  parentId?: number
  parentRelationship?: string
}>()

const metadataStore = useMetadataStore()
const showAddModal = ref(false)
const formData = ref<Record<string, any>>({})
const errorMessage = ref<string>('')
const errorCell = ref<{ node: any; column: any } | null>(null)
const isReverting = ref(false)

// Local state for data, loading, error, selectedRows
const data = ref<any[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
const selectedRows = ref<any[]>([])

const gridApi = ref<any>(null)
const router = useRouter()

const showEditRelatedModal = ref(false)
const editRelatedModel = ref<string | null>(null)
const editRelatedId = ref<number | null>(null)
const editRelatedError = ref<string>('')
const editRelatedLoading = ref(false)

// AG Grid + Vue caveat:
// AG Grid's reactivity with Vue is not perfect. When columns or relationships change dynamically,
// AG Grid may not update the UI as expected, especially with multiple grids or dynamic model switching.
// The reconcileGrid function ensures that the actual grid columns match the intended columns from the UI state.
// If they differ (order or content), we call fetchData() to force a refresh and keep the UI in sync.
const areDefsEqual = (a: any[], b: any[]) =>
  a.length === b.length && a.every((col: any, i: number) => col.field === b[i].field)

const reconcileGrid = () => {
  if (!gridApi.value) return
  const currentDefs = gridApi.value.getColumnDefs() || []
  const desiredDefs = [...columns.value, ...relationships.value]
  // If the column fields or order differ, force a data refresh
  if (!areDefsEqual(currentDefs, desiredDefs)) {
    fetchData()
  }
}

const fetchData = async () => {
  loading.value = true
  error.value = null
  try {
    if (props.parentModel && props.parentId && props.parentRelationship) {
      // Try backend filtering by relationship foreign key
      const relParam = `${props.parentRelationship}_id`
      const response = await axios.get(`/agmin/api/${props.modelName.toLowerCase()}`, { params: { [relParam]: props.parentId } })
      data.value = response.data
      if (data.value.length > 0) {
        // console.log('[ModelGrid] related rows:', data.value)
      } else {
        // console.log('[ModelGrid] no related data')
      }
    } else if (props.parentId) {
      const response = await axios.get(`/agmin/api/${props.modelName.toLowerCase()}/${props.parentId}`)
      data.value = response.data ? [response.data] : []
      if (data.value.length > 0) {
        // console.log('[ModelGrid] detail row:', data.value[0])
      } else {
        // console.log('[ModelGrid] no data')
      }
    } else {
      const response = await axios.get(`/agmin/api/${props.modelName.toLowerCase()}`)
      data.value = response.data
      if (data.value.length > 0) {
        // console.log('[ModelGrid] first row:', data.value[0])
      } else {
        // console.log('[ModelGrid] no data')
      }
    }
  } catch (err: any) {
    error.value = err instanceof Error ? err.message : 'Failed to fetch data'
  } finally {
    loading.value = false
  }
}

const createItem = async (form: Record<string, any>) => {
  loading.value = true
  error.value = null
  try {
    const response = await axios.post(`/agmin/api/${props.modelName.toLowerCase()}`, form)
    data.value.push(response.data)
    return response.data
  } catch (err: any) {
    error.value = err instanceof Error ? err.message : 'Failed to create item'
    throw err
  } finally {
    loading.value = false
  }
}

const updateItem = async (id: number, form: Record<string, any>) => {
  loading.value = true
  error.value = null
  try {
    const response = await axios.put(`/agmin/api/${props.modelName.toLowerCase()}/${id}`, form)
    const index = data.value.findIndex(item => item.id === id)
    if (index !== -1) {
      data.value[index] = response.data
    }
    return response.data
  } catch (err: any) {
    error.value = err instanceof Error ? err.message : 'Failed to update item'
    throw err
  } finally {
    loading.value = false
  }
}

const deleteItem = async (id: number) => {
  loading.value = true
  error.value = null
  try {
    await axios.delete(`/agmin/api/${props.modelName.toLowerCase()}/${id}`)
    data.value = data.value.filter(item => item.id !== id)
  } catch (err: any) {
    error.value = err instanceof Error ? err.message : 'Failed to delete item'
    throw err
  } finally {
    loading.value = false
  }
}

const filteredData = computed(() => data.value)

const gridHeight = computed(() => {
  const rowCount = filteredData.value.length
  // if (rowCount === 0 || rowCount === 1) return `${ROW_HEIGHT*2}px`
  // if (rowCount <= 5) return `${rowCount * ROW_HEIGHT}px`
  return `${ROW_HEIGHT * 5}px`
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

const getColumnType = (type: string) => {
  const typeMap: Record<string, string> = {
    'INTEGER': 'numericColumn',
    'VARCHAR': 'text',
    'DATE': 'dateColumn',
    'BOOLEAN': 'boolean',
    'FLOAT': 'numericColumn',
    'DECIMAL': 'numericColumn'
  }
  return typeMap[type.toUpperCase()] || 'text'
}

const columns = computed(() => {
  const cols = metadataStore.getColumns(props.modelName)
  return [
    {
      headerName: '',
      field: 'buttons',
      width: 40,
      pinned: 'left',
      cellRenderer: (params: any) => {
        return `
          <div style="display: flex; gap: 8px; justify-content: center;">
            <span 
              style="cursor: pointer; font-size: 16px;" 
              title="View Related Entities"
              class="relations-button"
              data-row-id="${params.data.id}"
            >🔗</span>
          </div>
        `
      },
      onCellClicked: (params: any) => {
        const target = params.event.target as HTMLElement
        if (target.classList.contains('relations-button')) {
          router.push(`/model/${props.modelName}/${params.data.id}`)
        }
      },
      cellClass: 'cell-non-editable',
    },
    {
      field: DISPLAY_NAME_FIELD,
      headerName: 'Display Name',
      pinned: 'left',
      editable: false,
      width: 250,
      cellClass: 'cell-non-editable',
    },
    ...Object.entries(cols)
      .filter(([name]) => name !== DISPLAY_NAME_FIELD)
      .map(([name, col]) => ({
        field: name,
        headerName: col.label || name,
        editable: !col.primary_key && name !== 'id' && name !== DISPLAY_NAME_FIELD,
        valueFormatter: (params: any) => {
          if (params.value === null || params.value === undefined) return ''
          if (typeof params.value === 'object') {
            // Try to show a display_name_ or name/title, else JSON
            if ('display_name_' in params.value) return params.value.display_name_
            if ('name' in params.value) return params.value.name
            if ('title' in params.value) return params.value.title
            return JSON.stringify(params.value)
          }
          if (col.type === 'DATE') return new Date(params.value).toLocaleDateString()
          return params.value
        },
        cellClassRules: {
          'cell-non-editable': () => col.primary_key || name === 'id' || name === DISPLAY_NAME_FIELD
        }
      }))
  ]
})

const relationships = computed(() => {
  const rels = metadataStore.getRelationships(props.modelName)
  return Object.entries(rels).map(([name, rel]) => ({
    field: name,
    headerName: name,  // Use the relationship key as header
    editable: false,
    valueFormatter: () => '',
    cellRenderer: RelationshipChipCell,
    cellRendererParams: {
      model: rel.target,
      displayNameField: DISPLAY_NAME_FIELD,
      onEditRelated: (payload: { model: string, id: number }) => openEditRelatedModal(payload.model, payload.id)
    },
    cellClass: 'cell-non-editable',
  }))
})

const handleModalSubmit = async (dataObj: Record<string, any>) => {
  try {
    await createItem(dataObj)
    showAddModal.value = false
    formData.value = {}
  } catch (error) {
    console.error('Error adding item:', error)
  }
}

const handleDeleteSelected = async () => {
  if (!selectedRows.value.length) return
  if (confirm(`Are you sure you want to delete ${selectedRows.value.length} items?`)) {
    await Promise.all(
      selectedRows.value.map(row => 
        deleteItem(row.id)
      )
    )
    selectedRows.value = []
  }
}

const onGridReady = (params: any) => {
  gridApi.value = params.api
  reconcileGrid()
}

watch([columns, relationships], () => {
  nextTick(reconcileGrid)
})

const dismissError = () => {
  errorMessage.value = ''
  if (errorCell.value) {
    const cellElement = errorCell.value.node.api.getCellRendererInstances({
      rowNodes: [errorCell.value.node],
      columns: [errorCell.value.column]
    })?.[0]?.getGui()
    if (cellElement) {
      cellElement.classList.remove('cell-error')
    }
    errorCell.value = null
  }
}

const onCellValueChanged = async (params: any) => {
  // Skip if we're in the process of reverting a value
  if (isReverting.value) {
    isReverting.value = false
    return
  }

  try {
    await updateItem(params.data.id, params.data)
    dismissError()
  } catch (error: any) {
    // Show error message
    errorMessage.value = error.response?.data?.detail?.msg || 'Error updating item'
    
    // Revert the cell value
    isReverting.value = true
    params.node.setDataValue(params.column.getColId(), params.oldValue)
    
    // Store error cell reference
    errorCell.value = { node: params.node, column: params.column }
    
    // Add error class to cell
    const cellElement = params.api.getCellRendererInstances({
      rowNodes: [params.node],
      columns: [params.column]
    })?.[0]?.getGui()
    if (cellElement) {
      cellElement.classList.add('cell-error')
    }
  }
}

const onSelectionChanged = (params: any) => {
  selectedRows.value = params.api.getSelectedRows()
}

const gridKey = computed(() => {
  // Use a hash of columnDefs fields and rowData length for uniqueness
  return JSON.stringify([...columns.value, ...relationships.value].map((c: any) => c.field).join(',')) + '-' + filteredData.value.length
})

const AgGridNamed = {
  name: 'AgGridVue',
  extends: AgGridVue
}

const goToListView = () => {
  router.push(`/model/${props.modelName}`)
}

const openEditRelatedModal = (model: string, id: number) => {
  editRelatedModel.value = model
  editRelatedId.value = id
  editRelatedError.value = ''
  editRelatedLoading.value = false
  showEditRelatedModal.value = true
}

const handleEditRelatedSubmit = async (form: Record<string, any>) => {
  if (!editRelatedModel.value || !editRelatedId.value) return
  editRelatedLoading.value = true
  editRelatedError.value = ''
  try {
    await axios.put(`/agmin/api/${editRelatedModel.value.toLowerCase()}/${editRelatedId.value}`, form)
    showEditRelatedModal.value = false
    editRelatedModel.value = null
    editRelatedId.value = null
    fetchData() // refresh grid
  } catch (err: any) {
    editRelatedError.value = err instanceof Error ? err.message : 'Failed to update entity'
  } finally {
    editRelatedLoading.value = false
  }
}

onMounted(() => {
  // console.log('[ModelGrid] modelName:', props.modelName)
  // console.log('[ModelGrid] columns:', metadataStore.getColumns(props.modelName))
  // console.log('[ModelGrid] relationships:', metadataStore.getRelationships(props.modelName))
  fetchData()
})

</script>

<style scoped>
.model-grid {
  position: relative;
}

.error-toast {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  background-color: #ff4444;
  color: white;
  padding: 12px 20px;
  border-radius: 4px;
  z-index: 1000;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
  animation: slideDown 0.3s ease-out;
}

.dismiss-button {
  background: none;
  border: none;
  color: white;
  font-size: 20px;
  cursor: pointer;
  padding: 0 4px;
  opacity: 0.8;
  transition: opacity 0.2s;
}

.dismiss-button:hover {
  opacity: 1;
}

@keyframes slideDown {
  from {
    transform: translate(-50%, -100%);
    opacity: 0;
  }
  to {
    transform: translate(-50%, 0);
    opacity: 1;
  }
}

:deep(.cell-error) {
  background-color: #ffebee !important;
  transition: background-color 0.3s ease;
  animation: errorPulse 2s ease-in-out infinite;
  border: 1px solid #ffcdd2 !important;
}

@keyframes errorPulse {
  0% { background-color: #ffebee !important; }
  50% { background-color: #ffcdd2 !important; }
  100% { background-color: #ffebee !important; }
}

.related-entities {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.related-grid {
  margin-bottom: 30px;
}

.related-grid h3 {
  margin-bottom: 10px;
  color: #666;
  font-size: 1.1em;
}
</style>

<style>
.cell-non-editable {
  background-color: #f3f3f3 !important;
  color: #888;
}
.chip-row {
  display: block;
  margin-bottom: 2px;
}
.chip {
  display: block;
  background: #e0e7ef;
  color: #234;
  border-radius: 12px;
  padding: 2px 10px;
  font-size: 0.95em;
  margin: 0;
  line-height: 1.7;
  font-weight: 500;
  border: 1px solid #b6c2d1;
  box-shadow: 0 1px 2px rgba(0,0,0,0.03);
  vertical-align: middle;
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ag-theme-alpine .ag-cell .chip {
  white-space: nowrap;
}

.ag-theme-alpine .ag-cell {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 2px;
}

.chip-link {
  text-decoration: none;
  color: #234;
  transition: background 0.15s, color 0.15s;
}
.chip-link:hover {
  background: #c7d7ef;
  color: #1a2a4a;
}

.chip-editable {
  cursor: pointer;
  text-decoration: underline;
}
.chip-editable:hover {
  background: #c7d7ef;
  color: #1a2a4a;
}
</style>