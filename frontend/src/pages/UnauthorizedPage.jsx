import { Link } from 'react-router-dom'

function UnauthorizedPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-600 to-primary-900 p-4">
      <div className="text-center text-white">
        <h1 className="text-9xl font-bold mb-4">403</h1>
        <h2 className="text-4xl font-bold mb-4">Access Denied</h2>
        <p className="text-xl mb-8">You don't have permission to access this page</p>
        <Link to="/dashboard" className="btn btn-primary btn-md">Go to Dashboard</Link>
      </div>
    </div>
  )
}

export default UnauthorizedPage
