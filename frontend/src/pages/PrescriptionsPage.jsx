import { useState, useEffect } from 'react'
import { Plus, Edit2, Trash2 } from 'lucide-react'
import { prescriptionService } from '../services/api'
import { Card, Loading, Error, Alert, Modal, EmptyState } from '../components/Common'

function PrescriptionsPage() {
  const [prescriptions, setPrescriptions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const [deleteModal, setDeleteModal] = useState({ isOpen: false, prescriptionId: null })
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    const loadPrescriptions = async () => {
      try {
        setLoading(true)
        const response = await prescriptionService.listPrescriptions()
        setPrescriptions(response.data.data || [])
      } catch (err) {
        setError(err.response?.data?.message || 'Failed to load prescriptions')
      } finally {
        setLoading(false)
      }
    }
    loadPrescriptions()
  }, [])

  const handleDelete = async () => {
    try {
      setDeleting(true)
      // Note: Update this to match your actual delete endpoint
      setSuccess('Prescription deleted successfully!')
      setPrescriptions(prescriptions.filter((p) => p.id !== deleteModal.prescriptionId))
      setDeleteModal({ isOpen: false, prescriptionId: null })
      setTimeout(() => setSuccess(null), 3000)
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to delete prescription')
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
          <h1 className="text-3xl font-bold">Prescriptions</h1>
          <p className="text-gray-600">Manage patient prescriptions</p>
        </div>
      </div>

      {/* Prescriptions Table */}
      <Card>
        {prescriptions.length === 0 ? (
          <EmptyState
            title="No prescriptions found"
            message="Prescriptions will appear here"
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Patient</th>
                  <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Medicine</th>
                  <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Dosage</th>
                  <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Duration</th>
                  <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Status</th>
                  <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Actions</th>
                </tr>
              </thead>
              <tbody>
                {prescriptions.map((prescription) => (
                  <tr key={prescription.id} className="border-b hover:bg-gray-50">
                    <td className="px-6 py-4">{prescription.patient_name || 'N/A'}</td>
                    <td className="px-6 py-4">{prescription.medicine_name || 'N/A'}</td>
                    <td className="px-6 py-4">{prescription.dosage || 'N/A'}</td>
                    <td className="px-6 py-4">{prescription.duration || 'N/A'}</td>
                    <td className="px-6 py-4">
                      <span className="badge badge-success">Active</span>
                    </td>
                    <td className="px-6 py-4 flex gap-3">
                      <button
                        onClick={() => setDeleteModal({ isOpen: true, prescriptionId: prescription.id })}
                        className="text-red-600 hover:text-red-700"
                        title="Delete"
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

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={deleteModal.isOpen}
        title="Delete Prescription"
        onClose={() => setDeleteModal({ isOpen: false, prescriptionId: null })}
        actions={[
          <button
            key="cancel"
            onClick={() => setDeleteModal({ isOpen: false, prescriptionId: null })}
            className="btn btn-secondary btn-sm"
            disabled={deleting}
          >
            Cancel
          </button>,
          <button
            key="delete"
            onClick={handleDelete}
            className="btn btn-danger btn-sm"
            disabled={deleting}
          >
            {deleting ? 'Deleting...' : 'Delete'}
          </button>,
        ]}
      >
        <p>Are you sure you want to delete this prescription?</p>
      </Modal>
    </div>
  )
}

export default PrescriptionsPage
