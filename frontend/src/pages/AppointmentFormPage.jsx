import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { appointmentService, patientService } from '../services/api'
import { useAppointmentsStore } from '../store'
import { Card, Alert, Loading } from '../components/Common'

function AppointmentFormPage() {
  const navigate = useNavigate()
  const { id } = useParams()
  const isEditMode = !!id
  const { addAppointment, updateAppointment } = useAppointmentsStore()

  const [loading, setLoading] = useState(false)
  const [submitLoading, setSubmitLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const [patients, setPatients] = useState([])
  const [doctors, setDoctors] = useState([])

  const [formData, setFormData] = useState({
    patientId: '',
    doctorId: '',
    appointmentDate: '',
    startTime: '',
    endTime: '',
    appointmentType: 'consultation',
    chiefComplaint: '',
    isEmergency: false,
    isTelemedicine: false,
  })

  useEffect(() => {
    const loadData = async () => {
      try {
        const [patientsRes, doctorsRes] = await Promise.all([
          patientService.listPatients({ limit: 1000 }),
          patientService.getDoctors(),
        ])
        setPatients(patientsRes.data.data.patients || [])
        setDoctors(doctorsRes.data.data || [])
      } catch (err) {
        console.error('Failed to load data')
      }
    }
    loadData()
  }, [])

  useEffect(() => {
    if (isEditMode) {
      const loadAppointment = async () => {
        try {
          setLoading(true)
          const response = await appointmentService.getAppointment(id)
          const apt = response.data.data
          setFormData({
            patientId: apt.patient_id || '',
            doctorId: apt.doctor_id || '',
            appointmentDate: apt.appointment_date || '',
            startTime: apt.start_time || '',
            endTime: apt.end_time || '',
            appointmentType: apt.appointment_type || 'consultation',
            chiefComplaint: apt.chief_complaint || '',
            isEmergency: apt.is_emergency || false,
            isTelemedicine: apt.is_telemedicine || false,
          })
        } catch (err) {
          setError(err.response?.data?.message || 'Failed to load appointment')
        } finally {
          setLoading(false)
        }
      }
      loadAppointment()
    }
  }, [id, isEditMode])

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setSuccess(null)
    setSubmitLoading(true)

    try {
      const data = {
        patient_id: formData.patientId,
        doctor_id: formData.doctorId,
        appointment_date: formData.appointmentDate,
        start_time: formData.startTime,
        end_time: formData.endTime,
        appointment_type: formData.appointmentType,
        chief_complaint: formData.chiefComplaint,
        is_emergency: formData.isEmergency,
        is_telemedicine: formData.isTelemedicine,
      }

      if (isEditMode) {
        await appointmentService.rescheduleAppointment(id, data)
        updateAppointment(id, data)
        setSuccess('Appointment updated successfully!')
      } else {
        const response = await appointmentService.createAppointment(data)
        addAppointment(response.data.data)
        setSuccess('Appointment booked successfully!')
      }

      setTimeout(() => {
        navigate('/appointments')
      }, 1500)
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to save appointment')
    } finally {
      setSubmitLoading(false)
    }
  }

  if (loading) return <Loading />

  return (
    <div className="container-custom py-8">
      <div className="flex items-center mb-6">
        <button
          onClick={() => navigate('/appointments')}
          className="flex items-center gap-2 text-primary-600 hover:text-primary-700 mb-4"
        >
          <ArrowLeft className="w-5 h-5" />
          Back to Appointments
        </button>
      </div>

      <Card className="max-w-2xl">
        <div className="mb-6">
          <h1 className="text-2xl font-bold">{isEditMode ? 'Reschedule Appointment' : 'Book Appointment'}</h1>
          <p className="text-gray-600">
            {isEditMode ? 'Update appointment details' : 'Schedule a new appointment for a patient'}
          </p>
        </div>

        {error && <Alert type="error" message={error} className="mb-4" />}
        {success && <Alert type="success" message={success} className="mb-4" />}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Information */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Appointment Details</h3>
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
                <label className="label">Doctor *</label>
                <select
                  name="doctorId"
                  required
                  value={formData.doctorId}
                  onChange={handleChange}
                  className="input"
                >
                  <option value="">Select Doctor</option>
                  {doctors.map((doctor) => (
                    <option key={doctor.id} value={doctor.id}>
                      Dr. {doctor.first_name} {doctor.last_name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="label">Appointment Date *</label>
                <input
                  type="date"
                  name="appointmentDate"
                  required
                  value={formData.appointmentDate}
                  onChange={handleChange}
                  className="input"
                />
              </div>

              <div>
                <label className="label">Appointment Type</label>
                <select
                  name="appointmentType"
                  value={formData.appointmentType}
                  onChange={handleChange}
                  className="input"
                >
                  <option value="consultation">Consultation</option>
                  <option value="follow-up">Follow-up</option>
                  <option value="procedure">Procedure</option>
                  <option value="emergency">Emergency</option>
                </select>
              </div>

              <div>
                <label className="label">Start Time *</label>
                <input
                  type="time"
                  name="startTime"
                  required
                  value={formData.startTime}
                  onChange={handleChange}
                  className="input"
                />
              </div>

              <div>
                <label className="label">End Time *</label>
                <input
                  type="time"
                  name="endTime"
                  required
                  value={formData.endTime}
                  onChange={handleChange}
                  className="input"
                />
              </div>

              <div className="md:col-span-2">
                <label className="label">Chief Complaint</label>
                <textarea
                  name="chiefComplaint"
                  value={formData.chiefComplaint}
                  onChange={handleChange}
                  className="input"
                  rows="3"
                  placeholder="Describe the patient's main concern"
                />
              </div>
            </div>
          </div>

          {/* Appointment Options */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Options</h3>
            <div className="space-y-3">
              <div className="flex items-center">
                <input
                  type="checkbox"
                  name="isEmergency"
                  checked={formData.isEmergency}
                  onChange={handleChange}
                  className="w-4 h-4 rounded"
                  id="isEmergency"
                />
                <label htmlFor="isEmergency" className="ml-3 text-sm">
                  Mark as Emergency
                </label>
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  name="isTelemedicine"
                  checked={formData.isTelemedicine}
                  onChange={handleChange}
                  className="w-4 h-4 rounded"
                  id="isTelemedicine"
                />
                <label htmlFor="isTelemedicine" className="ml-3 text-sm">
                  Telemedicine Appointment
                </label>
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
              {submitLoading ? 'Saving...' : isEditMode ? 'Update Appointment' : 'Book Appointment'}
            </button>
            <button
              type="button"
              onClick={() => navigate('/appointments')}
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

export default AppointmentFormPage
