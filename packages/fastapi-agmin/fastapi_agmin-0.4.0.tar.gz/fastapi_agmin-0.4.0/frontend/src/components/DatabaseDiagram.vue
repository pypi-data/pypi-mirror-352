<template>
  <div class="database-diagram">
    <div ref="diagramContainer"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { Graphviz } from '@hpcc-js/wasm'
import { useMetadataStore } from '../stores/metadata'
import { useRouter } from 'vue-router'

interface Column {
  type: string
  nullable: boolean
  primary_key: boolean
  unique: boolean
  enum_values?: string[]
  label?: string
  help_text?: string
}

interface Relationship {
  type: 'one_to_many' | 'many_to_one' | 'many_to_many'
  target: string
  back_populates?: string
  secondary?: string
  local_columns: string[]
  remote_columns: string[]
}

interface Model {
  table: string
  columns: Record<string, Column>
  relationships: Record<string, Relationship>
}

interface Metadata {
  models: Record<string, Model>
}

const props = defineProps<{
  model?: string
}>()

const metadataStore = useMetadataStore()
const router = useRouter()
const diagramContainer = ref<HTMLElement | null>(null)

const typeMap: Record<string, string> = {
  'INTEGER': 'int',
  'VARCHAR': 'string',
  'TEXT': 'string',
  'DATETIME': 'date',
  'DATE': 'date',
  'BOOLEAN': 'bool',
  'FLOAT': 'float',
  'NUMERIC': 'float',
  'BLOB': 'binary',
  'TIME': 'string',
};

function abbreviate(text: string, max: number = 22): string {
  return text.length > max ? text.slice(0, max - 1) + '…' : text;
}

const generateDiagram = () => {
  if (!metadataStore.metadata) return ''

  const models = metadataStore.metadata as Metadata['models']
  const dot = [
    'digraph G {',
    '  rankdir=TB;',
    '  node [shape=record, style=filled, fillcolor=honeydew, fontname="monospace", fontsize=12, width=2.5, height=0.5, labeljust="l", labelloc="t"];',
    '  edge [dir=both];'
  ]

  // 1. List all tables and fields with ports
  Object.entries(models).forEach(([modelName, model]) => {
    const fields = Object.entries(model.columns)
      .map(([name, col]) => {
        let baseType = col.type.split('(')[0].toUpperCase()
        baseType = typeMap[baseType] || 'string'
        const pk = col.primary_key ? ' (PK)' : ''
        // Use valid DOT record field syntax, no nested braces
        return `<${name}> ${abbreviate(name)}: ${abbreviate(baseType + pk, 12)}`
      })
      .join(' | ')
    dot.push(`  ${modelName} [label="{${modelName}|${fields}}"];
`)
  })

  // 2. Draw relationships (edges between specific fields, robust deduplication)
  const edgeSet = new Set<string>()
  Object.entries(models).forEach(([modelName, model]) => {
    Object.entries(model.relationships).forEach(([relKey, rel]) => {
      const left = modelName
      const right = rel.target
      const localCols = rel.local_columns || []
      const remoteCols = rel.remote_columns || []
      for (let i = 0; i < Math.max(localCols.length, remoteCols.length); i++) {
        const fromField = localCols[i] || localCols[0] || 'id'
        const toField = remoteCols[i] || remoteCols[0] || 'id'
        // Canonical key: sort table/field pairs so direction/type doesn't matter
        const keyArr = [left, fromField, right, toField]
        const canonicalKey = keyArr.sort().join('|')
        if (edgeSet.has(canonicalKey)) continue
        edgeSet.add(canonicalKey)
        // Arrow style
        let arrowhead = ''
        let arrowtail = ''
        if (rel.type === 'one_to_many') {
          arrowhead = 'crow'
          arrowtail = 'tee'
        } else if (rel.type === 'many_to_one') {
          arrowhead = 'tee'
          arrowtail = 'crow'
        } else if (rel.type === 'many_to_many') {
          arrowhead = 'crow'
          arrowtail = 'crow'
        }
        dot.push(`  ${left}:${fromField} -> ${right}:${toField} [arrowhead=${arrowhead}, arrowtail=${arrowtail}, dir=both, label="${fromField} → ${toField}"];
`)
      }
    })
  })

  dot.push('}')
  return dot.join('\n')
}

const renderDiagram = async () => {
  if (!diagramContainer.value) return

  try {
    const dotDefinition = generateDiagram()
    
    // Clear previous content
    diagramContainer.value.innerHTML = ''
    
    // Render the diagram
    const graphviz = await Graphviz.load();
    const svg = await graphviz.dot(dotDefinition);
    diagramContainer.value.innerHTML = svg

    // Add click handlers to table names
    const tableNames = diagramContainer.value.querySelectorAll('g.node')
    tableNames.forEach(table => {
      if (table instanceof HTMLElement) {
        table.style.cursor = 'pointer'
        table.addEventListener('click', () => {
          const modelName = table.querySelector('title')?.textContent?.trim()
          if (modelName) {
            router.push(`/model/${modelName}`)
          }
        })
      }
    })
  } catch (error) {
    console.error('Error rendering diagram:', error)
    console.error('Diagram definition:', generateDiagram())
  }
}

onMounted(async () => {
  if (!metadataStore.metadata) {
    await metadataStore.fetchMetadata()
  }
  await renderDiagram()
})

watch(() => metadataStore.metadata, async () => {
  await renderDiagram()
}, { deep: true })
</script>

<style scoped>
.database-diagram {
  padding: 20px;
  overflow: auto;
  height: 100%;
}

:deep(.node) {
  cursor: pointer;
  transition: fill 0.2s;
}

:deep(.node:hover) {
  fill: #f0f0f0;
}
</style> 