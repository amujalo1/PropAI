/**
 * Changes list page — ITIL Change Management
 */
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useChanges } from '@/hooks'
import { Table } from '@/components/Table'
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

const RISK_COLORS: Record<string, string> = {
  LOW: 'text-green-600',
  MEDIUM: 'text-yellow-600',
  HIGH: 'text-orange-600',
  CRITICAL: 'text-red-600',
}

export function Changes() {
  const navigate = useNavigate()
  const [limit] = useState(10)
  const [offset, setOffset] = useState(0)
  const { data, isLoading } = useChanges(limit, offset)

  const columns = [
    { key: 'title', label: 'Title' },
    {
      key: 'change_type',
      label: 'Type',
      render: (row: Change) => (
        <span className="text-sm font-medium">{row.change_type}</span>
      ),
    },
    {
      key: 'priority',
      label: 'Priority',
      render: (row: Change) => (
        <span className="font-semibold">{row.priority}</span>
      ),
    },
    {
      key: 'risk',
      label: 'Risk',
      render: (row: Change) => (
        <span className={`font-semibold ${RISK_COLORS[row.risk] ?? ''}`}>{row.risk}</span>
      ),
    },
    {
      key: 'status',
      label: 'Status',
      render: (row: Change) => (
        <span className={`px-2 py-1 rounded text-xs font-semibold ${STATUS_COLORS[row.status] ?? ''}`}>
          {row.status}
        </span>
      ),
    },
    {
      key: 'created_at',
      label: 'Created',
      render: (row: Change) => new Date(row.created_at).toLocaleDateString(),
    },
  ]

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold">Changes</h1>
          <p className="text-gray-500 mt-1">ITIL Change Management — planned changes to services and assets</p>
        </div>
        <button
          onClick={() => navigate('/changes/create')}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          New Change
        </button>
      </div>

      {isLoading ? (
        <div className="text-center py-8">Loading...</div>
      ) : !data?.data?.length ? (
        <div className="bg-white rounded shadow p-6">
          <p className="text-gray-500">No changes yet. Create your first change request.</p>
        </div>
      ) : (
        <div>
          <Table
            columns={columns}
            data={data.data}
            onRowClick={(row: Change) => navigate(`/changes/${row.id}`)}
          />
          <div className="mt-4 flex justify-between items-center">
            <span className="text-sm text-gray-600">
              Showing {offset + 1}–{Math.min(offset + limit, data.pagination.total)} of {data.pagination.total}
            </span>
            <div className="space-x-2">
              <button
                onClick={() => setOffset(Math.max(0, offset - limit))}
                disabled={offset === 0}
                className="px-4 py-2 bg-gray-200 rounded disabled:opacity-50"
              >
                Previous
              </button>
              <button
                onClick={() => setOffset(offset + limit)}
                disabled={offset + limit >= data.pagination.total}
                className="px-4 py-2 bg-gray-200 rounded disabled:opacity-50"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
