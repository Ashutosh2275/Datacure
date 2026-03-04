import { format, formatDistance } from 'date-fns'

// Date formatting utilities
export const formatDate = (date, formatStr = 'MMM dd, yyyy') => {
  if (!date) return ''
  return format(new Date(date), formatStr)
}

export const formatDateTime = (date) => {
  if (!date) return ''
  return format(new Date(date), 'MMM dd, yyyy HH:mm')
}

export const timeAgo = (date) => {
  if (!date) return ''
  return formatDistance(new Date(date), new Date(), { addSuffix: true })
}

// Currency formatting
export const formatCurrency = (amount, currency = 'INR') => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency,
  }).format(amount)
}

// Number formatting
export const formatNumber = (num, decimals = 0) => {
  return Number(num).toFixed(decimals)
}

export const formatPercentage = (num, decimals = 1) => {
  return `${Number(num).toFixed(decimals)}%`
}

// Role-based utilities
export const roleColors = {
  admin: 'bg-red-100 text-red-800',
  doctor: 'bg-blue-100 text-blue-800',
  nurse: 'bg-green-100 text-green-800',
  receptionist: 'bg-purple-100 text-purple-800',
  patient: 'bg-gray-100 text-gray-800',
  pharmacist: 'bg-yellow-100 text-yellow-800',
}

export const getRoleColor = (role) => {
  return roleColors[role] || 'bg-gray-100 text-gray-800'
}

// Status utilities
export const statusColors = {
  active: 'bg-green-100 text-green-800',
  inactive: 'bg-gray-100 text-gray-800',
  pending: 'bg-yellow-100 text-yellow-800',
  completed: 'bg-blue-100 text-blue-800',
  cancelled: 'bg-red-100 text-red-800',
  no_show: 'bg-orange-100 text-orange-800',
  paid: 'bg-green-100 text-green-800',
  unpaid: 'bg-red-100 text-red-800',
  partial: 'bg-yellow-100 text-yellow-800',
  available: 'bg-green-100 text-green-800',
  occupied: 'bg-red-100 text-red-800',
  maintenance: 'bg-orange-100 text-orange-800',
}

export const getStatusColor = (status) => {
  return statusColors[status] || 'bg-gray-100 text-gray-800'
}

// Validation utilities
export const isValidEmail = (email) => {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}

export const isValidPhone = (phone) => {
  return /^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$/.test(phone)
}

export const isValidAge = (age) => {
  return age >= 0 && age <= 120
}

// Blood group utilities
export const bloodGroups = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']

export const genders = ['Male', 'Female', 'Other']

export const appointmentTypes = ['Consultation', 'Follow-up', 'Procedure', 'Emergency']

export const appointmentStatuses = ['scheduled', 'completed', 'cancelled', 'no_show', 'rescheduled']

export const invoiceStatuses = ['pending', 'paid', 'partial', 'cancelled', 'refunded']

export const medicineCategories = [
  'Antibiotics',
  'Analgesics',
  'Anti-inflammatory',
  'Cardiovascular',
  'Respiratory',
  'GI',
  'Neurological',
  'Immunosuppressants',
  'Vaccines',
  'Other',
]

// Patient status
export const patientStatuses = ['active', 'inactive', 'deceased']

// Ward types
export const wardTypes = ['ICU', 'General', 'Pediatric', 'Maternity', 'Ortho', 'Cardiology']

// Bed status
export const bedStatuses = ['available', 'occupied', 'maintenance']

// Permission checker
export const hasPermission = (userRole, requiredRole) => {
  const roleHierarchy = {
    admin: 0,
    doctor: 1,
    nurse: 2,
    receptionist: 3,
    pharmacist: 2,
    patient: 4,
  }
  return (roleHierarchy[userRole] || 999) <= (roleHierarchy[requiredRole] || 999)
}

// Error handler
export const getErrorMessage = (error) => {
  if (typeof error === 'string') return error
  if (error?.response?.data?.message) return error.response.data.message
  if (error?.response?.data?.error) return error.response.data.error
  if (error?.message) return error.message
  return 'An unexpected error occurred'
}

// Success message handlers
export const getSuccessMessage = (action) => {
  const messages = {
    create: 'Created successfully',
    update: 'Updated successfully',
    delete: 'Deleted successfully',
    save: 'Saved successfully',
    send: 'Sent successfully',
    upload: 'Uploaded successfully',
    download: 'Downloaded successfully',
    login: 'Logged in successfully',
    logout: 'Logged out successfully',
    register: 'Registered successfully',
  }
  return messages[action] || 'Operation completed successfully'
}

// Array utilities
export const groupBy = (array, key) => {
  return array.reduce((acc, obj) => {
    const group = obj[key]
    if (!acc[group]) acc[group] = []
    acc[group].push(obj)
    return acc
  }, {})
}

export const sortBy = (array, key, order = 'asc') => {
  return [...array].sort((a, b) => {
    if (order === 'asc') {
      return a[key] > b[key] ? 1 : -1
    }
    return a[key] < b[key] ? 1 : -1
  })
}

// Pagination
export const getPaginationRange = (page, totalPages, neighbors = 2) => {
  const totalNumbers = neighbors * 2 + 3
  const totalBlocks = totalNumbers + 2

  if (totalPages <= totalBlocks) {
    return Array.from({ length: totalPages }, (_, i) => i + 1)
  }

  const startPage = Math.max(2, page - neighbors)
  const endPage = Math.min(totalPages - 1, page + neighbors)

  let pages = Array.from({ length: endPage - startPage + 1 }, (_, i) => startPage + i)

  const hasLeftDots = startPage > 2
  const hasRightDots = endPage < totalPages - 1

  if (hasLeftDots) pages.unshift('...')
  if (hasRightDots) pages.push('...')

  pages.unshift(1)
  pages.push(totalPages)

  return pages
}

export default {
  formatDate,
  formatDateTime,
  timeAgo,
  formatCurrency,
  formatNumber,
  formatPercentage,
  roleColors,
  getRoleColor,
  statusColors,
  getStatusColor,
  isValidEmail,
  isValidPhone,
  isValidAge,
  bloodGroups,
  genders,
  appointmentTypes,
  appointmentStatuses,
  invoiceStatuses,
  medicineCategories,
  patientStatuses,
  wardTypes,
  bedStatuses,
  hasPermission,
  getErrorMessage,
  getSuccessMessage,
  groupBy,
  sortBy,
  getPaginationRange,
}
