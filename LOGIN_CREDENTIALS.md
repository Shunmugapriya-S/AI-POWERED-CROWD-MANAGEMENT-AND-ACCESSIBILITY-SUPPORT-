# 🔐 Smart Bus Login System

## Overview
The Smart Bus application now has a **3-step authentication flow**:

1. **Portal Selection** - All 4 portals are displayed
2. **Login Page** - Email and password authentication
3. **Portal Access** - Only the selected portal is shown after successful login

---

## 🎯 Login Credentials

### 🧍 Passenger Portal
- **Email:** `passenger@smartbus.com`
- **Password:** `pass123`

### ♿ Disabled Portal
- **Email:** `disabled@smartbus.com`
- **Password:** `disabled123`

### 🚌 Driver Portal
- **Email:** `driver@smartbus.com`
- **Password:** `driver123`

### 🛠 Admin Portal
- **Email:** `admin@smartbus.com`
- **Password:** `admin123`

---

## 📋 How It Works

### Step 1: Portal Selection
When you first open the app, you'll see all 4 portals:
- 🧍 Passenger
- ♿ Disabled
- 🚌 Driver
- 🛠 Admin

Click on any portal to proceed to login.

### Step 2: Login
After selecting a portal, you'll see a login page with:
- 📧 Email ID field
- 🔑 Password field
- ✅ Login button
- 🔙 Back button (to return to portal selection)

Enter the credentials for your selected portal and click Login.

### Step 3: Portal Access
After successful login, you'll be taken directly to your selected portal. The other 3 portals will NOT be shown.

---

## 🔄 Switching Portals

To switch to a different portal:
1. Click the **"🔙 Switch Role"** button at the bottom of the page
2. You'll be returned to the portal selection screen
3. Select a different portal and login with the appropriate credentials

---

## 🛡️ Security Notes

**For Production Use:**
- Replace the simple authentication with a proper authentication system
- Use a database to store user credentials (hashed passwords)
- Implement session management with tokens
- Add password reset functionality
- Add multi-factor authentication (MFA)
- Use HTTPS for secure communication

**Current Implementation:**
- This is a demo authentication system
- Credentials are hardcoded in the application
- Suitable for demonstration and testing purposes only

---

## 📱 Phone Number Login (Future Enhancement)

The current system uses email and password. To add phone number login:
1. Add a phone number field to the login page
2. Implement OTP (One-Time Password) verification
3. Use SMS gateway services like Twilio or AWS SNS
4. Store phone numbers in the user database

---

## 🎨 Features

✅ **4 Distinct Portals** - Passengers, Disabled, Driver, Admin
✅ **Email & Password Authentication** - Secure login for each portal
✅ **Portal Isolation** - Only selected portal is shown after login
✅ **Easy Portal Switching** - Switch between portals anytime
✅ **Demo Credentials Display** - Expandable section showing login details
✅ **Back Navigation** - Return to portal selection from login page

---

## 🚀 Running the Application

```bash
streamlit run app.py
```

Then:
1. Open the URL in your browser
2. Select a portal (all 4 will be shown)
3. Login with the credentials above
4. Access your selected portal

---

**Last Updated:** February 17, 2026
