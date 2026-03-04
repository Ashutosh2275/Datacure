import { useState, useEffect } from 'react'
import { Plus, Calendar } from 'lucide-react'
import { appointmentService } from '../services/api'
import { Card, Loading, Error, Pagination, EmptyState } from '../components/Common'

function AppointmentsPage() {
  const [appointments, setAppointments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [page, setPage] = useState(1)

  useEffect(() => {
    const loadAppointments = async () => {
      try {
        const response = await appointmentService.listAppointments({ page, limit: 10 })
        setAppointments(response.data.data.appointments || [])
      } catch (err) {
        setError(err.response?.data?.message || 'Failed to load appointments')
      } finally {
        setLoading(false)
      }
    }
    loadAppointments()
  }, [page])

  if (loading) return <Loading />
  if (error) return <Error message={error} />

  return (
    <div className="container-custom py-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold">Appointments</h1>
          <p className="text-gray-600">Manage patient appointments</p>
        </div>
        <button className="btn btn-primary btn-md flex items-center gap-2">
          <Plus className="w-5 h-5" />
          New Appointment
        </button>
      </div>

      <Card>
        {appointments.length === 0 ? (
          <EmptyState
            icon={Calendar}
            title="No appointments"
            message="Schedule your first appointment"
            action={<button className="btn btn-primary btn-md">Book Appointment</button>}
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-6 py-3 text-left text-sm font-medium">Patient</th>
                  <th className="px-6 py-3 text-left text-sm font-medium">Doctor</th>
                  <th className="px-6 py-3 text-left text-sm font-medium">Date</th>
                  <th className="px-6 py-3 text-left text-sm font-medium">Time</th>
                  <th className="px-6 py-3 text-left text-sm font-medium">Status</th>
                  <th className="px-6 py-3 text-left text-sm font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {appointments.map((apt) => (
                  <tr key={apt.id} className="border-b hover:bg-gray-50">
                    <td className="px-6 py-4">{apt.patient_name}</td>
                    <td className="px-6 py-4">{apt.doctor_name}</td>
                    <td className="px-6 py-4">{apt.appointment_date}</td>
                    <td className="px-6 py-4">{apt.appointment_time}</td>
                    <td className="px-6 py-4"><span className="badge badge-info">{apt.status}</span></td>
                    <td className="px-6 py-4"><button className="text-primary-600 text-sm font-medium">View</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {appointments.length > 0 && <Pagination page={page} totalPages={5} onPageChange={setPage} />}
    </div>
  )
}

export default AppointmentsPage
