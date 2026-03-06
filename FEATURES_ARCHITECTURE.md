# 🚍 SMART BUS ACCESSIBILITY SYSTEM - REQUEST MANAGEMENT FEATURES

## Complete Architecture & Features Summary

**Date:** March 5, 2026  
**Version:** 1.0 - Explicit Request Management Edition  
**Status:** ✅ Ready for Integration

---

## 📋 System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      SMART BUS SYSTEM ARCHITECTURE                       │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────────────┐          ┌──────────────────┐
│  PASSENGER PORTAL    │          │  DRIVER PORTAL   │
│  passenger_page.py   │          │  driver_page.py  │
├──────────────────────┤          ├──────────────────┤
│                      │   HTTP   │                  │
│ 1. Route Search      ├─────────>│ 1. Live Location │
│ 2. Crowd Detection   │  WebSock  │ 2. Request Panel │
│ 3. REQUEST FORM ✨   │          │ 3. ACTION BTN ✨ │
│                      │<─────────┤                  │
└──────────────────────┘          └──────────────────┘
         △                                  △
         │                                  │
         │ send_pickup_request()            │ fetch_all_requests()
         │ update_request_status()   set    │ calculate_distance()
         │                          update  │
         └─────────────────────────────────┘
                       │
                  Firebase Database
                       │
    ┌──────────────────┴──────────────────────┐
    │                                          │
    ▼                                          ▼
┌──────────────┐                       ┌──────────────┐
│ /users       │                       │ /buses       │
│ /routes      │                       │ /drivers     │
│ /stops       │                       │ /crowd       │
│              │                       │              │
│ /REQUESTS ✨ │◄──────────────────────│/assignments  │
│  - pending   │    Sync in Real-time  │              │
│  - ack       │         (2-way)       │              │
│  - completed │                       │              │
└──────────────┘                       └──────────────┘

REQUEST FLOW:
════════════════════════════════════════════════════════════════

PASSENGER SUBMITS
      │
      ├─ Opens multi-step form
      ├─ Enters personal details
      ├─ Selects route & stops
      ├─ Specifies accessibility need
      ├─ Captures GPS location
      ├─ Reviews & submits
      │
      └─> firebase_manager.send_pickup_request()
           │
           └─> Record added to /pickup_requests/
               Status: pending
               │
               └─> FCM notification sent to drivers
                   (via request_manager.py)

DRIVER RECEIVES
      │
      ├─ Sees new request in dashboard
      ├─ Views request details (name, location, need)
      ├─ Sees distance from current location
      ├─ Views passenger location on map
      │
      └─> CHOOSES ACTION:
           │
           ├─ ✅ ACCEPT
           │   └─> request_manager.accept_request()
           │       └─> Status: acknowledged
           │
           ├─ 🏁 COMPLETE
           │   └─> request_manager.complete_request()
           │       └─> Status: completed
           │
           ├─ ⏱️ SNOOZE
           │   └─> request_manager.snooze_request()
           │       └─> Status: snoozed (5 mins)
           │
           └─ ❌ REJECT
               └─> request_manager.reject_request()
                   └─> Status: declined

PASSENGER NOTIFIED
      │
      └─ Real-time update when driver accepts
         (Firebase listener on -/pickup_requests/)
```

---

## 🎯 Core Components

### 1️⃣ REQUEST MANAGER (request_manager.py)

**Purpose:** Handle all request operations  
**Responsibility:** Fetch, update, analyze requests

```
RequestManager Class:
├─ Fetch Operations (explicit)
│  ├─ fetch_all_requests()           → List of all pending requests
│  ├─ fetch_requests_by_route()      → Filter by route
│  ├─ fetch_requests_by_priority()   → Sort by priority (Elderly first)
│  ├─ fetch_urgent_requests()        → Only high-priority requests
│  └─ fetch_request_by_id()          → Single request details
│
├─ Action Operations (explicit)
│  ├─ accept_request()               → Mark as acknowledged
│  ├─ complete_request()             → Mark as completed
│  ├─ reject_request()               → Mark as declined
│  └─ snooze_request()               → Pause until later
│
├─ Data Operations (explicit)
│  ├─ get_request_distance()         → Calculate km to passenger
│  ├─ get_request_summary()          → Formatted request info
│  ├─ get_request_stats()            → Overall statistics
│  └─ get_driver_performance()       → Driver metrics
│
└─ Singleton
   └─ get_request_manager()          → Cached instance
```

**Usage Pattern:**

```python
rm = get_request_manager()
requests = rm.fetch_all_requests()
for req in requests:
    rm.accept_request(req['id'], driver_name="Raj")
    dist = rm.get_request_distance(req['id'], lat, lng)
    summary = rm.get_request_summary(req['id'])
```

---

### 2️⃣ DRIVER FEATURES (driver_request_features.py)

**Purpose:** Provide UI components for driver dashboard  
**Responsibility:** Render request cards, filters, actions

```
User Interface Components:
├─ render_driver_request_panel()
│  ├─ View Tab
│  │  ├─ Filter buttons (All/Urgent/Priority/Distance)
│  │  ├─ Request metrics (Total/Pending/Ack/Complete)
│  │  └─ Request cards with details
│  ├─ Stats Tab
│  │  ├─ Total request count
│  │  ├─ Status breakdown
│  │  └─ Disability type distribution
│  └─ History Tab
│     └─ Activity log (ready for enhancement)
│
├─ render_requests_by_filter()
│  ├─ Filter type: "all"
│  ├─ Filter type: "urgent"
│  ├─ Filter type: "priority"
│  └─ Filter type: "nearby"
│
├─ render_request_card()
│  ├─ Passenger info (name, contact)
│  ├─ Route info (boarding, destination)
│  ├─ Accessibility details
│  ├─ Distance display
│  ├─ Location map
│  └─ Action buttons
│
└─ render_request_action_buttons()
   ├─ ✅ ACCEPT button
   ├─ 🏁 COMPLETE button
   ├─ ⏱️ SNOOZE button
   └─ ❌ REJECT button
```

**Usage Pattern:**

```python
# In driver dashboard
render_driver_request_panel()

# Or custom rendering
render_requests_by_filter("priority", driver_lat, driver_lng)
render_request_card(request_data, driver_lat, driver_lng)
```

---

### 3️⃣ PASSENGER SUBMISSION (passenger_request_submission.py)

**Purpose:** Provide guided form for passengers  
**Responsibility:** Collect, validate, submit request data

```
Multi-Step Form:
├─ Step 1: Personal Information
│  ├─ Full name
│  ├─ Email address
│  └─ Phone number
│
├─ Step 2: Route & Stops
│  ├─ Bus route selection
│  ├─ Boarding stop
│  └─ Destination stop
│
├─ Step 3: Accessibility Details
│  ├─ Disability/accessibility type
│  └─ Additional notes
│
├─ Step 4: Location Capture
│  ├─ Auto-detect GPS
│  ├─ Manual coordinates
│  └─ Map selection (placeholder)
│
└─ Step 5: Review & Submit
   ├─ Review all information
   ├─ Allow editing
   └─ Submit to Firebase

Components:
├─ render_passenger_request_form()    → Full 5-step form
└─ capture_passenger_location()       → GPS/manual location
```

**Usage Pattern:**

```python
# In passenger portal
render_passenger_request_form(routes_df, stops_df)

# Returns location data
location = capture_passenger_location()
# → {lat: 13.1234, lng: 80.2456, accuracy: 50}
```

---

## 💾 Data Models

### Request Object

```python
{
    # Identity
    "id": "unique_firebase_key",

    # Personal Information
    "user_name": "John Doe",
    "email": "john@example.com",
    "phone": "+91 9876543210",

    # Route Information
    "route": "5C",
    "location": "Adyar Bus Stand",
    "boarding_stop": "Adyar Bus Stand",
    "destination_stop": "Central Station",

    # Accessibility
    "disability_type": "Wheelchair User",  # See Priority List
    "photo_url": "https://...",  # Optional

    # Location Data
    "passenger_lat": 13.1234,
    "passenger_lng": 80.2456,
    "passenger_gmaps_url": "https://maps.google.com/...",

    # Status Tracking
    "status": "pending",  # pending|acknowledged|completed|declined|snoozed
    "timestamp": 1709619600,
    "last_update": {'.sv': 'timestamp'},

    # Notes
    "admin_note": "Completed by Driver Raj at 10:15:30"
}
```

### Priority Order (Disability Types)

```
1. 🔴 URGENT
   ├─ Elderly
   ├─ Wheelchair User
   └─ Visual Impairment

2. 🟡 IMPORTANT
   ├─ Hearing Impairment
   └─ Mobility Issue

3. ⚪ STANDARD
   └─ Other
```

---

## 🎨 Feature Details

### 📍 Distance Calculation

**How it works:**

1. Get driver's current location (GPS or session state)
2. Get passenger's location from request
3. Use Haversine formula to calculate km
4. Display: "📍 2.5 km away from Madhavaram Depot"

**Color coding:**

- 🟢 Green < 5 km (nearby)
- 🟡 Orange 5-15 km (moderate)
- 🔴 Red > 15 km (far)

### 🔔 Request Notifications

**Automatic Triggers:**

- New request → FCM notification to drivers
- Driver accepts → Updates visible to passenger
- Driver completes → Request marked done
- Status changes → Admin notified

### 📊 Statistics

**Available Metrics:**

- Total requests submitted
- Pending requests (need action)
- Acknowledged requests (in progress)
- Completed requests (done)
- Breakdown by disability type

### 🗺️ Location Features

**Capture Methods:**

1. **Auto-detect GPS** - Browser geolocation API
2. **Manual Entry** - Latitude/Longitude coordinates
3. **Map Selection** - Click on map (future)

**Display Features:**

- Google Maps embed showing passenger
- Exact coordinates display
- Distance from driver's current location
- Navigation link (open in Google Maps)

---

## 🚀 Integration Checklist

### Phase 1: Add Core Modules

- [ ] Copy `request_manager.py`
- [ ] Copy `driver_request_features.py`
- [ ] Copy `passenger_request_submission.py`
- [ ] Verify all imports in `__init__.py` or main files

### Phase 2: Update Existing Files

- [ ] Add imports to `passenger_page.py`
- [ ] Add form section to passenger portal
- [ ] Add imports to `driver_page.py`
- [ ] Add panel to driver dashboard
- [ ] Update `app.py` session state

### Phase 3: Testing

- [ ] Test passenger form submission (all 5 steps)
- [ ] Verify request appears in Firebase
- [ ] Test driver request viewing
- [ ] Test all action buttons (accept, complete, etc.)
- [ ] Verify distance calculation
- [ ] Test all filters (all, urgent, priority, distance)
- [ ] Confirm statistics display

### Phase 4: Deployment

- [ ] Clear cache and restart Streamlit
- [ ] Test with real Firebase
- [ ] Monitor logs for errors
- [ ] Get user feedback
- [ ] Deploy to production

---

## 🔑 Key Features Summary

| Feature          | Passenger          | Driver            | Admin           | Status         |
| ---------------- | ------------------ | ----------------- | --------------- | -------------- |
| Submit Request   | ✅ Multi-step form | -                 | -               | ✅ Ready       |
| View Requests    | -                  | ✅ Dashboard      | ✅ Admin panel  | ✅ Ready       |
| Filter Requests  | -                  | ✅ 4 filters      | ✅ Dashboard    | ✅ Ready       |
| Accept/Complete  | -                  | ✅ Action buttons | -               | ✅ Ready       |
| Location Capture | ✅ GPS/Manual      | -                 | -               | ✅ Ready       |
| Distance Display | -                  | ✅ Auto-calculate | ✅ Reports      | ✅ Ready       |
| Statistics       | -                  | -                 | ✅ Full metrics | ✅ Ready       |
| Activity Log     | -                  | -                 | ✅ Tracking     | 🚧 Placeholder |
| Notifications    | ✅ Mobile/Web      | ✅ FCM            | ✅ Email        | ✅ Ready       |

---

## 📈 Expected Impact

### For Passengers

- **Faster Response:** Drivers see requests instantly
- **Clear Status:** Know when driver accepts
- **Better Support:** Different accessibility types are prioritized
- **Location Sharing:** Drivers find them easily

### For Drivers

- **Easy Management:** Clear UI for requests
- **Smart Filtering:** See closest/urgent first
- **Quick Actions:** One-click accept/complete
- **Context:** Full passenger info visible

### For the System

- **Real-time:** Instant updates via Firebase
- **Scalable:** Handles many simultaneous requests
- **Flexible:** Easy to customize priority/categories
- **Transparent:** Full audit trail via admin notes

---

## 🛠️ Technical Stack

- **Frontend:** Streamlit 1.x
- **Database:** Firebase Real-Time Database
- **Backend:** Python 3.8+
- **APIs:** Google Maps, Geolocation, FCM
- **Storage:** Firebase Storage (for photos)

---

## 📞 Support & Customization

### Easy Customization Options:

1. **Priority Order** → Edit in `request_manager.py`
2. **Disability Types** → Edit in `passenger_request_submission.py`
3. **Snooze Duration** → Edit in `driver_request_features.py`
4. **Colors/Styling** → CSS in component files
5. **Distance Thresholds** → Edit in `driver_request_features.py`

---

## 🎓 Learning Resources

See included documentation:

- `EXPLICIT_REQUEST_FEATURES_GUIDE.md` - Detailed API reference
- `INTEGRATION_STEPS.md` - Code snippets for integration
- This file - Architecture overview

---

**System Ready for Integration! 🚀**

All modules tested and documented. Follow INTEGRATION_STEPS.md to get started.

Questions? Check EXPLICIT_REQUEST_FEATURES_GUIDE.md for complete API reference.
