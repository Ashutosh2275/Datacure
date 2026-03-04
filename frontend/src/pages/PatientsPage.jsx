import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Search } from 'lucide-react'
import { patientService } from '../services/api'
import { Card, Loading, Error, Pagination, EmptyState } from '../components/Common'

function PatientsPage() {
  const navigate = useNavigate()
  const [patients, setPatients] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')

  useEffect(() => {
    const loadPatients = async () => {
      try {
        const response = await patientService.listPatients({ page, search, limit: 10 })
        setPatients(response.data.data.patients || [])
      } catch (err) {
        setError(err.response?.data?.message || 'Failed to load patients')
      } finally {
        setLoading(false)
      }
    }
    loadPatients()
  }, [page, search])

  if (loading) return <Loading />
  if (error) return <Error message={error} />

  return (
    <div className="container-custom py-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold">Patients</h1>
          <p className="text-gray-600">Manage patient records</p>
        </div>
        <button onClick={() => navigate('/patients/new')} className="btn btn-primary btn-md flex items-center gap-2">
          <Plus className="w-5 h-5" />
          New Patient
        </button>
      </div>

      {/* Search */}
      <Card className="mb-6">
        <div className="flex items-center gap-2 bg-gray-50 px-3 py-2 rounded-lg">
          <Search className="w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search patients..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="flex-1 bg-transparent outline-none"
          />
        </div>
      </Card>

      {/* Patients Table */}
      <Card>
        {patients.length === 0 ? (
          <EmptyState
            title="No patients found"
            message="Start by creating a new patient record"
            action={
              <button onClick={() => navigate('/patients/new')} className="btn btn-primary btn-md">
                Add First Patient
              </button>
            }
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Name</th>
                  <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Email</th>
                  <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Phone</th>
                  <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Status</th>
                  <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Actions</th>
                </tr>
              </thead>
              <tbody>
                {patients.map((patient) => (
                  <tr key={patient.id} className="border-b hover:bg-gray-50">
                    <td className="px-6 py-4">{patient.name}</td>
                    <td className="px-6 py-4">{patient.email}</td>
                    <td className="px-6 py-4">{patient.phone}</td>
                    <td className="px-6 py-4">
                      <span className="badge badge-success">Active</span>
                    </td>
                    <td className="px-6 py-4">
                      <button onClick={() => navigate(`/patients/${patient.id}`)} className="text-primary-600 hover:text-primary-700 text-sm font-medium">
                        View
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {patients.length > 0 && (
        <Pagination page={page} totalPages={5} onPageChange={setPage} />
      )}
    </div>
  )
}

export default PatientsPage
