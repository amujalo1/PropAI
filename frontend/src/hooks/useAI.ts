/**
 * AI hooks
 */
import { useMutation, useQuery } from '@tanstack/react-query'
import apiClient from '@/services/api'

export const useValuation = () => {
  return useMutation({
    mutationFn: async (property_id: string) => {
      const response = await apiClient.post('/ai/valuation', { property_id })
      return response.data
    },
  })
}

export const useMarketAnalysis = () => {
  return useMutation({
    mutationFn: async (data: { location: string; property_type: string }) => {
      const response = await apiClient.post('/ai/market-analysis', data)
      return response.data
    },
  })
}

export const useRiskAssessment = () => {
  return useMutation({
    mutationFn: async (property_id: string) => {
      const response = await apiClient.post('/ai/risk-assessment', { property_id })
      return response.data
    },
  })
}

export const usePricePrediction = () => {
  return useMutation({
    mutationFn: async (data: { property_id: string; months_ahead: number }) => {
      const response = await apiClient.post('/ai/price-prediction', data)
      return response.data
    },
  })
}

export const useAIInsights = () => {
  return useQuery({
    queryKey: ['ai-insights'],
    queryFn: async () => {
      const response = await apiClient.get('/ai/insights/summary')
      return response.data
    },
  })
}
