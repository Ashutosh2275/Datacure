import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Calendar, Edit2, Trash2 } from 'lucide-react'
import { appointmentService } from '../services/api'
import { Card, Loading, Error, Pagination, EmptyState, Alert, Modal } from '../components/Common'

function AppointmentsPage() {
  const navigate = useNavigate()
  const [appointments, setAppointments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const [page, setPage] = useState(1)
  const [deleteModal, setDeleteModal] = useState({ isOpen: false, appointmentId: null })
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    const loadAppointments = async () => {
      try {
        setLoading(true)
        const response = await appointmentService.listAppointments({ page, limit: 10 })
        setAppointments(response.data.data || [])
      } catch (err) {
        setError(err.response?.data?.message || 'Failed to load appointments')
      } finally {
        setLoading(false)
      }
    }
    loadAppointments()
  }, [page])

  const handleDelete = async () => {
    try {
      setDeleting(true)
      await appointmentService.cancelAppointment(deleteModal.appointmentId, 'Cancelled by user')
      setSuccess('Appointment cancelled successfully!')
      setAppointments(appointments.filter((a) => a.id !== deleteModal.appointmentId))
      setDeleteModal({ isOpen: false, appointmentId: null })
      setTimeout(() => setSuccess(null), 3000)
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to cancel appointment')
    } finally {
      setDeleting(false)
    }
  }

  if (loading) return <Loading />
  if (error) return <Error message={error} />

  return (
    <div className="container-custom py-8">
      {success && <Alert type="success" message={success} onClose={() => setSuccess(null)} className="mb-4" />}

      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold">Appointments</h1>
          <p className="text-gray-600">Manage patient appointments</p>
        </div>
        <button onClick={() => navigate('/appointments/new')} className="btn btn-primary btn-md flex items-center gap-2">
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
            action={<button onClick={() => navigate('/appointments/new')} className="btn btn-primary btn-md">Book Appointment</button>}
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
                  <th className="px-6 py-3 text-left text-sm font-medium">Type</th>
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
                    <td className="px-6 py-4">{apt.start_time}</td>
                    <td className="px-6 py-4 capitalize">{apt.appointment_type}</td>
                    <td className="px-6 py-4"><span className="badge badge-info">{apt.status}</span></td>
                    <td className="px-6 py-4 flex gap-3">
                      <button 
                        onClick={() => navigate(`/appointments/${apt.id}`)} 
                        className="text-blue-600 hover:text-blue-700"
                        title="Edit"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button 
                        onClick={() => setDeleteModal({ isOpen: true, appointmentId: apt.id })}
                        className="text-red-600 hover:text-red-700"
                        title="Cancel"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {appointments.length > 0 && <Pagination page={page} totalPages={5} onPageChange={setPage} />}

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={deleteModal.isOpen}
        title="Cancel Appointment"
        onClose={() => setDeleteModal({ isOpen: false, appointmentId: null })}
        actions={[
          <button
            key="cancel"
            onClick={() => setDeleteModal({ isOpen: false, appointmentId: null })}
            className="btn btn-secondary btn-sm"
            disabled={deleting}
          >
            Close
          </button>,
          <button
            key="delete"
            onClick={handleDelete}
            className="btn btn-danger btn-sm"
            disabled={deleting}
          >
            {deleting ? 'Cancelling...' : 'Cancel Appointment'}
          </button>,
        ]}
      >
        <p>Are you sure you want to cancel this appointment?</p>
      </Modal>
    </div>
  )
}

export default AppointmentsPage
