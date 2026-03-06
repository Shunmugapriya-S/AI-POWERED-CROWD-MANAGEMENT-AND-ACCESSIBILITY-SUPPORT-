# -*- coding: utf-8 -*-
# ============================================================
#   ADMIN PORTAL MODULE
#   Features:
#     - Live operational stats (buses, requests, system health)
#     - View all pickup requests (pending + completed)
#     - Approve / Reject with admin notes
# ============================================================

import streamlit as st
from firebase_manager import get_firebase_manager


def render_admin():
    """Render Admin System Management page."""

    # ---- Header ----
    st.markdown("""
    <div style='text-align:center; margin-bottom:10px;'>
        <h2 style='color:#22d3ee;'>🛠️ Admin Control Panel</h2>
        <p style='opacity:0.7;'>Monitor and manage the entire smart bus system</p>
    </div>
    """, unsafe_allow_html=True)

    # ---- Live Stats ----
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 📊 Live Operational Stats")
    c1, c2, c3 = st.columns(3)
    c1.metric("🚌 Active Buses", "42")
    c2.metric("🙋 Assistance Requests", "12", delta="+3")
    c3.metric("💚 System Health", "98%")
    st.markdown("</div>", unsafe_allow_html=True)

    fb = get_firebase_manager()

    # ---- Offline Warning ----
    if not fb.initialized:
        st.warning("⚠️ Firebase not connected. Running in offline mode.")
        return

    # ---- All Pickup Requests ----
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 📋 All Pickup Requests")

    # Filter options
    filter_col1, filter_col2 = st.columns([1, 2])
    with filter_col1:
        status_filter = st.selectbox(
            "Filter by Status:",
            ["All", "Pending", "Acknowledged", "Approved", "Rejected", "Completed"],
            key="admin_status_filter"
        )

    all_requests = fb.get_all_requests()

    if status_filter != "All":
        all_requests = [r for r in all_requests if r.get("status", "").lower() == status_filter.lower()]

    if all_requests:
        for req in all_requests:
            req_id = req.get("id", "")
            user_name = req.get("user_name", "User")
            location = req.get("location", "Unknown")
            route = req.get("route", "N/A")
            disability = req.get("disability_type", "N/A")
            status = req.get("status", "pending")

            # Status emoji
            emoji_map = {
                "pending": "⏳",
                "acknowledged": "👁️",
                "approved": "✅",
                "rejected": "❌",
                "completed": "🏁"
            }
            emoji = emoji_map.get(status.lower(), "❓")

            with st.expander(f"{emoji} {user_name}  |  📍 {location}  |  Status: {status.title()}"):
                col_detail, col_action = st.columns([2, 1])

                with col_detail:
                    st.write(f"**🚌 Route:** {route}")
                    st.write(f"**♿ Disability Type:** {disability}")
                    st.write(f"**📌 Current Status:** {status.title()}")
                    if req.get("admin_note"):
                        st.info(f"📝 Admin Note: {req['admin_note']}")

                with col_action:
                    note = st.text_input("📝 Admin Note:", key=f"note_{req_id}", placeholder="Optional note...")

                    col_a, col_r = st.columns(2)
                    with col_a:
                        if st.button("✅ Approve", key=f"approve_{req_id}", use_container_width=True):
                            fb.update_request_status(req_id, "approved", admin_note=note)
                            st.success("Approved!")
                            st.rerun()
                    with col_r:
                        if st.button("❌ Reject", key=f"reject_{req_id}", use_container_width=True):
                            fb.update_request_status(req_id, "rejected", admin_note=note)
                            st.warning("Rejected!")
                            st.rerun()
    else:
        st.info(f"No requests found for filter: **{status_filter}**")

    st.markdown("</div>", unsafe_allow_html=True)

    # ---- Refresh ----
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    if st.button("🔄 Refresh Dashboard", key="admin_refresh", use_container_width=True):
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # ---- Switch Role ----
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 🔄 Switch Portal")
    st.caption("Switch to a different portal without logging out.")

    sr_cols = st.columns(4)
    portal_map = [
        ("🧍 Passenger", "passenger"),
        ("🚌 Driver",    "driver"),
        ("🛠 Admin",     "admin"),
        ("♿ Disabled",  "disabled"),
    ]
    for col, (label, role) in zip(sr_cols, portal_map):
        with col:
            if st.button(label, key=f"adm_switch_{role}", use_container_width=True,
                         disabled=(st.session_state.get("role") == role)):
                st.session_state.role = role
                st.session_state.selected_portal = role
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
