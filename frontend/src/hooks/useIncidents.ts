/**
 * ITIL Incident Management hooks
 * Incidents are a specialised subtype of Change.
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import apiClient from '@/services/api'
import { Incident } from '@/types'

// ---------------------------------------------------------------------------
// Queries
// ---------------------------------------------------------------------------

export const useIncidents = (limit = 10, offset = 0, filters?: Record<string, string>) => {
  return useQuery({
    queryKey: ['incidents', limit, offset, filters],
    queryFn: async () => {
      const response = await apiClient.get('/incidents', {
        params: { limit, offset, ...filters },
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
      return response.data as Incident
    },
    enabled: !!id,
  })
}

// ---------------------------------------------------------------------------
// Mutations
// ---------------------------------------------------------------------------

export const useCreateIncident = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (data: Partial<Incident>) => {
      const response = await apiClient.post('/incidents', data)
      return response.data as Incident
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['incidents'] })
    },
  })
}

export const useUpdateIncident = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, ...data }: Partial<Incident> & { id: string }) => {
      const response = await apiClient.put(`/incidents/${id}`, data)
      return response.data as Incident
    },
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['incidents'] })
      queryClient.invalidateQueries({ queryKey: ['incident', variables.id] })
    },
  })
}

// ---------------------------------------------------------------------------
// Lifecycle transitions
// ---------------------------------------------------------------------------

export const useStartIncident = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      const response = await apiClient.post(`/incidents/${id}/start`)
      return response.data as Incident
    },
    onSuccess: (_data, id) => {
      queryClient.invalidateQueries({ queryKey: ['incidents'] })
      queryClient.invalidateQueries({ queryKey: ['incident', id] })
    },
  })
}

export const useResolveIncident = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, resolution }: { id: string; resolution: string }) => {
      const response = await apiClient.post(`/incidents/${id}/resolve`, null, {
        params: { resolution },
      })
      return response.data as Incident
    },
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['incidents'] })
      queryClient.invalidateQueries({ queryKey: ['incident', variables.id] })
    },
  })
}

export const useCloseIncident = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      const response = await apiClient.post(`/incidents/${id}/close`)
      return response.data as Incident
    },
    onSuccess: (_data, id) => {
      queryClient.invalidateQueries({ queryKey: ['incidents'] })
      queryClient.invalidateQueries({ queryKey: ['incident', id] })
    },
  })
}

// ---------------------------------------------------------------------------
// Affected CIs
// ---------------------------------------------------------------------------

export const useAddIncidentCi = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ incidentId, ciId, impactDescription }: {
      incidentId: string
      ciId: string
      impactDescription?: string
    }) => {
      const response = await apiClient.post(`/incidents/${incidentId}/cis`, {
        ci_id: ciId,
        impact_description: impactDescription,
      })
      return response.data
    },
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['incident', variables.incidentId] })
    },
  })
}
