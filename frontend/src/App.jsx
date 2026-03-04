import { useEffect, Suspense, lazy } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore, useAppStore } from './store'
import { Layout } from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'
import { Loading } from './components/Common'

// Pages - lazy loaded
const LoginPage = lazy(() => import('./pages/LoginPage'))
const RegisterPage = lazy(() => import('./pages/RegisterPage'))
const DashboardPage = lazy(() => import('./pages/DashboardPage'))
const PatientsPage = lazy(() => import('./pages/PatientsPage'))
const PatientDetailPage = lazy(() => import('./pages/PatientDetailPage'))
const PatientFormPage = lazy(() => import('./pages/PatientFormPage'))
const AppointmentsPage = lazy(() => import('./pages/AppointmentsPage'))
const AppointmentFormPage = lazy(() => import('./pages/AppointmentFormPage'))
const BillingPage = lazy(() => import('./pages/BillingPage'))
const BillingFormPage = lazy(() => import('./pages/BillingFormPage'))
const InventoryPage = lazy(() => import('./pages/InventoryPage'))
const InventoryFormPage = lazy(() => import('./pages/InventoryFormPage'))
const WardsPage = lazy(() => import('./pages/WardsPage'))
const WardFormPage = lazy(() => import('./pages/WardFormPage'))
const UsersPage = lazy(() => import('./pages/UsersPage'))
const UserFormPage = lazy(() => import('./pages/UserFormPage'))
const AIPage = lazy(() => import('./pages/AIPage'))
const ReportsPage = lazy(() => import('./pages/ReportsPage'))
const AuditPage = lazy(() => import('./pages/AuditPage'))
const ProfilePage = lazy(() => import('./pages/ProfilePage'))
const SettingsPage = lazy(() => import('./pages/SettingsPage'))
const NotFoundPage = lazy(() => import('./pages/NotFoundPage'))
const UnauthorizedPage = lazy(() => import('./pages/UnauthorizedPage'))
const PrescriptionsPage = lazy(() => import('./pages/PrescriptionsPage'))
const MyPrescriptionsPage = lazy(() => import('./pages/MyPrescriptionsPage'))
const MyAppointmentsPage = lazy(() => import('./pages/MyAppointmentsPage'))
const MedicalRecordsPage = lazy(() => import('./pages/MedicalRecordsPage'))
const PatientDashboardPage = lazy(() => import('./pages/PatientDashboardPage'))
const MyReportsPage = lazy(() => import('./pages/MyReportsPage'))

function App() {
  const { initializeAuth } = useAuthStore()

  useEffect(() => {
    initializeAuth()
  }, [])

  return (
    <BrowserRouter>
      <Suspense fallback={<Loading />}>
        <Routes>
          {/* Auth Routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/unauthorized" element={<UnauthorizedPage />} />
          <Route path="*" element={<NotFoundPage />} />

          {/* Protected Routes */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Layout>
                  <Navigate to="/dashboard" replace />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Layout>
                  <DashboardPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/patients"
            element={
              <ProtectedRoute>
                <Layout>
                  <PatientsPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/patients/new"
            element={
              <ProtectedRoute>
                <Layout>
                  <PatientFormPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/patients/:id"
            element={
              <ProtectedRoute>
                <Layout>
                  <PatientDetailPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/patients/:id/edit"
            element={
              <ProtectedRoute>
                <Layout>
                  <PatientFormPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/appointments"
            element={
              <ProtectedRoute>
                <Layout>
                  <AppointmentsPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/appointments/new"
            element={
              <ProtectedRoute>
                <Layout>
                  <AppointmentFormPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/appointments/:id"
            element={
              <ProtectedRoute>
                <Layout>
                  <AppointmentFormPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/billing"
            element={
              <ProtectedRoute>
                <Layout>
                  <BillingPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/billing/new"
            element={
              <ProtectedRoute>
                <Layout>
                  <BillingFormPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/billing/:id"
            element={
              <ProtectedRoute>
                <Layout>
                  <BillingFormPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/inventory"
            element={
              <ProtectedRoute>
                <Layout>
                  <InventoryPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/inventory/new"
            element={
              <ProtectedRoute>
                <Layout>
                  <InventoryFormPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/inventory/:id"
            element={
              <ProtectedRoute>
                <Layout>
                  <InventoryFormPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/wards"
            element={
              <ProtectedRoute>
                <Layout>
                  <WardsPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/wards/new"
            element={
              <ProtectedRoute>
                <Layout>
                  <WardFormPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/wards/:id"
            element={
              <ProtectedRoute>
                <Layout>
                  <WardFormPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/users"
            element={
              <ProtectedRoute requiredRole="admin">
                <Layout>
                  <UsersPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/users/new"
            element={
              <ProtectedRoute requiredRole="admin">
                <Layout>
                  <UserFormPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/users/:id"
            element={
              <ProtectedRoute requiredRole="admin">
                <Layout>
                  <UserFormPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/ai"
            element={
              <ProtectedRoute requiredRole="admin">
                <Layout>
                  <AIPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/reports"
            element={
              <ProtectedRoute requiredRole="admin">
                <Layout>
                  <ReportsPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/audit"
            element={
              <ProtectedRoute requiredRole="admin">
                <Layout>
                  <AuditPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <Layout>
                  <ProfilePage />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/settings"
            element={
              <ProtectedRoute>
                <Layout>
                  <SettingsPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Doctor Routes */}
          <Route
            path="/prescriptions"
            element={
              <ProtectedRoute>
                <Layout>
                  <PrescriptionsPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/my-reports"
            element={
              <ProtectedRoute>
                <Layout>
                  <MyReportsPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Patient Routes */}
          <Route
            path="/patient-dashboard"
            element={
              <ProtectedRoute>
                <Layout>
                  <PatientDashboardPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/medical-records"
            element={
              <ProtectedRoute>
                <Layout>
                  <MedicalRecordsPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/my-appointments"
            element={
              <ProtectedRoute>
                <Layout>
                  <MyAppointmentsPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/my-prescriptions"
            element={
              <ProtectedRoute>
                <Layout>
                  <MyPrescriptionsPage />
                </Layout>
              </ProtectedRoute>
            }
          />
        </Routes>
      </Suspense>
    </BrowserRouter>
  )
}

export default App
