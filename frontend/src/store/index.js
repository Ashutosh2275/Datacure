import { create } from 'zustand'
import { authService } from '../services/api'

// Auth Store
export const useAuthStore = create((set, get) => ({
  user: null,
  isAuthenticated: false,
  loading: false,
  token: localStorage.getItem('access_token') || null,

  login: async (email, password) => {
    set({ loading: true })
    try {
      const response = await authService.login(email, password)
      const { access_token, user } = response.data.data
      localStorage.setItem('access_token', access_token)
      set({
        user,
        token: access_token,
        isAuthenticated: true,
        loading: false,
      })
      return { success: true }
    } catch (error) {
      set({ loading: false })
      console.error('Login error:', error)
      console.error('Error response:', error.response?.data)
      return { success: false, error: error.response?.data?.message || 'Login failed' }
    }
  },

  register: async (data) => {
    set({ loading: true })
    try {
      const response = await authService.register(data)
      set({ loading: false })
      return { success: true, data: response.data.data }
    } catch (error) {
      set({ loading: false })
      return { success: false, error: error.response?.data?.message || 'Registration failed' }
    }
  },

  logout: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    set({
      user: null,
      token: null,
      isAuthenticated: false,
    })
  },

  getCurrentUser: async () => {
    try {
      const response = await authService.getCurrentUser()
      set({ user: response.data.data })
      return response.data.data
    } catch (error) {
      return null
    }
  },

  changePassword: async (oldPassword, newPassword) => {
    try {
      await authService.changePassword(oldPassword, newPassword)
      return { success: true }
    } catch (error) {
      return { success: false, error: error.response?.data?.message || 'Failed to change password' }
    }
  },

  initializeAuth: async () => {
    const token = localStorage.getItem('access_token')
    if (token) {
      set({ token })
      try {
        const response = await authService.getCurrentUser()
        set({
          user: response.data.data,
          isAuthenticated: true,
        })
      } catch (error) {
        localStorage.removeItem('access_token')
        set({
          token: null,
          isAuthenticated: false,
        })
      }
    }
  },
}))

// App Store
export const useAppStore = create((set) => ({
  sidebarOpen: true,
  notifications: [],
  alerts: [],

  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),

  addNotification: (notification) => {
    set((state) => ({
      notifications: [...state.notifications, { id: Date.now(), ...notification }],
    }))
  },

  removeNotification: (id) => {
    set((state) => ({
      notifications: state.notifications.filter((n) => n.id !== id),
    }))
  },

  addAlert: (alert) => {
    set((state) => ({
      alerts: [...state.alerts, { id: Date.now(), ...alert }],
    }))
  },

  removeAlert: (id) => {
    set((state) => ({
      alerts: state.alerts.filter((a) => a.id !== id),
    }))
  },

  clearAlerts: () => set({ alerts: [] }),
  clearNotifications: () => set({ notifications: [] }),
}))

// Dashboard Store
export const useDashboardStore = create((set) => ({
  dashboardData: null,
  loading: false,
  error: null,

  setDashboardData: (data) => set({ dashboardData: data }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
}))

// Patients Store
export const usePatientsStore = create((set) => ({
  patients: [],
  currentPatient: null,
  loading: false,
  error: null,
  pagination: { page: 1, limit: 10, total: 0 },

  setPatients: (patients) => set({ patients }),
  setCurrentPatient: (patient) => set({ currentPatient: patient }),
  addPatient: (patient) => set((state) => ({ patients: [patient, ...state.patients] })),
  updatePatient: (id, updates) =>
    set((state) => ({
      patients: state.patients.map((p) => (p.id === id ? { ...p, ...updates } : p)),
    })),
  deletePatient: (id) => set((state) => ({ patients: state.patients.filter((p) => p.id !== id) })),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  setPagination: (pagination) => set({ pagination }),
}))

// Appointments Store
export const useAppointmentsStore = create((set) => ({
  appointments: [],
  currentAppointment: null,
  loading: false,
  error: null,
  todayAppointments: [],

  setAppointments: (appointments) => set({ appointments }),
  setCurrentAppointment: (appointment) => set({ currentAppointment: appointment }),
  addAppointment: (appointment) => set((state) => ({ appointments: [appointment, ...state.appointments] })),
  updateAppointment: (id, updates) =>
    set((state) => ({
      appointments: state.appointments.map((a) => (a.id === id ? { ...a, ...updates } : a)),
    })),
  deleteAppointment: (id) => set((state) => ({ appointments: state.appointments.filter((a) => a.id !== id) })),
  setTodayAppointments: (appointments) => set({ todayAppointments: appointments }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
}))

// Billing Store
export const useBillingStore = create((set) => ({
  invoices: [],
  currentInvoice: null,
  loading: false,
  error: null,

  setInvoices: (invoices) => set({ invoices }),
  setCurrentInvoice: (invoice) => set({ currentInvoice: invoice }),
  addInvoice: (invoice) => set((state) => ({ invoices: [invoice, ...state.invoices] })),
  updateInvoice: (id, updates) =>
    set((state) => ({
      invoices: state.invoices.map((i) => (i.id === id ? { ...i, ...updates } : i)),
    })),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
}))

// Inventory Store
export const useInventoryStore = create((set) => ({
  medicines: [],
  currentMedicine: null,
  loading: false,
  error: null,
  lowStockAlerts: [],

  setMedicines: (medicines) => set({ medicines }),
  setCurrentMedicine: (medicine) => set({ currentMedicine: medicine }),
  addMedicine: (medicine) => set((state) => ({ medicines: [medicine, ...state.medicines] })),
  updateMedicine: (id, updates) =>
    set((state) => ({
      medicines: state.medicines.map((m) => (m.id === id ? { ...m, ...updates } : m)),
    })),
  deleteMedicine: (id) => set((state) => ({ medicines: state.medicines.filter((m) => m.id !== id) })),
  setLowStockAlerts: (alerts) => set({ lowStockAlerts: alerts }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
}))

// Wards Store
export const useWardsStore = create((set) => ({
  wards: [],
  currentWard: null,
  loading: false,
  error: null,

  setWards: (wards) => set({ wards }),
  setCurrentWard: (ward) => set({ currentWard: ward }),
  addWard: (ward) => set((state) => ({ wards: [ward, ...state.wards] })),
  updateWard: (id, updates) =>
    set((state) => ({
      wards: state.wards.map((w) => (w.id === id ? { ...w, ...updates } : w)),
    })),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
}))

export default {
  useAuthStore,
  useAppStore,
  useDashboardStore,
  usePatientsStore,
  useAppointmentsStore,
  useBillingStore,
  useInventoryStore,
  useWardsStore,
}
