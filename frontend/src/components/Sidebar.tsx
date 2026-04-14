/**
 * Sidebar component
 */
import { useLocation } from 'react-router-dom'

export function Sidebar() {
  const location = useLocation()

  const isActive = (path: string) => location.pathname === path

  return (
    <aside className="w-64 bg-gray-800 text-white">
      <nav className="p-4">
        <ul className="space-y-2">
          <li>
            <a
              href="/dashboard"
              className={`block p-2 rounded ${
                isActive('/dashboard') ? 'bg-blue-600' : 'hover:bg-gray-700'
              }`}
            >
              Dashboard
            </a>
          </li>
          <li>
            <a
              href="/properties"
              className={`block p-2 rounded ${
                isActive('/properties') ? 'bg-blue-600' : 'hover:bg-gray-700'
              }`}
            >
              Properties
            </a>
          </li>
          <li>
            <a
              href="/incidents"
              className={`block p-2 rounded ${
                isActive('/incidents') ? 'bg-blue-600' : 'hover:bg-gray-700'
              }`}
            >
              Incidents
            </a>
          </li>
          <li>
            <a
              href="/ai"
              className={`block p-2 rounded ${
                isActive('/ai') ? 'bg-blue-600' : 'hover:bg-gray-700'
              }`}
            >
              🤖 AI Center
            </a>
          </li>
          <li>
            <a
              href="/profile"
              className={`block p-2 rounded ${
                isActive('/profile') ? 'bg-blue-600' : 'hover:bg-gray-700'
              }`}
            >
              My Profile
            </a>
          </li>
        </ul>
      </nav>
    </aside>
  )
}
