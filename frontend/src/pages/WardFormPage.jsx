import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { wardService } from '../services/api'
import { useWardsStore } from '../store'
import { Card, Alert, Loading } from '../components/Common'

function WardFormPage() {
  const navigate = useNavigate()
  const { id } = useParams()
  const isEditMode = !!id
  const { addWard, updateWard } = useWardsStore()

  const [loading, setLoading] = useState(false)
  const [submitLoading, setSubmitLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)

  const [formData, setFormData] = useState({
    name: '',
    wardType: 'General',
    floorNumber: '',
    totalBeds: 0,
    description: '',
    contactPhone: '',
    headNurseName: '',
    headNursePhone: '',
  })

  useEffect(() => {
    if (isEditMode) {
      const loadWard = async () => {
        try {
          setLoading(true)
          const response = await wardService.getWard(id)
          const ward = response.data.data
          setFormData({
            name: ward.name || '',
            wardType: ward.ward_type || 'General',
            floorNumber: ward.floor_number || '',
            totalBeds: ward.total_beds || 0,
            description: ward.description || '',
            contactPhone: ward.contact_phone || '',
            headNurseName: ward.head_nurse_name || '',
            headNursePhone: ward.head_nurse_phone || '',
          })
        } catch (err) {
          setError(err.response?.data?.message || 'Failed to load ward')
        } finally {
          setLoading(false)
        }
      }
      loadWard()
    }
  }, [id, isEditMode])

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'totalBeds' || name === 'floorNumber' ? parseInt(value) : value,
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
        ward_type: formData.wardType,
        floor_number: formData.floorNumber ? parseInt(formData.floorNumber) : null,
        total_beds: formData.totalBeds,
        description: formData.description,
        contact_phone: formData.contactPhone,
        head_nurse_name: formData.headNurseName,
        head_nurse_phone: formData.headNursePhone,
      }

      if (isEditMode) {
        await wardService.updateWard(id, data)
        updateWard(id, data)
        setSuccess('Ward updated successfully!')
      } else {
        const response = await wardService.createWard(data)
        addWard(response.data.data)
        setSuccess('Ward created successfully!')
      }

      setTimeout(() => {
        navigate('/wards')
      }, 1500)
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to save ward')
    } finally {
      setSubmitLoading(false)
    }
  }

  if (loading) return <Loading />

  const wardTypes = ['ICU', 'General', 'Pediatric', 'Maternity', 'Ortho', 'Cardiology', 'Neurology', 'Oncology']

  return (
    <div className="container-custom py-8">
      <div className="flex items-center mb-6">
        <button
          onClick={() => navigate('/wards')}
          className="flex items-center gap-2 text-primary-600 hover:text-primary-700 mb-4"
        >
          <ArrowLeft className="w-5 h-5" />
          Back to Wards
        </button>
      </div>

      <Card className="max-w-2xl">
        <div className="mb-6">
          <h1 className="text-2xl font-bold">{isEditMode ? 'Edit Ward' : 'Create Ward'}</h1>
          <p className="text-gray-600">
            {isEditMode ? 'Update ward information' : 'Create a new ward in the hospital'}
          </p>
        </div>

        {error && <Alert type="error" message={error} className="mb-4" />}
        {success && <Alert type="success" message={success} className="mb-4" />}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Ward Information */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Ward Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="label">Ward Name *</label>
                <input
                  type="text"
                  name="name"
                  required
                  value={formData.name}
                  onChange={handleChange}
                  className="input"
                  placeholder="e.g., ICU Ward A"
                />
              </div>

              <div>
                <label className="label">Ward Type *</label>
                <select
                  name="wardType"
                  required
                  value={formData.wardType}
                  onChange={handleChange}
                  className="input"
                >
                  {wardTypes.map((type) => (
                    <option key={type} value={type}>
                      {type}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="label">Floor Number</label>
                <input
                  type="number"
                  name="floorNumber"
                  value={formData.floorNumber}
                  onChange={handleChange}
                  className="input"
                  placeholder="1"
                />
              </div>

              <div>
                <label className="label">Total Beds *</label>
                <input
                  type="number"
                  name="totalBeds"
                  required
                  value={formData.totalBeds}
                  onChange={handleChange}
                  className="input"
                  min="1"
                  placeholder="Number of beds"
                />
              </div>

              <div className="md:col-span-2">
                <label className="label">Description</label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  className="input"
                  rows="3"
                  placeholder="Ward description and facilities"
                />
              </div>
            </div>
          </div>

          {/* Contact Information */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Contact Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="label">Ward Contact Phone</label>
                <input
                  type="tel"
                  name="contactPhone"
                  value={formData.contactPhone}
                  onChange={handleChange}
                  className="input"
                  placeholder="+91 98765 43210"
                />
              </div>

              <div>
                <label className="label">Head Nurse Name</label>
                <input
                  type="text"
                  name="headNurseName"
                  value={formData.headNurseName}
                  onChange={handleChange}
                  className="input"
                  placeholder="Name of head nurse"
                />
              </div>

              <div>
                <label className="label">Head Nurse Phone</label>
                <input
                  type="tel"
                  name="headNursePhone"
                  value={formData.headNursePhone}
                  onChange={handleChange}
                  className="input"
                  placeholder="+91 98765 43210"
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
              {submitLoading ? 'Saving...' : isEditMode ? 'Update Ward' : 'Create Ward'}
            </button>
            <button
              type="button"
              onClick={() => navigate('/wards')}
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

export default WardFormPage
