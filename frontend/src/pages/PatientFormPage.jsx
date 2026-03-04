import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { patientService, userService } from '../services/api'
import { usePatientsStore } from '../store'
import { Card, Alert, Loading } from '../components/Common'

function PatientFormPage() {
  const navigate = useNavigate()
  const { id } = useParams()
  const isEditMode = !!id
  const { addPatient, updatePatient } = usePatientsStore()

  const [loading, setLoading] = useState(false)
  const [submitLoading, setSubmitLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const [doctors, setDoctors] = useState([])

  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    dateOfBirth: '',
    gender: '',
    bloodGroup: '',
    height: '',
    weight: '',
    allergies: '',
    chronicConditions: '',
    insuranceProvider: '',
    insurancePolicyNumber: '',
    emergencyContactName: '',
    emergencyContactPhone: '',
  })

  useEffect(() => {
    const loadDoctors = async () => {
      try {
        const response = await patientService.getDoctors()
        setDoctors(response.data.data || [])
      } catch (err) {
        console.error('Failed to load doctors')
      }
    }
    loadDoctors()
  }, [])

  useEffect(() => {
    if (isEditMode) {
      const loadPatient = async () => {
        try {
          setLoading(true)
          const response = await patientService.getPatient(id)
          const patient = response.data.data
          setFormData({
            firstName: patient.user?.first_name || '',
            lastName: patient.user?.last_name || '',
            email: patient.user?.email || '',
            phone: patient.user?.phone || '',
            dateOfBirth: patient.date_of_birth || '',
            gender: patient.gender || '',
            bloodGroup: patient.blood_group || '',
            height: patient.height || '',
            weight: patient.weight || '',
            allergies: patient.allergies || '',
            chronicConditions: patient.chronic_conditions || '',
            insuranceProvider: patient.insurance_provider || '',
            insurancePolicyNumber: patient.insurance_policy_number || '',
            emergencyContactName: patient.emergency_contact_name || '',
            emergencyContactPhone: patient.emergency_contact_phone || '',
          })
        } catch (err) {
          setError(err.response?.data?.message || 'Failed to load patient')
        } finally {
          setLoading(false)
        }
      }
      loadPatient()
    }
  }, [id, isEditMode])

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setSuccess(null)
    setSubmitLoading(true)

    try {
      const data = {
        first_name: formData.firstName,
        last_name: formData.lastName,
        email: formData.email,
        phone: formData.phone,
        date_of_birth: formData.dateOfBirth,
        gender: formData.gender,
        blood_group: formData.bloodGroup,
        height: formData.height ? parseFloat(formData.height) : null,
        weight: formData.weight ? parseFloat(formData.weight) : null,
        allergies: formData.allergies,
        chronic_conditions: formData.chronicConditions,
        insurance_provider: formData.insuranceProvider,
        insurance_policy_number: formData.insurancePolicyNumber,
        emergency_contact_name: formData.emergencyContactName,
        emergency_contact_phone: formData.emergencyContactPhone,
      }

      if (isEditMode) {
        await patientService.updatePatient(id, data)
        updatePatient(id, data)
        setSuccess('Patient updated successfully!')
      } else {
        const response = await patientService.createPatient(data)
        addPatient(response.data.data)
        setSuccess('Patient created successfully!')
      }

      setTimeout(() => {
        navigate('/patients')
      }, 1500)
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to save patient')
    } finally {
      setSubmitLoading(false)
    }
  }

  if (loading) return <Loading />

  return (
    <div className="container-custom py-8">
      <div className="flex items-center mb-6">
        <button
          onClick={() => navigate('/patients')}
          className="flex items-center gap-2 text-primary-600 hover:text-primary-700 mb-4"
        >
          <ArrowLeft className="w-5 h-5" />
          Back to Patients
        </button>
      </div>

      <Card className="max-w-2xl">
        <div className="mb-6">
          <h1 className="text-2xl font-bold">{isEditMode ? 'Edit Patient' : 'New Patient'}</h1>
          <p className="text-gray-600">
            {isEditMode ? 'Update patient information' : 'Create a new patient record'}
          </p>
        </div>

        {error && <Alert type="error" message={error} className="mb-4" />}
        {success && <Alert type="success" message={success} className="mb-4" />}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Personal Information */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Personal Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="label">First Name *</label>
                <input
                  type="text"
                  name="firstName"
                  required
                  value={formData.firstName}
                  onChange={handleChange}
                  className="input"
                  placeholder="John"
                />
              </div>

              <div>
                <label className="label">Last Name *</label>
                <input
                  type="text"
                  name="lastName"
                  required
                  value={formData.lastName}
                  onChange={handleChange}
                  className="input"
                  placeholder="Doe"
                />
              </div>

              <div>
                <label className="label">Email *</label>
                <input
                  type="email"
                  name="email"
                  required
                  value={formData.email}
                  onChange={handleChange}
                  className="input"
                  placeholder="john@example.com"
                />
              </div>

              <div>
                <label className="label">Phone *</label>
                <input
                  type="tel"
                  name="phone"
                  required
                  value={formData.phone}
                  onChange={handleChange}
                  className="input"
                  placeholder="+91 98765 43210"
                />
              </div>

              <div>
                <label className="label">Date of Birth *</label>
                <input
                  type="date"
                  name="dateOfBirth"
                  required
                  value={formData.dateOfBirth}
                  onChange={handleChange}
                  className="input"
                />
              </div>

              <div>
                <label className="label">Gender *</label>
                <select
                  name="gender"
                  required
                  value={formData.gender}
                  onChange={handleChange}
                  className="input"
                >
                  <option value="">Select Gender</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                </select>
              </div>
            </div>
          </div>

          {/* Medical Information */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Medical Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="label">Blood Group</label>
                <select
                  name="bloodGroup"
                  value={formData.bloodGroup}
                  onChange={handleChange}
                  className="input"
                >
                  <option value="">Select Blood Group</option>
                  <option value="A+">A+</option>
                  <option value="A-">A-</option>
                  <option value="B+">B+</option>
                  <option value="B-">B-</option>
                  <option value="O+">O+</option>
                  <option value="O-">O-</option>
                  <option value="AB+">AB+</option>
                  <option value="AB-">AB-</option>
                </select>
              </div>

              <div>
                <label className="label">Height (cm)</label>
                <input
                  type="number"
                  name="height"
                  value={formData.height}
                  onChange={handleChange}
                  className="input"
                  placeholder="170"
                  step="0.1"
                />
              </div>

              <div>
                <label className="label">Weight (kg)</label>
                <input
                  type="number"
                  name="weight"
                  value={formData.weight}
                  onChange={handleChange}
                  className="input"
                  placeholder="70"
                  step="0.1"
                />
              </div>

              <div className="md:col-span-2">
                <label className="label">Allergies</label>
                <textarea
                  name="allergies"
                  value={formData.allergies}
                  onChange={handleChange}
                  className="input"
                  rows="3"
                  placeholder="List any allergies"
                />
              </div>

              <div className="md:col-span-2">
                <label className="label">Chronic Conditions</label>
                <textarea
                  name="chronicConditions"
                  value={formData.chronicConditions}
                  onChange={handleChange}
                  className="input"
                  rows="3"
                  placeholder="List any chronic conditions"
                />
              </div>
            </div>
          </div>

          {/* Insurance Information */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Insurance Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="label">Insurance Provider</label>
                <input
                  type="text"
                  name="insuranceProvider"
                  value={formData.insuranceProvider}
                  onChange={handleChange}
                  className="input"
                  placeholder="Provider name"
                />
              </div>

              <div>
                <label className="label">Policy Number</label>
                <input
                  type="text"
                  name="insurancePolicyNumber"
                  value={formData.insurancePolicyNumber}
                  onChange={handleChange}
                  className="input"
                  placeholder="Policy number"
                />
              </div>
            </div>
          </div>

          {/* Emergency Contact */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Emergency Contact</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="label">Contact Name</label>
                <input
                  type="text"
                  name="emergencyContactName"
                  value={formData.emergencyContactName}
                  onChange={handleChange}
                  className="input"
                  placeholder="Emergency contact name"
                />
              </div>

              <div>
                <label className="label">Contact Phone</label>
                <input
                  type="tel"
                  name="emergencyContactPhone"
                  value={formData.emergencyContactPhone}
                  onChange={handleChange}
                  className="input"
                  placeholder="Emergency contact phone"
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
              {submitLoading ? 'Saving...' : isEditMode ? 'Update Patient' : 'Create Patient'}
            </button>
            <button
              type="button"
              onClick={() => navigate('/patients')}
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

export default PatientFormPage
