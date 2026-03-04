import { Card, Loading } from '../components/Common'
import { useState, useEffect } from 'react'
import { auditService } from '../services/api'

function AuditPage() {
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadLogs = async () => {
      try {
        const response = await auditService.listAuditLogs({ limit: 50 })
        setLogs(response.data.data.logs || [])
      } catch (error) {
        console.error('Failed to load audit logs', error)
      } finally {
        setLoading(false)
      }
    }
    loadLogs()
  }, [])

  if (loading) return <Loading />

  return (
    <div className="container-custom py-8">
      <h1 className="text-3xl font-bold mb-6">Audit Logs</h1>

      <Card>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-medium">User</th>
                <th className="px-6 py-3 text-left text-sm font-medium">Action</th>
                <th className="px-6 py-3 text-left text-sm font-medium">Resource</th>
                <th className="px-6 py-3 text-left text-sm font-medium">Timestamp</th>
                <th className="px-6 py-3 text-left text-sm font-medium">Status</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log) => (
                <tr key={log.id} className="border-b hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm">{log.user_name}</td>
                  <td className="px-6 py-4 text-sm">{log.action}</td>
                  <td className="px-6 py-4 text-sm">{log.resource_type}</td>
                  <td className="px-6 py-4 text-sm">{log.timestamp}</td>
                  <td className="px-6 py-4 text-sm"><span className="badge badge-success">{log.status}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  )
}

export default AuditPage
