<template>
  <ModelGrid :modelName="modelName" />
</template>

<script setup lang="ts">
import ModelGrid from '../components/ModelGrid.vue'

defineProps<{
  modelName: string
}>()
</script> 