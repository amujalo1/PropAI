/**
 * Property Details page
 */
import { useParams, useNavigate } from 'react-router-dom'
import { useProperty, useDeleteProperty, useUpdateProperty } from '@/hooks'
import { useState } from 'react'
import { PropertyStatus } from '@/types'

const STATUS_COLORS: Record<string, string> = {
  DRAFT: 'bg-gray-100 text-gray-700',
  PENDING_REVIEW: 'bg-yellow-100 text-yellow-700',
  ACTIVE: 'bg-green-100 text-green-700',
  RESERVED: 'bg-blue-100 text-blue-700',
  SOLD: 'bg-purple-100 text-purple-700',
  RENTED: 'bg-indigo-100 text-indigo-700',
  SUSPENDED: 'bg-orange-100 text-orange-700',
  ARCHIVED: 'bg-gray-200 text-gray-500',
}

const ALL_STATUSES: PropertyStatus[] = [
  'DRAFT', 'PENDING_REVIEW', 'ACTIVE', 'RESERVED', 'SOLD', 'RENTED', 'SUSPENDED', 'ARCHIVED',
]

export function PropertyDetails() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { data: property, isLoading } = useProperty(id!)
  const deleteMutation = useDeleteProperty()
  const updateMutation = useUpdateProperty()
  const [error, setError] = useState('')
  const [statusChanging, setStatusChanging] = useState(false)

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this property?')) {
      try {
        await deleteMutation.mutateAsync(id!)
        navigate('/properties')
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to delete property')
      }
    }
  }

  const handleStatusChange = async (newStatus: PropertyStatus) => {
    if (newStatus === property?.status) return
    setStatusChanging(true)
    try {
      await updateMutation.mutateAsync({ id: id!, data: { status: newStatus } })
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update status')
    } finally {
      setStatusChanging(false)
    }
  }

  if (isLoading) return <div className="p-8 text-center">Loading...</div>
  if (!property) return <div className="p-8 text-center">Property not found</div>

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">{property.name}</h1>
        <div className="flex gap-2">
          <button
            onClick={() => navigate(`/properties/${id}/edit`)}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Edit
          </button>
          <button
            onClick={handleDelete}
            disabled={deleteMutation.isPending}
            className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
          >
            {deleteMutation.isPending ? 'Deleting...' : 'Delete'}
          </button>
          <button
            onClick={() => navigate('/properties')}
            className="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400"
          >
            Back
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <div className="bg-white p-8 rounded shadow">
        <div className="grid grid-cols-2 gap-6">
          <div>
            <h3 className="text-sm font-medium text-gray-500">Type</h3>
            <p className="text-lg font-semibold capitalize">{property.type.toLowerCase()}</p>
          </div>

          {/* Status with inline changer */}
          <div>
            <h3 className="text-sm font-medium text-gray-500 mb-1">Status</h3>
            <div className="flex items-center gap-3">
              <span className={`px-3 py-1 rounded-full text-sm font-semibold ${STATUS_COLORS[property.status] ?? ''}`}>
                {property.status.replace('_', ' ')}
              </span>
              <select
                value={property.status}
                onChange={e => handleStatusChange(e.target.value as PropertyStatus)}
                disabled={statusChanging || updateMutation.isPending}
                className="text-sm border border-gray-300 rounded px-2 py-1 focus:outline-none focus:border-blue-500 disabled:opacity-50"
              >
                {ALL_STATUSES.map(s => (
                  <option key={s} value={s}>{s.replace('_', ' ')}</option>
                ))}
              </select>
              {statusChanging && <span className="text-xs text-gray-400">Saving...</span>}
            </div>
          </div>

          <div>
            <h3 className="text-sm font-medium text-gray-500">Location</h3>
            <p className="text-lg font-semibold">{property.location}</p>
          </div>
          <div>
            <h3 className="text-sm font-medium text-gray-500">Price</h3>
            <p className="text-lg font-semibold">€{Number(property.price).toLocaleString()}</p>
          </div>
          <div className="col-span-2">
            <h3 className="text-sm font-medium text-gray-500">Description</h3>
            <p className="text-lg">{property.description || 'No description'}</p>
          </div>
          <div>
            <h3 className="text-sm font-medium text-gray-500">Created</h3>
            <p className="text-lg">{new Date(property.created_at).toLocaleDateString()}</p>
          </div>
          <div>
            <h3 className="text-sm font-medium text-gray-500">Updated</h3>
            <p className="text-lg">{new Date(property.updated_at).toLocaleDateString()}</p>
          </div>
        </div>
      </div>
    </div>
  )
}
