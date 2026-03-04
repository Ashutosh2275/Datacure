import { Plus } from 'lucide-react'
import { Card, EmptyState } from '../components/Common'

function InventoryPage() {
  return (
    <div className="container-custom py-8">
      <div className="flex items-center justify-between mb-6">
        <div><h1 className="text-3xl font-bold">Inventory</h1><p className="text-gray-600">Manage medicines and stock</p></div>
        <button className="btn btn-primary btn-md flex items-center gap-2"><Plus className="w-5 h-5" />Add Medicine</button>
      </div>
      <Card><EmptyState title="No medicines" message="Add medicines to inventory" action={<button className="btn btn-primary btn-md">Add Medicine</button>} /></Card>
    </div>
  )
}

export default InventoryPage
