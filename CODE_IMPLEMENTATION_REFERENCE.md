# Code Implementation Reference - DataCure Functional Buttons

This document shows the actual code implementations for the major changes made to enable all buttons to be fully functional.

## 1. Router Configuration (App.jsx)

### Key Route Additions
All routes follow this protected pattern with the Layout component:

```jsx
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
  path="/patients/:id/edit"
  element={
    <ProtectedRoute>
      <Layout>
        <PatientFormPage />
      </Layout>
    </ProtectedRoute>
  }
/>
```

This pattern is repeated for all resources:
- **Patients**: `/patients/new`, `/patients/:id`, `/patients/:id/edit`
- **Appointments**: `/appointments/new`, `/appointments/:id`
- **Billing**: `/billing/new`, `/billing/:id`
- **Inventory**: `/inventory/new`, `/inventory/:id`
- **Wards**: `/wards/new`, `/wards/:id`
- **Users**: `/users/new`, `/users/:id`

---

## 2. List Page Button Implementation

### Example: PatientsPage.jsx - Edit/Delete Buttons

```jsx
// State for delete confirmation modal
const [deleteModal, setDeleteModal] = useState({ isOpen: false, patientId: null })

// Delete handler that calls API
const handleDelete = async () => {
  try {
    setDeleting(true)
    await patientService.deletePatient(deleteModal.patientId)
    setSuccess('Patient deleted successfully!')
    setPatients(patients.filter((p) => p.id !== deleteModal.patientId))
    setDeleteModal({ isOpen: false, patientId: null })
    setTimeout(() => setSuccess(null), 3000)
  } catch (err) {
    setError(err.response?.data?.message || 'Failed to delete patient')
  } finally {
    setDeleting(false)
  }
}

// Rendering action buttons in table
<td className="px-6 py-4 flex gap-3">
  <button 
    onClick={() => navigate(`/patients/${patient.id}`)} 
    className="text-primary-600 hover:text-primary-700 text-sm font-medium"
  >
    View
  </button>
  <button 
    onClick={() => navigate(`/patients/${patient.id}/edit`)} 
    className="text-blue-600 hover:text-blue-700"
    title="Edit"
  >
    <Edit2 className="w-4 h-4" />
  </button>
  <button 
    onClick={() => setDeleteModal({ isOpen: true, patientId: patient.id })}
    className="text-red-600 hover:text-red-700"
    title="Delete"
  >
    <Trash2 className="w-4 h-4" />
  </button>
</td>

// Delete confirmation modal
<Modal
  isOpen={deleteModal.isOpen}
  title="Delete Patient"
  onClose={() => setDeleteModal({ isOpen: false, patientId: null })}
  actions={[
    <button
      key="cancel"
      onClick={() => setDeleteModal({ isOpen: false, patientId: null })}
      className="btn btn-secondary btn-sm"
      disabled={deleting}
    >
      Cancel
    </button>,
    <button
      key="delete"
      onClick={handleDelete}
      className="btn btn-danger btn-sm"
      disabled={deleting}
    >
      {deleting ? 'Deleting...' : 'Delete'}
    </button>,
  ]}
>
  <p>Are you sure you want to delete this patient? This action cannot be undone.</p>
</Modal>
```

### Success Message Display
```jsx
{success && <Alert type="success" message={success} onClose={() => setSuccess(null)} className="mb-4" />}
```

---

## 3. Form Page Implementation

### Example: PatientFormPage.jsx Structure

```jsx
function PatientFormPage() {
  const navigate = useNavigate()
  const { id } = useParams()
  const isEditMode = !!id
  
  const [loading, setLoading] = useState(false)
  const [submitLoading, setSubmitLoading] = useState(false)
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    // ... more fields
  })
  
  // Load existing data in edit mode
  useEffect(() => {
    if (isEditMode) {
      const loadPatient = async () => {
        try {
          setLoading(true)
          const response = await patientService.getPatient(id)
          const patient = response.data.data
          setFormData({
            firstName: patient.user?.first_name || '',
            lastName: patient.user?.last_name || '',
            // ... populate all fields
          })
        } catch (err) {
          setError(err.response?.data?.message || 'Failed to load patient')
        } finally {
          setLoading(false)
        }
      }
      loadPatient()
    }
  }, [id, isEditMode])
  
  // Handle form submission (create or update)
  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setSuccess(null)
    setSubmitLoading(true)
    
    try {
      const data = {
        first_name: formData.firstName,
        last_name: formData.lastName,
        email: formData.email,
        // ... format data for API
      }
      
      if (isEditMode) {
        await patientService.updatePatient(id, data)
        setSuccess('Patient updated successfully!')
      } else {
        await patientService.createPatient(data)
        setSuccess('Patient created successfully!')
      }
      
      // Redirect after success
      setTimeout(() => navigate('/patients'), 2000)
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to save patient')
    } finally {
      setSubmitLoading(false)
    }
  }
  
  return (
    <div className="container-custom py-8">
      <button onClick={() => navigate('/patients')} className="flex items-center gap-2 text-primary-600">
        <ArrowLeft className="w-5 h-5" />
        Back to Patients
      </button>
      
      <h1 className="text-3xl font-bold mt-4">
        {isEditMode ? `Edit ${formData.firstName}` : 'New Patient'}
      </h1>
      
      {error && <Alert type="error" message={error} />}
      {success && <Alert type="success" message={success} />}
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-2 gap-4">
          <input
            type="text"
            name="firstName"
            placeholder="First Name"
            value={formData.firstName}
            onChange={handleChange}
            required
            className="input input-bordered"
          />
          <input
            type="text"
            name="lastName"
            placeholder="Last Name"
            value={formData.lastName}
            onChange={handleChange}
            required
            className="input input-bordered"
          />
          {/* More fields */}
        </div>
        
        <div className="flex gap-4">
          <button
            type="submit"
            disabled={submitLoading}
            className="btn btn-primary"
          >
            {submitLoading ? 'Saving...' : isEditMode ? 'Update Patient' : 'Create Patient'}
          </button>
          <button
            type="button"
            onClick={() => navigate('/patients')}
            className="btn btn-secondary"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  )
}
```

---

## 4. Complex Form Example: BillingFormPage

### Dynamic Line Items with Auto-Calculation

```jsx
// State for line items
const [lineItems, setLineItems] = useState([])
const [newItem, setNewItem] = useState({
  itemType: '',
  description: '',
  quantity: 1,
  unitPrice: 0,
})

// Calculate totals automatically
const subtotal = lineItems.reduce((sum, item) => sum + (item.quantity * item.unitPrice), 0)
const gst = subtotal * 0.18  // 18% GST
const discount = parseFloat(formData.discount) || 0
const total = subtotal + gst - discount

// Add item to invoice
const handleAddItem = () => {
  if (!newItem.itemType || !newItem.description || newItem.quantity <= 0 || newItem.unitPrice <= 0) {
    setError('Please fill all item fields')
    return
  }
  
  setLineItems([...lineItems, { ...newItem, id: Date.now() }])
  setNewItem({ itemType: '', description: '', quantity: 1, unitPrice: 0 })
}

// Remove item from invoice
const handleRemoveItem = (itemId) => {
  setLineItems(lineItems.filter(item => item.id !== itemId))
}

// Rendering line items table with remove button
<table className="w-full">
  <thead>
    <tr>
      <th>Item Type</th>
      <th>Description</th>
      <th>Quantity</th>
      <th>Unit Price</th>
      <th>Amount</th>
      <th>Action</th>
    </tr>
  </thead>
  <tbody>
    {lineItems.map((item) => (
      <tr key={item.id}>
        <td>{item.itemType}</td>
        <td>{item.description}</td>
        <td>{item.quantity}</td>
        <td>${item.unitPrice.toFixed(2)}</td>
        <td className="text-green-600 font-semibold">
          ${(item.quantity * item.unitPrice).toFixed(2)}
        </td>
        <td>
          <button
            onClick={() => handleRemoveItem(item.id)}
            className="text-red-600 hover:text-red-700"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </td>
      </tr>
    ))}
  </tbody>
</table>

// Auto-calculated totals (displayed in green to show they're calculated)
<div className="bg-gray-50 p-4 rounded-lg space-y-2">
  <div className="flex justify-between">
    <span>Subtotal:</span>
    <span className="text-green-600 font-semibold">${subtotal.toFixed(2)}</span>
  </div>
  <div className="flex justify-between">
    <span>GST (18%):</span>
    <span className="text-green-600 font-semibold">${gst.toFixed(2)}</span>
  </div>
  <div className="flex justify-between">
    <span>Discount:</span>
    <input
      type="number"
      value={formData.discount}
      onChange={(e) => setFormData({ ...formData, discount: e.target.value })}
      className="input input-sm w-32"
      min="0"
    />
  </div>
  <div className="flex justify-between border-t pt-2 font-bold">
    <span>Total:</span>
    <span className="text-green-600">${total.toFixed(2)}</span>
  </div>
</div>
```

---

## 5. API Service Integration

### PatientService Example (from api.js)

```javascript
const patientService = {
  // List all patients with pagination and search
  listPatients: (params = {}) =>
    ApiClient.get('/patients', { params }),
    
  // Get single patient details
  getPatient: (id) =>
    ApiClient.get(`/patients/${id}`),
    
  // Create new patient
  createPatient: (data) =>
    ApiClient.post('/patients', data),
    
  // Update existing patient
  updatePatient: (id, data) =>
    ApiClient.put(`/patients/${id}`, data),
    
  // Delete patient
  deletePatient: (id) =>
    ApiClient.delete(`/patients/${id}`),
    
  // Get list of doctors for dropdown
  getDoctors: () =>
    ApiClient.get('/users?role=doctor'),
}
```

All other services follow the same pattern (appointmentService, billingService, etc.)

---

## 6. Alert & Modal Components

### Alert Component Usage
```jsx
{success && <Alert type="success" message={success} onClose={() => setSuccess(null)} className="mb-4" />}
{error && <Alert type="error" message={error} onClose={() => setError(null)} />}
```

### Modal Component Usage
```jsx
<Modal
  isOpen={deleteModal.isOpen}
  title="Delete Patient"
  onClose={() => setDeleteModal({ isOpen: false, patientId: null })}
  actions={[
    <button key="cancel" onClick={cancelHandler} className="btn btn-secondary btn-sm">
      Cancel
    </button>,
    <button key="delete" onClick={deleteHandler} className="btn btn-danger btn-sm">
      Delete
    </button>,
  ]}
>
  <p>Are you sure you want to delete this patient? This action cannot be undone.</p>
</Modal>
```

---

## 7. Navigation Between Pages

### In List Pages - Navigate to Create Form
```jsx
<button onClick={() => navigate('/patients/new')} className="btn btn-primary">
  <Plus className="w-5 h-5" />
  New Patient
</button>
```

### In List Pages - Navigate to Edit Form
```jsx
<button 
  onClick={() => navigate(`/patients/${patient.id}/edit`)} 
  className="text-blue-600"
>
  <Edit2 className="w-4 h-4" />
</button>
```

### In Form Pages - Navigate Back
```jsx
<button onClick={() => navigate('/patients')} className="flex items-center gap-2">
  <ArrowLeft className="w-5 h-5" />
  Back to Patients
</button>

// After successful submission:
setTimeout(() => navigate('/patients'), 2000)
```

---

## 8. Form Validation Example

### PatientFormPage - Validation
```jsx
// Required fields validation
<input
  type="email"
  name="email"
  value={formData.email}
  onChange={handleChange}
  required  // HTML5 validation
  className="input input-bordered"
/>

// Custom validation on submit
const handleSubmit = async (e) => {
  e.preventDefault()
  
  // Check required fields
  if (!formData.firstName || !formData.lastName) {
    setError('First name and last name are required')
    return
  }
  
  // Email format validation
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(formData.email)) {
    setError('Please enter a valid email')
    return
  }
  
  // Proceed with API call...
}
```

---

## 9. Error Handling Pattern

Used consistently across all forms and list pages:

```jsx
// State for error tracking
const [error, setError] = useState(null)

// Try-catch with user-friendly messages
try {
  setLoading(true)
  const response = await patientService.listPatients()
  setPatients(response.data.data.patients)
} catch (err) {
  // Use API error message if available, fallback to generic
  setError(err.response?.data?.message || 'Failed to load patients')
} finally {
  setLoading(false)
}

// Display error to user
{error && <Alert type="error" message={error} />}
```

---

## 10. Loading States

All async operations show loading state to user:

```jsx
// On form submission
<button disabled={submitLoading} className="btn btn-primary">
  {submitLoading ? 'Saving...' : 'Submit'}
</button>

// On page load
if (loading) return <Loading />

// On delete confirm
<button disabled={deleting} className="btn btn-danger">
  {deleting ? 'Deleting...' : 'Delete'}
</button>
```

---

## Summary of Key Changes

| File | Change | Purpose |
|------|--------|---------|
| App.jsx | Added 6 lazy imports + 18 routes | Enable navigation to form pages |
| PatientsPage.jsx | Added Edit/Delete buttons + Modal | CRUD on patients list |
| PatientFormPage.jsx | New file with form logic | Create/edit patients |
| AppointmentsPage.jsx | Added Edit/Cancel buttons | Manage appointments |
| AppointmentFormPage.jsx | New file with booking logic | Book/reschedule appointments |
| BillingPage.jsx | Rewrote with table + CRUD | Manage invoices |
| BillingFormPage.jsx | New file with line items | Complex invoice creation |
| InventoryPage.jsx | Added Edit/Delete with alerts | Medicine inventory CRUD |
| InventoryFormPage.jsx | New file with medicine form | Add/edit medicines |
| WardsPage.jsx | Added ward management buttons | Ward CRUD |
| WardFormPage.jsx | New file with ward form | Create/edit wards |
| UsersPage.jsx | Added user management | User CRUD (Admin) |
| UserFormPage.jsx | New file with user form | Create/edit users |
| ReportsPage.jsx | Enhanced with API data | Display real analytics |

---

All implementations follow React best practices:
- ✅ Proper state management with useState
- ✅ Effect hooks for data loading
- ✅ Error handling with try-catch
- ✅ Loading state indicators
- ✅ User feedback with alerts/modals
- ✅ Proper form validation
- ✅ Responsive design with Tailwind CSS
- ✅ Accessibility with proper labels and titles
