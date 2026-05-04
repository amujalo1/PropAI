/**
 * CI details page — ITIL SACM
 *
 * Shows CI attributes, hierarchy ancestors, child CIs, and any
 * Changes/Incidents that affect this CI.
 */
import { useParams, useNavigate, Link } from 'react-router-dom'
import { useCI, useCITree, useCIHierarchy, useCIChanges, useDeleteCI } from '@/hooks'

const STATUS_COLORS: Record<string, string> = {
  ACTIVE: 'bg-emerald-100 text-emerald-700',
  INACTIVE: 'bg-gray-100 text-gray-700',
  MAINTENANCE: 'bg-yellow-100 text-yellow-700',
  RETIRED: 'bg-gray-200 text-gray-600',
  PLANNED: 'bg-blue-100 text-blue-700',
}

function Field({ label, value }: { label: string; value?: string | null }) {
  if (!value) return null
  return (
    <div>
      <h3 className="text-sm font-medium text-gray-500">{label}</h3>
      <p className="mt-1 text-gray-900 whitespace-pre-wrap">{value}</p>
    </div>
  )
}

interface TreeNode {
  id: string
  ci_id: string
  name?: string
  type: string
  status: string
  level: number
  children: TreeNode[]
}

function TreeView({ node, currentId }: { node: TreeNode; currentId: string }) {
  return (
    <ul className="ml-4 border-l border-gray-200 pl-4 space-y-1">
      {node.children.map(child => (
        <li key={child.id}>
          <Link
            to={`/cmdb/${child.id}`}
            className={`text-sm hover:underline ${child.id === currentId ? 'font-bold text-blue-700' : 'text-gray-700'}`}
          >
            <span className="font-mono text-xs text-gray-500 mr-2">L{child.level}</span>
            {child.ci_id} — {child.name ?? child.type}
          </Link>
          {child.children.length > 0 && <TreeView node={child} currentId={currentId} />}
        </li>
      ))}
    </ul>
  )
}

export function CIDetails() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { data: ci, isLoading } = useCI(id!)
  const { data: hierarchy } = useCIHierarchy(ci?.ci_id ?? '')
  const { data: tree } = useCITree(ci?.ci_id ?? '')
  const { data: changes } = useCIChanges(id!)
  const deleteMutation = useDeleteCI()

  if (isLoading) return <div className="p-8 text-center">Loading...</div>
  if (!ci) return <div className="p-8 text-center">CI not found</div>

  const handleDelete = async () => {
    if (!window.confirm(`Delete CI ${ci.ci_id}? This cannot be undone.`)) return
    try {
      await deleteMutation.mutateAsync(id!)
      navigate('/cmdb')
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete CI')
    }
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex justify-between items-start mb-6">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <span className="font-mono text-sm bg-gray-100 px-2 py-1 rounded text-blue-700">
              {ci.ci_id}
            </span>
            <span className={`px-3 py-1 rounded-full text-sm font-semibold ${STATUS_COLORS[ci.status] ?? ''}`}>
              {ci.status}
            </span>
            <span className="px-3 py-1 rounded-full text-sm bg-gray-100 text-gray-700">
              {ci.type} · L{ci.hierarchy_level}
            </span>
          </div>
          <h1 className="text-3xl font-bold">{ci.name ?? ci.ci_id}</h1>
          <p className="text-sm text-gray-500 mt-1">Region: {ci.region} · Sequence: {ci.sequence}</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => navigate('/cmdb')}
            className="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400"
          >
            Back
          </button>
          <button
            onClick={handleDelete}
            disabled={deleteMutation.isPending}
            className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
          >
            Delete
          </button>
        </div>
      </div>

      {/* Hierarchy breadcrumb */}
      {hierarchy && hierarchy.length > 1 && (
        <div className="mb-6 bg-white p-4 rounded shadow">
          <h3 className="text-sm font-medium text-gray-500 mb-2">Hierarchy Path</h3>
          <div className="flex flex-wrap items-center gap-2 text-sm">
            {hierarchy.map((node, idx) => (
              <div key={node.id} className="flex items-center gap-2">
                {idx > 0 && <span className="text-gray-400">›</span>}
                {node.id === ci.id ? (
                  <span className="font-bold text-blue-700">{node.name ?? node.ci_id}</span>
                ) : (
                  <Link to={`/cmdb/${node.id}`} className="text-blue-600 hover:underline">
                    {node.name ?? node.ci_id}
                  </Link>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Attributes */}
        <div className="bg-white p-6 rounded shadow space-y-4">
          <h2 className="text-lg font-semibold border-b pb-2">Attributes</h2>
          <Field label="Description" value={ci.description} />
          <Field label="Version" value={ci.version} />
          <Field label="Serial Number" value={ci.serial_number} />
          <Field label="Location Detail" value={ci.location_detail} />
          <div className="grid grid-cols-2 gap-4 pt-2 border-t">
            <Field label="Created" value={new Date(ci.created_at).toLocaleString()} />
            <Field label="Updated" value={new Date(ci.updated_at).toLocaleString()} />
          </div>
        </div>

        {/* Subtree */}
        <div className="bg-white p-6 rounded shadow">
          <h2 className="text-lg font-semibold border-b pb-2 mb-4">Child CIs</h2>
          {tree && tree.children.length > 0 ? (
            <TreeView node={tree} currentId={ci.id} />
          ) : (
            <p className="text-sm text-gray-500">No child CIs.</p>
          )}
        </div>
      </div>

      {/* Affecting Changes/Incidents */}
      <div className="bg-white p-6 rounded shadow mt-6">
        <h2 className="text-lg font-semibold border-b pb-2 mb-4">
          Related Changes &amp; Incidents
        </h2>
        {Array.isArray(changes) && changes.length > 0 ? (
          <ul className="space-y-2">
            {changes.map((c: any) => (
              <li key={c.id} className="p-3 bg-gray-50 rounded flex items-center justify-between">
                <div>
                  <Link
                    to={c.record_type === 'incident' ? `/incidents/${c.id}` : `/changes/${c.id}`}
                    className="text-blue-600 hover:underline font-medium"
                  >
                    {c.title}
                  </Link>
                  <div className="text-xs text-gray-500 mt-1">
                    {c.record_type === 'incident' ? 'Incident' : 'Change'} · {c.status} · {c.priority}
                  </div>
                </div>
                <span className="text-xs text-gray-500">
                  {new Date(c.created_at).toLocaleDateString()}
                </span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-gray-500">No related changes or incidents.</p>
        )}
      </div>
    </div>
  )
}
