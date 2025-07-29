<template>
  <div class="header">
    <h2 class="header-title" @click="onHeaderClick">{{ modelName }}</h2>
    <div class="header-actions">
      <button @click="onDelete" class="delete-button" :disabled="selectedRowsCount === 0">
        Delete Selected
      </button>
      <button @click="onAdd" class="add-button">Add New</button>
      <button @click="onRefresh" class="refresh-button" title="Refresh">🔄</button>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  modelName: string
  selectedRowsCount: number
}>()

const emit = defineEmits(['add', 'delete', 'refresh', 'header-click'])

const onAdd = () => {
  emit('add')
}

const onDelete = () => {
  emit('delete')
}

const onRefresh = () => {
  emit('refresh')
}

const onHeaderClick = () => {
  emit('header-click')
}
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.add-button {
  background-color: #4CAF50;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.add-button:hover {
  background-color: #45a049;
}

.delete-button {
  background-color: #f44336;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.delete-button:hover {
  background-color: #d32f2f;
}

.delete-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.refresh-button {
  background-color: #e0e0e0;
  color: #333;
  padding: 10px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s, border 0.2s;
}

.refresh-button:hover {
  background-color: #bdbdbd;
}

.header-title {
  cursor: pointer;
  text-decoration: underline;
}
</style> 