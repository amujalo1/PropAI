/**
 * Change Create page — ITIL Change Management
 */
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useCreateChange, useProperties } from '@/hooks'

export function ChangeCreate() {
  const navigate = useNavigate()
  const createMutation = useCreateChange()
  const { data: propertiesData } = useProperties(100, 0)
  const [error, setError] = useState('')

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    change_type: 'NORMAL',
    priority: 'P3',
    risk: 'MEDIUM',
    justification: '',
    implementation_plan: '',
    backout_plan: '',
    test_plan: '',
    scheduled_start: '',
    scheduled_end: '',
    property_id: '',
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

    if (!formData.title || !formData.description || !formData.justification) {
      setError('Title, description, and justification are required')
      return
    }

    try {
      const payload: Record<string, any> = { ...formData }
      // Remove empty optional fields
      if (!payload.property_id) delete payload.property_id
      if (!payload.scheduled_start) delete payload.scheduled_start
      if (!payload.scheduled_end) delete payload.scheduled_end

      await createMutation.mutateAsync(payload)
      navigate('/changes')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create change')
    }
  }

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-2">New Change Request</h1>
      <p className="text-gray-500 mb-8">ITIL Change Management — submit a planned change for review</p>

      <div className="max-w-3xl bg-white p-8 rounded shadow">
        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          {/* Title */}
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

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description *</label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              rows={3}
              className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
              required
            />
          </div>

          {/* Justification */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Justification *</label>
            <textarea
              name="justification"
              value={formData.justification}
              onChange={handleChange}
              rows={2}
              placeholder="Why is this change needed?"
              className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
              required
            />
          </div>

          {/* Type / Priority / Risk */}
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Change Type</label>
              <select
                name="change_type"
                value={formData.change_type}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
              >
                <option value="STANDARD">Standard</option>
                <option value="NORMAL">Normal</option>
                <option value="EMERGENCY">Emergency</option>
              </select>
            </div>
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

          {/* Property */}
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

          {/* Schedule */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Scheduled Start</label>
              <input
                type="datetime-local"
                name="scheduled_start"
                value={formData.scheduled_start}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Scheduled End</label>
              <input
                type="datetime-local"
                name="scheduled_end"
                value={formData.scheduled_end}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>

          {/* Plans */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Implementation Plan</label>
            <textarea
              name="implementation_plan"
              value={formData.implementation_plan}
              onChange={handleChange}
              rows={2}
              placeholder="Step-by-step implementation approach"
              className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Backout Plan</label>
            <textarea
              name="backout_plan"
              value={formData.backout_plan}
              onChange={handleChange}
              rows={2}
              placeholder="How to roll back if something goes wrong"
              className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Test Plan</label>
            <textarea
              name="test_plan"
              value={formData.test_plan}
              onChange={handleChange}
              rows={2}
              placeholder="How to verify the change was successful"
              className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
            />
          </div>

          <div className="flex gap-4 pt-2">
            <button
              type="submit"
              disabled={createMutation.isPending}
              className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
            >
              {createMutation.isPending ? 'Creating...' : 'Create Change'}
            </button>
            <button
              type="button"
              onClick={() => navigate('/changes')}
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
