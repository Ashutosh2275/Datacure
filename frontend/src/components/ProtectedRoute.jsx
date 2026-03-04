import { Navigate } from 'react-router-dom'
import { useAuthStore } from '../store'

export function ProtectedRoute({ children, requiredRole }) {
  const { isAuthenticated, user } = useAuthStore()

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  if (requiredRole && user?.role !== requiredRole && requiredRole !== 'patient') {
    return <Navigate to="/unauthorized" replace />
  }

  return children
}

export default ProtectedRoute
