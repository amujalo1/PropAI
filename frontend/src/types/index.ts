/**
 * Type definitions for PropAI frontend
 */

export interface User {
  id: string
  email: string
  name: string
  role: 'admin' | 'data_steward' | 'ci_owner' | 'agent'
  created_at: string
  updated_at: string
}

export interface Property {
  id: string
  name: string
  type: 'residential' | 'commercial' | 'land'
  location: string
  status: 'DRAFT' | 'PENDING_REVIEW' | 'ACTIVE' | 'RESERVED' | 'SOLD' | 'RENTED' | 'SUSPENDED' | 'ARCHIVED'
  price: number
  description?: string
  created_at: string
  updated_at: string
}

export interface Incident {
  id: string
  title: string
  description: string
  property_id: string
  priority: 'P1' | 'P2' | 'P3' | 'P4'
  status: 'OPEN' | 'IN_PROGRESS' | 'RESOLVED' | 'CLOSED'
  created_at: string
  updated_at: string
}

export interface CI {
  id: string
  ci_id: string
  type: 'Location' | 'Complex' | 'Building' | 'Property' | 'Component'
  region: string
  sequence: number
  hierarchy_level: number
  parent_id?: string
  created_at: string
  updated_at: string
}

export interface Valuation {
  estimated_value: number
  currency: string
  note: string
}

export interface ApiResponse<T> {
  data: T
}

export interface ApiListResponse<T> {
  data: T[]
  pagination: {
    total: number
    limit: number
    offset: number
  }
}

export interface ApiError {
  error: string
  details?: Record<string, string>
}
