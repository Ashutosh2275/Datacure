import { useState, useEffect } from 'react'
import { Plus, Edit2, Trash2 } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { wardService } from '../services/api'
import { Card, EmptyState, Alert, Modal, Loading, Error } from '../components/Common'

function WardsPage() {
  const navigate = useNavigate()
  const [wards, setWards] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const [deleteModal, setDeleteModal] = useState({ isOpen: false, wardId: null })
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    const loadWards = async () => {
      try {
        setLoading(true)
        const response = await wardService.listWards({ limit: 100 })
        setWards(response.data.data || [])
      } catch (err) {
        setError(err.response?.data?.message || 'Failed to load wards')
      } finally {
        setLoading(false)
      }
    }
    loadWards()
  }, [])

  const handleDelete = async () => {
    try {
      setDeleting(true)
      setWards(wards.filter((w) => w.id !== deleteModal.wardId))
      setSuccess('Ward deleted successfully!')
      setDeleteModal({ isOpen: false, wardId: null })
      setTimeout(() => setSuccess(null), 3000)
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to delete ward')
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
        <div><h1 className="text-3xl font-bold">Wards</h1><p className="text-gray-600">Manage wards and beds</p></div>
        <button onClick={() => navigate('/wards/new')} className="btn btn-primary btn-md flex items-center gap-2"><Plus className="w-5 h-5" />New Ward</button>
      </div>

      {wards.length === 0 ? (
        <Card><EmptyState title="No wards" message="Create your first ward" action={<button onClick={() => navigate('/wards/new')} className="btn btn-primary btn-md">Create Ward</button>} /></Card>
      ) : (
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-6 py-3 text-left text-sm font-medium">Ward Name</th>
                  <th className="px-6 py-3 text-left text-sm font-medium">Type</th>
                  <th className="px-6 py-3 text-left text-sm font-medium">Total Beds</th>
                  <th className="px-6 py-3 text-left text-sm font-medium">Available Beds</th>
                  <th className="px-6 py-3 text-left text-sm font-medium">Floor</th>
                  <th className="px-6 py-3 text-left text-sm font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {wards.map((ward) => (
                  <tr key={ward.id} className="border-b hover:bg-gray-50">
                    <td className="px-6 py-4 font-medium">{ward.name}</td>
                    <td className="px-6 py-4">{ward.ward_type}</td>
                    <td className="px-6 py-4">{ward.total_beds}</td>
                    <td className="px-6 py-4">
                      <span className={`${ward.available_beds > 0 ? 'text-green-600' : 'text-red-600'} font-semibold`}>
                        {ward.available_beds || 0}
                      </span>
                    </td>
                    <td className="px-6 py-4">{ward.floor_number}</td>
                    <td className="px-6 py-4 flex gap-3">
                      <button 
                        onClick={() => navigate(`/wards/${ward.id}`)} 
                        className="text-blue-600 hover:text-blue-700"
                        title="Edit"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button 
                        onClick={() => setDeleteModal({ isOpen: true, wardId: ward.id })}
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
        </Card>
      )}

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={deleteModal.isOpen}
        title="Delete Ward"
        onClose={() => setDeleteModal({ isOpen: false, wardId: null })}
        actions={[
          <button
            key="cancel"
            onClick={() => setDeleteModal({ isOpen: false, wardId: null })}
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
        <p>Are you sure you want to delete this ward? This action cannot be undone.</p>
      </Modal>
    </div>
  )
}

export default WardsPage
