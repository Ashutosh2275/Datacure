import { useState } from 'react'
import { useAuthStore } from '../store'
import { Card, Alert } from '../components/Common'
import { Bell, Lock, Eye, Globe } from 'lucide-react'

function SettingsPage() {
  const { user, changePassword } = useAuthStore()
  const [passwords, setPasswords] = useState({ old: '', new: '', confirm: '' })
  const [message, setMessage] = useState(null)

  const handlePasswordChange = async (e) => {
    e.preventDefault()
    if (passwords.new !== passwords.confirm) {
      setMessage({ type: 'error', text: 'Passwords do not match' })
      return
    }
    const result = await changePassword(passwords.old, passwords.new)
    if (result.success) {
      setMessage({ type: 'success', text: 'Password changed successfully' })
      setPasswords({ old: '', new: '', confirm: '' })
    } else {
      setMessage({ type: 'error', text: result.error })
    }
  }

  return (
    <div className="container-custom py-8">
      <h1 className="text-3xl font-bold mb-6">Settings</h1>

      {message && <Alert type={message.type} message={message.text} onClose={() => setMessage(null)} />}

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mt-6">
        {/* Settings Menu */}
        <div className="lg:col-span-1">
          <Card className="p-0">
            <nav className="space-y-1">
              {[
                { icon: Lock, label: 'Security', id: 'security' },
                { icon: Bell, label: 'Notifications', id: 'notifications' },
                { icon: Globe, label: 'Preferences', id: 'preferences' },
              ].map((item) => (
                <button key={item.id} className="flex items-center gap-3 w-full px-4 py-3 hover:bg-gray-50 text-left">
                  <item.icon className="w-5 h-5" />
                  {item.label}
                </button>
              ))}
            </nav>
          </Card>
        </div>

        {/* Settings Content */}
        <div className="lg:col-span-3 space-y-6">
          {/* Security */}
          <Card title="Change Password">
            <form onSubmit={handlePasswordChange} className="space-y-4">
              <div>
                <label className="label">Current Password</label>
                <input type="password" className="input" value={passwords.old} onChange={(e) => setPasswords({...passwords, old: e.target.value})} />
              </div>
              <div>
                <label className="label">New Password</label>
                <input type="password" className="input" value={passwords.new} onChange={(e) => setPasswords({...passwords, new: e.target.value})} />
              </div>
              <div>
                <label className="label">Confirm Password</label>
                <input type="password" className="input" value={passwords.confirm} onChange={(e) => setPasswords({...passwords, confirm: e.target.value})} />
              </div>
              <button type="submit" className="btn btn-primary btn-md">Update Password</button>
            </form>
          </Card>

          {/* Notifications */}
          <Card title="Notifications">
            <div className="space-y-4">
              {['Email notifications', 'SMS alerts', 'Push notifications', 'Weekly reports'].map((notif) => (
                <label key={notif} className="flex items-center gap-3 cursor-pointer">
                  <input type="checkbox" defaultChecked className="w-4 h-4" />
                  <span>{notif}</span>
                </label>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}

export default SettingsPage
