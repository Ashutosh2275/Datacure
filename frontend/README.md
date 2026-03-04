# DataCure Frontend

Hospital Intelligence Platform - React Frontend Application

## Overview

DataCure Frontend is a modern React-based web application built with Vite, providing a comprehensive interface for hospital management, patient care, billing, inventory management, and analytics.

## Tech Stack

- **Framework**: React 18.2.0
- **Build Tool**: Vite 5.0.8
- **Routing**: React Router DOM 6.20.0
- **State Management**: Zustand 4.4.2
- **HTTP Client**: Axios 1.6.2
- **Styling**: Tailwind CSS 3.4.0
- **Charts**: Recharts 2.10.3
- **Icons**: Lucide React 0.294.0
- **Date Handling**: date-fns 2.30.0

## Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable React components
│   │   ├── Layout.jsx       # Header, Sidebar, Footer
│   │   ├── ProtectedRoute.jsx
│   │   └── Common.jsx       # Loading, Error, Alert, Modal, etc.
│   ├── pages/              # Page components
│   │   ├── LoginPage.jsx
│   │   ├── RegisterPage.jsx
│   │   ├── DashboardPage.jsx
│   │   ├── PatientsPage.jsx
│   │   ├── AppointmentsPage.jsx
│   │   ├── BillingPage.jsx
│   │   ├── InventoryPage.jsx
│   │   ├── WardsPage.jsx
│   │   ├── UsersPage.jsx
│   │   ├── AIPage.jsx
│   │   ├── ReportsPage.jsx
│   │   ├── AuditPage.jsx
│   │   ├── ProfilePage.jsx
│   │   ├── SettingsPage.jsx
│   │   ├── NotFoundPage.jsx
│   │   └── UnauthorizedPage.jsx
│   ├── services/           # API service layer
│   │   └── api.js          # Axios instance + all API methods
│   ├── store/              # State management (Zustand)
│   │   └── index.js        # Auth, App, Dashboard stores
│   ├── utils/              # Utility functions
│   │   └── helpers.js      # Formatting, validation, etc.
│   ├── App.jsx             # Main router configuration
│   ├── main.jsx            # Entry point
│   ├── index.css           # Global styles + Tailwind
│   └── vite.config.js
├── public/                 # Static assets
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
└── .gitignore
```

## Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Getting Started

### 1. Environment Setup

Set environment variables in `.env`:

```env
VITE_API_URL=http://localhost:5000/api/v1
```

### 2. Running Development Server

```bash
npm run dev
```

Server will run on `http://localhost:3000` and proxy API requests to backend at `http://localhost:5000`

### 3. Login Credentials

**Demo Admin:**
- Email: admin@hospital.com
- Password: Admin@123

**Demo Doctor:**
- Email: doctor@hospital.com
- Password: Doctor@123

**Demo Patient:**
- Email: patient@hospital.com
- Password: Patient@123

## Features by Role

### Admin
- Dashboard with KPIs and statistics
- Manage patients, appointments, doctors, nurses, staff
- Billing and revenue reports
- Inventory management
- Ward and bed management
- User management
- AI model analytics
- System audit logs
- Settings and configuration

### Doctor
- Dashboard
- Manage own patients
- View appointments
- Create prescriptions
- Access patient medical records
- View reports

### Nurse
- Dashboard
- Manage patients
- Ward management
- Check appointments
- Patient vital signs monitoring

### Receptionist
- Dashboard
- Patient management
- Appointment scheduling
- Billing and invoicing

### Patient
- Dashboard
- View medical records
- Book appointments
- Track prescriptions
- View invoices and payments

## API Integration

All API calls are centralized in `src/services/api.js`:

```javascript
// Example: List patients
const response = await patientService.listPatients({ page: 1, limit: 10 })

// Example: Create appointment
const response = await appointmentService.createAppointment(appointmentData)

// Example: Get billing report
const response = await billingService.getRevenue({ start_date, end_date })
```

## State Management

Using Zustand for state management:

```javascript
// Auth store
const { user, login, logout, isAuthenticated } = useAuthStore()

// App store
const { sidebarOpen, toggleSidebar, addNotification } = useAppStore()

// Data stores
const { patients, addPatient, updatePatient } = usePatientsStore()
```

## Components

### Layout Components
- `Header` - Top navigation with user menu
- `Sidebar` - Role-based navigation menu
- `Footer` - Application footer

### Common Components
- `Loading` - Loading spinner
- `Error` - Error message display
- `Alert` - Info/Warning/Error alerts
- `Modal` - Dialog component
- `Card` - Reusable card container
- `Pagination` - Table pagination
- `Badge` - Status badges
- `EmptyState` - Empty state display

## Styling

### Tailwind CSS Classes

```jsx
// Utility classes
<div className="container-custom">  {/* Max width container */}
<div className="card">              {/* White card with shadow */}
<button className="btn btn-primary"> {/* Primary button */}
<span className="badge badge-success"> {/* Success badge */}
```

### Responsive Design
- Mobile-first approach
- Breakpoints: sm (640px), md (768px), lg (1024px), xl (1280px)
- Responsive sidebar (hidden on mobile, shown on lg+)

## Utilities

### Helper Functions
- Date: `formatDate()`, `formatDateTime()`, `timeAgo()`
- Currency: `formatCurrency()`, `formatNumber()`
- Validation: `isValidEmail()`, `isValidPhone()`, `isValidAge()`
- Constants: `bloodGroups`, `genders`, `appointmentTypes`, `wardTypes`
- Error handling: `getErrorMessage()`, `getSuccessMessage()`

## Authentication

Protected routes use `ProtectedRoute` component:

```jsx
<ProtectedRoute requiredRole="admin">
  <AdminPage />
</ProtectedRoute>
```

JWT tokens stored in localStorage and automatically added to request headers.

## Error Handling

Global error handling with automatic logout on 401 (unauthorized).

## Development

### Linting
```bash
npm run lint
npm run lint:fix
```

### Code Style
- ES6+ JavaScript
- Functional components with hooks
- CSS-in-Tailwind (no separate CSS files)
- Component-based architecture

## Building for Production

```bash
npm run build
```

Output in `dist/` directory, ready for deployment.

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Performance

- Code splitting via Vite
- Lazy loading of page components
- Responsive images
- Optimized bundle size (~250KB gzipped)

## Deployment

### Vercel
```bash
vercel
```

### Netlify
```bash
netlify deploy --prod
```

### Docker
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "run", "preview"]
```

## Troubleshooting

### CORS Issues
Ensure backend is running on `http://localhost:5000` and has CORS enabled.

### API Connection Failed
Check that `.env` has correct `VITE_API_URL`

### Module Not Found
Run `npm install` to ensure all dependencies are installed

## Contributing

1. Create feature branch
2. Make changes
3. Run linting: `npm run lint:fix`
4. Commit changes
5. Push and create pull request

## License

Proprietary - DataCure Hospital Intelligence Platform

## Support

For issues, contact: support@datacure.dev
