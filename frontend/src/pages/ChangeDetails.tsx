/**
 * Change Details page — ITIL Change Management
 */
import { useParams, useNavigate } from 'react-router-dom'
import {
  useChange,
  useSubmitChange,
  useApproveChange,
  useRejectChange,
  useStartChange,
  useCompleteChange,
  useFailChange,
  useCloseChange,
} from '@/hooks'
import { Change } from '@/types'

const STATUS_COLORS: Record<string, string> = {
  DRAFT: 'bg-gray-100 text-gray-700',
  SUBMITTED: 'bg-blue-100 text-blue-700',
  APPROVED: 'bg-green-100 text-green-700',
  REJECTED: 'bg-red-100 text-red-700',
  IN_PROGRESS: 'bg-yellow-100 text-yellow-700',
  COMPLETED: 'bg-emerald-100 text-emerald-700',
  FAILED: 'bg-red-200 text-red-800',
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

export function ChangeDetails() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { data: change, isLoading } = useChange(id!)

  const submitMutation = useSubmitChange()
  const approveMutation = useApproveChange()
  const rejectMutation = useRejectChange()
  const startMutation = useStartChange()
  const completeMutation = useCompleteChange()
  const failMutation = useFailChange()
  const closeMutation = useCloseChange()

  if (isLoading) return <div className="p-8 text-center">Loading...</div>
  if (!change) return <div className="p-8 text-center">Change not found</div>

  const isPending =
    submitMutation.isPending ||
    approveMutation.isPending ||
    rejectMutation.isPending ||
    startMutation.isPending ||
    completeMutation.isPending ||
    failMutation.isPending ||
    closeMutation.isPending

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex justify-between items-start mb-8">
        <div>
          <h1 className="text-3xl font-bold">{change.title}</h1>
          <div className="flex items-center gap-3 mt-2">
            <span className={`px-3 py-1 rounded-full text-sm font-semibold ${STATUS_COLORS[change.status] ?? ''}`}>
              {change.status}
            </span>
            <span className="text-sm text-gray-500">{change.change_type} change</span>
            <span className="text-sm text-gray-500">Priority: {change.priority}</span>
            <span className="text-sm text-gray-500">Risk: {change.risk}</span>
          </div>
        </div>
        <button
          onClick={() => navigate('/changes')}
          className="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400"
        >
          Back
        </button>
      </div>

      {/* Lifecycle actions */}
      <div className="flex flex-wrap gap-2 mb-8">
        {change.status === 'DRAFT' && (
          <button
            onClick={() => submitMutation.mutate(id!)}
            disabled={isPending}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 text-sm"
          >
            Submit for Approval
          </button>
        )}
        {change.status === 'SUBMITTED' && (
          <>
            <button
              onClick={() => approveMutation.mutate(id!)}
              disabled={isPending}
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50 text-sm"
            >
              Approve
            </button>
            <button
              onClick={() => rejectMutation.mutate(id!)}
              disabled={isPending}
              className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50 text-sm"
            >
              Reject
            </button>
          </>
        )}
        {change.status === 'APPROVED' && (
          <button
            onClick={() => startMutation.mutate(id!)}
            disabled={isPending}
            className="px-4 py-2 bg-yellow-600 text-white rounded hover:bg-yellow-700 disabled:opacity-50 text-sm"
          >
            Start Implementation
          </button>
        )}
        {change.status === 'IN_PROGRESS' && (
          <>
            <button
              onClick={() => completeMutation.mutate(id!)}
              disabled={isPending}
              className="px-4 py-2 bg-emerald-600 text-white rounded hover:bg-emerald-700 disabled:opacity-50 text-sm"
            >
              Mark Completed
            </button>
            <button
              onClick={() => failMutation.mutate(id!)}
              disabled={isPending}
              className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50 text-sm"
            >
              Mark Failed
            </button>
          </>
        )}
        {(change.status === 'COMPLETED' || change.status === 'FAILED') && (
          <button
            onClick={() => closeMutation.mutate(id!)}
            disabled={isPending}
            className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 disabled:opacity-50 text-sm"
          >
            Close
          </button>
        )}
      </div>

      {/* Details */}
      <div className="bg-white p-8 rounded shadow space-y-6">
        <Field label="Description" value={change.description} />
        <Field label="Justification" value={change.justification} />
        <Field label="Implementation Plan" value={change.implementation_plan} />
        <Field label="Backout Plan" value={change.backout_plan} />
        <Field label="Test Plan" value={change.test_plan} />

        <div className="grid grid-cols-2 gap-6 pt-4 border-t">
          <Field
            label="Scheduled Start"
            value={change.scheduled_start ? new Date(change.scheduled_start).toLocaleString() : undefined}
          />
          <Field
            label="Scheduled End"
            value={change.scheduled_end ? new Date(change.scheduled_end).toLocaleString() : undefined}
          />
          <Field
            label="Actual Start"
            value={change.actual_start ? new Date(change.actual_start).toLocaleString() : undefined}
          />
          <Field
            label="Actual End"
            value={change.actual_end ? new Date(change.actual_end).toLocaleString() : undefined}
          />
          <Field label="Created" value={new Date(change.created_at).toLocaleString()} />
          <Field label="Updated" value={new Date(change.updated_at).toLocaleString()} />
        </div>

        {/* Affected CIs */}
        {change.affected_cis?.length > 0 && (
          <div className="pt-4 border-t">
            <h3 className="text-sm font-medium text-gray-500 mb-3">Affected Configuration Items</h3>
            <ul className="space-y-2">
              {change.affected_cis.map(assoc => (
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
