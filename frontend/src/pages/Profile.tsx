/**
 * Profile page - user info, stats, recent activity
 */
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMe, useUpdateMe } from '@/hooks/useUser'
import { useProperties } from '@/hooks/useProperties'
import { useIncidents } from '@/hooks/useIncidents'

const ROLE_LABELS: Record<string, string> = {
  admin: 'Administrator',
  data_steward: 'Data Steward',
  ci_owner: 'CI Owner',
  agent: 'Agent',
}

const ROLE_COLORS: Record<string, string> = {
  admin: 'bg-red-100 text-red-800',
  data_steward: 'bg-purple-100 text-purple-800',
  ci_owner: 'bg-blue-100 text-blue-800',
  agent: 'bg-green-100 text-green-800',
}

export function Profile() {
  const navigate = useNavigate()
  const { data: user, isLoading: userLoading } = useMe()
  const { data: propertiesData } = useProperties(100, 0)
  const { data: incidentsData } = useIncidents(100, 0)
  const updateMutation = useUpdateMe()

  const [editing, setEditing] = useState(false)
  const [name, setName] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const handleEdit = () => {
    setName(user?.name || '')
    setEditing(true)
    setSuccess('')
    setError('')
  }

  const handleSave = async () => {
    if (!name.trim()) {
      setError('Name cannot be empty')
      return
    }
    try {
      await updateMutation.mutateAsync({ name })
      setEditing(false)
      setSuccess('Profile updated successfully')
    } catch {
      setError('Failed to update profile')
    }
  }

  // Stats
  const totalProperties = propertiesData?.pagination?.total || 0
  const totalIncidents = incidentsData?.pagination?.total || 0
  const openIncidents = incidentsData?.data?.filter((i: any) => i.status === 'OPEN').length || 0
  const activeProperties = propertiesData?.data?.filter((p: any) => p.status === 'ACTIVE').length || 0

  if (userLoading) {
    return <div className="p-8 text-center text-gray-500">Loading profile...</div>
  }

  return (
    <div className="p-8 max-w-4xl">
      <h1 className="text-3xl font-bold mb-8">My Profile</h1>

      {/* Profile Card */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-4">
            {/* Avatar */}
            <div className="w-16 h-16 rounded-full bg-blue-600 flex items-center justify-center text-white text-2xl font-bold">
              {user?.name?.charAt(0).toUpperCase() || '?'}
            </div>
            <div>
              {editing ? (
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="text-xl font-semibold border border-gray-300 rounded px-2 py-1 focus:outline-none focus:border-blue-500"
                    autoFocus
                  />
                  <button
                    onClick={handleSave}
                    disabled={updateMutation.isPending}
                    className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 disabled:opacity-50"
                  >
                    {updateMutation.isPending ? 'Saving...' : 'Save'}
                  </button>
                  <button
                    onClick={() => setEditing(false)}
                    className="px-3 py-1 bg-gray-200 text-gray-700 text-sm rounded hover:bg-gray-300"
                  >
                    Cancel
                  </button>
                </div>
              ) : (
                <h2 className="text-xl font-semibold">{user?.name}</h2>
              )}
              <p className="text-gray-500">{user?.email}</p>
              <span className={`inline-block mt-1 px-2 py-0.5 rounded text-xs font-medium ${ROLE_COLORS[user?.role] || 'bg-gray-100 text-gray-800'}`}>
                {ROLE_LABELS[user?.role] || user?.role}
              </span>
            </div>
          </div>
          {!editing && (
            <button
              onClick={handleEdit}
              className="px-4 py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 text-sm"
            >
              Edit Name
            </button>
          )}
        </div>

        {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
        {success && <p className="mt-3 text-sm text-green-600">{success}</p>}

        <div className="mt-4 pt-4 border-t border-gray-100 grid grid-cols-2 gap-4 text-sm text-gray-500">
          <div>
            <span className="font-medium text-gray-700">Member since:</span>{' '}
            {user?.created_at ? new Date(user.created_at).toLocaleDateString() : '-'}
          </div>
          <div>
            <span className="font-medium text-gray-700">Last updated:</span>{' '}
            {user?.updated_at ? new Date(user.updated_at).toLocaleDateString() : '-'}
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-4 text-center">
          <p className="text-3xl font-bold text-blue-600">{totalProperties}</p>
          <p className="text-sm text-gray-500 mt-1">Total Properties</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4 text-center">
          <p className="text-3xl font-bold text-green-600">{activeProperties}</p>
          <p className="text-sm text-gray-500 mt-1">Active Properties</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4 text-center">
          <p className="text-3xl font-bold text-orange-600">{totalIncidents}</p>
          <p className="text-sm text-gray-500 mt-1">Total Incidents</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4 text-center">
          <p className="text-3xl font-bold text-red-600">{openIncidents}</p>
          <p className="text-sm text-gray-500 mt-1">Open Incidents</p>
        </div>
      </div>

      {/* My Properties */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">My Properties</h3>
          <button
            onClick={() => navigate('/properties/create')}
            className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
          >
            + Add Property
          </button>
        </div>
        {propertiesData?.data?.length ? (
          <div className="space-y-2">
            {propertiesData.data.slice(0, 5).map((p: any) => (
              <div
                key={p.id}
                onClick={() => navigate(`/properties/${p.id}`)}
                className="flex items-center justify-between p-3 border border-gray-100 rounded hover:bg-gray-50 cursor-pointer"
              >
                <div>
                  <p className="font-medium">{p.name}</p>
                  <p className="text-sm text-gray-500">{p.location} · {p.type}</p>
                </div>
                <div className="text-right">
                  <p className="font-semibold">€{Number(p.price).toLocaleString()}</p>
                  <span className={`text-xs px-2 py-0.5 rounded ${
                    p.status === 'ACTIVE' ? 'bg-green-100 text-green-700' :
                    p.status === 'DRAFT' ? 'bg-gray-100 text-gray-600' :
                    p.status === 'SOLD' ? 'bg-blue-100 text-blue-700' :
                    'bg-yellow-100 text-yellow-700'
                  }`}>
                    {p.status}
                  </span>
                </div>
              </div>
            ))}
            {propertiesData.data.length > 5 && (
              <button
                onClick={() => navigate('/properties')}
                className="w-full text-center text-sm text-blue-600 hover:underline pt-2"
              >
                View all {totalProperties} properties →
              </button>
            )}
          </div>
        ) : (
          <p className="text-gray-500 text-sm">No properties yet.</p>
        )}
      </div>

      {/* Recent Incidents */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">Recent Incidents</h3>
          <button
            onClick={() => navigate('/incidents')}
            className="text-sm text-blue-600 hover:underline"
          >
            View all →
          </button>
        </div>
        {incidentsData?.data?.length ? (
          <div className="space-y-2">
            {incidentsData.data.slice(0, 5).map((i: any) => (
              <div
                key={i.id}
                onClick={() => navigate(`/incidents/${i.id}`)}
                className="flex items-center justify-between p-3 border border-gray-100 rounded hover:bg-gray-50 cursor-pointer"
              >
                <div>
                  <p className="font-medium">{i.title}</p>
                  <p className="text-sm text-gray-500">{new Date(i.created_at).toLocaleDateString()}</p>
                </div>
                <div className="flex gap-2">
                  <span className={`text-xs px-2 py-0.5 rounded font-medium ${
                    i.priority === 'P1' ? 'bg-red-100 text-red-700' :
                    i.priority === 'P2' ? 'bg-orange-100 text-orange-700' :
                    i.priority === 'P3' ? 'bg-yellow-100 text-yellow-700' :
                    'bg-gray-100 text-gray-600'
                  }`}>
                    {i.priority}
                  </span>
                  <span className={`text-xs px-2 py-0.5 rounded ${
                    i.status === 'OPEN' ? 'bg-red-50 text-red-600' :
                    i.status === 'RESOLVED' ? 'bg-green-50 text-green-600' :
                    'bg-gray-50 text-gray-600'
                  }`}>
                    {i.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-sm">No incidents yet.</p>
        )}
      </div>
    </div>
  )
}
