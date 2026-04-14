/**
 * Dashboard page
 */
import { useProperties, useIncidents } from '@/hooks'
import { Table } from '@/components/Table'

export function Dashboard() {
  const { data: propertiesData } = useProperties(5, 0)
  const { data: incidentsData } = useIncidents(5, 0)

  const propertyColumns = [
    { key: 'name', label: 'Name' },
    { key: 'type', label: 'Type' },
    { key: 'status', label: 'Status' },
    { key: 'price', label: 'Price' },
  ]

  const incidentColumns = [
    { key: 'title', label: 'Title' },
    { key: 'priority', label: 'Priority' },
    { key: 'status', label: 'Status' },
  ]

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">Dashboard</h1>
      
      <div className="grid grid-cols-2 gap-4 mb-8">
        <div className="bg-white p-6 rounded shadow">
          <h2 className="text-xl font-semibold">Total Properties</h2>
          <p className="text-3xl font-bold text-blue-600">{propertiesData?.pagination?.total || 0}</p>
        </div>
        <div className="bg-white p-6 rounded shadow">
          <h2 className="text-xl font-semibold">Total Incidents</h2>
          <p className="text-3xl font-bold text-red-600">{incidentsData?.pagination?.total || 0}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-8">
        <div className="bg-white p-6 rounded shadow">
          <h2 className="text-2xl font-semibold mb-4">Recent Properties</h2>
          {propertiesData?.data?.length ? (
            <Table columns={propertyColumns} data={propertiesData.data} />
          ) : (
            <p className="text-gray-500">No properties yet</p>
          )}
        </div>

        <div className="bg-white p-6 rounded shadow">
          <h2 className="text-2xl font-semibold mb-4">Recent Incidents</h2>
          {incidentsData?.data?.length ? (
            <Table columns={incidentColumns} data={incidentsData.data} />
          ) : (
            <p className="text-gray-500">No incidents yet</p>
          )}
        </div>
      </div>
    </div>
  )
}
