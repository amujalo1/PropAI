/**
 * Authentication hooks
 */
import { useMutation } from '@tanstack/react-query'
import apiClient from '@/services/api'

export const useLogin = () => {
  return useMutation({
    mutationFn: async (credentials: { email: string; password: string }) => {
      const response = await apiClient.post('/auth/login', credentials)
      return response.data
    },
  })
}

export const useRegister = () => {
  return useMutation({
    mutationFn: async (data: { email: string; password: string; name: string }) => {
      const response = await apiClient.post('/auth/register', data)
      return response.data
    },
  })
}

export const useLogout = () => {
  return useMutation({
    mutationFn: async () => {
      const response = await apiClient.post('/auth/logout')
      return response.data
    },
  })
}
