/**
 * Sidebar navigation
 */
import { useLocation, Link } from 'react-router-dom'

interface NavItem {
  path: string
  label: string
  icon?: string
  matchPrefix?: boolean
}

const NAV_ITEMS: NavItem[] = [
  { path: '/dashboard', label: 'Dashboard' },
  { path: '/properties', label: 'Properties', matchPrefix: true },
  { path: '/changes', label: 'Changes', matchPrefix: true },
  { path: '/incidents', label: 'Incidents', matchPrefix: true },
  { path: '/ai', label: '🤖 AI Center' },
  { path: '/profile', label: 'My Profile' },
]

export function Sidebar() {
  const location = useLocation()

  const isActive = (item: NavItem) => {
    if (item.matchPrefix) {
      return location.pathname.startsWith(item.path)
    }
    return location.pathname === item.path
  }

  return (
    <aside className="w-64 bg-gray-800 text-white flex flex-col">
      <div className="p-4 border-b border-gray-700">
        <span className="text-lg font-bold text-white">PropAI</span>
        <p className="text-xs text-gray-400 mt-0.5">ITIL Service Management</p>
      </div>
      <nav className="p-4 flex-1">
        <ul className="space-y-1">
          {NAV_ITEMS.map(item => (
            <li key={item.path}>
              <Link
                to={item.path}
                className={`block px-3 py-2 rounded text-sm transition-colors ${
                  isActive(item)
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                }`}
              >
                {item.label}
              </Link>
            </li>
          ))}
        </ul>

        {/* ITIL section labels */}
        <div className="mt-6 pt-4 border-t border-gray-700">
          <p className="text-xs text-gray-500 uppercase tracking-wider px-3 mb-2">ITIL Processes</p>
          <ul className="space-y-1">
            <li>
              <Link
                to="/changes"
                className={`block px-3 py-2 rounded text-sm transition-colors ${
                  location.pathname.startsWith('/changes')
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                }`}
              >
                Change Management
              </Link>
            </li>
            <li>
              <Link
                to="/incidents"
                className={`block px-3 py-2 rounded text-sm transition-colors ${
                  location.pathname.startsWith('/incidents')
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                }`}
              >
                Incident Management
              </Link>
            </li>
          </ul>
        </div>
      </nav>
    </aside>
  )
}
