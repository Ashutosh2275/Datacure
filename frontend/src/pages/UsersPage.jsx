import { Plus } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { Card, EmptyState } from '../components/Common'

function UsersPage() {
  const navigate = useNavigate()
  return (
    <div className="container-custom py-8">
      <div className="flex items-center justify-between mb-6">
        <div><h1 className="text-3xl font-bold">Users</h1><p className="text-gray-600">Manage system users and roles</p></div>
        <button onClick={() => navigate('/users/new')} className="btn btn-primary btn-md flex items-center gap-2"><Plus className="w-5 h-5" />Add User</button>
      </div>
      <Card><EmptyState title="No users" message="Add users to the system" action={<button onClick={() => navigate('/users/new')} className="btn btn-primary btn-md">Add User</button>} /></Card>
    </div>
  )
}

export default UsersPage
