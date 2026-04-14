/**
 * Properties hooks
 */
import { useQuery, useMutation } from '@tanstack/react-query'
import apiClient from '@/services/api'
import { Property } from '@/types'

export const useProperties = (limit = 10, offset = 0) => {
  return useQuery({
    queryKey: ['properties', limit, offset],
    queryFn: async () => {
      const response = await apiClient.get('/properties', {
        params: { limit, offset },
      })
      return response.data
    },
  })
}

export const useProperty = (id: string) => {
  return useQuery({
    queryKey: ['property', id],
    queryFn: async () => {
      const response = await apiClient.get(`/properties/${id}`)
      return response.data
    },
  })
}

export const useCreateProperty = () => {
  return useMutation({
    mutationFn: async (data: Partial<Property>) => {
      const response = await apiClient.post('/properties', data)
      return response.data
    },
  })
}

export const useUpdateProperty = () => {
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<Property> }) => {
      const response = await apiClient.put(`/properties/${id}`, data)
      return response.data
    },
  })
}

export const useDeleteProperty = () => {
  return useMutation({
    mutationFn: async (id: string) => {
      const response = await apiClient.delete(`/properties/${id}`)
      return response.data
    },
  })
}
