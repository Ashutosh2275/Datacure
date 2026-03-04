import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Menu, X, LogOut, Settings, Bell, User } from 'lucide-react'
import { useAuthStore, useAppStore } from '../store'

function Header() {
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()
  const { sidebarOpen, toggleSidebar } = useAppStore()
  const [showUserMenu, setShowUserMenu] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="flex items-center justify-between h-16 px-4 sm:px-6">
        <div className="flex items-center gap-4">
          {/* Sidebar toggle */}
          <button
            onClick={toggleSidebar}
            className="lg:hidden p-2 hover:bg-gray-100 rounded-lg"
            aria-label="Toggle sidebar"
          >
            {sidebarOpen ? (
              <X className="w-6 h-6" />
            ) : (
              <Menu className="w-6 h-6" />
            )}
          </button>

          {/* Logo/Brand */}
          <Link to="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold">D</span>
            </div>
            <h1 className="font-bold text-xl text-gray-900 hidden sm:block">DataCure</h1>
          </Link>
        </div>

        <div className="flex items-center gap-4">
          {/* Notifications */}
          <button className="p-2 hover:bg-gray-100 rounded-lg relative">
            <Bell className="w-5 h-5 text-gray-600" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-danger rounded-full"></span>
          </button>

          {/* User menu */}
          <div className="relative">
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="p-2 hover:bg-gray-100 rounded-lg flex items-center gap-2"
            >
              <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                <User className="w-5 h-5 text-primary-600" />
              </div>
              <span className="text-sm font-medium hidden sm:block">{user?.name}</span>
            </button>

            {/* User dropdown */}
            {showUserMenu && (
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-10">
                <div className="px-4 py-2 border-b border-gray-200">
                  <p className="text-sm font-medium">{user?.name}</p>
                  <p className="text-xs text-gray-500">{user?.email}</p>
                </div>
                <Link
                  to="/profile"
                  className="flex items-center gap-2 px-4 py-2 hover:bg-gray-50 text-sm"
                  onClick={() => setShowUserMenu(false)}
                >
                  <User className="w-4 h-4" />
                  Profile
                </Link>
                <Link
                  to="/settings"
                  className="flex items-center gap-2 px-4 py-2 hover:bg-gray-50 text-sm"
                  onClick={() => setShowUserMenu(false)}
                >
                  <Settings className="w-4 h-4" />
                  Settings
                </Link>
                <button
                  onClick={handleLogout}
                  className="flex items-center gap-2 px-4 py-2 hover:bg-gray-50 text-sm w-full text-left text-danger"
                >
                  <LogOut className="w-4 h-4" />
                  Logout
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}

function Sidebar() {
  const { user } = useAuthStore()
  const { sidebarOpen } = useAppStore()

  const menuItems = {
    admin: [
      { label: 'Dashboard', path: '/dashboard', icon: '📊' },
      { label: 'Patients', path: '/patients', icon: '👥' },
      { label: 'Appointments', path: '/appointments', icon: '📅' },
      { label: 'Billing', path: '/billing', icon: '💳' },
      { label: 'Inventory', path: '/inventory', icon: '📦' },
      { label: 'Wards', path: '/wards', icon: '🏥' },
      { label: 'Users', path: '/users', icon: '👨‍⚕️' },
      { label: 'AI Analytics', path: '/ai', icon: '🤖' },
      { label: 'Reports', path: '/reports', icon: '📈' },
      { label: 'Audit', path: '/audit', icon: '📋' },
    ],
    doctor: [
      { label: 'Dashboard', path: '/dashboard', icon: '📊' },
      { label: 'My Patients', path: '/patients', icon: '👥' },
      { label: 'Appointments', path: '/appointments', icon: '📅' },
      { label: 'Prescriptions', path: '/prescriptions', icon: '💊' },
      { label: 'Reports', path: '/my-reports', icon: '📄' },
    ],
    nurse: [
      { label: 'Dashboard', path: '/dashboard', icon: '📊' },
      { label: 'Patients', path: '/patients', icon: '👥' },
      { label: 'Wards', path: '/wards', icon: '🏥' },
      { label: 'Appointments', path: '/appointments', icon: '📅' },
    ],
    receptionist: [
      { label: 'Dashboard', path: '/dashboard', icon: '📊' },
      { label: 'Patients', path: '/patients', icon: '👥' },
      { label: 'Appointments', path: '/appointments', icon: '📅' },
      { label: 'Billing', path: '/billing', icon: '💳' },
    ],
    patient: [
      { label: 'Dashboard', path: '/patient-dashboard', icon: '📊' },
      { label: 'My Records', path: '/medical-records', icon: '📄' },
      { label: 'My Appointments', path: '/my-appointments', icon: '📅' },
      { label: 'Prescriptions', path: '/my-prescriptions', icon: '💊' },
    ],
  }

  const items = menuItems[user?.role] || []

  return (
    <aside
      className={`${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      } lg:translate-x-0 fixed lg:static left-0 top-16 lg:top-0 h-screen w-64 bg-gray-900 text-white transition-transform duration-200 z-40 overflow-y-auto`}
    >
      <nav className="p-4 space-y-2">
        {items.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className="block px-4 py-3 rounded-lg hover:bg-gray-800 transition-colors"
          >
            <span className="mr-3">{item.icon}</span>
            {item.label}
          </Link>
        ))}
      </nav>
    </aside>
  )
}

function Footer() {
  return (
    <footer className="bg-gray-900 text-white py-8 mt-12">
      <div className="container-custom">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          <div>
            <h3 className="font-bold text-lg mb-4">DataCure</h3>
            <p className="text-gray-400 text-sm">Hospital Intelligence Platform</p>
          </div>
          <div>
            <h4 className="font-semibold mb-4">Product</h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><a href="#" className="hover:text-white">Features</a></li>
              <li><a href="#" className="hover:text-white">Pricing</a></li>
              <li><a href="#" className="hover:text-white">Security</a></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-4">Support</h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><a href="#" className="hover:text-white">Documentation</a></li>
              <li><a href="#" className="hover:text-white">Help Center</a></li>
              <li><a href="#" className="hover:text-white">Contact</a></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-4">Legal</h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><a href="#" className="hover:text-white">Privacy</a></li>
              <li><a href="#" className="hover:text-white">Terms</a></li>
              <li><a href="#" className="hover:text-white">Compliance</a></li>
            </ul>
          </div>
        </div>
        <div className="border-t border-gray-800 pt-8 text-center text-gray-400 text-sm">
          <p>&copy; 2024 DataCure. All rights reserved.</p>
        </div>
      </div>
    </footer>
  )
}

export function Layout({ children }) {
  return (
    <div className="flex flex-col lg:flex-row min-h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Header />
        <main className="flex-1 overflow-auto">
          {children}
        </main>
        <Footer />
      </div>
    </div>
  )
}

export default Layout
