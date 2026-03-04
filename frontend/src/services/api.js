import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api/v1'

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth Service
export const authService = {
  register: (data) => apiClient.post('/auth/register', data),
  login: (email, password) => apiClient.post('/auth/login', { email, password }),
  logout: () => apiClient.post('/auth/logout'),
  getCurrentUser: () => apiClient.get('/auth/me'),
  changePassword: (oldPassword, newPassword) =>
    apiClient.post('/auth/change-password', { old_password: oldPassword, new_password: newPassword }),
  refreshToken: () => apiClient.post('/auth/refresh'),
}

// Patient Service
export const patientService = {
  listPatients: (params) => apiClient.get('/patients', { params }),
  getPatient: (id) => apiClient.get(`/patients/${id}`),
  createPatient: (data) => apiClient.post('/patients', data),
  updatePatient: (id, data) => apiClient.put(`/patients/${id}`, data),
  deletePatient: (id) => apiClient.delete(`/patients/${id}`),
  getMedicalRecords: (patientId) => apiClient.get(`/patients/${patientId}/medical-records`),
  getDoctors: () => apiClient.get('/doctors'),
}

// Appointment Service
export const appointmentService = {
  listAppointments: (params) => apiClient.get('/appointments', { params }),
  getAppointment: (id) => apiClient.get(`/appointments/${id}`),
  createAppointment: (data) => apiClient.post('/appointments', data),
  rescheduleAppointment: (id, data) => apiClient.put(`/appointments/${id}`, data),
  cancelAppointment: (id, reason) => apiClient.delete(`/appointments/${id}`, { data: { reason } }),
  completeAppointment: (id, notes) => apiClient.post(`/appointments/${id}/complete`, { notes }),
  getTodayAppointments: () => apiClient.get('/appointments/today'),
}

// Prescription Service
export const prescriptionService = {
  listPrescriptions: (params) => apiClient.get('/prescriptions', { params }),
  getPrescription: (id) => apiClient.get(`/prescriptions/${id}`),
  createPrescription: (data) => apiClient.post('/prescriptions', data),
  updatePrescription: (id, data) => apiClient.put(`/prescriptions/${id}`, data),
  dispenseMedicine: (id) => apiClient.post(`/prescriptions/${id}/dispense`),
}

// Billing Service
export const billingService = {
  listInvoices: (params) => apiClient.get('/billing/invoices', { params }),
  getInvoice: (id) => apiClient.get(`/billing/invoices/${id}`),
  createInvoice: (data) => apiClient.post('/billing/invoices', data),
  updateInvoice: (id, data) => apiClient.put(`/billing/invoices/${id}`, data),
  recordPayment: (id, data) => apiClient.post(`/billing/invoices/${id}/pay`, data),
  generatePDF: (id) => apiClient.get(`/billing/invoices/${id}/pdf`),
  getRevenue: (params) => apiClient.get('/billing/reports/revenue', { params }),
  getUnpaidInvoices: () => apiClient.get('/billing/reports/unpaid'),
  getPaymentBreakdown: (params) => apiClient.get('/billing/reports/breakdown', { params }),
}

// Inventory Service
export const inventoryService = {
  listMedicines: (params) => apiClient.get('/inventory/medicines', { params }),
  getMedicine: (id) => apiClient.get(`/inventory/medicines/${id}`),
  createMedicine: (data) => apiClient.post('/inventory/medicines', data),
  updateMedicine: (id, data) => apiClient.put(`/inventory/medicines/${id}`, data),
  getStockStatus: (params) => apiClient.get('/inventory/stock', { params }),
  addStock: (data) => apiClient.post('/inventory/stock/add', data),
  consumeStock: (data) => apiClient.post('/inventory/stock/consume', data),
  getExpiringMedicines: (days = 30) => apiClient.get('/inventory/expiry', { params: { days } }),
  getLowStockAlerts: () => apiClient.get('/inventory/low-stock'),
  createPurchaseOrder: (data) => apiClient.post('/inventory/purchase-order', data),
  batchUpdateStock: (data) => apiClient.post('/inventory/batch-update', data),
  adjustStock: (id, data) => apiClient.post(`/inventory/adjust-stock/${id}`, data),
}

// Ward Service
export const wardService = {
  listWards: (params) => apiClient.get('/wards', { params }),
  getWard: (id) => apiClient.get(`/wards/${id}`),
  createWard: (data) => apiClient.post('/wards', data),
  updateWard: (id, data) => apiClient.put(`/wards/${id}`, data),
  getWardBeds: (wardId) => apiClient.get(`/wards/${wardId}/beds`),
  getOccupancyStats: (wardId) => apiClient.get(`/wards/${wardId}/occupancy`),
  admitPatient: (wardId, data) => apiClient.post(`/wards/${wardId}/admit`, data),
  dischargePatient: (wardId, data) => apiClient.post(`/wards/${wardId}/discharge`, data),
  transferPatient: (data) => apiClient.post('/wards/transfer-patient', data),
  getWardSummary: (wardId) => apiClient.get(`/wards/${wardId}/summary`),
  getBedAllocation: (wardId) => apiClient.get(`/wards/${wardId}/bed-allocation`),
}

// User Service
export const userService = {
  listUsers: (params) => apiClient.get('/users', { params }),
  getUser: (id) => apiClient.get(`/users/${id}`),
  updateUser: (id, data) => apiClient.put(`/users/${id}`, data),
  deactivateUser: (id) => apiClient.delete(`/users/${id}`),
  listDoctors: (params) => apiClient.get('/users/doctors', { params }),
  listNurses: (params) => apiClient.get('/users/nurses', { params }),
  listStaff: (params) => apiClient.get('/users/staff', { params }),
  resetPassword: (id, newPassword) => apiClient.post(`/users/${id}/reset-password`, { password: newPassword }),
}

// AI Service
export const aiService = {
  getReadmissionRisk: (patientId) => apiClient.get(`/ai/readmission-risk/${patientId}`),
  getNoShowPrediction: (appointmentId) => apiClient.get(`/ai/no-show-prediction/${appointmentId}`),
  getPatientFlow: (params) => apiClient.get('/ai/patient-flow', { params }),
  getMedicineDemand: (params) => apiClient.get('/ai/medicine-demand', { params }),
  getRiskScores: (params) => apiClient.get('/ai/risk-scores', { params }),
  getMetrics: () => apiClient.get('/ai/metrics'),
}

// Admin Service
export const adminService = {
  getDashboard: () => apiClient.get('/admin/dashboard'),
  getPatientKPI: (params) => apiClient.get('/admin/kpi/patients', { params }),
  getAppointmentKPI: (params) => apiClient.get('/admin/kpi/appointments', { params }),
  getRevenueKPI: (params) => apiClient.get('/admin/kpi/revenue', { params }),
  getOccupancyKPI: (params) => apiClient.get('/admin/kpi/occupancy', { params }),
  getTrends: (params) => apiClient.get('/admin/analytics/trends', { params }),
  getSystemPerformance: () => apiClient.get('/admin/analytics/performance'),
  getAIModelsAnalytics: () => apiClient.get('/admin/analytics/ai-models'),
  getErrorLogs: (params) => apiClient.get('/admin/logs/errors', { params }),
  getSettings: () => apiClient.get('/admin/settings'),
  updateSettings: (data) => apiClient.put('/admin/settings', data),
}

// Audit Service
export const auditService = {
  listAuditLogs: (params) => apiClient.get('/audit/logs', { params }),
  getAuditLog: (id) => apiClient.get(`/audit/logs/${id}`),
  getUserActivityReport: (params) => apiClient.get('/audit/reports/user-activity', { params }),
  getComplianceReport: (params) => apiClient.get('/audit/reports/compliance', { params }),
  getDataAccessReport: (params) => apiClient.get('/audit/reports/data-access', { params }),
  exportAuditLogs: (params) => apiClient.get('/audit/export', { params }),
  searchAuditLogs: (data) => apiClient.post('/audit/search', data),
  getAuditSummary: () => apiClient.get('/audit/summary'),
}

export default apiClient
