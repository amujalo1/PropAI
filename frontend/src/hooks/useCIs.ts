/**
 * ITIL SACM (Service Asset & Configuration Management) hooks
 *
 * Manages Configuration Items (CIs) in the CMDB hierarchy:
 *   Location → Complex → Building → Property → Component
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import apiClient from '@/services/api'
import { CI, ApiListResponse } from '@/types'

// ---------------------------------------------------------------------------
// Queries
// ---------------------------------------------------------------------------

export const useCIs = (limit = 10, offset = 0, filters?: Record<string, string>) => {
  return useQuery({
    queryKey: ['cis', limit, offset, filters],
    queryFn: async () => {
      const response = await apiClient.get('/ci', {
        params: { limit, offset, ...filters },
      })
      return response.data as ApiListResponse<CI>
    },
  })
}

export const useCI = (id: string) => {
  return useQuery({
    queryKey: ['ci', id],
    queryFn: async () => {
      const response = await apiClient.get(`/ci/uuid/${id}`)
      return response.data as CI
    },
    enabled: !!id,
  })
}

interface CITreeNode {
  id: string
  ci_id: string
  name?: string
  type: string
  status: string
  level: number
  children: CITreeNode[]
}

export const useCITree = (ciId: string) => {
  return useQuery({
    queryKey: ['ci-tree', ciId],
    queryFn: async () => {
      const response = await apiClient.get(`/ci/tree/${ciId}`)
      return response.data as CITreeNode
    },
    enabled: !!ciId,
  })
}

export const useCIHierarchy = (ciId: string) => {
  return useQuery({
    queryKey: ['ci-hierarchy', ciId],
    queryFn: async () => {
      const response = await apiClient.get(`/ci/hierarchy/${ciId}`)
      return response.data as CITreeNode[]
    },
    enabled: !!ciId,
  })
}

export const useCIChanges = (id: string) => {
  return useQuery({
    queryKey: ['ci-changes', id],
    queryFn: async () => {
      const response = await apiClient.get(`/ci/uuid/${id}/changes`)
      return response.data
    },
    enabled: !!id,
  })
}

// ---------------------------------------------------------------------------
// Mutations
// ---------------------------------------------------------------------------

export const useCreateCI = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (data: Partial<CI>) => {
      const response = await apiClient.post('/ci', data)
      return response.data as CI
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cis'] })
    },
  })
}

export const useUpdateCI = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, ...data }: Partial<CI> & { id: string }) => {
      const response = await apiClient.put(`/ci/uuid/${id}`, data)
      return response.data as CI
    },
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['cis'] })
      queryClient.invalidateQueries({ queryKey: ['ci', variables.id] })
    },
  })
}

export const useDeleteCI = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/ci/uuid/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cis'] })
    },
  })
}
