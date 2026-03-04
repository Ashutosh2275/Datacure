import { useEffect, useState } from 'react'
import { useAuthStore, useDashboardStore } from '../store'
import { adminService } from '../services/api'
import { Card, Loading, Error } from '../components/Common'
import { Users, Calendar, DollarSign, TrendingUp } from 'lucide-react'

function DashboardPage() {
  const { user } = useAuthStore()
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        const response = await adminService.getDashboard()
        setStats(response.data.data)
      } catch (err) {
        setError(err.response?.data?.message || 'Failed to load dashboard')
      } finally {
        setLoading(false)
      }
    }

    if (user?.role === 'admin') {
      loadDashboard()
    } else {
      setLoading(false)
    }
  }, [user])

  if (loading) return <Loading />
  if (error && user?.role === 'admin') return <Error message={error} />

  return (
    <div className="container-custom py-8">
      {/* Welcome */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Welcome, {user?.name}!</h1>
        <p className="text-gray-600 mt-2">Here's what's happening in your hospital today</p>
      </div>

      {/* Key Metrics */}
      {user?.role === 'admin' && stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="p-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Total Patients</p>
                <p className="text-3xl font-bold">{stats.summary?.total_patients || 0}</p>
              </div>
              <div className="p-3 bg-blue-100 rounded-lg">
                <Users className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Appointments Today</p>
                <p className="text-3xl font-bold">{stats.summary?.appointments_today || 0}</p>
              </div>
              <div className="p-3 bg-green-100 rounded-lg">
                <Calendar className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Pending Payments</p>
                <p className="text-3xl font-bold">{stats.summary?.pending_payments || 0}</p>
              </div>
              <div className="p-3 bg-orange-100 rounded-lg">
                <DollarSign className="w-6 h-6 text-orange-600" />
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">High Risk Patients</p>
                <p className="text-3xl font-bold">{stats.summary?.high_risk_patients || 0}</p>
              </div>
              <div className="p-3 bg-red-100 rounded-lg">
                <TrendingUp className="w-6 h-6 text-red-600" />
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Appointments */}
        <Card title="Today's Appointments" className="lg:col-span-2">
          <div className="space-y-4">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="flex items-start justify-between p-3 border rounded-lg hover:bg-gray-50">
                <div className="flex-1">
                  <p className="font-medium">Patient Name</p>
                  <p className="text-sm text-gray-500">Doctor: Dr. Name</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium">10:{i}0 AM</p>
                  <span className="inline-block px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">Scheduled</span>
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Quick Actions */}
        <Card title="Quick Actions">
          <div className="space-y-3">
            <button className="btn btn-primary btn-md w-full text-left">+ New Patient</button>
            <button className="btn btn-secondary btn-md w-full text-left">+ New Appointment</button>
            <button className="btn btn-secondary btn-md w-full text-left">+ Create Invoice</button>
            <button className="btn btn-secondary btn-md w-full text-left">📊 View Reports</button>
          </div>
        </Card>
      </div>

      {/* Additional Info */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        <Card title="Bed Occupancy">
          <div className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">ICU Ward</span>
                <span className="text-sm text-gray-600">85%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-primary-600 h-2 rounded-full" style={{ width: '85%' }}></div>
              </div>
            </div>
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">General Ward</span>
                <span className="text-sm text-gray-600">60%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-green-600 h-2 rounded-full" style={{ width: '60%' }}></div>
              </div>
            </div>
          </div>
        </Card>

        <Card title="System Alerts">
          <div className="space-y-3">
            <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
              <p className="text-sm font-medium">5 medicines expiring soon</p>
              <p className="text-xs text-gray-600">Check inventory</p>
            </div>
            <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm font-medium">3 failed login attempts</p>
              <p className="text-xs text-gray-600">Review security logs</p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}

export default DashboardPage
