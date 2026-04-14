/**
 * Property Details page
 */
import { useParams, useNavigate } from 'react-router-dom'
import { useProperty, useDeleteProperty } from '@/hooks'
import { useState } from 'react'

export function PropertyDetails() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { data: property, isLoading } = useProperty(id!)
  const deleteMutation = useDeleteProperty()
  const [error, setError] = useState('')

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

  if (isLoading) {
    return <div className="p-8 text-center">Loading...</div>
  }

  if (!property) {
    return <div className="p-8 text-center">Property not found</div>
  }

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">{property.name}</h1>
        <div className="space-x-2">
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
            <p className="text-lg font-semibold">{property.type}</p>
          </div>
          <div>
            <h3 className="text-sm font-medium text-gray-500">Status</h3>
            <p className="text-lg font-semibold">{property.status}</p>
          </div>
          <div>
            <h3 className="text-sm font-medium text-gray-500">Location</h3>
            <p className="text-lg font-semibold">{property.location}</p>
          </div>
          <div>
            <h3 className="text-sm font-medium text-gray-500">Price</h3>
            <p className="text-lg font-semibold">€{property.price.toLocaleString()}</p>
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
