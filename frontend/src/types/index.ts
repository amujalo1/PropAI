/**
 * Type definitions for PropAI
 */

export interface User {
  id: string
  email: string
  name: string
  role: 'ADMIN' | 'DATA_STEWARD' | 'CI_OWNER' | 'AGENT'
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

// ---------------------------------------------------------------------------
// ITIL Change Management
// ---------------------------------------------------------------------------

export type ChangeType = 'STANDARD' | 'NORMAL' | 'EMERGENCY'
export type ChangeStatus =
  | 'DRAFT'
  | 'SUBMITTED'
  | 'APPROVED'
  | 'REJECTED'
  | 'IN_PROGRESS'
  | 'COMPLETED'
  | 'FAILED'
  | 'CLOSED'
export type ChangePriority = 'P1' | 'P2' | 'P3' | 'P4'
export type ChangeRisk = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'

export interface ChangeCIAssociation {
  id: string
  change_id: string
  ci_id: string
  impact_description?: string
  created_at: string
}

export interface Change {
  id: string
  record_type: 'change' | 'incident'
  title: string
  description: string
  change_type: ChangeType
  status: ChangeStatus
  priority: ChangePriority
  risk: ChangeRisk
  justification?: string
  implementation_plan?: string
  backout_plan?: string
  test_plan?: string
  scheduled_start?: string
  scheduled_end?: string
  actual_start?: string
  actual_end?: string
  property_id?: string
  requested_by_id?: string
  assigned_to_id?: string
  approved_by_id?: string
  affected_cis: ChangeCIAssociation[]
  created_at: string
  updated_at: string
}

// ---------------------------------------------------------------------------
// ITIL Incident Management (extends Change)
// ---------------------------------------------------------------------------

export type IncidentImpact = 'EXTENSIVE' | 'SIGNIFICANT' | 'MODERATE' | 'MINOR'
export type IncidentUrgency = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW'
export type IncidentCategory =
  | 'HARDWARE'
  | 'SOFTWARE'
  | 'NETWORK'
  | 'SECURITY'
  | 'FACILITY'
  | 'SERVICE_REQUEST'
  | 'OTHER'

export interface Incident extends Change {
  record_type: 'incident'
  incident_number?: string
  impact: IncidentImpact
  urgency: IncidentUrgency
  category: IncidentCategory
  resolution?: string
  resolved_at?: string
  root_cause?: string
}

// ---------------------------------------------------------------------------
// ITIL SACM — Configuration Items
// ---------------------------------------------------------------------------

export type CIType = 'Location' | 'Complex' | 'Building' | 'Property' | 'Component'
export type CIStatus = 'ACTIVE' | 'INACTIVE' | 'MAINTENANCE' | 'RETIRED' | 'PLANNED'

export interface CI {
  id: string
  ci_id: string
  name?: string
  type: CIType
  status: CIStatus
  region: string
  sequence: number
  hierarchy_level: number
  description?: string
  owner_id?: string
  version?: string
  serial_number?: string
  location_detail?: string
  parent_id?: string
  property_id?: string
  created_at: string
  updated_at: string
}

// ---------------------------------------------------------------------------
// Generic API response wrappers
// ---------------------------------------------------------------------------

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
