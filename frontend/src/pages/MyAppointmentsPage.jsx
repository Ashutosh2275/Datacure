import { useState, useEffect } from 'react'
import { Card, Loading, Error, Alert, EmptyState } from '../components/Common'

function MyAppointmentsPage() {
  const [appointments, setAppointments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const loadAppointments = async () => {
      try {
        setLoading(true)
        // Simulate loading patient's appointments
        setTimeout(() => {
          setAppointments([])
          setLoading(false)
        }, 500)
      } catch (err) {
        setError('Failed to load appointments')
        setLoading(false)
      }
    }
    loadAppointments()
  }, [])

  if (loading) return <Loading />
  if (error) return <Error message={error} />

  return (
    <div className="container-custom py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">My Appointments</h1>
        <p className="text-gray-600">View your scheduled appointments</p>
      </div>

      <Card>
        {appointments.length === 0 ? (
          <EmptyState
            title="No appointments scheduled"
            message="You don't have any scheduled appointments yet"
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Date</th>
                  <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Time</th>
                  <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Doctor</th>
                  <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Status</th>
                </tr>
              </thead>
              <tbody>
                {/* Appointments will appear here */}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  )
}

export default MyAppointmentsPage
