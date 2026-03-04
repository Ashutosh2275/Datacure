import { useState } from 'react'
import { Card, Loading } from '../components/Common'

function PatientDetailPage() {
  const [loading] = useState(false)

  if (loading) return <Loading />

  return (
    <div className="container-custom py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Patient Details</h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card title="Personal Information" className="lg:col-span-2">
          <div className="grid grid-cols-2 gap-4">
            <div><label className="text-sm font-medium">Name:</label><p>Patient Name</p></div>
            <div><label className="text-sm font-medium">DOB:</label><p>01/01/1990</p></div>
            <div><label className="text-sm font-medium">Gender:</label><p>Male</p></div>
            <div><label className="text-sm font-medium">Blood Group:</label><p>O+</p></div>
          </div>
        </Card>

        <Card title="Quick Info">
          <div className="space-y-3">
            <div><span className="text-sm text-gray-600">ID:</span><p className="font-medium">PAT001</p></div>
            <div><span className="text-sm text-gray-600">Status:</span><p className="font-medium">Active</p></div>
            <div><span className="text-sm text-gray-600">Doctor:</span><p className="font-medium">Dr. John</p></div>
          </div>
        </Card>
      </div>

      <Card title="Medical Records" className="mt-6">
        <div className="text-center text-gray-500">No records found</div>
      </Card>

      <Card title="Appointments" className="mt-6">
        <div className="text-center text-gray-500">No appointments found</div>
      </Card>
    </div>
  )
}

export default PatientDetailPage
