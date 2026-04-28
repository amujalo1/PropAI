import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useState, useEffect } from 'react'
import { Header } from '@/components/Header'
import { Sidebar } from '@/components/Sidebar'
import { Dashboard } from '@/pages/Dashboard'
import { Properties } from '@/pages/Properties'
import { PropertyCreate } from '@/pages/PropertyCreate'
import { PropertyDetails } from '@/pages/PropertyDetails'
import { PropertyEdit } from '@/pages/PropertyEdit'
import { Profile } from '@/pages/Profile'
import { AICenter } from '@/pages/AICenter'
import { Changes } from '@/pages/Changes'
import { ChangeCreate } from '@/pages/ChangeCreate'
import { ChangeDetails } from '@/pages/ChangeDetails'
import { Incidents } from '@/pages/Incidents'
import { IncidentCreate } from '@/pages/IncidentCreate'
import { IncidentDetails } from '@/pages/IncidentDetails'
import { Login } from '@/pages/Login'
import { Register } from '@/pages/Register'

const queryClient = new QueryClient()

function useAuth() {
  const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem('token'))

  useEffect(() => {
    const handleStorage = () => {
      setIsAuthenticated(!!localStorage.getItem('token'))
    }
    window.addEventListener('storage', handleStorage)
    window.addEventListener('auth-change', handleStorage)
    return () => {
      window.removeEventListener('storage', handleStorage)
      window.removeEventListener('auth-change', handleStorage)
    }
  }, [])

  return isAuthenticated
}

function App() {
  const isAuthenticated = useAuth()

  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        {isAuthenticated ? (
          <div className="flex h-screen">
            <Sidebar />
            <div className="flex-1 flex flex-col">
              <Header />
              <main className="flex-1 overflow-auto">
                <Routes>
                  <Route path="/" element={<Navigate to="/dashboard" replace />} />
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/properties" element={<Properties />} />
                  <Route path="/properties/create" element={<PropertyCreate />} />
                  <Route path="/properties/:id" element={<PropertyDetails />} />
                  <Route path="/properties/:id/edit" element={<PropertyEdit />} />
                  {/* ITIL Change Management */}
                  <Route path="/changes" element={<Changes />} />
                  <Route path="/changes/create" element={<ChangeCreate />} />
                  <Route path="/changes/:id" element={<ChangeDetails />} />
                  {/* ITIL Incident Management */}
                  <Route path="/incidents" element={<Incidents />} />
                  <Route path="/incidents/create" element={<IncidentCreate />} />
                  <Route path="/incidents/:id" element={<IncidentDetails />} />
                  <Route path="/profile" element={<Profile />} />
                  <Route path="/ai" element={<AICenter />} />
                  <Route path="*" element={<Navigate to="/dashboard" replace />} />
                </Routes>
              </main>
            </div>
          </div>
        ) : (
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="*" element={<Navigate to="/login" replace />} />
          </Routes>
        )}
      </Router>
    </QueryClientProvider>
  )
}

export default App
