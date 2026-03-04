import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { inventoryService } from '../services/api'
import { useInventoryStore } from '../store'
import { Card, Alert, Loading } from '../components/Common'

function InventoryFormPage() {
  const navigate = useNavigate()
  const { id } = useParams()
  const isEditMode = !!id
  const { addMedicine, updateMedicine } = useInventoryStore()

  const [loading, setLoading] = useState(false)
  const [submitLoading, setSubmitLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)

  const [formData, setFormData] = useState({
    name: '',
    genericName: '',
    manufacturer: '',
    category: 'Antibiotics',
    strength: '',
    unit: 'tablet',
    packagingSize: 1,
    batchNumber: '',
    manufacturingDate: '',
    expiryDate: '',
    costPrice: 0,
    sellingPrice: 0,
    quantity: 0,
    reorderLevel: 10,
    description: '',
    sideEffects: '',
    contraindications: '',
    dosageInstructions: '',
  })

  useEffect(() => {
    if (isEditMode) {
      const loadMedicine = async () => {
        try {
          setLoading(true)
          const response = await inventoryService.getMedicine(id)
          const medicine = response.data.data
          setFormData({
            name: medicine.name || '',
            genericName: medicine.generic_name || '',
            manufacturer: medicine.manufacturer || '',
            category: medicine.category || 'Antibiotics',
            strength: medicine.strength || '',
            unit: medicine.unit || 'tablet',
            packagingSize: medicine.packaging_size || 1,
            batchNumber: medicine.batch_number || '',
            manufacturingDate: medicine.manufacturing_date || '',
            expiryDate: medicine.expiry_date || '',
            costPrice: medicine.cost_price || 0,
            sellingPrice: medicine.selling_price || 0,
            quantity: medicine.quantity || 0,
            reorderLevel: medicine.reorder_level || 10,
            description: medicine.description || '',
            sideEffects: medicine.side_effects || '',
            contraindications: medicine.contraindications || '',
            dosageInstructions: medicine.dosage_instructions || '',
          })
        } catch (err) {
          setError(err.response?.data?.message || 'Failed to load medicine')
        } finally {
          setLoading(false)
        }
      }
      loadMedicine()
    }
  }, [id, isEditMode])

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: 
        name === 'costPrice' || name === 'sellingPrice' || name === 'quantity' || name === 'reorderLevel' || name === 'packagingSize'
          ? parseFloat(value)
          : value,
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setSuccess(null)
    setSubmitLoading(true)

    try {
      const data = {
        name: formData.name,
        generic_name: formData.genericName,
        manufacturer: formData.manufacturer,
        category: formData.category,
        strength: formData.strength,
        unit: formData.unit,
        packaging_size: formData.packagingSize,
        batch_number: formData.batchNumber,
        manufacturing_date: formData.manufacturingDate,
        expiry_date: formData.expiryDate,
        cost_price: formData.costPrice,
        selling_price: formData.sellingPrice,
        quantity: formData.quantity,
        reorder_level: formData.reorderLevel,
        description: formData.description,
        side_effects: formData.sideEffects,
        contraindications: formData.contraindications,
        dosage_instructions: formData.dosageInstructions,
      }

      if (isEditMode) {
        await inventoryService.updateMedicine(id, data)
        updateMedicine(id, data)
        setSuccess('Medicine updated successfully!')
      } else {
        const response = await inventoryService.createMedicine(data)
        addMedicine(response.data.data)
        setSuccess('Medicine added successfully!')
      }

      setTimeout(() => {
        navigate('/inventory')
      }, 1500)
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to save medicine')
    } finally {
      setSubmitLoading(false)
    }
  }

  if (loading) return <Loading />

  const medicineCategories = [
    'Antibiotics',
    'Analgesics',
    'Anti-inflammatory',
    'Cardiovascular',
    'Respiratory',
    'GI',
    'Neurological',
    'Immunosuppressants',
    'Vaccines',
    'Other',
  ]

  return (
    <div className="container-custom py-8">
      <div className="flex items-center mb-6">
        <button
          onClick={() => navigate('/inventory')}
          className="flex items-center gap-2 text-primary-600 hover:text-primary-700 mb-4"
        >
          <ArrowLeft className="w-5 h-5" />
          Back to Inventory
        </button>
      </div>

      <Card className="max-w-3xl">
        <div className="mb-6">
          <h1 className="text-2xl font-bold">{isEditMode ? 'Edit Medicine' : 'Add Medicine'}</h1>
          <p className="text-gray-600">
            {isEditMode ? 'Update medicine information' : 'Add a new medicine to the inventory'}
          </p>
        </div>

        {error && <Alert type="error" message={error} className="mb-4" />}
        {success && <Alert type="success" message={success} className="mb-4" />}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Information */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Basic Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="label">Medicine Name *</label>
                <input
                  type="text"
                  name="name"
                  required
                  value={formData.name}
                  onChange={handleChange}
                  className="input"
                  placeholder="Medicine brand name"
                />
              </div>

              <div>
                <label className="label">Generic Name</label>
                <input
                  type="text"
                  name="genericName"
                  value={formData.genericName}
                  onChange={handleChange}
                  className="input"
                  placeholder="Generic name"
                />
              </div>

              <div>
                <label className="label">Manufacturer</label>
                <input
                  type="text"
                  name="manufacturer"
                  value={formData.manufacturer}
                  onChange={handleChange}
                  className="input"
                  placeholder="Manufacturer name"
                />
              </div>

              <div>
                <label className="label">Category *</label>
                <select
                  name="category"
                  required
                  value={formData.category}
                  onChange={handleChange}
                  className="input"
                >
                  {medicineCategories.map((cat) => (
                    <option key={cat} value={cat}>
                      {cat}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="label">Strength</label>
                <input
                  type="text"
                  name="strength"
                  value={formData.strength}
                  onChange={handleChange}
                  className="input"
                  placeholder="e.g., 500mg"
                />
              </div>

              <div>
                <label className="label">Unit</label>
                <select
                  name="unit"
                  value={formData.unit}
                  onChange={handleChange}
                  className="input"
                >
                  <option value="tablet">Tablet</option>
                  <option value="capsule">Capsule</option>
                  <option value="injection">Injection</option>
                  <option value="syrup">Syrup</option>
                  <option value="ointment">Ointment</option>
                  <option value="drops">Drops</option>
                  <option value="cream">Cream</option>
                </select>
              </div>
            </div>
          </div>

          {/* Batch and Expiry */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Batch Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="label">Batch Number</label>
                <input
                  type="text"
                  name="batchNumber"
                  value={formData.batchNumber}
                  onChange={handleChange}
                  className="input"
                  placeholder="Batch number"
                />
              </div>

              <div>
                <label className="label">Packaging Size</label>
                <input
                  type="number"
                  name="packagingSize"
                  value={formData.packagingSize}
                  onChange={handleChange}
                  className="input"
                  min="1"
                />
              </div>

              <div>
                <label className="label">Manufacturing Date</label>
                <input
                  type="date"
                  name="manufacturingDate"
                  value={formData.manufacturingDate}
                  onChange={handleChange}
                  className="input"
                />
              </div>

              <div>
                <label className="label">Expiry Date *</label>
                <input
                  type="date"
                  name="expiryDate"
                  required
                  value={formData.expiryDate}
                  onChange={handleChange}
                  className="input"
                />
              </div>
            </div>
          </div>

          {/* Pricing and Quantity */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Pricing & Stock</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="label">Cost Price (₹) *</label>
                <input
                  type="number"
                  name="costPrice"
                  required
                  value={formData.costPrice}
                  onChange={handleChange}
                  className="input"
                  min="0"
                  step="0.01"
                />
              </div>

              <div>
                <label className="label">Selling Price (₹) *</label>
                <input
                  type="number"
                  name="sellingPrice"
                  required
                  value={formData.sellingPrice}
                  onChange={handleChange}
                  className="input"
                  min="0"
                  step="0.01"
                />
              </div>

              <div>
                <label className="label">Current Quantity *</label>
                <input
                  type="number"
                  name="quantity"
                  required
                  value={formData.quantity}
                  onChange={handleChange}
                  className="input"
                  min="0"
                />
              </div>

              <div>
                <label className="label">Reorder Level</label>
                <input
                  type="number"
                  name="reorderLevel"
                  value={formData.reorderLevel}
                  onChange={handleChange}
                  className="input"
                  min="1"
                />
              </div>
            </div>
          </div>

          {/* Medical Information */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Medical Information</h3>
            <div className="grid grid-cols-1 gap-4">
              <div>
                <label className="label">Description</label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  className="input"
                  rows="2"
                  placeholder="Medicine description"
                />
              </div>

              <div>
                <label className="label">Dosage Instructions</label>
                <textarea
                  name="dosageInstructions"
                  value={formData.dosageInstructions}
                  onChange={handleChange}
                  className="input"
                  rows="2"
                  placeholder="How to use this medicine"
                />
              </div>

              <div>
                <label className="label">Side Effects</label>
                <textarea
                  name="sideEffects"
                  value={formData.sideEffects}
                  onChange={handleChange}
                  className="input"
                  rows="2"
                  placeholder="List possible side effects"
                />
              </div>

              <div>
                <label className="label">Contraindications</label>
                <textarea
                  name="contraindications"
                  value={formData.contraindications}
                  onChange={handleChange}
                  className="input"
                  rows="2"
                  placeholder="When not to use this medicine"
                />
              </div>
            </div>
          </div>

          {/* Form Actions */}
          <div className="flex gap-4 pt-6 border-t">
            <button
              type="submit"
              disabled={submitLoading}
              className="btn btn-primary btn-md"
            >
              {submitLoading ? 'Saving...' : isEditMode ? 'Update Medicine' : 'Add Medicine'}
            </button>
            <button
              type="button"
              onClick={() => navigate('/inventory')}
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

export default InventoryFormPage
