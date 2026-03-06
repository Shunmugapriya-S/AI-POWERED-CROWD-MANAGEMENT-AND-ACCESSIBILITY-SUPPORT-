# -*- coding: utf-8 -*-
# ============================================================
#   DRIVER PORTAL MODULE
#   Features:
#     - Live GPS location of the driver (browser geolocation)
#     - Map display with current position
#     - View & manage pending pickup requests from Firebase
#     - Acknowledge / Complete requests
# ============================================================

import streamlit as st
import streamlit.components.v1 as components
from firebase_manager import get_firebase_manager
from accessibility_alerts import AccessibilityAlerts
from driver_voice_assistant import render_voice_assistant_portal


# ================================================================
# UTILITY FUNCTIONS
# ================================================================

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates in km (Haversine formula)."""
    from math import radians, cos, sin, asin, sqrt
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371
    return c * r


def speak_alert(text):
    """Inject TTS for accessibility alerts in driver's browser."""
    safe = text.replace("'", "\\'").replace("\n", " ")
    components.html(f"""
    <script>
    (function() {{
        window.speechSynthesis.cancel();
        var u = new SpeechSynthesisUtterance('{safe}');
        u.lang  = 'en-IN';
        u.rate  = 0.95;
        u.pitch = 1.0;
        u.volume = 1.0;
        window.speechSynthesis.speak(u);
    }})();
    </script>
    """, height=0)


# ================================================================
# LIVE GPS LOCATION WITH GOOGLE MAPS
# ================================================================

def render_driver_location():
    """Show driver's real-time GPS location using browser Geolocation API + Google Maps."""

    st.markdown("### 📍 Your Current Location")

    location_html = """
    <style>
      #gmapDriver { 
        width:100%; height:420px; border-radius:16px;
        border:2px solid rgba(34,211,238,.35);
        box-shadow:0 8px 24px rgba(0,0,0,.4);
      }
      .loc-box {
        background:rgba(15,23,42,.9); border:1px solid rgba(34,211,238,.3);
        border-radius:12px; padding:14px 18px; margin:10px 0;
        font-family:'Outfit',sans-serif;
      }
      .loc-val { color:#22d3ee; font-size:1.05rem; font-weight:700; }
      .loc-lbl { color:#94a3b8; font-size:.82rem; }
      .loc-status { color:#22c55e; font-size:.9rem; margin-top:6px; font-weight:700; }
      .depot-info { color:#f59e0b; font-size:.85rem; font-weight:600; margin-top:8px; }
    </style>

    <div class="loc-box">
      <div class="loc-lbl">📡 GPS Coordinates</div>
      <div class="loc-val" id="driverCoordDisplay">Fetching location...</div>
      <div class="loc-lbl" style="margin-top:8px;">📍 Current Area</div>
      <div class="loc-val" id="driverAreaDisplay">-</div>
      <div class="loc-status" id="driverStatusMsg">🔄 Requesting GPS permission...</div>
      <div class="depot-info">� Your Service Area (as per GPS location)</div>
    </div>

    <!-- Map will be updated dynamically with driver's GPS location -->
    <div id="driverMapContainer\" style="width: 100%; height: 400px; border-radius: 12px; background: #0f172a; display: flex; align-items: center; justify-content: center; color: #94a3b8; font-weight: 600;\">
        📍 Waiting for your GPS location...
    </div>

    <script>
    function calculateDistance(lat1, lon1, lat2, lon2) {
      const R = 6371;
      const dLat = (lat2 - lat1) * Math.PI / 180;
      const dLon = (lon2 - lon1) * Math.PI / 180;
      const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
                Math.sin(dLon/2) * Math.sin(dLon/2);
      const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
      return (R * c).toFixed(2);
    }

    // Driver's current location (fetched via geolocation - no default coordinates)
    let driverLat = null;
    let driverLng = null;

    function updateDriverLocation(pos) {
      const lat = pos.coords.latitude;
      const lng = pos.coords.longitude;
      const acc = Math.round(pos.coords.accuracy);

      document.getElementById('driverCoordDisplay').innerText =
        lat.toFixed(6) + ', ' + lng.toFixed(6);
      
      const distance = calculateDistance(lat, lng, depotLat, depotLon);
      document.getElementById('driverStatusMsg').innerText =
        '✅ GPS Active - Distance from depot: ' + distance + ' km';
      document.getElementById('driverStatusMsg').style.color = '#22c55e';

      const mapSrc = 'https://www.google.com/maps/embed?pb=!1m14!1m12!1m3!1d' +
        (Math.round(5000/Math.pow(2, 15)) * 100) + '!2d' + lng + '!3d' + lat +
        '!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!5e0!3m2!1sen!2sin!4v=' + Date.now();
      document.getElementById('gmapDriver').src = mapSrc;

      fetch('https://nominatim.openstreetmap.org/reverse?lat=' + lat +
            '&lon=' + lng + '&format=json')
        .then(r => r.json())
        .then(d => {
          const area = d.address?.suburb || d.address?.neighbourhood || d.address?.village ||
                      d.address?.town || d.address?.city || 'Chennai';
          document.getElementById('driverAreaDisplay').innerText = area + ', Chennai';
        }).catch(() => {
          document.getElementById('driverAreaDisplay').innerText = 'Madhavaram Area, Chennai';
        });

      window.parent.postMessage({
        type:'streamlit:setComponentValue',
        value: {lat: lat, lng: lng, acc: acc, distance: distance, depot_distance: distance}
      }, '*');
    }

    function locationError(err) {
      const msg = {1:'Permission denied',2:'Position unavailable',3:'Timeout'}[err.code] || 'Unknown';
      document.getElementById('driverStatusMsg').innerText = '❌ GPS Error: ' + msg;
      document.getElementById('driverStatusMsg').style.color = '#ef4444';
    }

    if ('geolocation' in navigator) {
      navigator.geolocation.watchPosition(updateDriverLocation, locationError, {
        enableHighAccuracy: true,
        maximumAge: 3000,
        timeout: 10000
      });
    } else {
      document.getElementById('driverStatusMsg').innerText = '❌ Geolocation not supported.';
    }
    </script>
    """

    components.html(location_html, height=520)


def render_google_live_location():
    """Show live location on Google Maps using browser Geolocation API - DEPRECATED."""
    st.info("ℹ️ Location tracking is now integrated in the driver map above.")


def render_passenger_location_map(lat, lng, passenger_name="", distance_km=None):
    """Show passenger's location on Google Maps with distance information."""
    
    distance_text = f"📍 {distance_km} km away" if distance_km else "📍 Passenger Location"
    
    map_html = f"""
    <div style='margin:12px 0;'>
        <div style='color:#22d3ee; font-weight:700; margin-bottom:8px;'>
            🗺️ {distance_text}
            {f"- {passenger_name}" if passenger_name else ""}
        </div>
        <iframe width="100%" height="300" style="border-radius: 12px; border: 2px solid rgba(34,211,238,.35);"
                src="https://maps.google.com/maps?q={lat},{lng}&z=17&output=embed"></iframe>
    </div>
    """
    st.markdown(map_html, unsafe_allow_html=True)


# ================================================================
# MAIN DRIVER RENDER
# ================================================================

def render_driver():
    """Render Driver Dashboard page."""

    st.markdown("""
    <div style='text-align:center; margin-bottom:12px;'>
        <h2 style='color:#22d3ee;'>🚍 Driver Dashboard</h2>
        <p style='color:#94a3b8;'>Live location tracking & pickup request management</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ================================================================
    # DRIVER PORTAL TABS
    # ================================================================
    tab1, tab2 = st.tabs(["📋 Dashboard", "🎤 Voice Assistant - Disability Pickups"])
    
    with tab1:
        _render_driver_dashboard()
    
    with tab2:
        render_voice_assistant_portal()


def _render_driver_dashboard():
    """Render the main driver dashboard."""
    
    # AUTO-REFRESH DISPLAY FOR REAL-TIME UPDATES
    refresh_placeholder = st.empty()

    st.markdown("""
    <div style='background:rgba(15,23,42,.88); border:1px solid rgba(34,211,238,.25);
                border-radius:18px; padding:20px; margin-bottom:20px;'>
    """, unsafe_allow_html=True)
    render_driver_location()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div style='background:rgba(15,23,42,.88); border:1px solid rgba(34,211,238,.25);
                border-radius:18px; padding:20px; margin-bottom:20px;'>
    """, unsafe_allow_html=True)

    st.markdown("### 📋 Pickup Requests - Real-Time Dashboard")

    fb = get_firebase_manager()

    if not fb.initialized:
        st.warning("⚠️ Firebase not connected - showing demo data.")
        _render_demo_requests()
    else:
        active_requests = fb.get_active_requests()
        
        # PROMINENT REQUEST STATUS BANNER WITH ALERT ANIMATION
        if active_requests:
            pending_count = sum(1 for r in active_requests if r.get("status") == "pending")
            ack_count = sum(1 for r in active_requests if r.get("status") == "acknowledged")
            
            # Alert banner for accessibility requests with animation
            st.markdown(f"""
            <style>
            @keyframes pulse-alert {{
              0%, 100% {{ box-shadow: 0 0 0 4px rgba(239,68,68,.4); }}
              50% {{ box-shadow: 0 0 0 12px rgba(239,68,68,.1); }}
            }}
            .request-alert {{
              animation: pulse-alert 2s infinite;
            }}
            </style>
            <div class='request-alert' style='background:linear-gradient(135deg,rgba(239,68,68,.2),rgba(220,38,38,.2)); 
                        border:2px solid #f87171; border-radius:14px; padding:16px; margin:12px 0;
                        box-shadow: 0 0 20px rgba(239,68,68,.3);'>
                <div style='color:#fca5a5; font-size:1.3rem; font-weight:800; margin-bottom:8px;'>
                    🔴 LIVE ACCESSIBILITY ALERTS
                </div>
                <div style='color:#f1f5f9; font-size:0.95rem;'>
                    <strong>{pending_count}</strong> pending request(s) waiting for driver attention<br/>
                    <strong>{ack_count}</strong> request(s) acknowledged and in progress
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Request Summary Dashboard
            stats_col1, stats_col2, stats_col3 = st.columns(3)
            with stats_col1:
                st.metric("📍 Total Requests", len(active_requests))
            with stats_col2:
                st.metric("⏳ Pending", pending_count)
            with stats_col3:
                st.metric("👁️ Acknowledged", ack_count)
        
        if active_requests:
            # GPS Request Heatmap View
            st.markdown("#### 🗺️ GPS Requests Map View")
            
            gps_requests = [r for r in active_requests if r.get("passenger_lat") and r.get("passenger_lng")]
            
            if gps_requests:
                # Create a simple map HTML showing all request locations
                map_centers = []
                for req in gps_requests:
                    try:
                        lat = float(req.get("passenger_lat"))
                        lng = float(req.get("passenger_lng"))
                        map_centers.append({"lat": lat, "lng": lng, "name": req.get("user_name", "Unknown")})
                    except:
                        pass
                
                if map_centers:
                    center_lat = sum(m["lat"] for m in map_centers) / len(map_centers)
                    center_lng = sum(m["lng"] for m in map_centers) / len(map_centers)
                    
                    map_html = f"""
                    <iframe width="100%" height="350" style="border-radius: 12px; border: 2px solid rgba(34,211,238,.35);"
                        src="https://maps.google.com/maps?q={center_lat},{center_lng}&z=14&output=embed"></iframe>
                    """
                    components.html(map_html, height=370)
            
            st.markdown("---")
            
            # HIGHLIGHT PENDING REQUESTS FIRST
            st.markdown("#### 🔴 PENDING ACCESSIBILITY REQUESTS - ACTION REQUIRED")
            
            # Add refresh button for live location fetching
            refresh_col1, refresh_col2, refresh_col3 = st.columns([2, 1, 1])
            with refresh_col2:
                if st.button("🔄 Refresh Requests", use_container_width=True, key="refresh_requests_btn", help="Fetch latest requests from Firebase"):
                    st.rerun()
            with refresh_col3:
                if st.button("📍 Get Live Locations", use_container_width=True, key="fetch_locations_btn", help="Fetch latest passenger GPS locations"):
                    st.session_state.force_location_refresh = True
                    st.rerun()
            
            pending_requests = [r for r in active_requests if r.get("status") == "pending"]
            
            if not pending_requests:
                st.success("✅ All requests acknowledged - Great job!")
            else:
                st.markdown("##### ⚠️ The requests below need your immediate attention:")
            
            for i, req in enumerate(pending_requests):
                req_id = req.get("id", "")
                user_name = req.get("user_name", "User")
                location = req.get("location", "Unknown")
                route = req.get("route", "N/A")
                disability = req.get("disability_type", "N/A")
                email = req.get("email", "")
                phone = req.get("phone", "")
                status = req.get("status", "pending")
                boarding = req.get("boarding_stop", location)
                destination = req.get("destination_stop", "")
                passenger_lat = req.get("passenger_lat")
                passenger_lng = req.get("passenger_lng")
                gmaps_url = req.get("passenger_gmaps_url", "")
                timestamp = req.get("timestamp", "")

                try:
                    passenger_lat = float(passenger_lat) if passenger_lat is not None else None
                    passenger_lng = float(passenger_lng) if passenger_lng is not None else None
                except Exception:
                    passenger_lat, passenger_lng = None, None

                # CALCULATE DISTANCE using driver's current location
                distance_km = None
                if passenger_lat and passenger_lng:
                    driver_lat = st.session_state.get("driver_lat")
                    driver_lng = st.session_state.get("driver_lng")
                    if driver_lat and driver_lng:
                        distance_km = calculate_distance(driver_lat, driver_lng, passenger_lat, passenger_lng)
                    # else: driver hasn't provided location yet, show pending

                if not gmaps_url and passenger_lat is not None and passenger_lng is not None:
                    gmaps_url = f"https://www.google.com/maps?q={passenger_lat},{passenger_lng}"

                dis_label = {
                    "blind": "👁️ Visual Impairment",
                    "hand_disabled": "🤚 Hand Disability",
                    "leg_disabled": "🦽 Mobility Impairment",
                    "deaf": "🔇 Deaf",
                }.get(disability, f"♿ {str(disability).title()}")

                # PROMINENT CARD DISPLAY FOR PENDING REQUESTS WITH DISTANCE
                distance_display = f"📍 {distance_km} km away" if distance_km else "📍 Location pending"
                
                # VISUAL ALERT BOX - NEW REQUEST
                alert_bg_color = "#ef4444" if i == 0 else "#dc2626"  # Brighter red for first request
                
                st.markdown(f"""
                <div style='background:linear-gradient(135deg,rgba(239,68,68,.15),rgba(220,38,38,.1)); 
                            border:3px solid {alert_bg_color}; border-radius:12px; padding:16px; margin:12px 0;
                            box-shadow: 0 4px 16px rgba(239,68,68,.3);
                            position: relative;'>
                    <div style='position: absolute; top: -15px; left: 20px; background:#ef4444; color:#fff; 
                                padding:4px 12px; border-radius:20px; font-weight:800; font-size:0.8rem;'>
                        🚨 NEW ALERT
                    </div>
                    <div style='color:#fca5a5; font-size:1.1rem; font-weight:800; margin-bottom:10px; margin-top:5px;'>
                        🔴 PENDING - REQUIRES IMMEDIATE ATTENTION
                    </div>
                    <div style='color:#f1f5f9; font-size:0.95rem; line-height:1.8;'>
                        <div>👤 <strong>Passenger:</strong> {user_name}</div>
                        <div>🚍 <strong>Route:</strong> {route}</div>
                        <div>🛫 <strong>Boarding:</strong> {boarding}</div>
                        <div>🏁 <strong>Destination:</strong> {destination or 'Not specified'}</div>
                        <div>{dis_label}</div>
                        <div style='color:#f59e0b; margin-top:8px; font-weight:700;'>{distance_display} from Madhavaram Depot</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # PROVIDE SPECIALIZED ACCESSIBILITY ALERTS FOR DEAF & BLIND USERS
                if i == 0:  # Alert only for first pending request
                    disability_type = disability.replace("_", " ").title()
                    boarding_clean = str(boarding).replace("Bus Stand", "").replace("busstand", "").strip()
                    
                    if disability == "deaf":
                        # VISUAL ALERT FOR DEAF USERS - VERY HIGH CONTRAST
                        AccessibilityAlerts.show_visual_alert_deaf(
                            title=f"DEAF PASSENGER ALERT - {user_name.upper()}",
                            message=f"""
🔴 <strong>URGENT ACTION REQUIRED</strong><br>
👤 Passenger: <strong>{user_name}</strong><br>
🚌 Route: <strong>{route}</strong><br>
🛫 Boarding at: <strong>{boarding_clean}</strong><br>
📍 Distance: <strong>{distance_km} km from depot</strong><br>
<br>
⏰ <strong>ACKNOWLEDGE THIS REQUEST IMMEDIATELY</strong><br>
This passenger is DEAF - they CANNOT hear your honking or voice calls.
They MUST see you or receive visual signals to know you've arrived.
                            """,
                            alert_type="warning"
                        )
                        st.info("👁️ **VISUAL INTERFACE**: This passenger is Deaf. Use visual signals (lights, signs) and screen communication.")
                    elif disability == "blind":
                        # AUDIO ALERT FOR BLIND USERS
                        blind_alert_msg = (
                            f"ACCESSIBILITY ALERT! "
                            f"A BLIND passenger named {user_name} is requesting pickup at {boarding_clean}. "
                            f"This passenger is approximately {distance_km} kilometers from Madhavaram Depot. "
                            f"Please tap the ACKNOWLEDGE button immediately to confirm receipt. "
                            f"When you arrive, use voice communication and honk clearly to alert the passenger. "
                            f"The passenger will be waiting at the boarding point."
                        )
                        AccessibilityAlerts.speak_alert(blind_alert_msg)
                        st.info("🔊 **VOICE COMMUNICATION REQUIRED**: This passenger is Blind. Use clear voice/audio signals when you arrive.")
                    
                    # Enhanced voice message for other disabilities
                    else:
                        voice_msg = (
                            f"ACCESSIBILITY ALERT! "
                            f"A {disability_type} passenger named {user_name} is requesting pickup at {boarding_clean}. "
                            f"This passenger is approximately {distance_km} kilometers from Madhavaram Depot. "
                            f"Please tap the ACKNOWLEDGE button immediately to confirm receipt. "
                            f"The passenger will be waiting at the boarding point."
                        )
                        speak_alert(voice_msg)
                
                # ==================== PROMINENT LOCATION DISPLAY ====================
                if passenger_lat and passenger_lng:
                    st.markdown(f"""
                    <div style='background:linear-gradient(135deg,rgba(34,211,238,.2),rgba(59,130,246,.15)); 
                                border:2px solid #22d3ee; border-radius:12px; padding:14px; margin:12px 0;
                                box-shadow: 0 4px 12px rgba(34,211,238,.2);'>
                        <div style='color:#22d3ee; font-weight:700; font-size:1rem; margin-bottom:10px;'>
                            📍 PASSENGER LIVE LOCATION
                        </div>
                        <div style='color:#f1f5f9; font-size:0.95rem; font-family:monospace; 
                                    background:rgba(15,23,42,.6); padding:10px; border-radius:8px; margin-bottom:8px;'>
                            <div>📍 Latitude: <strong>{passenger_lat:.6f}</strong></div>
                            <div>📍 Longitude: <strong>{passenger_lng:.6f}</strong></div>
                            <div style='margin-top:8px; color:#f59e0b; font-weight:700;'>
                                📐 Distance: <strong>{distance_km} km</strong> from Madhavaram Depot
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Display Google Maps - render immediately
                    st.markdown("##### 🗺️ Passenger Location Map")
                    render_passenger_location_map(passenger_lat, passenger_lng, user_name, distance_km)
                    
                    if gmaps_url:
                        st.link_button("🔗 Open in Google Maps (Full View)", gmaps_url, use_container_width=True)
                else:
                    # Location not available - provide option to fetch
                    st.warning(f"⚠️ Live location not yet received from {user_name}")
                    st.markdown("""
                    <div style='background:rgba(239,68,68,.1); border:2px solid #f87171; border-radius:12px; 
                                padding:14px; margin:12px 0;'>
                        <div style='color:#fca5a5; font-weight:700; margin-bottom:8px;'>
                            📍 Waiting for Passenger Location
                        </div>
                        <div style='color:#f1f5f9; font-size:0.9rem;'>
                            The passenger's GPS location has not been shared yet.<br/>
                            Click "Get Live Locations" button above to refresh and fetch latest data.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Allow manual location input
                    with st.expander("📍 Enter Manual Location Coordinates", expanded=False):
                        manual_lat = st.number_input("Latitude:", min_value=-90.0, max_value=90.0, step=0.001, key=f"manual_lat_{req_id}", placeholder="e.g. 13.0500")
                        manual_lng = st.number_input("Longitude:", min_value=-180.0, max_value=180.0, step=0.001, key=f"manual_lng_{req_id}", placeholder="e.g. 80.2500")
                        
                        if st.button("📍 Use This Location", key=f"use_manual_loc_{req_id}", use_container_width=True):
                            if manual_lat and manual_lng:
                                st.success(f"✅ Using location: {manual_lat:.6f}, {manual_lng:.6f}")
                                render_passenger_location_map(manual_lat, manual_lng, user_name, None)
                            else:
                                st.error("❌ Please enter both latitude and longitude")
                
                st.markdown("---")
                
                # Info column with request details
                ci, ca = st.columns([2, 1])
                with ci:
                    st.markdown(f"**👤 Passenger Name:** {user_name}")
                    st.markdown(f"**🚍 Route:** {route}")
                    st.markdown(f"**🛫 Boarding Stop:** {boarding}")
                    if destination:
                        st.markdown(f"**🏁 Destination:** {destination}")
                    
                    st.markdown(f"**♿ Accessibility Need:** {dis_label}")
                    
                    if email:
                        st.markdown(f"**📧 Email:** {email}")
                    if phone:
                        st.markdown(f"**📞 Phone:** {phone}")

                with ca:
                    if st.button("✅ ACKNOWLEDGE", key=f"ack_{req_id}", use_container_width=True, type="primary",
                                 help="Tap to confirm you received this accessibility request"):
                        fb.update_request_status(req_id, "acknowledged")
                        st.success("✅ Request Acknowledged! Please proceed to pickup location.")
                        # Play confirmation sound
                        speak_alert("Request acknowledged. Proceeding to pickup location.")
                        st.rerun()

                    if st.button("🏁 Complete", key=f"done_{req_id}", use_container_width=True):
                        fb.update_request_status(req_id, "completed")
                        st.success("🏁 Completed!")
                        st.rerun()
                
                st.markdown("---")
            
            # ACKNOWLEDGED REQUESTS SECTION
            ack_requests = [r for r in active_requests if r.get("status") == "acknowledged"]
            if ack_requests:
                st.markdown("#### ✅ ACKNOWLEDGED REQUESTS")
                for ack_req in ack_requests:
                    req_id = ack_req.get("id", "")
                    user_name = ack_req.get("user_name", "User")
                    location = ack_req.get("location", "Unknown")
                    route = ack_req.get("route", "N/A")
                    disability = ack_req.get("disability_type", "N/A")
                    boarding = ack_req.get("boarding_stop", location)
                    destination = ack_req.get("destination_stop", "")
                    passenger_lat = ack_req.get("passenger_lat")
                    passenger_lng = ack_req.get("passenger_lng")

                    try:
                        passenger_lat = float(passenger_lat) if passenger_lat is not None else None
                        passenger_lng = float(passenger_lng) if passenger_lng is not None else None
                    except Exception:
                        passenger_lat, passenger_lng = None, None

                    with st.expander(f"✅ {location} - {user_name}"):
                        st.markdown(f"**Route:** {route}")
                        st.markdown(f"**From:** {boarding}")
                        if destination:
                            st.markdown(f"**To:** {destination}")
                        if passenger_lat and passenger_lng:
                            st.markdown(f"**📍 GPS:** {passenger_lat:.6f}, {passenger_lng:.6f}")
                        
                        if st.button("🏁 Mark Complete", key=f"complete_{req_id}", use_container_width=True):
                            fb.update_request_status(req_id, "completed")
                            st.success("🏁 Completed!")
                            st.rerun()
        else:
            st.success("✅ No pending pickup requests - all clear!")

    st.markdown("""
    <div style='background:rgba(15,23,42,.88); border:1px solid rgba(34,211,238,.25);
                border-radius:18px; padding:20px; margin-top:20px;'>
    """, unsafe_allow_html=True)
    
    # AUTO-REFRESH AND REAL-TIME UPDATE FEATURE
    st.markdown("### 🔄 Real-Time Update & Navigation")
    
    refresh_cols = st.columns(3)
    with refresh_cols[0]:
        if st.button("🔄 Refresh Now", use_container_width=True, key="driver_refresh_manual"):
            st.rerun()
    
    with refresh_cols[1]:
        refresh_interval = st.selectbox(
            "Auto-refresh every:",
            ["5 seconds", "10 seconds", "15 seconds", "Manual"],
            index=0,
            key="driver_auto_refresh"
        )
    
    with refresh_cols[2]:
        if st.button("🔓 Logout", use_container_width=True, key="driver_logout_btn"):
            st.session_state.logged_in = False
            st.session_state.role = None
            st.rerun()
    
    # Auto-refresh JavaScript
    if refresh_interval != "Manual":
        delay_map = {
            "5 seconds": 5000,
            "10 seconds": 10000,
            "15 seconds": 15000
        }
        delay = delay_map.get(refresh_interval, 5000)
        
        st.markdown(f"""
        <script>
        setTimeout(function() {{
            window.parent.location.reload();
        }}, {delay});
        </script>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("### 🔄 Switch Portal")
    st.caption("Switch to a different portal without logging out.")

    sr_cols = st.columns(4)
    portal_map = [
        ("🧍 Passenger", "passenger"),
        ("🚍 Driver", "driver"),
        ("🛠 Admin", "admin"),
        ("♿ Disabled", "disabled"),
    ]
    for col, (label, role) in zip(sr_cols, portal_map):
        with col:
            if st.button(label, key=f"drv_switch_{role}", use_container_width=True,
                         disabled=(st.session_state.get("role") == role)):
                st.session_state.role = role
                st.session_state.selected_portal = role
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def _render_demo_requests():
    """Demo offline pickup requests when Firebase is unavailable."""
    demo = [
        {"user": "Anitha", "location": "Adyar Bus Stand", "type": "🦽 Mobility", "route": "5C"},
        {"user": "Ravi", "location": "CMBT", "type": "👁️ Visual", "route": "19B"},
    ]
    for d in demo:
        with st.expander(f"📍 {d['location']} - 👤 {d['user']} | ⏳ Pending"):
            st.write(f"**Route:** {d['route']}")
            st.write(f"**Type:** {d['type']}")
            st.info("(Offline demo - Firebase not connected)")
