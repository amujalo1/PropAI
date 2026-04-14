/**
 * Incidents page
 */
import { useIncidents } from '@/hooks'
import { Table } from '@/components/Table'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export function Incidents() {
  const navigate = useNavigate()
  const [limit, setLimit] = useState(10)
  const [offset, setOffset] = useState(0)
  const { data, isLoading } = useIncidents(limit, offset)

  const columns = [
    { key: 'title', label: 'Title' },
    { key: 'priority', label: 'Priority' },
    { key: 'status', label: 'Status' },
    { key: 'created_at', label: 'Created' },
  ]

  const handleRowClick = (row: any) => {
    navigate(`/incidents/${row.id}`)
  }

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Incidents</h1>
        <button
          onClick={() => navigate('/incidents/create')}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Create Incident
        </button>
      </div>

      {isLoading ? (
        <div className="text-center py-8">Loading...</div>
      ) : data?.data?.length ? (
        <div>
          <Table columns={columns} data={data.data} onRowClick={handleRowClick} />
          <div className="mt-4 flex justify-between items-center">
            <span className="text-sm text-gray-600">
              Showing {offset + 1} to {Math.min(offset + limit, data.pagination.total)} of {data.pagination.total}
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
      ) : (
        <div className="bg-white rounded shadow p-4">
          <p className="text-gray-500">No incidents yet</p>
        </div>
      )}
    </div>
  )
}
