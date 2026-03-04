import { useState, useEffect } from 'react'
import { Plus, Edit2, Trash2 } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { inventoryService } from '../services/api'
import { Card, EmptyState, Alert, Modal, Loading, Error } from '../components/Common'

function InventoryPage() {
  const navigate = useNavigate()
  const [medicines, setMedicines] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const [deleteModal, setDeleteModal] = useState({ isOpen: false, medicineId: null })
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    const loadMedicines = async () => {
      try {
        setLoading(true)
        const response = await inventoryService.listMedicines({ limit: 100 })
        setMedicines(response.data.data || [])
      } catch (err) {
        setError(err.response?.data?.message || 'Failed to load medicines')
      } finally {
        setLoading(false)
      }
    }
    loadMedicines()
  }, [])

  const handleDelete = async () => {
    try {
      setDeleting(true)
      setMedicines(medicines.filter((m) => m.id !== deleteModal.medicineId))
      setSuccess('Medicine deleted successfully!')
      setDeleteModal({ isOpen: false, medicineId: null })
      setTimeout(() => setSuccess(null), 3000)
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to delete medicine')
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
        <div><h1 className="text-3xl font-bold">Inventory</h1><p className="text-gray-600">Manage medicines and stock</p></div>
        <button onClick={() => navigate('/inventory/new')} className="btn btn-primary btn-md flex items-center gap-2"><Plus className="w-5 h-5" />Add Medicine</button>
      </div>

      {medicines.length === 0 ? (
        <Card><EmptyState title="No medicines" message="Add medicines to inventory" action={<button onClick={() => navigate('/inventory/new')} className="btn btn-primary btn-md">Add Medicine</button>} /></Card>
      ) : (
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-6 py-3 text-left text-sm font-medium">Medicine Name</th>
                  <th className="px-6 py-3 text-left text-sm font-medium">Category</th>
                  <th className="px-6 py-3 text-left text-sm font-medium">Quantity</th>
                  <th className="px-6 py-3 text-left text-sm font-medium">Price</th>
                  <th className="px-6 py-3 text-left text-sm font-medium">Expiry</th>
                  <th className="px-6 py-3 text-left text-sm font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {medicines.map((medicine) => (
                  <tr key={medicine.id} className="border-b hover:bg-gray-50">
                    <td className="px-6 py-4 font-medium">{medicine.name}</td>
                    <td className="px-6 py-4">{medicine.category}</td>
                    <td className="px-6 py-4">
                      {medicine.quantity}
                      {medicine.quantity < (medicine.reorder_level || 10) && (
                        <span className="ml-2 text-red-600 text-xs font-semibold">LOW STOCK</span>
                      )}
                    </td>
                    <td className="px-6 py-4">₹{medicine.selling_price?.toFixed(2) || '0.00'}</td>
                    <td className="px-6 py-4">
                      {medicine.expiry_date && (
                        <span className={medicine.expiry_date < new Date().toISOString().split('T')[0] ? 'text-red-600' : ''}>
                          {medicine.expiry_date}
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 flex gap-3">
                      <button 
                        onClick={() => navigate(`/inventory/${medicine.id}`)} 
                        className="text-blue-600 hover:text-blue-700"
                        title="Edit"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button 
                        onClick={() => setDeleteModal({ isOpen: true, medicineId: medicine.id })}
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
        title="Delete Medicine"
        onClose={() => setDeleteModal({ isOpen: false, medicineId: null })}
        actions={[
          <button
            key="cancel"
            onClick={() => setDeleteModal({ isOpen: false, medicineId: null })}
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
        <p>Are you sure you want to delete this medicine from inventory?</p>
      </Modal>
    </div>
  )
}

export default InventoryPage
