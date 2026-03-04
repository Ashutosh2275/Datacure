import { useState, useEffect } from 'react'
import { Card, Loading, Error, EmptyState } from '../components/Common'

function MyReportsPage() {
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const loadReports = async () => {
      try {
        setLoading(true)
        // Simulate loading doctor's reports
        setTimeout(() => {
          setReports([])
          setLoading(false)
        }, 500)
      } catch (err) {
        setError('Failed to load reports')
        setLoading(false)
      }
    }
    loadReports()
  }, [])

  if (loading) return <Loading />
  if (error) return <Error message={error} />

  return (
    <div className="container-custom py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">My Reports</h1>
        <p className="text-gray-600">View and manage your clinical reports</p>
      </div>

      <Card>
        {reports.length === 0 ? (
          <EmptyState
            title="No reports generated"
            message="Your clinical reports will appear here"
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Report Type</th>
                  <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Patient</th>
                  <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Date</th>
                  <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Status</th>
                </tr>
              </thead>
              <tbody>
                {/* Reports will appear here */}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  )
}

export default MyReportsPage
