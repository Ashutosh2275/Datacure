import { Plus } from 'lucide-react'
import { Card, EmptyState } from '../components/Common'

function WardsPage() {
  return (
    <div className="container-custom py-8">
      <div className="flex items-center justify-between mb-6">
        <div><h1 className="text-3xl font-bold">Wards</h1><p className="text-gray-600">Manage wards and beds</p></div>
        <button className="btn btn-primary btn-md flex items-center gap-2"><Plus className="w-5 h-5" />New Ward</button>
      </div>
      <Card><EmptyState title="No wards" message="Create your first ward" action={<button className="btn btn-primary btn-md">Create Ward</button>} /></Card>
    </div>
  )
}

export default WardsPage
