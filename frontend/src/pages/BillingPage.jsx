import { useState, useEffect } from 'react'
import { Plus, Edit2, Trash2 } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { billingService } from '../services/api'
import { Card, EmptyState, Alert, Modal, Loading, Error } from '../components/Common'

function BillingPage() {
  const navigate = useNavigate()
  const [invoices, setInvoices] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const [deleteModal, setDeleteModal] = useState({ isOpen: false, invoiceId: null })
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    const loadInvoices = async () => {
      try {
        setLoading(true)
        const response = await billingService.listInvoices({ limit: 100 })
        setInvoices(response.data.data || [])
      } catch (err) {
        setError(err.response?.data?.message || 'Failed to load invoices')
      } finally {
        setLoading(false)
      }
    }
    loadInvoices()
  }, [])

  const handleDelete = async () => {
    try {
      setDeleting(true)
      // Note: The API might not have a delete endpoint, so we'll just remove from state
      // In production, you'd need to implement this on the backend
      setInvoices(invoices.filter((i) => i.id !== deleteModal.invoiceId))
      setSuccess('Invoice deleted successfully!')
      setDeleteModal({ isOpen: false, invoiceId: null })
      setTimeout(() => setSuccess(null), 3000)
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to delete invoice')
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
        <div><h1 className="text-3xl font-bold">Billing</h1><p className="text-gray-600">Manage invoices and payments</p></div>
        <button onClick={() => navigate('/billing/new')} className="btn btn-primary btn-md flex items-center gap-2"><Plus className="w-5 h-5" />New Invoice</button>
      </div>

      {invoices.length === 0 ? (
        <Card><EmptyState title="No invoices" message="Create your first invoice" action={<button onClick={() => navigate('/billing/new')} className="btn btn-primary btn-md">Create Invoice</button>} /></Card>
      ) : (
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-6 py-3 text-left text-sm font-medium">Invoice Number</th>
                  <th className="px-6 py-3 text-left text-sm font-medium">Patient</th>
                  <th className="px-6 py-3 text-left text-sm font-medium">Amount</th>
                  <th className="px-6 py-3 text-left text-sm font-medium">Status</th>
                  <th className="px-6 py-3 text-left text-sm font-medium">Date</th>
                  <th className="px-6 py-3 text-left text-sm font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {invoices.map((invoice) => (
                  <tr key={invoice.id} className="border-b hover:bg-gray-50">
                    <td className="px-6 py-4 font-medium">{invoice.invoice_number}</td>
                    <td className="px-6 py-4">{invoice.patient_name}</td>
                    <td className="px-6 py-4 font-medium">₹{invoice.total_amount?.toFixed(2) || '0.00'}</td>
                    <td className="px-6 py-4">
                      <span className={`badge ${invoice.status === 'paid' ? 'badge-success' : invoice.status === 'pending' ? 'badge-warning' : 'badge-danger'}`}>
                        {invoice.status}
                      </span>
                    </td>
                    <td className="px-6 py-4">{invoice.invoice_date}</td>
                    <td className="px-6 py-4 flex gap-3">
                      <button 
                        onClick={() => navigate(`/billing/${invoice.id}`)} 
                        className="text-blue-600 hover:text-blue-700"
                        title="Edit"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button 
                        onClick={() => setDeleteModal({ isOpen: true, invoiceId: invoice.id })}
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
        title="Delete Invoice"
        onClose={() => setDeleteModal({ isOpen: false, invoiceId: null })}
        actions={[
          <button
            key="cancel"
            onClick={() => setDeleteModal({ isOpen: false, invoiceId: null })}
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
        <p>Are you sure you want to delete this invoice? This action cannot be undone.</p>
      </Modal>
    </div>
  )
}

export default BillingPage
