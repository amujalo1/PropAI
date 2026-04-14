/**
 * User profile hooks
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import apiClient from '@/services/api'

export const useMe = () => {
  return useQuery({
    queryKey: ['me'],
    queryFn: async () => {
      const response = await apiClient.get('/users/me')
      return response.data
    },
    retry: false,
  })
}

export const useUpdateMe = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (data: { name: string }) => {
      const response = await apiClient.put('/users/me', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['me'] })
    },
  })
}
