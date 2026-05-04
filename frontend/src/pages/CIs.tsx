/**
 * CMDB / CI list page — ITIL Service Asset & Configuration Management
 *
 * Lists all Configuration Items in the CMDB with filtering by type, status,
 * region, and hierarchy level.
 */
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useCIs } from '@/hooks'
import { Table } from '@/components/Table'
import { CI } from '@/types'

const STATUS_COLORS: Record<string, string> = {
  ACTIVE: 'bg-emerald-100 text-emerald-700',
  INACTIVE: 'bg-gray-100 text-gray-700',
  MAINTENANCE: 'bg-yellow-100 text-yellow-700',
  RETIRED: 'bg-gray-200 text-gray-600',
  PLANNED: 'bg-blue-100 text-blue-700',
}

const TYPE_COLORS: Record<string, string> = {
  Location: 'bg-purple-100 text-purple-700',
  Complex: 'bg-indigo-100 text-indigo-700',
  Building: 'bg-blue-100 text-blue-700',
  Property: 'bg-green-100 text-green-700',
  Component: 'bg-orange-100 text-orange-700',
}

export function CIs() {
  const navigate = useNavigate()
  const [limit] = useState(20)
  const [offset, setOffset] = useState(0)
  const [typeFilter, setTypeFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')

  const filters: Record<string, string> = {}
  if (typeFilter) filters.type = typeFilter
  if (statusFilter) filters.status = statusFilter

  const { data, isLoading } = useCIs(limit, offset, filters)

  const columns = [
    {
      key: 'ci_id',
      label: 'CI ID',
      render: (row: CI) => (
        <span className="font-mono text-sm text-blue-700">{row.ci_id}</span>
      ),
    },
    {
      key: 'name',
      label: 'Name',
      render: (row: CI) => row.name ?? <span className="text-gray-400">—</span>,
    },
    {
      key: 'type',
      label: 'Type',
      render: (row: CI) => (
        <span className={`px-2 py-1 rounded text-xs font-semibold ${TYPE_COLORS[row.type] ?? ''}`}>
          {row.type}
        </span>
      ),
    },
    {
      key: 'hierarchy_level',
      label: 'Level',
      render: (row: CI) => <span className="text-sm">L{row.hierarchy_level}</span>,
    },
    { key: 'region', label: 'Region' },
    {
      key: 'status',
      label: 'Status',
      render: (row: CI) => (
        <span className={`px-2 py-1 rounded text-xs font-semibold ${STATUS_COLORS[row.status] ?? ''}`}>
          {row.status}
        </span>
      ),
    },
  ]

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold">CMDB</h1>
          <p className="text-gray-500 mt-1">
            ITIL SACM — Configuration Items in hierarchy: Location → Complex → Building → Property → Component
          </p>
        </div>
        <button
          onClick={() => navigate('/cmdb/create')}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          New CI
        </button>
      </div>

      {/* Filters */}
      <div className="flex gap-4 mb-6 bg-white p-4 rounded shadow">
        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1">Type</label>
          <select
            value={typeFilter}
            onChange={e => { setTypeFilter(e.target.value); setOffset(0) }}
            className="px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
          >
            <option value="">All types</option>
            <option value="Location">Location</option>
            <option value="Complex">Complex</option>
            <option value="Building">Building</option>
            <option value="Property">Property</option>
            <option value="Component">Component</option>
          </select>
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1">Status</label>
          <select
            value={statusFilter}
            onChange={e => { setStatusFilter(e.target.value); setOffset(0) }}
            className="px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
          >
            <option value="">All statuses</option>
            <option value="ACTIVE">Active</option>
            <option value="INACTIVE">Inactive</option>
            <option value="MAINTENANCE">Maintenance</option>
            <option value="RETIRED">Retired</option>
            <option value="PLANNED">Planned</option>
          </select>
        </div>
      </div>

      {isLoading ? (
        <div className="text-center py-8">Loading...</div>
      ) : !data?.data?.length ? (
        <div className="bg-white rounded shadow p-6">
          <p className="text-gray-500">
            No configuration items yet. Create your first CI or seed test data via <code className="bg-gray-100 px-1">POST /test/seed</code>.
          </p>
        </div>
      ) : (
        <div>
          <Table
            columns={columns}
            data={data.data}
            onRowClick={(row: CI) => navigate(`/cmdb/${row.id}`)}
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
