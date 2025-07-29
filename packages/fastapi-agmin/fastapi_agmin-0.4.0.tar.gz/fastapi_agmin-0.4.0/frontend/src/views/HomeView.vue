<template>
  <DatabaseDiagram :onTableClick="handleTableClick" />
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import DatabaseDiagram from '../components/DatabaseDiagram.vue'

const router = useRouter()

const handleTableClick = (tableName: string) => {
  router.push(`/model/${tableName}`)
}
</script> 