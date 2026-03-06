# 🚍 QUICK REFERENCE - Request Management API

## One-Page Cheat Sheet

### 📥 FETCHING REQUESTS

```python
from request_manager import get_request_manager
rm = get_request_manager()

# All pending requests
all_reqs = rm.fetch_all_requests()

# Specific route only
route_reqs = rm.fetch_requests_by_route("5C")

# High priority only (Elderly, Wheelchair, Visual)
urgent = rm.fetch_urgent_requests()

# Sorted by priority (Elderly first)
sorted_reqs = rm.fetch_requests_by_priority()

# Single request
one_req = rm.fetch_request_by_id("req_id_123")
```

---

### ✍️ REQUEST ACTIONS

```python
# Accept a request
rm.accept_request(request_id, driver_name="Vikram")

# Mark as completed
rm.complete_request(request_id, driver_name="Vikram", notes="Done!")

# Reject with reason
rm.reject_request(request_id, driver_name="Vikram", reason="Wrong route")

# Pause for 5 minutes
rm.snooze_request(request_id, minutes=5)
```

---

### 📊 REQUEST DATA

```python
# Get distance from driver to passenger (in km)
dist_km = rm.get_request_distance(req_id, driver_lat, driver_lng)

# Get formatted summary
summary = rm.get_request_summary(req_id)
# → {passenger_name, contact, disability_type, location, ...}

# Get all statistics
stats = rm.get_request_stats()
# → {total, pending, acknowledged, completed, by_disability: {...}}

# Get driver performance
perf = rm.get_driver_performance(driver_name="Vikram")
```

---

### 📱 UI COMPONENTS

```python
# Full request management panel (tabbed interface)
from driver_request_features import render_driver_request_panel
render_driver_request_panel()

# Render filtered requests
from driver_request_features import render_requests_by_filter
render_requests_by_filter("priority")  # or "all", "urgent", "nearby"

# Single request card
from driver_request_features import render_request_card
render_request_card(request_data, driver_lat, driver_lng)

# Action buttons only
from driver_request_features import render_request_action_buttons
render_request_action_buttons(request_id, request_data)
```

---

### 📋 PASSENGER FORM

```python
# Complete 5-step form
from passenger_request_submission import render_passenger_request_form
render_passenger_request_form(routes_df, stops_df)

# GPS location capture
from passenger_request_submission import capture_passenger_location
location = capture_passenger_location()
# → {lat: float, lng: float, accuracy: float}
```

---

### 🔄 REQUEST STATUSES

| Status           | Meaning            | User      | Driver      | Next Action |
| ---------------- | ------------------ | --------- | ----------- | ----------- |
| **pending**      | Waiting for driver | Waiting   | Assign      | Accept      |
| **acknowledged** | Driver accepted    | Notified  | In progress | Complete    |
| **completed**    | Pickup done        | Done      | Submitted   | -           |
| **declined**     | Driver rejected    | Try again | Rejected    | Resubmit    |
| **snoozed**      | Paused             | Waiting   | Later       | Resume      |

---

### 📍 DISTANCE DISPLAY

```
🟢 < 5 km    → Nearby
🟡 5-15 km   → Moderate
🔴 > 15 km   → Far
```

---

### ♿ PRIORITY ORDER

```
1. Elderly                    🔴
2. Wheelchair User            🔴
3. Visual Impairment          🔴
4. Hearing Impairment         🟡
5. Mobility Issue             🟡
6. Other                      ⚪
```

---

### 🎯 FILTER OPTIONS

| Filter       | Shows              | Order         | Use Case          |
| ------------ | ------------------ | ------------- | ----------------- |
| **all**      | All pending        | Default       | Overview          |
| **urgent**   | High priority only | Priority      | Time-critical     |
| **priority** | All sorted         | Elderly→Other | Plan efficiently  |
| **nearby**   | All sorted         | Closest first | Minimize distance |

---

### 📦 REQUEST OBJECT STRUCTURE

```python
{
    "id": "unique_id",
    "user_name": "Name",
    "email": "email@example.com",
    "phone": "+91 9876543210",
    "route": "5C",
    "location": "Adyar Bus Stand",
    "boarding_stop": "Adyar",
    "destination_stop": "Central",
    "disability_type": "Elderly",
    "passenger_lat": 13.1234,
    "passenger_lng": 80.2456,
    "passenger_gmaps_url": "https://...",
    "status": "pending",
    "timestamp": 1709619600,
    "admin_note": "Updated notes..."
}
```

---

### ⚡ COMMON PATTERNS

```python
# Pattern 1: Get urgent requests and accept them
urgent = rm.fetch_urgent_requests()
for req in urgent:
    if req['disability_type'] == 'Elderly':
        rm.accept_request(req['id'], driver_name="Raj")

# Pattern 2: Show requests sorted by distance
requests = rm.fetch_all_requests()
for req in requests:
    dist = rm.get_request_distance(req['id'], driver_lat, driver_lng)
    req['distance'] = dist
requests.sort(key=lambda x: x.get('distance') or float('inf'))

# Pattern 3: Get statistics
stats = rm.get_request_stats()
print(f"Pending: {stats['pending']}")
print(f"Completion rate: {stats['completed']}/{stats['total']}")

# Pattern 4: Complete request with notes
rm.complete_request(
    req_id,
    driver_name="Vikram",
    notes="Passenger safely dropped, very polite"
)
```

---

### 🐛 ERROR HANDLING

```python
# Check if request exists
req = rm.fetch_request_by_id("req_id")
if req is None:
    print("Request not found")

# Check if action succeeded
success = rm.accept_request(req_id, "Raj")
if not success:
    print("Failed to accept request")

# Handle missing distance
dist = rm.get_request_distance(req_id, lat, lng)
if dist is None:
    print("Distance unavailable")
```

---

### 🎨 STATUS COLORS

```
🔴 PENDING      - Red (urgent)
🟠 ACKNOWLEDGED - Orange (in progress)
🟢 COMPLETED    - Green (done)
⚪ DECLINED     - Gray (rejected)
🔵 SNOOZED      - Blue (paused)
```

---

### 📁 FILES CREATED

```
request_manager.py                    ← Core API
driver_request_features.py           ← Driver UI
passenger_request_submission.py      ← Passenger form
EXPLICIT_REQUEST_FEATURES_GUIDE.md   ← Full docs
INTEGRATION_STEPS.md                 ← Code snippets
FEATURES_ARCHITECTURE.md             ← System design
QUICK_DEMO.md                        ← Examples
QUICK_REFERENCE.md                   ← This file
```

---

### 🚀 INTEGRATION (3 STEPS)

1. **Add imports** to `passenger_page.py` and `driver_page.py`
2. **Add UI components** to render forms and panels
3. **Test end-to-end** (form → database → dashboard)

See `INTEGRATION_STEPS.md` for exact code.

---

### 📞 API SUMMARY

| Operation      | Function                             | Returns       |
| -------------- | ------------------------------------ | ------------- |
| Fetch all      | `fetch_all_requests()`               | List          |
| Fetch route    | `fetch_requests_by_route(route)`     | List          |
| Fetch urgent   | `fetch_urgent_requests()`            | List          |
| Fetch priority | `fetch_requests_by_priority()`       | List (sorted) |
| Fetch one      | `fetch_request_by_id(id)`            | Dict \| None  |
| Accept         | `accept_request(id, driver)`         | Bool          |
| Complete       | `complete_request(id, driver)`       | Bool          |
| Reject         | `reject_request(id, driver, reason)` | Bool          |
| Snooze         | `snooze_request(id, mins)`           | Bool          |
| Distance       | `get_request_distance(id, lat, lng)` | Float \| None |
| Summary        | `get_request_summary(id)`            | Dict \| None  |
| Stats          | `get_request_stats()`                | Dict          |

---

### 🎓 USAGE FLOW

```
Passenger
   ↓
render_passenger_request_form()
   ↓
Form submission
   ↓
firebase_manager.send_pickup_request()
   ↓
Firebase Database
   ↓
Driver Dashboard
   ↓
render_driver_request_panel()
   ↓
request_manager.fetch_all_requests()
   ↓
Display request cards
   ↓
Driver clicks action button
   ↓
request_manager.accept/complete/reject()
   ↓
firebase_manager.update_request_status()
   ↓
Status updated in database
   ↓
Request moves to acknowledged/completed
```

---

### ✅ READY TO USE! 🎉

All features documented. Refer to:

- **API Details** → EXPLICIT_REQUEST_FEATURES_GUIDE.md
- **Code Examples** → INTEGRATION_STEPS.md
- **Full Scenarios** → QUICK_DEMO.md
- **Architecture** → FEATURES_ARCHITECTURE.md

**Version:** 1.0  
**Status:** ✅ Production Ready
