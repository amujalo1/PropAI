/**
 * Incidents hooks
 */
import { useQuery, useMutation } from '@tanstack/react-query'
import apiClient from '@/services/api'
import { Incident } from '@/types'

export const useIncidents = (limit = 10, offset = 0) => {
  return useQuery({
    queryKey: ['incidents', limit, offset],
    queryFn: async () => {
      const response = await apiClient.get('/incidents', {
        params: { limit, offset },
      })
      return response.data
    },
  })
}

export const useIncident = (id: string) => {
  return useQuery({
    queryKey: ['incident', id],
    queryFn: async () => {
      const response = await apiClient.get(`/incidents/${id}`)
      return response.data
    },
  })
}

export const useCreateIncident = () => {
  return useMutation({
    mutationFn: async (data: Partial<Incident>) => {
      const response = await apiClient.post('/incidents', data)
      return response.data
    },
  })
}
