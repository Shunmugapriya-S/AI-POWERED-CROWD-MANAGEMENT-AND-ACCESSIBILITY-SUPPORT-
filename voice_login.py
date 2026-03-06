# -*- coding: utf-8 -*-
import streamlit as st
import time
from datetime import datetime, timedelta


def init_voice_state():
    """Initialize voice login session state."""
    if "voice_email" not in st.session_state:
        st.session_state.voice_email = ""
    if "voice_password" not in st.session_state:
        st.session_state.voice_password = ""
    if "voice_input_mode" not in st.session_state:
        st.session_state.voice_input_mode = "email"
    if "voice_login_step" not in st.session_state:
        st.session_state.voice_login_step = "input"  # input, welcome, routes


def render_voice_input():
    """Render voice input UI for email and password."""
    st.markdown("### 🎤 Voice-Assisted Login")
    st.info("Speak each letter/number clearly. Say 'AT' for @, 'DOT' for period, 'SPACE' for space.")

    col_email1, col_email2, col_email3 = st.columns(3)
    with col_email1:
        if st.button("🎤 Add Email Char", key="voice_email_btn", use_container_width=True):
            st.session_state.voice_input_mode = "email"
            st.info("🎤 Say one character (A-Z, 0-9, or @, DOT, SPACE)")

    with col_email2:
        if st.button("⌫ Delete Last Email", key="email_backspace", use_container_width=True):
            if st.session_state.voice_email:
                st.session_state.voice_email = st.session_state.voice_email[:-1]
                st.rerun()

    with col_email3:
        if st.button("🗑️ Clear Email", key="email_clear", use_container_width=True):
            st.session_state.voice_email = ""
            st.rerun()

    # Display current email
    st.markdown(f"**📧 Email:** `{st.session_state.voice_email if st.session_state.voice_email else '(empty)'}`")

    # Manual input for testing
    manual_email_char = st.text_input("Type one character (for testing):", max_chars=1, key="manual_email_voice", label_visibility="collapsed")
    if manual_email_char:
        char = manual_email_char.lower()
        if char == '@':
            st.session_state.voice_email += "@"
        elif char == ".":
            st.session_state.voice_email += "."
        elif char == " ":
            st.session_state.voice_email += " "
        else:
            st.session_state.voice_email += char
        st.rerun()

    # Quick add buttons
    st.markdown("**Quick Add:**")
    qcol1, qcol2, qcol3, qcol4 = st.columns(4)
    with qcol1:
        if st.button("@", key="add_at_voice"):
            st.session_state.voice_email += "@"
            st.rerun()
    with qcol2:
        if st.button(".", key="add_dot_voice"):
            st.session_state.voice_email += "."
            st.rerun()
    with qcol3:
        if st.button("gmail.com", key="add_gmail_voice"):
            st.session_state.voice_email += "gmail.com"
            st.rerun()
    with qcol4:
        if st.button("smartbus.com", key="add_smartbus_voice"):
            st.session_state.voice_email += "smartbus.com"
            st.rerun()

    st.markdown("---")

    # Password section
    col_pass1, col_pass2, col_pass3 = st.columns(3)
    with col_pass1:
        if st.button("🎤 Add Password Char", key="voice_pass_btn", use_container_width=True):
            st.session_state.voice_input_mode = "password"
            st.info("🎤 Say one character for password")

    with col_pass2:
        if st.button("⌫ Delete Last Pass", key="pass_backspace", use_container_width=True):
            if st.session_state.voice_password:
                st.session_state.voice_password = st.session_state.voice_password[:-1]
                st.rerun()

    with col_pass3:
        if st.button("🗑️ Clear Password", key="pass_clear", use_container_width=True):
            st.session_state.voice_password = ""
            st.rerun()

    # Display password (masked)
    pass_display = "*" * len(st.session_state.voice_password) if st.session_state.voice_password else "(empty)"
    st.markdown(f"**🔑 Password:** `{pass_display}` ({len(st.session_state.voice_password)} chars)")

    # Manual input for testing
    manual_pass_char = st.text_input("Type one character (for testing):", max_chars=1, key="manual_pass_voice", type="password", label_visibility="collapsed")
    if manual_pass_char:
        st.session_state.voice_password += manual_pass_char
        st.rerun()

    st.markdown("---")

    # Login button
    if st.button("✅ Login with Voice", key="voice_login_submit", use_container_width=True, type="primary"):
        if not st.session_state.voice_email or not st.session_state.voice_password:
            st.error("Please enter both email and password using voice")
        else:
            st.session_state.user_name = st.session_state.voice_email.split("@")[0].title()
            st.session_state.voice_login_step = "welcome"
            st.success(f"✅ Login successful! Welcome {st.session_state.user_name}!")
            st.balloons()
            time.sleep(1)
            st.rerun()


def render_welcome():
    """Render welcome screen showing login details and access level."""
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"### 👋 Welcome, {st.session_state.user_name}!")

    disability_type = st.session_state.get('disability_type', 'General User')
    disability_labels = {
        "blind": "👁️ Visual Impairment",
        "hand_disabled": "🤚 Hand Disability",
        "leg_disabled": "🦽 Mobility Impairment"
    }
    label = disability_labels.get(disability_type, disability_type)

    st.info(f"**Access Level:** {label}")
    st.success(f"**Email:** {st.session_state.voice_email}")
    st.caption(f"**Login Time:** {datetime.now().strftime('%I:%M %p')}")

    st.markdown("---")
    st.markdown("### 🚌 Select Your Route")
    st.markdown("Tell us where you're going so we can show you the bus ETA and crowd levels.")

    # Proceed to route selection
    if st.button("📍 Select Pickup & Dropoff Points", key="proceed_routes", use_container_width=True, type="primary"):
        st.session_state.voice_login_step = "routes"
        st.rerun()

    if st.button("🔙 Back to Login", key="back_to_login"):
        st.session_state.voice_email = ""
        st.session_state.voice_password = ""
        st.session_state.voice_login_step = "input"
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def render_route_selection(routes, stops):
    """Render pickup/dropoff selection and calculate ETA."""
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"### 🚌 Select Your Journey - {st.session_state.user_name}")

    # Route selection
    if routes is None or routes.empty:
        st.error("Route data not available")
        return

    route_option = st.selectbox("Select Bus Route:", routes["bus_details"].unique(), key="voice_route_select")
    route_row = routes[routes["bus_details"] == route_option].iloc[0]
    route_stop_ids = list(map(int, str(route_row["route"]).split()))

    route_stops = stops[stops["stop_id"].isin(route_stop_ids)].copy()
    route_stops["order"] = route_stops["stop_id"].apply(lambda x: route_stop_ids.index(x))
    route_stops = route_stops.sort_values("order")

    st.markdown("---")

    # Pickup point
    st.markdown("#### 🟢 Boarding Point (Where you are now)")
    from_stop = st.selectbox("Select your location:", route_stops["stop_name"].unique(), key="voice_from_stop")

    # Dropoff point
    st.markdown("#### 🔴 Destination Point (Where you want to go)")
    to_stop = st.selectbox("Select your destination:", route_stops["stop_name"].unique(), key="voice_to_stop")

    st.markdown("---")

    # Calculate ETA
    from_data = route_stops[route_stops["stop_name"] == from_stop]
    to_data = route_stops[route_stops["stop_name"] == to_stop]

    if from_data.empty or to_data.empty:
        st.error("Invalid stop selection")
    else:
        from_idx = from_data["order"].values[0]
        to_idx = to_data["order"].values[0]

        if from_idx >= to_idx:
            st.error("❌ Destination must be after boarding point")
        else:
            remaining_stops = to_idx - from_idx
            # Assume 2 minutes per stop + 1 minute initial wait
            eta_minutes = max(2, (remaining_stops * 2) + 1)

            st.markdown("### ⏱️ Estimated Time & Crowd Info")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("🚏 Stops Away", remaining_stops)

            with col2:
                arrival_time = datetime.now() + timedelta(minutes=eta_minutes)
                st.metric("⏰ Estimated Arrival", arrival_time.strftime("%I:%M %p"))

            with col3:
                st.metric("⏱️ Time Remaining", f"{eta_minutes} mins")

            st.markdown("---")

            # Crowd level simulation
            st.markdown("### 👥 Current Crowd Status")
            crowd_level = "Low"
            crowd_count = 3
            if remaining_stops > 3:
                crowd_level = "Medium"
                crowd_count = 6
            if remaining_stops > 5:
                crowd_level = "High"
                crowd_count = 9

            if crowd_level == "Low":
                st.success(f"🟢 **{crowd_level} Crowd** ({crowd_count} people detected) - Plenty of seats available!")
            elif crowd_level == "Medium":
                st.warning(f"🟡 **{crowd_level} Crowd** ({crowd_count} people detected) - Standing room available")
            else:
                st.error(f"🔴 **{crowd_level} Crowd** ({crowd_count} people detected) - Bus is quite crowded")

            st.markdown("---")

            # Confirm journey
            col_confirm, col_back = st.columns(2)
            with col_confirm:
                if st.button("✅ Confirm & Request Pickup", key="confirm_journey", use_container_width=True, type="primary"):
                    st.session_state.selected_from_stop = from_stop
                    st.session_state.selected_to_stop = to_stop
                    st.session_state.selected_route = route_option
                    st.session_state.selected_eta_minutes = eta_minutes
                    st.success(f"✅ Bus {route_option} will arrive at {arrival_time.strftime('%I:%M %p')}")
                    st.info(f"📍 Boarding at: {from_stop}")
                    st.info(f"📍 Destination: {to_stop}")
                    time.sleep(2)
                    st.rerun()

            with col_back:
                if st.button("🔙 Back to Welcome", key="back_welcome"):
                    st.session_state.voice_login_step = "welcome"
                    st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
