import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft, Plus, Trash2 } from 'lucide-react'
import { billingService, patientService } from '../services/api'
import { useBillingStore } from '../store'
import { Card, Alert, Loading } from '../components/Common'

function BillingFormPage() {
  const navigate = useNavigate()
  const { id } = useParams()
  const isEditMode = !!id
  const { addInvoice, updateInvoice } = useBillingStore()

  const [loading, setLoading] = useState(false)
  const [submitLoading, setSubmitLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const [patients, setPatients] = useState([])

  const [formData, setFormData] = useState({
    patientId: '',
    appointmentId: '',
    dueDate: '',
    discount: 0,
    gstPercentage: 18,
    notes: '',
  })

  const [items, setItems] = useState([
    { description: '', quantity: 1, unitPrice: 0, serviceType: 'consultation' },
  ])

  useEffect(() => {
    const loadPatients = async () => {
      try {
        const response = await patientService.listPatients({ limit: 1000 })
        setPatients(response.data.data.patients || [])
      } catch (err) {
        console.error('Failed to load patients')
      }
    }
    loadPatients()
  }, [])

  useEffect(() => {
    if (isEditMode) {
      const loadInvoice = async () => {
        try {
          setLoading(true)
          const response = await billingService.getInvoice(id)
          const invoice = response.data.data
          setFormData({
            patientId: invoice.patient_id || '',
            appointmentId: invoice.appointment_id || '',
            dueDate: invoice.due_date || '',
            discount: invoice.discount || 0,
            gstPercentage: invoice.gst_percentage || 18,
            notes: invoice.notes || '',
          })
          setItems(
            invoice.items?.map((item) => ({
              description: item.description,
              quantity: item.quantity,
              unitPrice: item.unit_price,
              serviceType: item.service_type,
            })) || []
          )
        } catch (err) {
          setError(err.response?.data?.message || 'Failed to load invoice')
        } finally {
          setLoading(false)
        }
      }
      loadInvoice()
    }
  }, [id, isEditMode])

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'discount' || name === 'gstPercentage' ? parseFloat(value) : value,
    }))
  }

  const handleItemChange = (index, field, value) => {
    const newItems = [...items]
    newItems[index] = {
      ...newItems[index],
      [field]: field === 'quantity' || field === 'unitPrice' ? parseFloat(value) : value,
    }
    setItems(newItems)
  }

  const addItem = () => {
    setItems([
      ...items,
      { description: '', quantity: 1, unitPrice: 0, serviceType: 'consultation' },
    ])
  }

  const removeItem = (index) => {
    setItems(items.filter((_, i) => i !== index))
  }

  const calculateSubtotal = () => {
    return items.reduce((sum, item) => sum + item.quantity * item.unitPrice, 0)
  }

  const calculateGST = () => {
    const subtotal = calculateSubtotal()
    return (subtotal * formData.gstPercentage) / 100
  }

  const calculateTotal = () => {
    const subtotal = calculateSubtotal()
    const gst = calculateGST()
    return subtotal + gst - formData.discount
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setSuccess(null)

    if (items.length === 0) {
      setError('Please add at least one item to the invoice')
      return
    }

    setSubmitLoading(true)

    try {
      const data = {
        patient_id: formData.patientId,
        appointment_id: formData.appointmentId,
        items: items.map((item) => ({
          description: item.description,
          quantity: item.quantity,
          unit_price: item.unitPrice,
          service_type: item.serviceType,
        })),
        discount: formData.discount,
        gst_percentage: formData.gstPercentage,
        due_date: formData.dueDate,
        notes: formData.notes,
      }

      if (isEditMode) {
        await billingService.updateInvoice(id, data)
        updateInvoice(id, data)
        setSuccess('Invoice updated successfully!')
      } else {
        const response = await billingService.createInvoice(data)
        addInvoice(response.data.data)
        setSuccess('Invoice created successfully!')
      }

      setTimeout(() => {
        navigate('/billing')
      }, 1500)
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to save invoice')
    } finally {
      setSubmitLoading(false)
    }
  }

  if (loading) return <Loading />

  const subtotal = calculateSubtotal()
  const gst = calculateGST()
  const total = calculateTotal()

  return (
    <div className="container-custom py-8">
      <div className="flex items-center mb-6">
        <button
          onClick={() => navigate('/billing')}
          className="flex items-center gap-2 text-primary-600 hover:text-primary-700 mb-4"
        >
          <ArrowLeft className="w-5 h-5" />
          Back to Billing
        </button>
      </div>

      <Card className="max-w-4xl">
        <div className="mb-6">
          <h1 className="text-2xl font-bold">{isEditMode ? 'Edit Invoice' : 'Create Invoice'}</h1>
          <p className="text-gray-600">
            {isEditMode ? 'Update invoice details' : 'Create a new invoice for a patient'}
          </p>
        </div>

        {error && <Alert type="error" message={error} className="mb-4" />}
        {success && <Alert type="success" message={success} className="mb-4" />}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Invoice Header */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Invoice Details</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="label">Patient *</label>
                <select
                  name="patientId"
                  required
                  value={formData.patientId}
                  onChange={handleChange}
                  className="input"
                >
                  <option value="">Select Patient</option>
                  {patients.map((patient) => (
                    <option key={patient.id} value={patient.id}>
                      {patient.name || `${patient.first_name} ${patient.last_name}`}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="label">Due Date</label>
                <input
                  type="date"
                  name="dueDate"
                  value={formData.dueDate}
                  onChange={handleChange}
                  className="input"
                />
              </div>
            </div>
          </div>

          {/* Invoice Items */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Invoice Items</h3>
              <button
                type="button"
                onClick={addItem}
                className="btn btn-secondary btn-sm flex items-center gap-2"
              >
                <Plus className="w-4 h-4" />
                Add Item
              </button>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-2 text-left text-sm font-medium">Description</th>
                    <th className="px-4 py-2 text-left text-sm font-medium">Type</th>
                    <th className="px-4 py-2 text-left text-sm font-medium">Qty</th>
                    <th className="px-4 py-2 text-left text-sm font-medium">Unit Price</th>
                    <th className="px-4 py-2 text-left text-sm font-medium">Total</th>
                    <th className="px-4 py-2 text-left text-sm font-medium">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {items.map((item, index) => (
                    <tr key={index} className="border-b">
                      <td className="px-4 py-2">
                        <input
                          type="text"
                          value={item.description}
                          onChange={(e) => handleItemChange(index, 'description', e.target.value)}
                          className="input text-sm"
                          placeholder="Item description"
                          required
                        />
                      </td>
                      <td className="px-4 py-2">
                        <select
                          value={item.serviceType}
                          onChange={(e) => handleItemChange(index, 'serviceType', e.target.value)}
                          className="input text-sm"
                        >
                          <option value="consultation">Consultation</option>
                          <option value="lab_test">Lab Test</option>
                          <option value="medicine">Medicine</option>
                          <option value="room_charge">Room Charge</option>
                          <option value="procedure">Procedure</option>
                          <option value="other">Other</option>
                        </select>
                      </td>
                      <td className="px-4 py-2">
                        <input
                          type="number"
                          value={item.quantity}
                          onChange={(e) => handleItemChange(index, 'quantity', e.target.value)}
                          className="input text-sm"
                          min="1"
                          required
                        />
                      </td>
                      <td className="px-4 py-2">
                        <input
                          type="number"
                          value={item.unitPrice}
                          onChange={(e) => handleItemChange(index, 'unitPrice', e.target.value)}
                          className="input text-sm"
                          min="0"
                          step="0.01"
                          required
                        />
                      </td>
                      <td className="px-4 py-2 text-sm font-medium">
                        ₹{(item.quantity * item.unitPrice).toFixed(2)}
                      </td>
                      <td className="px-4 py-2">
                        <button
                          type="button"
                          onClick={() => removeItem(index)}
                          className="text-red-600 hover:text-red-700"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Calculations */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600">Subtotal</p>
              <p className="text-2xl font-bold">₹{subtotal.toFixed(2)}</p>
            </div>

            <div>
              <label className="label">Discount (₹)</label>
              <input
                type="number"
                name="discount"
                value={formData.discount}
                onChange={handleChange}
                className="input"
                min="0"
                step="0.01"
              />
            </div>

            <div>
              <label className="label">GST (%)</label>
              <input
                type="number"
                name="gstPercentage"
                value={formData.gstPercentage}
                onChange={handleChange}
                className="input"
                min="0"
                max="100"
                step="0.1"
              />
            </div>

            <div className="bg-primary-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600">Total</p>
              <p className="text-2xl font-bold text-primary-600">₹{total.toFixed(2)}</p>
            </div>
          </div>

          {/* Notes */}
          <div>
            <label className="label">Notes</label>
            <textarea
              name="notes"
              value={formData.notes}
              onChange={handleChange}
              className="input"
              rows="3"
              placeholder="Additional notes for the invoice"
            />
          </div>

          {/* Form Actions */}
          <div className="flex gap-4 pt-6 border-t">
            <button
              type="submit"
              disabled={submitLoading}
              className="btn btn-primary btn-md"
            >
              {submitLoading ? 'Saving...' : isEditMode ? 'Update Invoice' : 'Create Invoice'}
            </button>
            <button
              type="button"
              onClick={() => navigate('/billing')}
              className="btn btn-secondary btn-md"
            >
              Cancel
            </button>
          </div>
        </form>
      </Card>
    </div>
  )
}

export default BillingFormPage
