import { useState, useEffect } from 'react'
import { Card, Loading, Error, EmptyState } from '../components/Common'

function MedicalRecordsPage() {
  const [records, setRecords] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const loadRecords = async () => {
      try {
        setLoading(true)
        // Simulate loading patient's medical records
        setTimeout(() => {
          setRecords([])
          setLoading(false)
        }, 500)
      } catch (err) {
        setError('Failed to load medical records')
        setLoading(false)
      }
    }
    loadRecords()
  }, [])

  if (loading) return <Loading />
  if (error) return <Error message={error} />

  return (
    <div className="container-custom py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">My Medical Records</h1>
        <p className="text-gray-600">View your complete medical history</p>
      </div>

      <Card>
        {records.length === 0 ? (
          <EmptyState
            title="No medical records"
            message="Your medical records will appear here"
          />
        ) : (
          <div className="space-y-4">
            {records.map((record) => (
              <div key={record.id} className="border rounded-lg p-4 hover:bg-gray-50">
                <h3 className="font-semibold">{record.title}</h3>
                <p className="text-gray-600">{record.description}</p>
                <p className="text-sm text-gray-500 mt-2">{record.date}</p>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  )
}

export default MedicalRecordsPage
