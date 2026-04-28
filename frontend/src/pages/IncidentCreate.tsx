/**
 * Incident Create page — ITIL Incident Management
 */
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useCreateIncident, useProperties } from '@/hooks'

export function IncidentCreate() {
  const navigate = useNavigate()
  const createMutation = useCreateIncident()
  const { data: propertiesData } = useProperties(100, 0)
  const [error, setError] = useState('')

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    property_id: '',
    priority: 'P3',
    risk: 'MEDIUM',
    impact: 'MODERATE',
    urgency: 'MEDIUM',
    category: 'OTHER',
    justification: '',
  })

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!formData.title || !formData.description) {
      setError('Title and description are required')
      return
    }

    try {
      const payload: Record<string, any> = { ...formData }
      if (!payload.property_id) delete payload.property_id

      await createMutation.mutateAsync(payload)
      navigate('/incidents')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create incident')
    }
  }

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-2">Report Incident</h1>
      <p className="text-gray-500 mb-8">ITIL Incident Management — report an unplanned service disruption</p>

      <div className="max-w-2xl bg-white p-8 rounded shadow">
        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Title *</label>
            <input
              type="text"
              name="title"
              value={formData.title}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description *</label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              rows={4}
              className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Affected Property</label>
            <select
              name="property_id"
              value={formData.property_id}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
            >
              <option value="">None</option>
              {propertiesData?.data?.map((prop: any) => (
                <option key={prop.id} value={prop.id}>{prop.name}</option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
              <select
                name="priority"
                value={formData.priority}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
              >
                <option value="P1">P1 – Critical</option>
                <option value="P2">P2 – High</option>
                <option value="P3">P3 – Medium</option>
                <option value="P4">P4 – Low</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Risk</label>
              <select
                name="risk"
                value={formData.risk}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
              >
                <option value="LOW">Low</option>
                <option value="MEDIUM">Medium</option>
                <option value="HIGH">High</option>
                <option value="CRITICAL">Critical</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Impact</label>
              <select
                name="impact"
                value={formData.impact}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
              >
                <option value="EXTENSIVE">Extensive – whole organisation</option>
                <option value="SIGNIFICANT">Significant – department</option>
                <option value="MODERATE">Moderate – small group</option>
                <option value="MINOR">Minor – single user</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Urgency</label>
              <select
                name="urgency"
                value={formData.urgency}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
              >
                <option value="CRITICAL">Critical</option>
                <option value="HIGH">High</option>
                <option value="MEDIUM">Medium</option>
                <option value="LOW">Low</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
            <select
              name="category"
              value={formData.category}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
            >
              <option value="HARDWARE">Hardware</option>
              <option value="SOFTWARE">Software</option>
              <option value="NETWORK">Network</option>
              <option value="SECURITY">Security</option>
              <option value="FACILITY">Facility</option>
              <option value="SERVICE_REQUEST">Service Request</option>
              <option value="OTHER">Other</option>
            </select>
          </div>

          <div className="flex gap-4 pt-2">
            <button
              type="submit"
              disabled={createMutation.isPending}
              className="px-6 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
            >
              {createMutation.isPending ? 'Reporting...' : 'Report Incident'}
            </button>
            <button
              type="button"
              onClick={() => navigate('/incidents')}
              className="px-6 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
