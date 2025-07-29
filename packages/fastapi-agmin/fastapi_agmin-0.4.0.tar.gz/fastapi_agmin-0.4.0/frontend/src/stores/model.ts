import { defineStore } from 'pinia'
import axios from 'axios'

export interface SearchResult {
  id: number
  name?: string
  title?: string
}

export interface FormData {
  [key: string]: any
}

interface ModelState {
  data: any[]
  loading: boolean
  error: string | null
  selectedRows: any[]
}

export const useModelStore = defineStore('model', {
  state: (): ModelState => ({
    data: [],
    loading: false,
    error: null,
    selectedRows: []
  }),

  actions: {
    async fetchData(modelName: string) {
      this.loading = true
      this.error = null
      try {
        const response = await axios.get(`/agmin/api/${modelName.toLowerCase()}`)
        this.data = response.data
      } catch (error) {
        this.error = error instanceof Error ? error.message : 'Failed to fetch data'
        console.error('Error fetching data:', error)
      } finally {
        this.loading = false
      }
    },

    async createItem(modelName: string, formData: FormData) {
      this.loading = true
      this.error = null
      try {
        const response = await axios.post(`/agmin/api/${modelName.toLowerCase()}`, formData)
        this.data.push(response.data)
        return response.data
      } catch (error) {
        this.error = error instanceof Error ? error.message : 'Failed to create item'
        console.error('Error creating item:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async updateItem(modelName: string, id: number, formData: FormData) {
      this.loading = true
      this.error = null
      try {
        const response = await axios.put(`/agmin/api/${modelName.toLowerCase()}/${id}`, formData)
        const index = this.data.findIndex(item => item.id === id)
        if (index !== -1) {
          this.data[index] = response.data
        }
        return response.data
      } catch (error) {
        this.error = error instanceof Error ? error.message : 'Failed to update item'
        console.error('Error updating item:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async deleteItem(modelName: string, id: number) {
      this.loading = true
      this.error = null
      try {
        await axios.delete(`/agmin/api/${modelName.toLowerCase()}/${id}`)
        this.data = this.data.filter(item => item.id !== id)
      } catch (error) {
        this.error = error instanceof Error ? error.message : 'Failed to delete item'
        console.error('Error deleting item:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async searchItems(modelName: string, term: string): Promise<SearchResult[]> {
      this.loading = true
      this.error = null
      try {
        const response = await axios.get(`/agmin/api/${modelName.toLowerCase()}/search`, {
          params: { q: term }
        })
        return response.data
      } catch (error) {
        this.error = error instanceof Error ? error.message : 'Failed to search items'
        console.error('Error searching items:', error)
        throw error
      } finally {
        this.loading = false
      }
    }
  }
}) 