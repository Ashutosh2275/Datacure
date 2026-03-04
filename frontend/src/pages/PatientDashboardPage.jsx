import { useState, useEffect } from 'react'
import { Card, Loading } from '../components/Common'

function PatientDashboardPage() {
  const [stats, setStats] = useState({
    upcomingAppointments: 0,
    activePrescriptions: 0,
    medicalRecords: 0,
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Simulate loading patient stats
    setTimeout(() => {
      setStats({
        upcomingAppointments: 0,
        activePrescriptions: 0,
        medicalRecords: 0,
      })
      setLoading(false)
    }, 500)
  }, [])

  if (loading) return <Loading />

  return (
    <div className="container-custom py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Patient Dashboard</h1>
        <p className="text-gray-600">Welcome to your health portal</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card>
          <div className="text-center">
            <div className="text-4xl font-bold text-primary-600">{stats.upcomingAppointments}</div>
            <p className="text-gray-600 mt-2">Upcoming Appointments</p>
          </div>
        </Card>
        <Card>
          <div className="text-center">
            <div className="text-4xl font-bold text-warning-600">{stats.activePrescriptions}</div>
            <p className="text-gray-600 mt-2">Active Prescriptions</p>
          </div>
        </Card>
        <Card>
          <div className="text-center">
            <div className="text-4xl font-bold text-secondary-600">{stats.medicalRecords}</div>
            <p className="text-gray-600 mt-2">Medical Records</p>
          </div>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card>
        <h2 className="text-xl font-bold mb-4">Recent Activity</h2>
        <div className="text-center text-gray-500 py-8">
          <p>No recent activity</p>
        </div>
      </Card>
    </div>
  )
}

export default PatientDashboardPage
