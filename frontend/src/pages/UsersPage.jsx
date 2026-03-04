import { Plus } from 'lucide-react'
import { Card, EmptyState } from '../components/Common'

function UsersPage() {
  return (
    <div className="container-custom py-8">
      <div className="flex items-center justify-between mb-6">
        <div><h1 className="text-3xl font-bold">Users</h1><p className="text-gray-600">Manage hospital staff</p></div>
        <button className="btn btn-primary btn-md flex items-center gap-2"><Plus className="w-5 h-5" />Add User</button>
      </div>
      <Card><EmptyState title="No users" message="Add users to the system" action={<button className="btn btn-primary btn-md">Add User</button>} /></Card>
    </div>
  )
}

export default UsersPage
