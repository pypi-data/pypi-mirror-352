<template>
  <div class="chip-cell">
    <div v-for="chip in chips" :key="chip.id || chip.label" class="chip-row">
      <span
        v-if="chip.id"
        class="chip chip-editable"
        @click.stop="onEdit(chip)"
      >
        {{ chip.label }}
      </span>
      <span v-else class="chip">{{ chip.label }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits, computed } from 'vue'

const props = defineProps<{ params: any }>()
const emit = defineEmits(['edit-related'])

const chips = computed(() => {
  const val = props.params.value
  const arr = Array.isArray(val) ? val : val ? [val] : []
  return arr.map(v => {
    let label = ''
    let id = null
    if (v && typeof v === 'object') {
      if (props.params.displayNameField in v) label = v[props.params.displayNameField]
      else if ('id' in v) label = `ID ${v.id}`
      else label = JSON.stringify(v)
      if ('id' in v) id = v.id
    } else {
      label = String(v)
    }
    return { label, id }
  })
})

function onEdit(chip: {label: string, id: number|null}) {
  if (chip.id && typeof props.params.onEditRelated === 'function') {
    props.params.onEditRelated({ model: props.params.model, id: chip.id })
  }
}

</script>

<style scoped>
.chip-cell {
  display: block;
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
  cursor: default;
}
.chip-editable {
  cursor: pointer;
  text-decoration: underline;
  transition: background 0.15s, color 0.15s;
}
.chip-editable:hover {
  background: #c7d7ef;
  color: #1a2a4a;
}
</style> 