# -*- coding: utf-8 -*-
import streamlit as st
from datetime import datetime
from helpers import get_live_detector, get_firebase_manager, get_ai_response
from voice_login import init_voice_state, render_voice_input, render_welcome, render_route_selection


def render(routes, stops):
    """Render the app pages based on `st.session_state` values."""
    # Navigation and pages are controlled by session_state set in main `app.py`
    if not st.session_state.logged_in:
        render_login()
    elif st.session_state.role == 'passenger':
        render_passenger(routes, stops)
    elif st.session_state.role == 'disabled':
        render_disabled(routes, stops)
    elif st.session_state.role == 'driver':
        render_driver()
    elif st.session_state.role == 'admin':
        render_admin()


def render_login():
    # This mirrors the original login UI but kept concise here; the app still manages session_state keys
    st.markdown("<h1 style='text-align: center;'>🚌 TAMIL NADU SMART BUS</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2em; opacity: 0.8;'>Inclusive & Automated Public Transport Solution</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 🔐 Central Login Dashboard")
    st.markdown("---")
    portal_options = {"🧍 Passenger": "passenger", "♿ Disabled": "disabled", "🚌 Driver": "driver", "🛠 Admin": "admin"}
    selected_portal_display = st.selectbox("Portal Type:", options=list(portal_options.keys()))
    selected_portal = portal_options[selected_portal_display]
    st.markdown("---")
    # For brevity, provide simple inputs for non-disabled flows; the full voice flows remain in `app.py` session state handling
    email = st.text_input("📧 Email ID", key="central_login_email")
    password = st.text_input("🔑 Password", type="password", key="central_login_password")
    phone = st.text_input("📱 Phone Number", key="central_login_phone", max_chars=10)
    if st.button("✅ Login"):
        if not email or not password or not phone:
            st.error("Please fill all fields")
        else:
            st.session_state.logged_in = True
            st.session_state.role = selected_portal
            st.session_state.selected_portal = selected_portal
            st.session_state.user_email = email
            st.session_state.user_phone = phone
            st.success("Login successful")
            st.experimental_rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def render_passenger(routes, stops):
    st.markdown("## 🧍 Passenger Portal")
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    route_option = st.selectbox("Search Route / Bus No:", routes["bus_details"].unique())
    st.markdown("---")
    st.markdown("### <span class='live-indicator'></span>🎥 Live Crowd Detection", unsafe_allow_html=True)
    c1, c2 = st.columns([2,1])
    with c1:
        if st.button("📹 Start Live Detection"):
            st.session_state.live_detection_active = True
            detector = get_live_detector()
            detector.start_detection(camera_index=0)
            st.success("Live detection started")
        if st.button("⏹️ Stop Detection"):
            st.session_state.live_detection_active = False
            detector = get_live_detector()
            detector.stop_detection()
            st.info("Detection stopped")
        if st.session_state.live_detection_active:
            detector = get_live_detector()
            frame = detector.get_latest_frame()
            if frame is not None:
                st.image(frame, caption='Live Crowd Detection', use_container_width=True)
            else:
                st.info(detector.status_msg)
    with c2:
        if st.session_state.live_detection_active:
            detector = get_live_detector()
            crowd = detector.get_crowd_data()
            st.metric("👥 People Count", crowd['count'])
            level = crowd['level']
            if level == 'Low':
                st.success(f"🟢 {level}")
            elif level == 'Medium':
                st.warning(f"🟡 {level}")
            else:
                st.error(f"🔴 {level}")
    st.markdown("</div>", unsafe_allow_html=True)


def render_disabled(routes, stops):
    st.markdown("## ♿ Inclusive Accessibility Portal")
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    
    # Initialize voice state on first visit
    init_voice_state()
    
    # Handle different steps of voice login flow
    if st.session_state.voice_login_step == "input":
        render_voice_input()
    elif st.session_state.voice_login_step == "welcome":
        render_welcome()
    elif st.session_state.voice_login_step == "routes":
        render_route_selection(routes, stops)
    
    st.markdown("</div>", unsafe_allow_html=True)


def render_driver():
    st.markdown("## 🚌 Driver Dashboard")
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.write("Driver UI: view pickup requests and acknowledge in the app.")
    st.markdown("</div>", unsafe_allow_html=True)


def render_admin():
    st.markdown("## 🛠 System Management")
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Live Operational Stats")
    c1, c2, c3 = st.columns(3)
    c1.metric("Active Buses", "42")
    c2.metric("Assistance Requests", "12", "3")
    c3.metric("System Health", "98%")
    st.markdown("</div>", unsafe_allow_html=True)
