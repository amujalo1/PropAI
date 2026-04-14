/**
 * Incident Details page
 */
import { useParams, useNavigate } from 'react-router-dom'
import { useIncident } from '@/hooks'

export function IncidentDetails() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { data: incident, isLoading } = useIncident(id!)

  if (isLoading) {
    return <div className="p-8 text-center">Loading...</div>
  }

  if (!incident) {
    return <div className="p-8 text-center">Incident not found</div>
  }

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">{incident.title}</h1>
        <button
          onClick={() => navigate('/incidents')}
          className="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400"
        >
          Back
        </button>
      </div>

      <div className="bg-white p-8 rounded shadow">
        <div className="grid grid-cols-2 gap-6">
          <div>
            <h3 className="text-sm font-medium text-gray-500">Priority</h3>
            <p className="text-lg font-semibold">{incident.priority}</p>
          </div>
          <div>
            <h3 className="text-sm font-medium text-gray-500">Status</h3>
            <p className="text-lg font-semibold">{incident.status}</p>
          </div>
          <div className="col-span-2">
            <h3 className="text-sm font-medium text-gray-500">Description</h3>
            <p className="text-lg">{incident.description}</p>
          </div>
          <div>
            <h3 className="text-sm font-medium text-gray-500">Created</h3>
            <p className="text-lg">{new Date(incident.created_at).toLocaleDateString()}</p>
          </div>
          <div>
            <h3 className="text-sm font-medium text-gray-500">Updated</h3>
            <p className="text-lg">{new Date(incident.updated_at).toLocaleDateString()}</p>
          </div>
        </div>
      </div>
    </div>
  )
}
