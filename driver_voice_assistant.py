# -*- coding: utf-8 -*-
# ============================================================
#   DRIVER VOICE ASSISTANT PORTAL
#   Features:
#     - Voice announcements for all pending disability pickups
#     - Real-time position announcements
#     - Voice-based navigation & alerts
#     - Position-based location updates
#     - Interactive voice commands
# ============================================================

import streamlit as st
import streamlit.components.v1 as components
from firebase_manager import get_firebase_manager
from math import radians, cos, sin, asin, sqrt


def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates in km (Haversine formula)."""
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371
    return c * r


def speak_announcement(text):
    """Use browser's TTS to speak announcements to driver."""
    safe = text.replace("'", "\\'").replace("\n", " ")
    components.html(f"""
    <script>
    (function() {{
        window.speechSynthesis.cancel();
        var u = new SpeechSynthesisUtterance('{safe}');
        u.lang  = 'en-IN';
        u.rate  = 0.85;
        u.pitch = 1.0;
        u.volume = 1.0;
        window.speechSynthesis.speak(u);
    }})();
    </script>
    """, height=0)


def announce_pickup_position(passenger_name, location, distance_km, disability_type, boarding_stop):
    """Create a voice announcement for a specific pickup position."""
    disability_msg = {
        "blind": "This passenger is BLIND",
        "deaf": "This passenger is DEAF",
        "hand_disabled": "This passenger has HAND DISABILITY",
        "leg_disabled": "This passenger has MOBILITY IMPAIRMENT",
    }
    
    disability_desc = disability_msg.get(disability_type, f"This passenger has {disability_type.replace('_', ' ').title()}")
    
    announcement = (
        f"ACCESSIBILITY PICKUP ALERT! "
        f"Passenger {passenger_name} is waiting at {boarding_stop}. "
        f"{disability_desc}. "
        f"Located approximately {distance_km} kilometers from the depot. "
        f"Please approach the pickup location carefully and use appropriate communication methods. "
        f"Acknowledge when ready to proceed."
    )
    
    return announcement


def render_voice_assistant_portal():
    """Render the Voice Assistant Portal for drivers with disability pickup announcements."""
    
    st.markdown("""
    <div style='background:linear-gradient(135deg,rgba(139,92,246,.15),rgba(59,130,246,.1)); 
                border:2px solid #a78bfa; border-radius:16px; padding:20px; margin-bottom:20px;'>
        <div style='color:#a78bfa; font-size:1.4rem; font-weight:800; margin-bottom:8px;'>
            🎤 VOICE ASSISTANT PORTAL - DISABILITY PICKUPS
        </div>
        <div style='color:#f1f5f9; font-size:0.95rem;'>
            Real-time voice announcements for all accessibility-related passenger pickups and their exact positions.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state for voice assistant
    if "voice_assistant_active" not in st.session_state:
        st.session_state.voice_assistant_active = False
    if "announced_pickups" not in st.session_state:
        st.session_state.announced_pickups = []
    
    # Get Firebase data
    fb = get_firebase_manager()
    active_requests = []
    
    if fb.initialized:
        active_requests = fb.get_active_requests()
    
    # Filter only pending requests with disability types
    disability_requests = [
        r for r in active_requests 
        if r.get("status") == "pending" and r.get("disability_type")
    ]
    
    if not disability_requests:
        st.info("✅ No pending disability pickups at this time.")
        return
    
    # ================================================================
    # VOICE ANNOUNCEMENT CONTROLS
    # ================================================================
    st.markdown("### 🎤 Voice Announcements")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔊 Announce All Pickups", use_container_width=True, key="announce_all"):
            all_announcement = "VOICE ASSISTANT ACTIVE. "
            all_announcement += f"You have {len(disability_requests)} accessibility pickups waiting. "
            
            for idx, req in enumerate(disability_requests, 1):
                all_announcement += f"Pickup number {idx}. "
                all_announcement += announce_pickup_position(
                    req.get("user_name", "Passenger"),
                    req.get("location", "Unknown"),
                    req.get("distance_km", 0),
                    req.get("disability_type", "unknown"),
                    req.get("boarding_stop", req.get("location", "Unknown"))
                ) + " "
            
            speak_announcement(all_announcement)
            st.success("✅ Announcement started")
    
    with col2:
        if st.button("🗺️ Announce Nearest Pickup", use_container_width=True, key="announce_nearest"):
            if disability_requests:
                # Find nearest by distance_km
                try:
                    nearest = min(disability_requests, 
                                key=lambda r: float(r.get("distance_km", float('inf'))))
                    nearest_announcement = announce_pickup_position(
                        nearest.get("user_name", "Passenger"),
                        nearest.get("location", "Unknown"),
                        nearest.get("distance_km", 0),
                        nearest.get("disability_type", "unknown"),
                        nearest.get("boarding_stop", nearest.get("location", "Unknown"))
                    )
                    speak_announcement(nearest_announcement)
                    st.success("✅ Nearest pickup announced")
                except Exception as e:
                    st.error(f"Error: {e}")
    
    with col3:
        if st.button("🔇 Stop Announcements", use_container_width=True, key="stop_announcements"):
            st.session_state.voice_assistant_active = False
            st.success("✅ Announcements stopped")
    
    st.markdown("---")
    
    # ================================================================
    # DISABILITY PICKUPS - POSITION-BASED DISPLAY
    # ================================================================
    st.markdown("### 📍 DISABILITY PICKUPS - ACTIVE POSITIONS")
    
    # Calculate distances and sort by distance
    for idx, req in enumerate(disability_requests):
        if not req.get("distance_km"):
            try:
                lat = float(req.get("passenger_lat", 0))
                lng = float(req.get("passenger_lng", 0))
                # Use driver's current location (from session) instead of hardcoded depot
                driver_lat = st.session_state.get("driver_lat")
                driver_lng = st.session_state.get("driver_lng")
                
                if lat and lng and driver_lat and driver_lng:
                    distance = calculate_distance(driver_lat, driver_lng, lat, lng)
                    req["distance_km"] = round(distance, 2)
                else:
                    req["distance_km"] = 0
            except:
                req["distance_km"] = 0
    
    # Sort by distance km
    try:
        sorted_requests = sorted(
            disability_requests,
            key=lambda r: float(r.get("distance_km", float('inf')))
        )
    except:
        sorted_requests = disability_requests
    
    # Create columns for overview
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🚨 Total Accessibility Requests", len(sorted_requests))
    with col2:
        st.metric("📍 Awaiting Pickup", len([r for r in sorted_requests if r.get("status") == "pending"]))
    with col3:
        st.metric("✅ Acknowledged", len([r for r in sorted_requests if r.get("status") == "acknowledged"]))
    
    st.markdown("---")
    
    # Display each pickup with position details
    for idx, req in enumerate(sorted_requests, 1):
        req_id = req.get("id", "")
        user_name = req.get("user_name", "Passenger")
        location = req.get("location", "Unknown")
        disability = req.get("disability_type", "unknown")
        boarding = req.get("boarding_stop", location)
        distance_km = req.get("distance_km", 0)
        passenger_lat = req.get("passenger_lat")
        passenger_lng = req.get("passenger_lng")
        status = req.get("status", "pending")
        
        try:
            passenger_lat = float(passenger_lat) if passenger_lat else None
            passenger_lng = float(passenger_lng) if passenger_lng else None
            distance_km = float(distance_km) if distance_km else 0
        except:
            passenger_lat, passenger_lng = None, None
            distance_km = 0
        
        # Round distance to 2 decimal places for display
        distance_display = round(distance_km, 2) if distance_km else 0
        
        # Disability icon and label
        disability_icons = {
            "blind": "👁️ BLIND",
            "deaf": "🔇 DEAF",
            "hand_disabled": "🤚 HAND DISABILITY",
            "leg_disabled": "🦽 MOBILITY IMPAIRMENT",
        }
        dis_label = disability_icons.get(disability, f"♿ {disability.title()}")
        
        # Status color
        status_badge = "🔴 PENDING" if status == "pending" else "✅ ACKNOWLEDGED"
        status_bg = "rgba(239,68,68,.2)" if status == "pending" else "rgba(34,197,94,.2)"
        status_border = "#f87171" if status == "pending" else "#86efac"
        
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,{status_bg},rgba(30,41,59,.3)); 
                    border:2px solid {status_border}; border-radius:14px; padding:18px; margin:15px 0;
                    box-shadow: 0 4px 12px rgba(0,0,0,.3);'>
            <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;'>
                <div style='color:#a78bfa; font-size:1.2rem; font-weight:800;'>
                    #{idx} - {dis_label}
                </div>
                <div style='color:#f1f5f9; font-size:0.9rem; font-weight:700;'>
                    {status_badge}
                </div>
            </div>
            
            <div style='color:#f1f5f9; font-size:0.95rem; line-height:1.8;'>
                <div>👤 <strong>Passenger:</strong> {user_name}</div>
                <div>🛫 <strong>Boarding Location:</strong> {boarding}</div>
                <div style='color:#f59e0b; font-weight:700; margin-top:8px;'>
                    📍 <strong>Distance: {distance_display} km from your current location</strong>
                </div>
        """, unsafe_allow_html=True)
        
        # GPS Coordinates if available
        if passenger_lat and passenger_lng:
            st.markdown(f"""
                <div style='background:rgba(34,211,238,.15); border-left:4px solid #22d3ee; 
                            padding:10px; border-radius:8px; margin:10px 0;'>
                    <div style='color:#22d3ee; font-weight:700; margin-bottom:6px;'>📍 GPS POSITION:</div>
                    <div style='color:#f1f5f9; font-family:monospace; font-size:0.9rem;'>
                        Latitude: <strong>{passenger_lat:.6f}</strong> | Longitude: <strong>{passenger_lng:.6f}</strong>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Voice announcement button for this specific pickup
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button(f"🎤 Announce This Position", key=f"announce_pos_{req_id}", use_container_width=True):
                announcement = announce_pickup_position(user_name, location, distance_km, disability, boarding)
                speak_announcement(announcement)
                st.success("✅ Position announced")
        
        with col2:
            if st.button(f"🗣️ Navigation Instructions", key=f"nav_inst_{req_id}", use_container_width=True):
                nav_msg = (
                    f"Navigating to {boarding}. "
                    f"The passenger is {distance_km} kilometers away. "
                    f"Please proceed carefully. {dis_label} passenger ahead."
                )
                speak_announcement(nav_msg)
                st.success("✅ Navigation instructions given")
        
        with col3:
            if st.button(f"✅ Acknowledge", key=f"voice_ack_{req_id}", use_container_width=True):
                fb.update_request_status(req_id, "acknowledged")
                speak_announcement(f"Pickup {idx} acknowledged. Proceeding to location.")
                st.success("✅ Request acknowledged")
                st.rerun()
        
        with col4:
            if st.button(f"🏁 Complete", key=f"voice_done_{req_id}", use_container_width=True):
                fb.update_request_status(req_id, "completed")
                speak_announcement(f"Pickup {idx} completed.")
                st.success("✅ Pickup completed")
                st.rerun()
        
        st.markdown("---")
    
    # ================================================================
    # POSITION REFERENCE GUIDE
    # ================================================================
    with st.expander("📖 Position Reference & Accessibility Guidelines"):
        st.markdown("""
        ### 🎯 How to Use Position Information
        
        **For each pickup:**
        - 📍 Distance shows how far the passenger is from your current location
        - 🗺️ GPS coordinates (Latitude, Longitude) show the exact position
        - 🎤 Voice announcements help you understand the location without looking at screen
        
        ### ♿ Accessibility Communication Guide
        
        **👁️ BLIND Passengers:**
        - Use clear voice communication when you arrive
        - Honk loudly and distinctly to alert them
        - Announce your arrival verbally
        - Guide them verbally to the bus entrance
        - Speak clearly about steps/obstacles
        
        **🔇 DEAF Passengers:**
        - Use visual signals (lights, signs)
        - Flash headlights when arriving
        - Use hand signals to guide them
        - Display boarding information visibly
        - Write messages if needed
        
        **🦽 MOBILITY IMPAIRMENT Patients:**
        - Arrive at exact location
        - Provide extra time for boarding
        - Offer physical assistance as needed
        - Ensure wheelchair accessibility (if applicable)
        - Park close to boarding point
        
        **🤚 HAND DISABILITY Passengers:**
        - Park close to boarding point
        - Allow extra boarding time
        - Offer assistance if needed
        - Be patient with boarding process
        """)
    
    st.markdown("---")
    
    # Driver location reference
    st.markdown("### 📍 YOUR CURRENT AREA")
    st.markdown("""
    - **Reference Point:** Your GPS-provided location
    - **Service Area:** Distance calculated from your current position
    
    All distances above are calculated from your current GPS location.
    """)
