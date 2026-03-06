# 🚍 EXPLICIT REQUEST MANAGEMENT SYSTEM - IMPLEMENTATION GUIDE

## Overview

This implementation adds **explicit request management features** to your smart bus system. The system now has clear, structured operations for:

1. **Passengers** → Submit detailed accessibility requests
2. **Drivers** → View, filter, and manage requests with explicit actions
3. **Administrators** → Track request statistics and performance

---

## 📦 New Modules Created

### 1. **request_manager.py** - Core Request Operations

Central module handling all request operations with explicit methods:

#### Fetching Operations:

```python
from request_manager import get_request_manager

rm = get_request_manager()

# EXPLICIT FETCH OPERATIONS
all_requests = rm.fetch_all_requests()                    # Get all pending requests
route_requests = rm.fetch_requests_by_route("5C")        # Get requests for specific route
urgent_requests = rm.fetch_urgent_requests()              # Get high-priority requests only
priority_sorted = rm.fetch_requests_by_priority()         # Get sorted by priority level
single_request = rm.fetch_request_by_id("request_id123") # Get one specific request
```

#### Action Operations:

```python
# EXPLICIT ACTION OPERATIONS
rm.accept_request(request_id, driver_name="Raj")          # Accept a request
rm.complete_request(request_id, driver_name="Raj")        # Mark as completed
rm.reject_request(request_id, driver_name="Raj", reason="Not available")  # Decline
rm.snooze_request(request_id, minutes=5)                  # Snooze for later
```

#### Data Retrieval:

```python
# GET DETAILED INFORMATION
distance = rm.get_request_distance(request_id, driver_lat, driver_lng)  # Distance in km
summary = rm.get_request_summary(request_id)              # Formatted request details
stats = rm.get_request_stats()                            # Overall statistics
```

#### Statistics:

```python
# PERFORMANCE TRACKING
stats = rm.get_request_stats()
# Returns:
# {
#   "total": 15,
#   "pending": 5,
#   "acknowledged": 3,
#   "completed": 7,
#   "by_disability": {"Elderly": 4, "Wheelchair User": 3, ...}
# }
```

---

### 2. **driver_request_features.py** - Driver UI Components

Pre-built UI components for the driver dashboard:

#### Main Panel:

```python
from driver_request_features import render_driver_request_panel

# Add to driver dashboard
render_driver_request_panel()  # Shows all features in tabbed interface
```

#### Features included:

- **View Requests Tab**
  - Filter by: All, Urgent, Priority, Distance
  - Real-time request cards with detailed information
  - Action buttons for each request
- **Statistics Tab**
  - Total/pending/acknowledged/completed counts
  - Breakdown by disability type
- **History Tab**
  - Activity log (placeholder for future enhancement)

#### Individual Components:

```python
from driver_request_features import (
    render_request_card,
    render_request_action_buttons,
    render_requests_by_filter
)

# Render a single request card
render_request_card(request_data, driver_lat, driver_lng)

# Show action buttons for a request
render_request_action_buttons(request_id, request_data)

# Filter and display requests
render_requests_by_filter("priority", driver_lat, driver_lng)
# Filters: "all", "urgent", "priority", "nearby"
```

---

### 3. **passenger_request_submission.py** - Passenger UI for Requests

Complete multi-step form for passengers to submit requests:

```python
from passenger_request_submission import render_passenger_request_form

# Add to passenger portal
render_passenger_request_form(routes_df, stops_df)
```

#### 5-Step Form:

1. **👤 Personal Information** - Name, email, phone
2. **🚌 Route & Stops** - Bus selection, boarding, destination
3. **♿ Accessibility Details** - Disability type, special needs
4. **📍 Location Capture** - GPS auto-detect or manual coordinates
5. **✅ Review & Submit** - Confirmation before submission

#### Location Capture Methods:

```python
from passenger_request_submission import capture_passenger_location

# Auto-capture GPS location from browser
location = capture_passenger_location()
# Returns: {lat: float, lng: float, accuracy: float}
```

---

## 🚀 Integration Guide

### Step 1: Update Passenger Portal

In `passenger_page.py`, add the new request submission form:

```python
from passenger_request_submission import render_passenger_request_form

def render_passenger(routes, stops):
    # ... existing code ...

    # Add new request section
    st.markdown("### 📋 Accessibility Pickup Request")
    render_passenger_request_form(routes, stops)
```

### Step 2: Update Driver Dashboard

In `driver_page.py`, add the request management panel:

```python
from driver_request_features import render_driver_request_panel

def _render_driver_dashboard():
    # ... existing code ...

    # Add explicit request management
    st.markdown("### 🚍 Request Management Center")
    render_driver_request_panel()
```

### Step 3: Session State for Driver Location (Recommended)

```python
# In app.py or driver_page.py initialization
if "driver_lat" not in st.session_state:
    st.session_state.driver_lat = 13.1180  # Madhavaram depot
if "driver_lng" not in st.session_state:
    st.session_state.driver_lng = 80.2350
```

---

## 📋 Request Data Structure

### Request Object:

```python
{
    "id": "request_unique_id",
    "user_name": "John Doe",
    "email": "john@example.com",
    "phone": "+91 9876543210",
    "location": "Adyar Bus Stand",
    "route": "5C",
    "disability_type": "Wheelchair User",
    "boarding_stop": "Adyar Bus Stand",
    "destination_stop": "Central Station",
    "passenger_lat": 13.1234,
    "passenger_lng": 80.2456,
    "passenger_gmaps_url": "https://maps.google.com/...",
    "photo_url": "https://...", (optional)
    "status": "pending",  # pending, acknowledged, completed, declined, snoozed
    "timestamp": 1234567890,
    "admin_note": "Completed by Driver John at 10:15:30"
}
```

---

## 🎯 Usage Examples

### Example 1: Driver Accepting a Request

```python
from request_manager import get_request_manager

rm = get_request_manager()

# Get urgent requests
urgent = rm.fetch_urgent_requests()

for request in urgent:
    request_id = request.get("id")
    passenger = request.get("user_name")

    # Driver decides to accept
    if user_clicks_accept:
        rm.accept_request(request_id, driver_name="Raj")
        # Request status changes to "acknowledged"
```

### Example 2: Display Requests by Distance

```python
from driver_request_features import render_requests_by_filter

# Get driver's current location (e.g., from GPS)
driver_lat = 13.1245
driver_lng = 80.2500

# Show requests sorted by distance
render_requests_by_filter("nearby", driver_lat, driver_lng)
```

### Example 3: Get Statistics for Admin

```python
from request_manager import get_request_manager

rm = get_request_manager()
stats = rm.get_request_stats()

print(f"Total: {stats['total']}")
print(f"Pending: {stats['pending']}")
print(f"Completed: {stats['completed']}")

for disability, count in stats['by_disability'].items():
    print(f"{disability}: {count}")
```

---

## 🎨 Features Breakdown

### For Drivers:

✅ **Real-time Request View**

- See incoming accessibility requests instantly
- Get notifications when new requests arrive

✅ **Smart Filtering**

- Filter by: All, Urgent, Priority, Distance
- See requests closest to you first

✅ **Explicit Actions**

- ACCEPT - Acknowledge receipt of request
- COMPLETE - Mark pickup as done
- SNOOZE - Deal with later (5 mins)
- REJECT - Decline with reason

✅ **Location Intelligence**

- View passenger GPS location on map
- Calculate distance automatically
- Get ETA based on coordinates

✅ **Accessibility Awareness**

- See disability type for each request
- Get accessibility-specific guidance
- Priority sorting (Elderly, Wheelchair, etc.)

---

### For Passengers:

✅ **Guided Form Process**

- 5-step form with clear instructions
- Progress indicator showing current step
- Back/Next navigation

✅ **Location Capture**

- Auto-detect GPS from browser
- Manual coordinate entry backup
- Accuracy display

✅ **Accessibility Details**

- Select specific accessibility need
- Add custom notes
- Contact information preserved

✅ **Summary Review**

- Review all entered data before submission
- Edit capability at any step
- Clear confirmation messaging

---

### For Administrators:

✅ **Request Analytics**

- Total requests, pending, acknowledged, completed
- Breakdown by disability type
- Request metrics in one dashboard

✅ **Request History**

- Track all request actions
- Timestamps for all operations
- Admin notes on updates

---

## 🔄 Request Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│ PASSENGER submits request via form                          │
│ Status: PENDING                                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ DRIVER sees request in dashboard                            │
│ Can: Accept, Snooze, or Reject                             │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
    ACCEPTED         SNOOZED            REJECTED
    Status:          Status:            Status:
    ACKNOWLEDGED     SNOOZED            DECLINED
        │                │                │
        └────────────────┼────────────────┘
                         │
                         ▼
            ┌─────────────────────────┐
            │ DRIVER proceeds to      │
            │ pickup location         │
            │ Status: ACKNOWLEDGED    │
            └────────────┬────────────┘
                         │
                         ▼
            ┌─────────────────────────┐
            │ DRIVER marks COMPLETE   │
            │ Status: COMPLETED       │
            └─────────────────────────┘
```

---

## 🛠️ Customization Options

### Customize Priority Levels:

Edit in `request_manager.py`:

```python
priority_order = {
    "Elderly": 1,                   # Highest priority
    "Wheelchair User": 2,
    "Visual Impairment": 3,
    "Hearing Impairment": 4,
    "Mobility Issue": 5,
    "Other": 6                      # Lowest priority
}
```

### Customize Snooze Duration:

Edit in `driver_request_features.py`:

```python
# Change default snooze time (currently 5 minutes)
rm.snooze_request(request_id, minutes=10)  # 10 minutes instead
```

### Customize Disability Types:

Edit in `passenger_request_submission.py`:

```python
disability_options = [
    "Elderly",
    "Wheelchair User",
    "Visual Impairment",
    "Hearing Impairment",
    "Mobility Issue",
    "Pregnant",                # Add new
    "Temporary Injury",        # Add new
    "Other"
]
```

---

## 📊 Data Flow Diagram

```
PASSENGER PORTAL
│
├─ render_passenger_request_form()
│  ├─ Step 1: Personal Info
│  ├─ Step 2: Route Selection
│  ├─ Step 3: Accessibility Details
│  ├─ Step 4: Location Capture
│  └─ Step 5: Review & Submit
│
└─ firebase_manager.send_pickup_request()
   │
   └─ Firebase Real-Time Database
      │
      └─ DRIVER PORTAL
         │
         ├─ request_manager.fetch_all_requests()
         ├─ request_manager.fetch_requests_by_priority()
         ├─ request_manager.fetch_requests_by_distance()
         │
         └─ driver_request_features.render_driver_request_panel()
            ├─ View Tab: render_requests_by_filter()
            ├─ Stats Tab: Display statistics
            ├─ Action Buttons: render_request_action_buttons()
            │
            └─ Driver Actions
               ├─ accept_request()
               ├─ complete_request()
               ├─ snooze_request()
               └─ reject_request()
                  │
                  └─ firebase_manager.update_request_status()
                     └─ Update in Firebase
```

---

## ⚡ Quick Start Checklist

- [ ] Copy `request_manager.py` to project
- [ ] Copy `driver_request_features.py` to project
- [ ] Copy `passenger_request_submission.py` to project
- [ ] Update `passenger_page.py` with new form (Step 1)
- [ ] Update `driver_page.py` with request panel (Step 2)
- [ ] Test passenger request submission
- [ ] Test driver request viewing and actions
- [ ] Verify Firebase integration working
- [ ] Deploy and test end-to-end

---

## 🐛 Troubleshooting

### Problem: Requests not showing in driver dashboard

**Solution:** Check Firebase connection and ensure requests have status="pending"

### Problem: Location not capturing

**Solution:** Check browser geolocation permissions; fallback to manual entry

### Problem: Distance showing 0

**Solution:** Verify driver_lat/driver_lng in session state

### Problem: Request actions not working

**Solution:** Verify Firebase write permissions and request_id format

---

## 📝 Notes

- All features are built with **Streamlit** for compatibility
- **Firebase Real-Time Database** used for data persistence
- **Google Maps** used for location display
- **Browser Geolocation API** used for GPS capture
- System is **mobile-responsive** and **accessible**

---

**Created:** 2026-03-05  
**Version:** 1.0  
**Status:** Ready for Integration
