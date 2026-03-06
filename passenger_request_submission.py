# -*- coding: utf-8 -*-
# ============================================================
#   PASSENGER REQUEST SUBMISSION MODULE  
#   Explicit features for passengers to submit pickup requests
#   - Multi-step form for detailed request data
#   - Location capture (GPS or manual)
#   - Visual feedback and confirmation
# ============================================================

import streamlit as st
import streamlit.components.v1 as components
from firebase_manager import get_firebase_manager
from datetime import datetime


def capture_passenger_location():
    """
    EXPLICIT: Capture passenger GPS location using browser geolocation API.
    Returns: Dictionary with {lat, lng, accuracy} or None
    """
    location_html = """
    <div id="locationStatus">
        <div style="color: #94a3b8; padding: 20px; text-align: center; font-size: 0.95rem;">
            📍 Requesting GPS location... Please allow location access in your browser.
        </div>
    </div>
    
    <script>
    function updateLocationStatus(lat, lng, accuracy) {
        document.getElementById('locationStatus').innerHTML = `
            <div style="background: rgba(34, 211, 238, 0.1); border: 2px solid #22d3ee; 
                        border-radius: 12px; padding: 16px; margin: 10px 0;">
                <div style="color: #22d3ee; font-weight: 700; margin-bottom: 10px;">
                    ✅ Location Captured
                </div>
                <div style="color: #f1f5f9; font-family: monospace; font-size: 0.9rem;">
                    📍 Latitude: ${lat.toFixed(6)}<br/>
                    📍 Longitude: ${lng.toFixed(6)}<br/>
                    📡 Accuracy: ${accuracy.toFixed(0)}m
                </div>
            </div>
        `;
        window.parent.postMessage({
            type: 'streamlit:setComponentValue',
            value: {lat: lat, lng: lng, accuracy: accuracy}
        }, '*');
    }
    
    function locationError(err) {
        const msg = {1:'Permission denied',2:'Position unavailable',3:'Timeout'}[err.code] || 'Unknown';
        document.getElementById('locationStatus').innerHTML = `
            <div style="background: rgba(239, 68, 68, 0.1); border: 2px solid #ef4444; 
                        border-radius: 12px; padding: 16px; margin: 10px 0;">
                <div style="color: #ef4444; font-weight: 700;">
                    ❌ Location Error: ${msg}
                </div>
                <div style="color: #f1f5f9; font-size: 0.9rem; margin-top: 8px;">
                    Please enable location access or enter coordinates manually.
                </div>
            </div>
        `;
    }
    
    if ('geolocation' in navigator) {
        navigator.geolocation.getCurrentPosition(
            pos => updateLocationStatus(pos.coords.latitude, pos.coords.longitude, pos.coords.accuracy),
            locationError,
            {enableHighAccuracy: true, timeout: 10000, maximumAge: 0}
        );
    } else {
        document.getElementById('locationStatus').innerHTML = `
            <div style="color: #ef4444; padding: 20px; text-align: center;">
                ❌ Geolocation not supported in your browser
            </div>
        `;
    }
    </script>
    """
    
    return components.html(location_html, height=150)


def render_passenger_request_form(routes_df, stops_df):
    """
    EXPLICIT: Render multi-step form for passenger to submit accessibility request.
    
    Steps:
    1. Personal Information (Name, Contact)
    2. Route & Stops Selection
    3. Accessibility Details
    4. Location Capture
    5. Review & Submit
    """
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(34,211,238,0.15), rgba(59,130,246,0.1));
                border: 2px solid rgba(34,211,238,0.3);
                border-radius: 16px;
                padding: 20px;
                margin: 20px 0;">
        <div style="color: #22d3ee; font-size: 1.6rem; font-weight: 800;">
            📋 Book Accessibility Pickup Request
        </div>
        <div style="color: #94a3b8; font-size: 0.95rem; margin-top: 8px;">
            Complete this form to request a special accessibility-enabled pickup
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize multi-step form state
    if "request_step" not in st.session_state:
        st.session_state.request_step = 1
    
    # Step Indicator
    st.markdown("""
    <div style="display: flex; justify-content: space-between; margin: 20px 0; gap: 10px;">
    """, unsafe_allow_html=True)
    
    steps = ["👤 Personal", "🚌 Route", "♿ Need", "📍 Location", "✅ Review"]
    for i, step in enumerate(steps, 1):
        color = "#22d3ee" if i == st.session_state.request_step else "#94a3b8" if i < st.session_state.request_step else "#475569"
        weight = "800" if i == st.session_state.request_step else "600"
        
        st.markdown(f"""
        <div style="flex: 1; text-align: center; color: {color}; font-weight: {weight}; font-size: 0.85rem;">
            Step {i}<br/>{step}
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.divider()
    
    # ================================================================
    # STEP 1: PERSONAL INFORMATION
    # ================================================================
    if st.session_state.request_step == 1:
        st.markdown("### 👤 Step 1: Personal Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            passenger_name = st.text_input(
                "Full Name *",
                key="request_name",
                placeholder="Enter your full name"
            )
        
        with col2:
            passenger_email = st.text_input(
                "Email Address *",
                key="request_email",
                placeholder="your.email@example.com"
            )
        
        passenger_phone = st.text_input(
            "Phone Number *",
            key="request_phone",
            placeholder="+91 9876543210"
        )
        
        st.info("ℹ️ We'll use this information to contact you about your pickup request")
        
        # Navigation buttons
        nav_col1, nav_col2 = st.columns([1, 3])
        with nav_col2:
            if st.button("Next Step →", use_container_width=True, type="primary", key="step1_next"):
                if passenger_name and passenger_email and passenger_phone:
                    st.session_state.request_name = passenger_name
                    st.session_state.request_email = passenger_email
                    st.session_state.request_phone = passenger_phone
                    st.session_state.request_step = 2
                    st.rerun()
                else:
                    st.error("❌ Please fill in all required fields")
    
    # ================================================================
    # STEP 2: ROUTE & STOPS SELECTION
    # ================================================================
    elif st.session_state.request_step == 2:
        st.markdown("### 🚌 Step 2: Select Route & Stops")
        
        if routes_df is not None and not routes_df.empty:
            route_option = st.selectbox(
                "Bus Route *",
                routes_df["bus_details"].unique(),
                key="request_route",
                placeholder="Select your bus route"
            )
            
            # Get stops for selected route
            selected_row = routes_df[routes_df["bus_details"] == route_option].iloc[0]
            
            if stops_df is not None and not stops_df.empty:
                try:
                    stop_ids = str(selected_row["route"]).strip().split()
                    stop_ids = [s.strip() for s in stop_ids if s.strip().isdigit()]
                    stops_sub = stops_df[stops_df["stop_id"].astype(str).isin(stop_ids)]
                    stop_list = stops_sub["stop_name"].tolist()
                except Exception:
                    stop_list = []
            else:
                stop_list = []
            
            if stop_list:
                col1, col2 = st.columns(2)
                
                with col1:
                    boarding_stop = st.selectbox(
                        "Boarding Stop *",
                        stop_list,
                        key="request_boarding",
                        placeholder="Where you want to board"
                    )
                
                with col2:
                    dest_options = [s for s in stop_list if s != boarding_stop]
                    if dest_options:
                        destination_stop = st.selectbox(
                            "Destination Stop *",
                            dest_options,
                            key="request_destination",
                            placeholder="Where you want to go"
                        )
                    else:
                        destination_stop = boarding_stop
            else:
                st.warning("⚠️ No stops available for this route")
                boarding_stop = st.text_input("Boarding Stop (Manual):")
                destination_stop = st.text_input("Destination Stop (Manual):")
        
        st.info("ℹ️ Double-check your route and stops")
        
        # Navigation buttons
        nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 1])
        with nav_col1:
            if st.button("← Previous", use_container_width=True, key="step2_prev"):
                st.session_state.request_step = 1
                st.rerun()
        with nav_col3:
            if st.button("Next Step →", use_container_width=True, type="primary", key="step2_next"):
                if boarding_stop and destination_stop:
                    st.session_state.request_boarding = boarding_stop
                    st.session_state.request_destination = destination_stop
                    st.session_state.request_route = route_option
                    st.session_state.request_step = 3
                    st.rerun()
                else:
                    st.error("❌ Please select both stops")
    
    # ================================================================
    # STEP 3: ACCESSIBILITY DETAILS
    # ================================================================
    elif st.session_state.request_step == 3:
        st.markdown("### ♿ Step 3: Accessibility Requirements")
        
        disability_options = [
            "Elderly",
            "Wheelchair User",
            "Visual Impairment",
            "Hearing Impairment",
            "Mobility Issue",
            "Other"
        ]
        
        disability_type = st.selectbox(
            "Type of Accessibility Need *",
            disability_options,
            key="request_disability",
            placeholder="Select your accessibility requirement"
        )
        
        additional_info = st.text_area(
            "Additional Information (Optional)",
            placeholder="Tell us about your specific needs so we can better assist you...",
            key="request_additional",
            height=100
        )
        
        st.info("ℹ️ This helps us prepare the bus with appropriate accommodations")
        
        # Navigation buttons
        nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 1])
        with nav_col1:
            if st.button("← Previous", use_container_width=True, key="step3_prev"):
                st.session_state.request_step = 2
                st.rerun()
        with nav_col3:
            if st.button("Next Step →", use_container_width=True, type="primary", key="step3_next"):
                st.session_state.request_disability = disability_type
                st.session_state.request_additional = additional_info
                st.session_state.request_step = 4
                st.rerun()
    
    # ================================================================
    # STEP 4: LOCATION CAPTURE
    # ================================================================
    elif st.session_state.request_step == 4:
        st.markdown("### 📍 Step 4: Your Current Location")
        
        st.markdown("""
        <div style="background: rgba(34, 211, 238, 0.1); border: 2px solid rgba(34, 211, 238, 0.3);
                   border-radius: 12px; padding: 14px; margin: 10px 0;">
            <div style="color: #22d3ee; font-weight: 700; margin-bottom: 8px;">
                🔒 Your Location is Used For
            </div>
            <ul style="color: #f1f5f9; margin: 0; padding-left: 20px;">
                <li>Help drivers find you quickly</li>
                <li>Calculate distance and ETA</li>
                <li>Send emergency responders if needed</li>
                <li>Never shared with unauthorized parties</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        location_method = st.radio(
            "How would you like to share your location?",
            ["📍 Auto-detect using GPS", "🗺️ Enter coordinates manually", "📌 Select on map"],
            key="location_method"
        )
        
        if location_method == "📍 Auto-detect using GPS":
            st.markdown("#### Requesting your location from browser...")
            
            location_data = capture_passenger_location()
            
            if location_data:
                st.session_state.request_lat = location_data.get("lat")
                st.session_state.request_lng = location_data.get("lng")
            
            if "request_lat" in st.session_state and st.session_state.request_lat:
                st.success(f"✅ Location captured: {st.session_state.request_lat:.6f}, {st.session_state.request_lng:.6f}")
        
        elif location_method == "🗺️ Enter coordinates manually":
            col1, col2 = st.columns(2)
            with col1:
                manual_lat = st.number_input(
                    "Latitude",
                    min_value=-90.0,
                    max_value=90.0,
                    value=None,
                    step=0.0001,
                    key="manual_lat_request"
                )
            with col2:
                manual_lng = st.number_input(
                    "Longitude",
                    min_value=-180.0,
                    max_value=180.0,
                    value=None,
                    step=0.0001,
                    key="manual_lng_request"
                )
            
            st.session_state.request_lat = manual_lat
            st.session_state.request_lng = manual_lng
            st.success(f"✅ Location set: {manual_lat:.6f}, {manual_lng:.6f}")
        
        # Navigation buttons
        nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 1])
        with nav_col1:
            if st.button("← Previous", use_container_width=True, key="step4_prev"):
                st.session_state.request_step = 3
                st.rerun()
        with nav_col3:
            if st.button("Next Step →", use_container_width=True, type="primary", key="step4_next"):
                if "request_lat" in st.session_state and "request_lng" in st.session_state:
                    st.session_state.request_step = 5
                    st.rerun()
                else:
                    st.error("❌ Please capture your location")
    
    # ================================================================
    # STEP 5: REVIEW & SUBMIT
    # ================================================================
    elif st.session_state.request_step == 5:
        st.markdown("### ✅ Step 5: Review & Submit")
        
        # Review all information
        st.markdown("""
        <div style="background: rgba(34, 211, 238, 0.1); border: 2px solid rgba(34, 211, 238, 0.3);
                   border-radius: 12px; padding: 18px;">
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**👤 Personal Information**")
            st.write(f"Name: {st.session_state.request_name}")
            st.write(f"Email: {st.session_state.request_email}")
            st.write(f"Phone: {st.session_state.request_phone}")
            
            st.divider()
            
            st.markdown("**♿ Accessibility Need**")
            st.write(f"Type: {st.session_state.request_disability}")
            if st.session_state.request_additional:
                st.write(f"Note: {st.session_state.request_additional}")
        
        with col2:
            st.markdown("**🚌 Route & Stops**")
            st.write(f"Route: {st.session_state.request_route}")
            st.write(f"From: {st.session_state.request_boarding}")
            st.write(f"To: {st.session_state.request_destination}")
            
            st.divider()
            
            st.markdown("**📍 Location**")
            st.write(f"Latitude: {st.session_state.request_lat:.6f}")
            st.write(f"Longitude: {st.session_state.request_lng:.6f}")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.info("📋 Please review all information above before submitting")
        
        # Navigation buttons
        nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 1])
        with nav_col1:
            if st.button("← Edit", use_container_width=True, key="step5_prev"):
                st.session_state.request_step = 1
                st.rerun()
        
        with nav_col3:
            if st.button("✅ Submit Request", use_container_width=True, type="primary", key="submit_request"):
                fb = get_firebase_manager()
                
                request_id = fb.send_pickup_request(
                    user_name=st.session_state.request_name,
                    email=st.session_state.request_email,
                    phone=st.session_state.request_phone,
                    location=st.session_state.request_boarding,
                    route=st.session_state.request_route,
                    disability_type=st.session_state.request_disability,
                    boarding_stop=st.session_state.request_boarding,
                    destination_stop=st.session_state.request_destination,
                    passenger_lat=st.session_state.request_lat,
                    passenger_lng=st.session_state.request_lng
                )
                
                if request_id:
                    st.success(f"✅ Request submitted successfully! ID: {request_id}")
                    st.balloons()
                    
                    # Reset form
                    st.session_state.request_step = 1
                    st.session_state.clear()
                    
                    st.info("📋 Your request has been sent to drivers. You will be notified when a driver accepts your request.")
                else:
                    st.error("❌ Failed to submit request. Please try again.")
