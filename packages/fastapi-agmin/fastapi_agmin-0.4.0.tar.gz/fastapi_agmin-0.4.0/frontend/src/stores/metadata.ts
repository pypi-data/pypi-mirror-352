import { defineStore } from 'pinia'
import axios from 'axios'

export interface Column {
  type: string
  nullable: boolean
  primary_key: boolean
  unique: boolean | null
  enum_values: string[] | null
  label: string | null
  help_text: string | null
}

export interface Relationship {
  type: 'many_to_one' | 'one_to_many' | 'many_to_many' | 'unknown'
  target: string
  label: string | null
  back_populates: string | null
  secondary: string | null
  local_columns?: string[]
  remote_columns?: string[]
}

export interface ModelMetadata {
  table: string
  columns: Record<string, Column>
  relationships: Record<string, Relationship>
}

export interface Metadata {
  [key: string]: ModelMetadata
}

interface MetadataState {
  metadata: Metadata | null
  loading: boolean
  error: string | null
}

export const useMetadataStore = defineStore('metadata', {
  state: (): MetadataState => ({
    metadata: null,
    loading: false,
    error: null
  }),

  getters: {
    models: (state: MetadataState) => state.metadata ? Object.keys(state.metadata) : [],
    getColumns: (state: MetadataState) => (modelName: string) => 
      state.metadata?.[modelName]?.columns || {},
    getRelationships: (state: MetadataState) => (modelName: string) => 
      state.metadata?.[modelName]?.relationships || {}
  },

  actions: {
    async fetchMetadata() {
      this.loading = true
      this.error = null
      try {
        const response = await axios.get('/agmin/api/metadata')
        this.metadata = response.data.models
      } catch (error) {
        this.error = error instanceof Error ? error.message : 'Failed to fetch metadata'
        console.error('Error fetching metadata:', error)
      } finally {
        this.loading = false
      }
    }
  }
})

// Metadata is fetched once and cached for the session.
// It will only be refreshed if the page is reloaded or the store is reset. 