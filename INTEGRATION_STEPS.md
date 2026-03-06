# INTEGRATION INSTRUCTIONS

# This file shows EXACTLY how to update your existing files

# ================================================================

# FILE 1: passenger_page.py

# ADD THIS SECTION after the route/stop selection section (around line 300)

# ================================================================

# Add this import at the top of passenger_page.py:

"""
from passenger_request_submission import render_passenger_request_form
"""

# Then in the render_passenger() function, add this section after the crowd detection:

""" # ================================================================ # SECTION 3 — ACCESSIBILITY PICKUP REQUEST # ================================================================
st.markdown("<div class='pass-card'>", unsafe_allow_html=True)
st.markdown("### 📋 Book Accessibility Pickup Request")
st.caption("Need special assistance? Submit a detailed accessibility request that drivers can see and respond to.")

    render_passenger_request_form(routes, stops)

    st.markdown("</div>", unsafe_allow_html=True)

"""

# ================================================================

# FILE 2: driver_page.py

# ADD THIS SECTION in \_render_driver_dashboard() function

# ================================================================

# Add this import at the top of driver_page.py:

"""
from driver_request_features import render_driver_request_panel
"""

# Then in \_render_driver_dashboard() function, add BEFORE the "Switch Portal" section:

""" # ================================================================ # REQUEST MANAGEMENT PANEL WITH EXPLICIT FEATURES # ================================================================
st.markdown(\"\"\"
<div style='background:rgba(15,23,42,.88); border:1px solid rgba(34,211,238,.25);
                border-radius:18px; padding:20px; margin:20px 0;'>
\"\"\", unsafe_allow_html=True)

    render_driver_request_panel()

    st.markdown(\"</div>\", unsafe_allow_html=True)

"""

# ================================================================

# FILE 3: app.py

# ADD THIS SESSION STATE INITIALIZATION to the login section

# ================================================================

# In render_login() or \_init_session_state() function, add:

""" # Driver location tracking for request distance calculation
if "driver_lat" not in st.session_state:
st.session_state.driver_lat = 13.1180 # Madhavaram depot default
if "driver_lng" not in st.session_state:
st.session_state.driver_lng = 80.2350
if "driver_name" not in st.session_state:
st.session_state.driver_name = "Driver"
if "request_filter" not in st.session_state:
st.session_state.request_filter = "all"
"""

# ================================================================

# QUICK TEST - Run these in your terminal to verify

# ================================================================

"""

# Test imports

python -c "from request_manager import get_request_manager; rm = get_request_manager(); print('✅ request_manager imported successfully')"

python -c "from driver_request_features import render_driver_request_panel; print('✅ driver_request_features imported successfully')"

python -c "from passenger_request_submission import render_passenger_request_form; print('✅ passenger_request_submission imported successfully')"

# Or run Streamlit

streamlit run app.py
"""

# ================================================================

# EXPECTED BEHAVIOR AFTER INTEGRATION

# ================================================================

"""
PASSENGER PORTAL:
├─ Route search (existing)
├─ Crowd detection (existing)
└─ [NEW] Accessibility Pickup Request Form
├─ 5-step multi-step form
├─ Personal info collection
├─ Route/stop selection
├─ Accessibility need specification
├─ GPS/manual location capture
└─ Review & submit

DRIVER DASHBOARD:
├─ Location tracking (existing)
├─ Request list (existing - may be removed)
└─ [NEW] Request Management Panel
├─ View Tab
│ ├─ Filter buttons (All, Urgent, Priority, Distance)
│ └─ Request cards with details & actions
├─ Stats Tab
│ └─ Request metrics & breakdown
└─ History Tab
└─ Activity log (placeholder)
"""

# ================================================================

# FUNCTIONS AVAILABLE FOR USE

# ================================================================

"""
From request_manager.py:
═══════════════════════

Fetching:
rm.fetch_all_requests() → List[Request]
rm.fetch_requests_by_route(route_id) → List[Request]
rm.fetch_requests_by_priority() → List[Request]
rm.fetch_urgent_requests() → List[Request]
rm.fetch_request_by_id(request_id) → Request | None

Actions:
rm.accept_request(request_id, driver) → bool
rm.complete_request(request_id, driver) → bool
rm.reject_request(request_id, driver, reason) → bool
rm.snooze_request(request_id, minutes) → bool

Data:
rm.get_request_distance(id, lat, lng) → float | None
rm.get_request_summary(request_id) → dict
rm.get_request_stats() → dict
rm.get_driver_performance(driver_name) → dict

From driver_request_features.py:
═════════════════════════════════

render_driver_request_panel() → None (renders UI)
render_requests_by_filter(type, lat, lng) → None (renders UI)
render_request_card(request, lat, lng) → None (renders UI)
render_request_action_buttons(id, req) → None (renders UI)

From passenger_request_submission.py:
═════════════════════════════════════

render_passenger_request_form(routes, stops) → None (renders UI)
capture_passenger_location() → dict | None
"""

# ================================================================

# TESTING GUIDE

# ================================================================

"""
TEST CASE 1: Passenger Submits Request
─────────────────────────────────────────

1. Go to Passenger Portal
2. Select route and stops
3. Click "Book Accessibility Pickup Request"
4. Fill 5-step form:
   - Enter name, email, phone
   - Select route and stops again
   - Choose accessibility type
   - Capture location (GPS or manual)
   - Review and submit
5. Expected: ✅ Request submitted message with ID
6. Verify in Firebase: Check pickup_requests node

TEST CASE 2: Driver Views Requests
───────────────────────────────────

1. Go to Driver Dashboard
2. Scroll to "Request Management Panel"
3. Click "View Requests" tab
4. Should see statistics and request cards
5. Try different filters: All → Urgent → Priority → Distance
6. Expected: Requests sorted accordingly

TEST CASE 3: Driver Takes Action
──────────────────────────────────

1. In Request Management Panel
2. Click ✅ ACCEPT on any request
3. Expected: Request status changes to "acknowledged"
4. Verify in Firebase: Request status updated
5. Try other actions: COMPLETE, SNOOZE, REJECT

TEST CASE 4: Statistics Display
─────────────────────────────────

1. Submit multiple requests from passenger
2. Accept some as driver
3. Go to Driver Dashboard → Request Management → Stats tab
4. Should see:
   - Total count
   - Pending/Acknowledged/Completed counts
   - Breakdown by disability type
     """

# ================================================================

# COMMON ISSUES & FIXES

# ================================================================

"""
ISSUE: ImportError: cannot import name 'render_passenger_request_form'
FIX: Ensure passenger_request_submission.py is in same directory as app.py

ISSUE: Requests not showing in driver panel
FIX: Check firebase_manager.py is initialized correctly
Verify Firebase credentials in firebase_key.json
Check that requests are stored with status="pending"

ISSUE: Location not capturing
FIX: Check browser geolocation permissions
Try manual entry instead
Verify browser supports Geolocation API

ISSUE: Distance showing as None
FIX: Check driver_lat/driver_lng in session state
Ensure passenger request has valid lat/lng coordinates

ISSUE: Action buttons not working
FIX: Check Firebase write permissions
Verify request_id format is correct
Check Firebase connection status
"""

# ================================================================

# CONFIGURATION & CUSTOMIZATION

# ================================================================

"""
Priority Order (edit in request_manager.py):
priority_order = {
"Elderly": 1,
"Wheelchair User": 2,
"Visual Impairment": 3,
"Hearing Impairment": 4,
"Mobility Issue": 5,
"Other": 6
}

Snooze Duration (edit in driver_request_features.py):
Default is 5 minutes. Change:
rm.snooze_request(request_id, minutes=10)

Disability Types (edit in passenger_request_submission.py):
disability_options = [
"Elderly",
"Wheelchair User",
"Visual Impairment",
"Hearing Impairment",
"Mobility Issue",
"Other"
]
"""

# ================================================================

# SUCCESS INDICATORS

# ================================================================

"""
✅ System is working if you see:

1. Passenger form submits without errors
2. Request appears in Firebase immediately
3. Driver dashboard shows incoming requests
4. Distance calculated correctly
5. Action buttons update request status
6. Statistics update in real-time
7. Filters work (All/Urgent/Priority/Distance)
8. No console errors in browser
   """
