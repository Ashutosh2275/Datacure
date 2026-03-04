import { Plus } from 'lucide-react'
import { Card, EmptyState } from '../components/Common'

function BillingPage() {
  return (
    <div className="container-custom py-8">
      <div className="flex items-center justify-between mb-6">
        <div><h1 className="text-3xl font-bold">Billing</h1><p className="text-gray-600">Manage invoices and payments</p></div>
        <button className="btn btn-primary btn-md flex items-center gap-2"><Plus className="w-5 h-5" />New Invoice</button>
      </div>
      <Card><EmptyState title="No invoices" message="Create your first invoice" action={<button className="btn btn-primary btn-md">Create Invoice</button>} /></Card>
    </div>
  )
}

export default BillingPage
