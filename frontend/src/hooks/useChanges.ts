/**
 * ITIL Change Management hooks
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import apiClient from '@/services/api'
import { Change } from '@/types'

// ---------------------------------------------------------------------------
// Queries
// ---------------------------------------------------------------------------

export const useChanges = (limit = 10, offset = 0, filters?: Record<string, string>) => {
  return useQuery({
    queryKey: ['changes', limit, offset, filters],
    queryFn: async () => {
      const response = await apiClient.get('/changes', {
        params: { limit, offset, ...filters },
      })
      return response.data
    },
  })
}

export const useChange = (id: string) => {
  return useQuery({
    queryKey: ['change', id],
    queryFn: async () => {
      const response = await apiClient.get(`/changes/${id}`)
      return response.data as Change
    },
    enabled: !!id,
  })
}

// ---------------------------------------------------------------------------
// Mutations
// ---------------------------------------------------------------------------

export const useCreateChange = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (data: Partial<Change>) => {
      const response = await apiClient.post('/changes', data)
      return response.data as Change
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['changes'] })
    },
  })
}

export const useUpdateChange = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, ...data }: Partial<Change> & { id: string }) => {
      const response = await apiClient.put(`/changes/${id}`, data)
      return response.data as Change
    },
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['changes'] })
      queryClient.invalidateQueries({ queryKey: ['change', variables.id] })
    },
  })
}

// ---------------------------------------------------------------------------
// Lifecycle transitions
// ---------------------------------------------------------------------------

const useChangeTransition = (action: string) => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      const response = await apiClient.post(`/changes/${id}/${action}`)
      return response.data as Change
    },
    onSuccess: (_data, id) => {
      queryClient.invalidateQueries({ queryKey: ['changes'] })
      queryClient.invalidateQueries({ queryKey: ['change', id] })
    },
  })
}

export const useSubmitChange = () => useChangeTransition('submit')
export const useApproveChange = () => useChangeTransition('approve')
export const useRejectChange = () => useChangeTransition('reject')
export const useStartChange = () => useChangeTransition('start')
export const useCompleteChange = () => useChangeTransition('complete')
export const useFailChange = () => useChangeTransition('fail')
export const useCloseChange = () => useChangeTransition('close')

// ---------------------------------------------------------------------------
// Affected CIs
// ---------------------------------------------------------------------------

export const useAddChangeCi = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ changeId, ciId, impactDescription }: {
      changeId: string
      ciId: string
      impactDescription?: string
    }) => {
      const response = await apiClient.post(`/changes/${changeId}/cis`, {
        ci_id: ciId,
        impact_description: impactDescription,
      })
      return response.data
    },
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['change', variables.changeId] })
    },
  })
}

export const useRemoveChangeCi = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ changeId, ciId }: { changeId: string; ciId: string }) => {
      await apiClient.delete(`/changes/${changeId}/cis/${ciId}`)
    },
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['change', variables.changeId] })
    },
  })
}
