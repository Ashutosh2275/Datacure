import { useState, useEffect } from 'react'
import { Card, Loading, Error } from '../components/Common'
import { adminService } from '../services/api'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

function ReportsPage() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [trends, setTrends] = useState([])
  const [performance, setPerformance] = useState(null)

  useEffect(() => {
    const loadReports = async () => {
      try {
        setLoading(true)
        const [trendsRes, perfRes] = await Promise.all([
          adminService.getTrends({ period: 'monthly' }),
          adminService.getSystemPerformance(),
        ])
        setTrends(trendsRes.data.data || [])
        setPerformance(perfRes.data.data)
      } catch (err) {
        setError(err.response?.data?.message || 'Failed to load reports')
      } finally {
        setLoading(false)
      }
    }
    loadReports()
  }, [])

  if (loading) return <Loading />
  if (error) return <Error message={error} />

  return (
    <div className="container-custom py-8">
      <h1 className="text-3xl font-bold mb-2">Reports & Analytics</h1>
      <p className="text-gray-600 mb-6">System reports and performance analytics</p>

      {/* KPIs */}
      {performance && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <Card className="p-6">
            <p className="text-sm text-gray-600">API Response Time</p>
            <p className="text-2xl font-bold">{performance.api_response_time || 0}ms</p>
          </Card>

          <Card className="p-6">
            <p className="text-sm text-gray-600">Database Queries</p>
            <p className="text-2xl font-bold">{performance.db_queries || 0}</p>
          </Card>

          <Card className="p-6">
            <p className="text-sm text-gray-600">Cache Hit Rate</p>
            <p className="text-2xl font-bold">{performance.cache_hit_rate || 0}%</p>
          </Card>

          <Card className="p-6">
            <p className="text-sm text-gray-600">Error Rate</p>
            <p className="text-2xl font-bold text-red-600">{performance.error_rate || 0}%</p>
          </Card>
        </div>
      )}

      {/* Trends Chart */}
      {trends.length > 0 && (
        <Card title="System Trends" className="mb-6">
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={trends}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="patients" stroke="#0ea5e9" />
              <Line type="monotone" dataKey="appointments" stroke="#10b981" />
              <Line type="monotone" dataKey="revenue" stroke="#f59e0b" />
            </LineChart>
          </ResponsiveContainer>
        </Card>
      )}

      {/* Additional Reports */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="System Health">
          <div className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Database</span>
                <span className="text-sm text-green-600">Healthy</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-green-600 h-2 rounded-full" style={{ width: '95%' }}></div>
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">API Server</span>
                <span className="text-sm text-green-600">Healthy</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-green-600 h-2 rounded-full" style={{ width: '98%' }}></div>
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Storage</span>
                <span className="text-sm text-yellow-600">Warning</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-yellow-600 h-2 rounded-full" style={{ width: '75%' }}></div>
              </div>
            </div>
          </div>
        </Card>

        <Card title="Recent Activity">
          <div className="space-y-3 text-sm">
            <div className="flex items-center justify-between py-2 border-b">
              <span>System backup completed</span>
              <span className="text-gray-500">2 hours ago</span>
            </div>
            <div className="flex items-center justify-between py-2 border-b">
              <span>Database optimization</span>
              <span className="text-gray-500">5 hours ago</span>
            </div>
            <div className="flex items-center justify-between py-2">
              <span>User permissions updated</span>
              <span className="text-gray-500">1 day ago</span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}

export default ReportsPage
