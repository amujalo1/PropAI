/**
 * Incident Details page — ITIL Incident Management
 */
import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useIncident, useStartIncident, useResolveIncident, useCloseIncident } from '@/hooks'

const STATUS_COLORS: Record<string, string> = {
  DRAFT: 'bg-gray-100 text-gray-700',
  SUBMITTED: 'bg-blue-100 text-blue-700',
  IN_PROGRESS: 'bg-yellow-100 text-yellow-700',
  COMPLETED: 'bg-emerald-100 text-emerald-700',
  CLOSED: 'bg-gray-200 text-gray-600',
}

function Field({ label, value }: { label: string; value?: string | null }) {
  if (!value) return null
  return (
    <div>
      <h3 className="text-sm font-medium text-gray-500">{label}</h3>
      <p className="mt-1 text-gray-900 whitespace-pre-wrap">{value}</p>
    </div>
  )
}

export function IncidentDetails() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { data: incident, isLoading } = useIncident(id!)
  const startMutation = useStartIncident()
  const resolveMutation = useResolveIncident()
  const closeMutation = useCloseIncident()
  const [resolution, setResolution] = useState('')
  const [showResolveForm, setShowResolveForm] = useState(false)

  if (isLoading) return <div className="p-8 text-center">Loading...</div>
  if (!incident) return <div className="p-8 text-center">Incident not found</div>

  const isPending = startMutation.isPending || resolveMutation.isPending || closeMutation.isPending

  const handleResolve = async () => {
    if (!resolution.trim()) return
    await resolveMutation.mutateAsync({ id: id!, resolution })
    setShowResolveForm(false)
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex justify-between items-start mb-8">
        <div>
          <div className="flex items-center gap-3 mb-1">
            {incident.incident_number && (
              <span className="font-mono text-sm bg-gray-100 px-2 py-1 rounded text-gray-600">
                {incident.incident_number}
              </span>
            )}
            <span className={`px-3 py-1 rounded-full text-sm font-semibold ${STATUS_COLORS[incident.status] ?? ''}`}>
              {incident.status}
            </span>
          </div>
          <h1 className="text-3xl font-bold">{incident.title}</h1>
          <div className="flex gap-4 mt-2 text-sm text-gray-500">
            <span>Priority: <strong>{incident.priority}</strong></span>
            <span>Impact: <strong>{incident.impact}</strong></span>
            <span>Urgency: <strong>{incident.urgency}</strong></span>
            <span>Category: <strong>{incident.category}</strong></span>
          </div>
        </div>
        <button
          onClick={() => navigate('/incidents')}
          className="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400"
        >
          Back
        </button>
      </div>

      {/* Lifecycle actions */}
      <div className="flex flex-wrap gap-2 mb-8">
        {incident.status === 'SUBMITTED' && (
          <button
            onClick={() => startMutation.mutate(id!)}
            disabled={isPending}
            className="px-4 py-2 bg-yellow-600 text-white rounded hover:bg-yellow-700 disabled:opacity-50 text-sm"
          >
            Start Investigation
          </button>
        )}
        {incident.status === 'IN_PROGRESS' && !showResolveForm && (
          <button
            onClick={() => setShowResolveForm(true)}
            className="px-4 py-2 bg-emerald-600 text-white rounded hover:bg-emerald-700 text-sm"
          >
            Resolve
          </button>
        )}
        {incident.status === 'COMPLETED' && (
          <button
            onClick={() => closeMutation.mutate(id!)}
            disabled={isPending}
            className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 disabled:opacity-50 text-sm"
          >
            Close Incident
          </button>
        )}
      </div>

      {/* Resolve form */}
      {showResolveForm && (
        <div className="mb-8 p-4 bg-emerald-50 border border-emerald-200 rounded">
          <h3 className="font-medium text-emerald-800 mb-2">Resolution Details</h3>
          <textarea
            value={resolution}
            onChange={e => setResolution(e.target.value)}
            rows={3}
            placeholder="Describe how the incident was resolved..."
            className="w-full px-3 py-2 border border-emerald-300 rounded focus:outline-none focus:border-emerald-500"
          />
          <div className="flex gap-2 mt-2">
            <button
              onClick={handleResolve}
              disabled={!resolution.trim() || isPending}
              className="px-4 py-2 bg-emerald-600 text-white rounded hover:bg-emerald-700 disabled:opacity-50 text-sm"
            >
              {isPending ? 'Resolving...' : 'Confirm Resolution'}
            </button>
            <button
              onClick={() => setShowResolveForm(false)}
              className="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400 text-sm"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Details */}
      <div className="bg-white p-8 rounded shadow space-y-6">
        <Field label="Description" value={incident.description} />
        <Field label="Justification" value={incident.justification} />
        <Field label="Resolution" value={incident.resolution} />
        <Field label="Root Cause" value={incident.root_cause} />

        <div className="grid grid-cols-2 gap-6 pt-4 border-t">
          <Field label="Created" value={new Date(incident.created_at).toLocaleString()} />
          <Field label="Updated" value={new Date(incident.updated_at).toLocaleString()} />
          {incident.resolved_at && (
            <Field label="Resolved At" value={new Date(incident.resolved_at).toLocaleString()} />
          )}
        </div>

        {/* Affected CIs */}
        {incident.affected_cis?.length > 0 && (
          <div className="pt-4 border-t">
            <h3 className="text-sm font-medium text-gray-500 mb-3">Affected Configuration Items</h3>
            <ul className="space-y-2">
              {incident.affected_cis.map(assoc => (
                <li key={assoc.id} className="flex items-start gap-3 p-3 bg-gray-50 rounded">
                  <span className="font-mono text-sm text-blue-700">{assoc.ci_id}</span>
                  {assoc.impact_description && (
                    <span className="text-sm text-gray-600">— {assoc.impact_description}</span>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}
