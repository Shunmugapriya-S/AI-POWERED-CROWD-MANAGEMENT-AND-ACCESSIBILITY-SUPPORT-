# QUICK DEMO - How to Use the Explicit Request Management System

# This file shows real usage examples

# ================================================================

# EXAMPLE 1: Passenger Submits a Request

# ================================================================

"""
SCENARIO: Rajini, an elderly passenger, needs to go from Adyar to Central Station

PASSENGER'S ACTIONS:
────────────────────

1. Opens Passenger Portal (Streamlit app)
2. Selects route "5C" from dropdown
3. Clicks "📋 Book Accessibility Pickup Request"
4. Form appears with 5 steps

STEP 1: Personal Information
Name: Rajini K
Email: rajini.k@example.com
Phone: +91 9876543210
→ Clicks "Next Step →"

STEP 2: Route & Stops
Route: 5C
Boarding: Adyar Bus Stand
Destination: Central Station
→ Clicks "Next Step →"

STEP 3: Accessibility Details
Type: "Elderly"
Notes: "I need help boarding the bus due to knee pain"
→ Clicks "Next Step →"

STEP 4: Location
Browser automatically captures GPS:
Latitude: 13.0285
Longitude: 80.2603
Accuracy: 25 meters
→ Clicks "Next Step →"

STEP 5: Review & Submit
Reviews all entered information
→ Clicks "✅ Submit Request"

RESULT: "✅ Request submitted successfully! ID: -Nk2e3f4g5h6i7"

BEHIND THE SCENES:
─────────────────

1. request_manager.py receives submit
2. firebase_manager.send_pickup_request() called
3. Request stored in Firebase:
   /pickup_requests/-Nk2e3f4g5h6i7 = {
   user_name: "Rajini K",
   email: "rajini.k@example.com",
   phone: "+91 9876543210",
   route: "5C",
   boarding_stop: "Adyar Bus Stand",
   destination_stop: "Central Station",
   disability_type: "Elderly",
   passenger_lat: 13.0285,
   passenger_lng: 80.2603,
   status: "pending",
   timestamp: 1709619600
   }
4. FCM notification sent to all drivers on route "5C":
   "🚌 New Pickup Request - Pickup at Adyar Bus Stand for route 5C"
5. Driver sees request in dashboard instantly
   """

# ================================================================

# EXAMPLE 2: Driver Receives and Views Request

# ================================================================

"""
SCENARIO: Vikram is driving bus 5C and receives a new request

DRIVER'S ACTIONS:
─────────────────

1. Driver Dashboard opens automatically
2. Sees notification: "🚨 LIVE ACCESSIBILITY ALERTS - 1 pending request"
3. Scrolls down to "Request Management Panel"
4. Clicks on "View Requests" tab

THE DRIVER SEES:
────────────────
📋 All Requests (selected)

Request Cards Display:
┌─────────────────────────────────────────────┐
│ 🔴 Rajini K PENDING │
│ Request ID: -Nk2e3f4g5h6i7 │
├─────────────────────────────────────────────┤
│ 🧍 Passenger Name: Rajini K │
│ ♿ Accessibility: Elderly │
│ 📞 Contact: +91 9876543210 / rajini@... │
│ 🛫 Boarding: Adyar Bus Stand │
│ 🏁 Destination: Central Station │
│ 📍 Distance: 2.3 km away │
│ │
│ 🗺️ Passenger Location Map (embedded) │
│ │
│ ⚡ Actions: │
│ [✅ ACCEPT] [🏁 COMPLETE] [⏱️ SNOOZE] [❌ REJECT]
└─────────────────────────────────────────────┘

DRIVER CLICKS: ✅ ACCEPT

WHAT HAPPENS:
──────────────

1. render_request_action_buttons() triggers
2. request_manager.accept_request() called with:
   - request_id = "-Nk2e3f4g5h6i7"
   - driver_name = "Vikram" (from session state)
3. firebase_manager.update_request_status() executes:
   - Updates status to "acknowledged"
   - Adds note: "Accepted by Vikram at 10:23:45"
   - Timestamp updated
4. Firebase updates: status: "acknowledged"
5. UI shows: ✅ Request -Nk2e3f4g5h6i7 accepted!
6. Request moves to "Acknowledged Requests" section
7. Passenger gets real-time notification:
   "Driver Vikram has accepted your request! Expected pickup in 5 minutes"
   """

# ================================================================

# EXAMPLE 3: Driver Takes Action After Pickup

# ================================================================

"""
SCENARIO: Vikram reaches Adyar Bus Stand and picks up Rajini

DRIVER'S ACTIONS:
─────────────────
After picking up Rajini and completing the route:

1. Request still visible in "Acknowledged" section
2. Driver clicks [🏁 COMPLETE] button

WHAT HAPPENS:
──────────────

1. render_request_action_buttons() triggers
2. request_manager.complete_request() called:
   - request_id = "-Nk2e3f4g5h6i7"
   - driver_name = "Vikram"
   - notes = "" (optional)
3. firebase_manager.update_request_status():
   - Updates status to "completed"
   - Note: "Completed by Vikram at 10:45:30"
4. Firebase updates request
5. UI shows: 🏁 Request completed!
6. Request removed from active lists
7. Passenger notified: "Your ride is complete. Thank you!"
8. Request now in "History" and counted in statistics
   """

# ================================================================

# EXAMPLE 4: Driver Using Smart Filters

# ================================================================

"""
SCENARIO: Vikram wants to see only the most urgent requests

DRIVER'S ACTIONS:
─────────────────
In Request Management Panel:

1. Click "View Requests" tab
2. Filter buttons visible:
   [📋 All Requests] [🚨 Urgent Only] [🏆 By Priority] [📍 By Distance]
3. Click "🚨 Urgent Only"

WHAT HAPPENS:
──────────────

1. render_requests_by_filter("urgent") called
2. request_manager.fetch_urgent_requests() executes
3. Returns only requests with:
   - disability_type in ["Elderly", "Wheelchair User", "Visual Impairment"]
4. Filters out:
   - Hearing Impairment
   - Mobility Issue
   - Other
5. Driver sees only 3 urgent requests (if any)

FILTER OPTIONS EXPLAINED:
────────────────────────
📋 All Requests
→ Shows ALL pending requests
→ No filtering applied
→ Useful for overview

🚨 Urgent Only
→ Shows only HIGH priority
→ Elderly, Wheelchair Users, Visually Impaired
→ Useful when time-sensitive

🏆 By Priority
→ Sorted by accessibility need
→ Elderly → Wheelchair → Visual → Hearing → Mobility → Other
→ Useful for plan route efficiently

📍 By Distance
→ Sorted nearest to farthest from driver
→ Uses current location and passenger GPS
→ Useful to pick up nearby passengers first
"""

# ================================================================

# EXAMPLE 5: Admin Views Statistics

# ================================================================

"""
SCENARIO: Admin wants to see request metrics for the day

ADMIN'S ACTIONS:
─────────────────

1. Opens Driver Dashboard (or go to admin panel)
2. Clicks "Request Management Panel"
3. Click "Statistics" tab

ADMIN SEES:
────────────
📊 Request Statistics

┌────────┬────────────┬────────┬──────────┐
│ Total │ Pending │ Ack │ Complete │
│ 25 │ 3 │ 4 │ 18 │
└────────┴────────────┴────────┴──────────┘

By Accessibility Need:
├─ Elderly: 8
├─ Wheelchair User: 7
├─ Visual Impairment: 5
├─ Hearing Impairment: 3
└─ Other: 2

INSIGHTS:
─────────
• 25 total requests today (high volume)
• 18 completed (72% completion rate)
• 3 still pending (need attention)
• Elderly has highest requests (32%)
• System is handling load well
"""

# ================================================================

# EXAMPLE 6: Code Usage - Direct API Calls

# ================================================================

"""
For developers who want to use the API directly:

PYTHON CODE EXAMPLES:
═════════════════════

# Get the request manager

from request_manager import get_request_manager
rm = get_request_manager()

# EXAMPLE 1: Get all urgent requests

urgent_reqs = rm.fetch_urgent_requests()
for req in urgent_reqs:
print(f"🚨 {req['user_name']} at {req['location']}")

# EXAMPLE 2: Accept a request

if rm.accept_request("request_id_123", driver_name="Vikram"):
print("✅ Request accepted")
else:
print("❌ Failed to accept")

# EXAMPLE 3: Calculate distance

dist = rm.get_request_distance("req_123", driver_lat=13.0285, driver_lng=80.2603)
print(f"📍 Passenger is {dist:.1f} km away")

# EXAMPLE 4: Get formatted summary

summary = rm.get_request_summary("req_123")
print(f"Passenger: {summary['passenger_name']}")
print(f"Contact: {summary['contact']}")
print(f"Disability: {summary['disability_type']}")

# EXAMPLE 5: Get statistics for dashboard

stats = rm.get_request_stats()
print(f"Total: {stats['total']}")
print(f"Pending: {stats['pending']}")
print(f"Completed: {stats['completed']}")

# EXAMPLE 6: Snooze a request for 10 minutes

if rm.snooze_request("req_123", minutes=10):
print("⏱️ Request snoozed")

# EXAMPLE 7: Reject with reason

if rm.reject_request("req_123", driver_name="Vikram", reason="Wrong route"):
print("❌ Request declined")
"""

# ================================================================

# EXAMPLE 7: Complete Request Lifecycle

# ================================================================

"""
FULL JOURNEY: From Submit to Complete

T=00:00 - 10:15 AM
├─ Rajini opens app
├─ Fills 5-step form
├─ Submits request
│ Status: PENDING
│
└─ Firebase: /pickup_requests/-Nk2e3f4g5h6i7
{status: "pending", ...}

T=00:30 - 10:15:30 AM
├─ Vikram sees request notification
├─ Opens Request Management Panel
├─ Views request card
├─ Sees distance: 2.3 km
│
└─ Clicks ✅ ACCEPT
Firebase updates: status: "acknowledged"
Rajini gets notification: "Driver accepted!"

T=20:00 - 10:35 AM
├─ Vikram reaches Adyar Bus Stand
├─ Finds Rajini waiting
├─ Helps her board bus
├─ Bus heads to Central Station
│
└─ Confirms boarding in app

T=30:00 - 10:45 AM
├─ Bus reaches Central Station
├─ Rajini gets off
├─ Driver marks complete
│
└─ Clicks 🏁 COMPLETE
Firebase updates: status: "completed"
Rajini gets: "Ride completed! Thank you!"

STATISTICS UPDATED:
──────────────────
Total: 25 → 26
Pending: 3 → 2
Acknowledged: 4 → 3
Completed: 18 → 19
Elderly: 8 → 8 (request counted)

ADMIN SEES:
───────────
📊 Stats updated in real-time
92% of elderly requests are being served well
Average response time: ~5 minutes
"""

# ================================================================

# EXAMPLE 8: Error Handling

# ================================================================

"""
WHAT IF THINGS GO WRONG?

Scenario 1: Driver Location Not Available
─────────────────────────────────────────
Driver hasn't shared location yet:
distance = rm.get_request_distance("req_123", None, None)
→ Returns None
UI shows: "📍 Distance unavailable (driver location pending)"

Scenario 2: Request Not Found
──────────────────────────────
Trying to access deleted/invalid request:
req = rm.fetch_request_by_id("invalid_id")
→ Returns None
UI shows: "⚠️ Request not found"

Scenario 3: Firebase Not Connected
───────────────────────────────────
No internet or Firebase credentials missing:
fb = get_firebase_manager()
if not fb.initialized:
st.warning("⚠️ Firebase not connected - showing demo data")
UI shows: Demo data instead of real requests

Scenario 4: Location Capture Failed
────────────────────────────────────
Browser blocks geolocation:
location = capture_passenger_location()
→ Returns None
Fallback: User can enter coordinates manually
UI shows: Manual entry form

HANDLING IN CODE:
─────────────────
try:
reqs = rm.fetch_all_requests()
if not reqs:
st.info("✅ No pending requests")
else:
for req in reqs:
render_request_card(req)
except Exception as e:
st.error(f"❌ Error loading requests: {e}")
"""

# ================================================================

# TESTING CHECKLIST

# ================================================================

"""
✅ MULTI-STEP FORM (Passenger)
□ Can enter all fields
□ Navigation buttons work (next, previous)
□ Form resets after submit
□ Success message appears
□ Request ID displayed

✅ REQUEST VIEWING (Driver)
□ Requests appear immediately after submit
□ Request shows correct details
□ Distance calculates correctly
□ Location map displays
□ All buttons visible

✅ FILTER FUNCTIONALITY
□ "All Requests" shows everything
□ "Urgent Only" filters correctly
□ "By Priority" sorts by disability
□ "By Distance" sorts by km
□ Stats update with filter

✅ ACTION BUTTONS
□ ACCEPT changes status to "acknowledged"
□ COMPLETE changes status to "completed"
□ SNOOZE pauses request
□ REJECT marks as "declined"
□ Firebase updates immediately

✅ STATISTICS
□ Total count accurate
□ Pending/Ack/Complete counts correct
□ Breakdown by disability shows
□ Updates in real-time

✅ EDGE CASES
□ Works with no Firebase
□ Works without location
□ Works with invalid request ID
□ Handles duplicate submits
□ Handles network errors
"""

print("""
✅ EXPLICIT REQUEST MANAGEMENT SYSTEM
🎯 All features documented and ready to use!

Next steps:

1. Read EXPLICIT_REQUEST_FEATURES_GUIDE.md for API details
2. Follow INTEGRATION_STEPS.md for code changes
3. Run tests from this file
4. Deploy and enjoy! 🚀
   """)
