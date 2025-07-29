<template>
  <div v-if="metadataReady">
    <ModelGrid :key="modelName + (id || '')" :modelName="modelName" :parentId="id" />
    <div v-if="id" v-for="related in relatedModels" :key="related.modelName + '-detail'" style="margin-top: 32px;">
      <ModelGrid :key="related.modelName + '-' + id" :modelName="related.modelName"
                 :parentModel="modelName"
                 :parentId="id"
                 :parentRelationship="related.relationshipKey" />
    </div>
  </div>
  <div v-else>
    Loading metadata...
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useMetadataStore } from '../stores/metadata'
import ModelGrid from './ModelGrid.vue'

const route = useRoute()
const modelName = computed(() => route.params.modelName as string)
const id = computed(() => route.params.id ? Number(route.params.id) : undefined)
const metadataStore = useMetadataStore()

onMounted(async () => {
  if (!metadataStore.metadata) {
    await metadataStore.fetchMetadata()
  }
})

const metadataReady = computed(() => !!metadataStore.metadata)

const relatedModels = computed(() => {
  if (!metadataStore.metadata || !modelName.value) return []
  const result: { modelName: string, relationshipKey: string }[] = []
  for (const [otherModel, meta] of Object.entries(metadataStore.metadata)) {
    for (const [relKey, rel] of Object.entries(meta.relationships)) {
      if (rel.target === modelName.value) {
        result.push({ modelName: otherModel, relationshipKey: relKey })
      }
    }
  }
  return result
})
</script>
