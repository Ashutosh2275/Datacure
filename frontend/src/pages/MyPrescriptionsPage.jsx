import { useState, useEffect } from 'react'
import { Card, Loading, Error, EmptyState } from '../components/Common'

function MyPrescriptionsPage() {
  const [prescriptions, setPrescriptions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const loadPrescriptions = async () => {
      try {
        setLoading(true)
        // Simulate loading patient's prescriptions
        setTimeout(() => {
          setPrescriptions([])
          setLoading(false)
        }, 500)
      } catch (err) {
        setError('Failed to load prescriptions')
        setLoading(false)
      }
    }
    loadPrescriptions()
  }, [])

  if (loading) return <Loading />
  if (error) return <Error message={error} />

  return (
    <div className="container-custom py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">My Prescriptions</h1>
        <p className="text-gray-600">View your active prescriptions</p>
      </div>

      <Card>
        {prescriptions.length === 0 ? (
          <EmptyState
            title="No active prescriptions"
            message="You don't have any active prescriptions"
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Medicine</th>
                  <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Dosage</th>
                  <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Duration</th>
                  <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Prescribed By</th>
                </tr>
              </thead>
              <tbody>
                {/* Prescriptions will appear here */}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  )
}

export default MyPrescriptionsPage
