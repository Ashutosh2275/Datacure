import { Link } from 'react-router-dom'

function NotFoundPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-600 to-primary-900 p-4">
      <div className="text-center text-white">
        <h1 className="text-9xl font-bold mb-4">404</h1>
        <h2 className="text-4xl font-bold mb-4">Page Not Found</h2>
        <p className="text-xl mb-8">The page you're looking for doesn't exist</p>
        <Link to="/" className="btn btn-primary btn-md">Go to Dashboard</Link>
      </div>
    </div>
  )
}

export default NotFoundPage
