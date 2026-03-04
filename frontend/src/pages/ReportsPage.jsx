import { Download } from 'lucide-react'
import { Card } from '../components/Common'

function ReportsPage() {
  return (
    <div className="container-custom py-8">
      <h1 className="text-3xl font-bold mb-6">Reports</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {['Patient Report', 'Revenue Report', 'Appointment Report', 'Inventory Report'].map((report) => (
          <Card key={report} className="p-6 hover:shadow-md cursor-pointer">
            <div className="flex items-center justify-between">
              <div><h3 className="font-semibold">{report}</h3><p className="text-sm text-gray-600">Generate and download</p></div>
              <Download className="w-6 h-6 text-gray-400" />
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}

export default ReportsPage
