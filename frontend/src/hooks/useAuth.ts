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

/** Decode the JWT stored in localStorage and return the payload. */
function decodeToken(token: string): Record<string, any> | null {
  try {
    const payload = token.split('.')[1]
    return JSON.parse(atob(payload))
  } catch {
    return null
  }
}

/** Returns basic info about the currently logged-in user from the JWT. */
export const useCurrentUser = () => {
  const token = localStorage.getItem('token')
  if (!token) return null
  const payload = decodeToken(token)
  if (!payload) return null
  return {
    id: payload.sub as string,
    role: payload.role as string,
    isAdmin: payload.role === 'ADMIN',
  }
}
