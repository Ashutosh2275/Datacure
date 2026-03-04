# Testing Guide - DataCure Functional Buttons

## System Requirements

Ensure you have:
- Node.js 16+ and npm installed
- Python 3.8+ with Flask backend running
- PostgreSQL database running
- `VITE_API_URL` environment variable set to backend API URL (default: http://localhost:5000/api/v1)

## Starting the Application

### 1. Start the Backend Server
```bash
cd backend
python -m venv venv          # Create virtual environment if needed
source venv/bin/activate     # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py                # Should run on http://localhost:5000
```

### 2. Start the Frontend Development Server
```bash
cd frontend
npm install                  # Install dependencies if needed
npm run dev                  # Should run on http://localhost:5173
```

### 3. Access the Application
- Open your browser to the frontend URL (usually http://localhost:5173)
- Login with your credentials
- You should see the Dashboard

## Testing Button Functionality

### Test 1: Patient Management (Complete CRUD)

#### Create New Patient
1. Navigate to **Patients** page (left sidebar)
2. Click **"New Patient"** button (top right)
3. Fill in the form:
   - First Name: John
   - Last Name: Doe
   - Email: john@example.com
   - Phone: 1234567890
   - Date of Birth: 1990-01-15
   - Gender: Male
   - Blood Group: O+
   - Height: 180
   - Weight: 75
   - Allergies: Penicillin (or leave blank)
   - Insurance Provider: Aetna (or your health insurance)
   - Insurance Policy Number: POL123456
   - Emergency Contact Name: Jane Doe
   - Emergency Contact Phone: 9876543210
4. Click **Submit** button
5. ✅ Success! You should see "Patient created successfully" alert and be redirected to Patients page
6. ✅ New patient should appear in the list

#### Edit Existing Patient
1. On **Patients** page, find any patient in the list
2. Click the **Edit icon (pencil)** in the Actions column
3. You should be taken to the form with all data pre-filled
4. Modify any field (e.g., change phone number)
5. Click **Submit**
6. ✅ Success! Alert should confirm "Patient updated successfully"
7. ✅ Changes should be reflected in the list

#### Delete Patient
1. On **Patients** page, hover over any patient
2. Click the **Delete icon (trash)** in the Actions column
3. A confirmation modal should appear with message: "Are you sure you want to delete this patient?"
4. Click **Cancel** to close modal (without deleting)
5. Click Delete icon again, then click **Delete** button on modal
6. ✅ Success! Alert should confirm "Patient deleted successfully"
7. ✅ Patient should disappear from the list

#### View Patient Details
1. On **Patients** page, click **View** link on any patient
2. You should be taken to the PatientDetailPage
3. Click **Back** button to return to list

---

### Test 2: Appointment Management

#### Book New Appointment
1. Navigate to **Appointments** page
2. Click **"New Appointment"** button
3. Fill in the form:
   - Patient: Select from dropdown
   - Doctor: Select from dropdown
   - Appointment Date: Select a future date
   - Appointment Time: Select time
   - Type: Select (e.g., Consultation, Follow-up)
   - Chief Complaint: Describe the issue
   - Emergency: Check if urgent
   - Telemedicine: Check if remote
4. Click **Submit**
5. ✅ Success! Alert should confirm "Appointment booked successfully"

#### Edit/Reschedule Appointment
1. On **Appointments** page, click **Edit icon** on any appointment
2. Modify the appointment date/time
3. Click **Submit**
4. ✅ Success! Appointment should be updated

#### Cancel Appointment
1. On **Appointments** page, click **Delete icon** on any appointment
2. Confirmation modal appears: "Are you sure you want to cancel this appointment?"
3. Click **Delete** to confirm
4. ✅ Success! Alert confirms deletion and appointment disappears from list

---

### Test 3: Billing/Invoice Management

#### Create New Invoice
1. Navigate to **Billing** page
2. Click **"New Invoice"** button
3. Fill invoice details:
   - Patient: Select from dropdown
   - Invoice Date: Auto-populated (can change)
4. Add line items by clicking **"Add Item"**:
   - Item Type: Select (Consultation, Lab Test, Medicine, Room Charge, Procedure)
   - Description: E.g., "General Consultation"
   - Quantity: 1
   - Unit Price: 500
5. Click **Add Item** button in the table
6. System should auto-calculate:
   - Subtotal: Sum of all items
   - GST (18%): Calculated automatically
   - Discount: Enter if applicable
   - Total: Auto-calculated
7. Fields display in green: This is the auto-calculation working!
8. Click **Submit**
9. ✅ Success! Invoice created and appears in list

#### Edit Invoice
1. On **Billing** page, click **Edit icon** on any invoice
2. Modify items or amounts
3. Click **Submit**
4. ✅ Changes saved

#### Delete Invoice
1. On **Billing** page, click **Delete icon** on any invoice
2. Confirm in modal
3. ✅ Invoice deleted and removed from list

---

### Test 4: Inventory Management

#### Add Medicine
1. Navigate to **Inventory** page
2. Click **"Add Medicine"** button
3. Fill in medicine details:
   - Medicine Name: Aspirin
   - Generic Name: Acetylsalicylic Acid
   - Category: Select from dropdown
   - Batch Number: BATCH001
   - Manufacturing Date: Select date
   - Expiry Date: Select future date
   - Cost Price: 10
   - Selling Price: 15
   - Quantity in Stock: 100
   - Reorder Level: 20
4. Click **Submit**
5. ✅ Medicine appears in inventory list

#### Edit Medicine
1. Click **Edit icon** on any medicine
2. Modify quantities/prices
3. Click **Submit**
4. ✅ Changes appear in list

#### Delete Medicine
1. Click **Delete icon** on any medicine  
2. Confirm deletion
3. ✅ Removed from list

#### Stock Alerts
1. On **Inventory** page, look for medicines with quantity less than reorder level
2. They should be highlighted with "LOW STOCK" warning in red
3. Expiry dates in the past should appear in red color

---

### Test 5: Ward Management

#### Create Ward
1. Navigate to **Wards** page
2. Click **"Create Ward"** button
3. Fill ward details:
   - Ward Name: ICU-1
   - Ward Type: Select from dropdown (ICU, General, Pediatric, etc.)
   - Floor Number: 2
   - Total Beds: 10
   - Ward Phone: 555-1234
   - Head Nurse Name: Sarah Johnson
   - Head Nurse Phone: 555-5678
   - Description: Intensive Care Unit
4. Click **Submit**
5. ✅ Ward created and appears in list

#### Edit Ward
1. Click **Edit icon** on any ward
2. Modify bed count or contact info
3. Click **Submit**
4. ✅ Updated in list

#### Delete Ward
1. Click **Delete icon** on any ward
2. Confirm deletion
3. ✅ Removed from list

#### Bed Availability
1. Look at each ward's row
2. Available Beds column shows count
3. Should be green if > 0, red if 0 (no beds available)

---

### Test 6: User Management (Admin Only)

#### Add User
1. Navigate to **Users** page (Admin access required)
2. Click **"Add User"** button
3. Fill in user details:
   - First Name: Jane
   - Last Name: Smith
   - Email: jane@example.com
   - Phone: 555-1111
   - Role: Select from dropdown (doctor, nurse, reception, staff, etc.)
4. If role is Doctor:
   - Specialization dropdown appears
   - License Number field appears
5. Set password or leave for auto-generation
6. Click **Submit**
7. ✅ User created and appears in list

#### Edit User
1. Click **Edit icon** on any user
2. Modify details (phone, role, etc.)
3. Click **Submit**
4. ✅ Updated

#### Delete User
1. Click **Delete icon** on any user
2. Confirm deletion
3. ✅ User deactivated/removed

#### User Badges
1. Look at each user's row
2. Role appears as colored badge (different color for each role)
3. Status shows Active or Inactive

---

### Test 7: Reports & Analytics (Admin)

#### View Reports
1. Navigate to **Reports** page (Admin access required)
2. You should see:
   - System Performance KPIs (API Response Time, DB Queries, Cache Hit Rate, Error Rate)
   - Charts showing trends (Patient, Appointment, Revenue trends)
   - System Health indicators with progress bars

#### Charts and Metrics
1. Line charts should display real data loaded from backend
2. System Health indicators show percentage values
3. Recent Activity log shows timestamped events

---

## Common Issues & Solutions

### Issue: "Failed to load" error
- **Solution**: Check backend is running on correct port (5000 by default)
- Check `VITE_API_URL` environment variable is set correctly
- Check API routes exist in backend

### Issue: Forms not submitting
- **Solution**: Check browser console for errors (F12)
- Verify all required fields are filled
- Ensure authentication token is valid (check login)

### Issue: Delete button doesn't work
- **Solution**: Verify modal appears when clicking delete
- Check backend DELETE endpoint exists
- Look for API errors in browser console

### Issue: Edit form doesn't pre-fill data
- **Solution**: Check GET endpoint for loading single record works
- Verify ID parameter is being passed correctly in URL
- Check browser console for API errors

### Issue: Authentication/401 errors  
- **Solution**: Login again to refresh token
- Check token expiry on backend
- Verify CORS settings are correct

---

## Verification Checklist

Use this checklist to verify all functionality:

### Patients Module
- [ ] Can create new patient
- [ ] New patient appears in list
- [ ] Can edit patient (data pre-fills)
- [ ] Changes saved after editing
- [ ] Can delete patient with confirmation
- [ ] Patient removed after deletion
- [ ] Can search patients
- [ ] Can view patient details

### Appointments Module
- [ ] Can book new appointment
- [ ] Appointment appears in list
- [ ] Can reschedule appointment
- [ ] Can cancel appointment with confirmation
- [ ] Appointment status updates

### Billing Module
- [ ] Can create invoice with multiple line items
- [ ] Subtotal, GST, Total calculate automatically
- [ ] Can add/remove line items
- [ ] Can edit invoice
- [ ] Can delete invoice
- [ ] Discount properly reduces total

### Inventory Module
- [ ] Can add new medicine
- [ ] Medicine appears in list
- [ ] Low stock items highlighted in red
- [ ] Expired medicines shown in red
- [ ] Can edit medicine details
- [ ] Can delete medicine

### Wards Module
- [ ] Can create ward
- [ ] Ward appears with bed count
- [ ] Available beds shows correct color (green/red)
- [ ] Can edit ward details
- [ ] Can delete ward

### Users Module (Admin)
- [ ] Can create new user
- [ ] User role properly assigned
- [ ] Doctor-specific fields appear when role = doctor
- [ ] Can edit user
- [ ] Can delete user
- [ ] Role badge displays correctly

### Reports & Analytics
- [ ] Performance metrics load correctly
- [ ] Charts display trend data
- [ ] System Health indicators show values
- [ ] Recent Activity log populated

---

## Performance Notes

- **Large Lists**: If loading many records (1000+), pagination helps performance
- **Form Submission**: Should complete within 2-3 seconds normally
- **Deletes**: With confirmation modal, should be instant after confirmation
- **Search**: Debounced search updates as you type

---

## Support

If you encounter issues:
1. Check browser console (F12) for JavaScript errors
2. Check Network tab to see API requests/responses
3. Review backend logs for server errors
4. Ensure all dependencies are installed: `npm install`
5. Restart frontend: `npm run dev`
6. Clear browser cache/cookies if needed

## Next Steps

After verifying all functionality works:
1. Deploy backend to production server
2. Deploy frontend to production server
3. Configure environment variables for production
4. Test all flows in production environment
5. Set up monitoring and logging
6. Train users on new features
