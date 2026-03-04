import { useAuthStore } from '../store'
import { Card } from '../components/Common'
import { User, Mail, Phone, MapPin } from 'lucide-react'

function ProfilePage() {
  const { user } = useAuthStore()

  return (
    <div className="container-custom py-8">
      <h1 className="text-3xl font-bold mb-6">My Profile</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="p-6 text-center">
          <div className="w-24 h-24 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <User className="w-12 h-12 text-primary-600" />
          </div>
          <h2 className="text-xl font-semibold">{user?.name}</h2>
          <p className="text-sm text-gray-600 uppercase">{user?.role}</p>
        </Card>

        <Card title="Contact Information" className="lg:col-span-2">
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <Mail className="w-5 h-5 text-gray-400" />
              <div><p className="text-sm text-gray-600">Email</p><p className="font-medium">{user?.email}</p></div>
            </div>
            <div className="flex items-center gap-3">
              <Phone className="w-5 h-5 text-gray-400" />
              <div><p className="text-sm text-gray-600">Phone</p><p className="font-medium">{user?.phone || 'Not set'}</p></div>
            </div>
            <div className="flex items-center gap-3">
              <MapPin className="w-5 h-5 text-gray-400" />
              <div><p className="text-sm text-gray-600">Location</p><p className="font-medium">{user?.city || 'Not set'}</p></div>
            </div>
          </div>
        </Card>
      </div>

      <Card title="Account Details" className="mt-6">
        <div className="grid grid-cols-2 gap-6">
          <div><label className="text-sm text-gray-600">Member Since</label><p className="font-medium">2024</p></div>
          <div><label className="text-sm text-gray-600">Status</label><p className="font-medium text-green-600">Active</p></div>
        </div>
      </Card>
    </div>
  )
}

export default ProfilePage
