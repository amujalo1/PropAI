/**
 * CI create page — ITIL SACM
 *
 * Creates a new Configuration Item. CI ID is auto-generated server-side
 * using the naming convention PROP-[TYPE]-[REGION]-[SEQUENCE].
 */
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useCreateCI, useCIs, useProperties } from '@/hooks'

export function CICreate() {
  const navigate = useNavigate()
  const createMutation = useCreateCI()
  const { data: parentCandidates } = useCIs(100, 0)
  const { data: propertiesData } = useProperties(100, 0)
  const [error, setError] = useState('')

  const [formData, setFormData] = useState({
    name: '',
    type: 'Property',
    status: 'ACTIVE',
    region: 'SA',
    description: '',
    parent_id: '',
    property_id: '',
    version: '',
    serial_number: '',
    location_detail: '',
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

    if (!formData.type || !formData.region) {
      setError('Type and region are required')
      return
    }

    try {
      const payload: Record<string, any> = { ...formData }
      // strip empty optional fields
      for (const key of ['parent_id', 'property_id', 'version', 'serial_number', 'location_detail', 'description', 'name']) {
        if (!payload[key]) delete payload[key]
      }
      await createMutation.mutateAsync(payload)
      navigate('/cmdb')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create CI')
    }
  }

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-2">New Configuration Item</h1>
      <p className="text-gray-500 mb-8">
        ITIL SACM — register a new asset in the CMDB. CI ID is auto-generated.
      </p>

      <div className="max-w-2xl bg-white p-8 rounded shadow">
        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder="e.g. Stan 3A, 68m², 2. sprat"
              className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">CI Type *</label>
              <select
                name="type"
                value={formData.type}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
                required
              >
                <option value="Location">Location (L1)</option>
                <option value="Complex">Complex (L2)</option>
                <option value="Building">Building (L3)</option>
                <option value="Property">Property (L4)</option>
                <option value="Component">Component (L5)</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Region *</label>
              <select
                name="region"
                value={formData.region}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
                required
              >
                <option value="SA">SA — Sarajevo</option>
                <option value="BL">BL — Banja Luka</option>
                <option value="MO">MO — Mostar</option>
                <option value="TZ">TZ — Tuzla</option>
                <option value="ZE">ZE — Zenica</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select
              name="status"
              value={formData.status}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
            >
              <option value="ACTIVE">Active</option>
              <option value="INACTIVE">Inactive</option>
              <option value="MAINTENANCE">Maintenance</option>
              <option value="RETIRED">Retired</option>
              <option value="PLANNED">Planned</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              rows={3}
              className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Parent CI</label>
            <select
              name="parent_id"
              value={formData.parent_id}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
            >
              <option value="">None (root-level CI)</option>
              {parentCandidates?.data?.map(ci => (
                <option key={ci.id} value={ci.id}>
                  L{ci.hierarchy_level} · {ci.ci_id} · {ci.name ?? ci.type}
                </option>
              ))}
            </select>
          </div>

          {formData.type === 'Property' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Linked Property</label>
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
          )}

          {formData.type === 'Component' && (
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Version</label>
                <input
                  type="text"
                  name="version"
                  value={formData.version}
                  onChange={handleChange}
                  placeholder="e.g. OTIS-2018"
                  className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Serial Number</label>
                <input
                  type="text"
                  name="serial_number"
                  value={formData.serial_number}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Location Detail</label>
            <input
              type="text"
              name="location_detail"
              value={formData.location_detail}
              onChange={handleChange}
              placeholder="e.g. Lamela A — podrum"
              className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
            />
          </div>

          <div className="flex gap-4 pt-2">
            <button
              type="submit"
              disabled={createMutation.isPending}
              className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
            >
              {createMutation.isPending ? 'Creating...' : 'Create CI'}
            </button>
            <button
              type="button"
              onClick={() => navigate('/cmdb')}
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
