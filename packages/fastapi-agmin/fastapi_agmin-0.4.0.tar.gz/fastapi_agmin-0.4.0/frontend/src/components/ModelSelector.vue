<template>
  <div>
    <label>Select Model:</label>
    <select @change="$emit('selectModel', ($event.target as HTMLSelectElement).value)">
      <option value="">-- Select --</option>
      <option v-for="model in models" :key="model" :value="model">{{ model }}</option>
    </select>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'

const models = ref<string[]>([])

onMounted(async () => {
  const res = await axios.get('/models/metadata')
  models.value = Object.keys(res.data.models)
})
</script>
