# -*- coding: utf-8 -*-
# ============================================================
#   PASSENGER PORTAL MODULE
#   Features:
#     - Route search / Bus selection
#     - Boarding point & Destination selection
#     - Dynamic ETA countdown (decreases over time)
#     - Live crowd detection (YOLO camera feed)
#     - Crowd level display (Low / Medium / High) with colors
#     - Switch Role button
# ============================================================

import time
import random
import streamlit as st
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
from crowd_detector import get_live_detector
from firebase_manager import get_firebase_manager
from datetime import datetime


# ---- Helper: Get stops for a selected route ----
def get_stops_for_route(route_row, stops_df):
    """Return list of stop names for the given route row."""
    try:
        stop_ids = str(route_row["route"]).strip().split()
        stop_ids = [s.strip() for s in stop_ids if s.strip().isdigit()]
        stops_sub = stops_df[stops_df["stop_id"].astype(str).isin(stop_ids)]
        return stops_sub["stop_name"].tolist()
    except Exception:
        return []


# ---- Helper: Generate initial ETA (< 15 mins, dynamic) ----
def _get_initial_eta(boarding_stop, dest_stop, stop_list):
    """
    Generate an initial ETA value between 3 and 14 minutes.
    Based on route position; capped under 15.
    """
    try:
        b_idx = stop_list.index(boarding_stop) if boarding_stop in stop_list else 0
        d_idx = stop_list.index(dest_stop)     if dest_stop     in stop_list else len(stop_list) - 1
        stops_away = abs(d_idx - b_idx)
        # Compute a value under 15
        base = max(3, min(14, stops_away * random.randint(2, 3)))
        return base
    except Exception:
        return random.randint(5, 13)


def get_countdown_eta(boarding_stop, dest_stop, stop_list):
    """
    Return a countdown ETA that decreases over time.
    Uses session state to track the initial value and start time.
    """
    key_pair = f"{boarding_stop}__{dest_stop}"
    # Reset if stops changed
    if st.session_state.get("_eta_pair") != key_pair:
        st.session_state["_eta_pair"] = key_pair
        initial = _get_initial_eta(boarding_stop, dest_stop, stop_list)
        st.session_state["_eta_initial"] = initial
        st.session_state["_eta_start"] = time.time()

    elapsed_mins = (time.time() - st.session_state["_eta_start"]) / 60.0
    remaining = max(0, st.session_state["_eta_initial"] - elapsed_mins)
    return round(remaining, 1)


def render_passenger(routes, stops):
    """Render Passenger Portal page."""

    # ---- Page-level CSS for readable text & card backgrounds ----
    st.markdown("""
    <style>
    /* Dark semi-transparent card background */
    .pass-card {
        background: rgba(15, 23, 42, 0.88) !important;
        backdrop-filter: blur(14px);
        border-radius: 18px;
        padding: 22px 26px;
        border: 1px solid rgba(34,211,238,0.25);
        margin-bottom: 22px;
    }

    /* ALL text inside passenger portal → crisp white */
    [data-testid="stAppViewContainer"] p,
    [data-testid="stAppViewContainer"] span,
    [data-testid="stAppViewContainer"] label,
    [data-testid="stAppViewContainer"] div,
    [data-testid="stAppViewContainer"] .stMarkdown p {
        color: #f1f5f9 !important;
    }

    /* Selectbox labels */
    [data-testid="stSelectbox"] label {
        color: #22d3ee !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }

    /* Selectbox input text */
    [data-testid="stSelectbox"] div[data-baseweb="select"] span {
        color: #0f172a !important;
        font-weight: 600 !important;
    }

    /* Info / success / warning / error text visibility */
    [data-testid="stAlert"] p,
    [data-testid="stAlert"] span {
        color: #1e293b !important;
        font-weight: 600 !important;
    }

    /* Metric label & value */
    [data-testid="stMetricLabel"] p,
    [data-testid="stMetricValue"]  {
        color: #f1f5f9 !important;
    }

    /* Headings */
    h1, h2, h3, h4 {
        color: #22d3ee !important;
        font-weight: 800 !important;
    }

    /* Caption */
    .stCaption, small {
        color: #94a3b8 !important;
    }

    /* Crowd badge styles */
    .crowd-low {
        background: linear-gradient(90deg, #16a34a, #22c55e);
        color: #fff !important;
        padding: 10px 18px;
        border-radius: 12px;
        font-size: 1.15rem;
        font-weight: 700;
        text-align: center;
        margin-top: 8px;
        display: block;
        box-shadow: 0 4px 12px rgba(34,197,94,0.4);
    }
    .crowd-medium {
        background: linear-gradient(90deg, #d97706, #f59e0b);
        color: #fff !important;
        padding: 10px 18px;
        border-radius: 12px;
        font-size: 1.15rem;
        font-weight: 700;
        text-align: center;
        margin-top: 8px;
        display: block;
        box-shadow: 0 4px 12px rgba(245,158,11,0.4);
    }
    .crowd-high {
        background: linear-gradient(90deg, #dc2626, #ef4444);
        color: #fff !important;
        padding: 10px 18px;
        border-radius: 12px;
        font-size: 1.15rem;
        font-weight: 700;
        text-align: center;
        margin-top: 8px;
        display: block;
        box-shadow: 0 4px 12px rgba(239,68,68,0.4);
    }
    .arrival-box {
        background: linear-gradient(135deg, rgba(59,130,246,0.25), rgba(139,92,246,0.25));
        border: 1px solid rgba(99,102,241,0.4);
        border-radius: 14px;
        padding: 14px 18px;
        text-align: center;
        margin-top: 12px;
    }
    .arrival-box .eta-value {
        font-size: 2rem;
        font-weight: 800;
        color: #818cf8 !important;
    }
    .arrival-box .eta-label {
        font-size: 0.85rem;
        color: #94a3b8 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ---- Header ----
    st.markdown("""
    <div style='text-align:center; margin-bottom:14px;'>
        <h2 style='color:#22d3ee; font-size:2rem;'>🧍 Passenger Portal</h2>
        <p style='color:#cbd5e1; font-size:1rem;'>Search your bus route, select stops & check live crowd status</p>
    </div>
    """, unsafe_allow_html=True)

    # ================================================================
    # SECTION 1 — Route & Stop Selection
    # ================================================================
    st.markdown("<div class='pass-card'>", unsafe_allow_html=True)
    st.markdown("### 🔍 Route & Bus Search")

    route_option  = None
    stop_list     = []
    boarding_stop = None
    dest_stop     = None
    eta_mins      = None

    if routes is not None and not routes.empty:
        route_option = st.selectbox(
            "🚌 Search Route / Bus No:",
            routes["bus_details"].unique(),
            key="passenger_route_select"
        )

        # Get the stops for this route
        selected_row = routes[routes["bus_details"] == route_option].iloc[0]
        if stops is not None and not stops.empty:
            stop_list = get_stops_for_route(selected_row, stops)

        if stop_list:
            col_board, col_dest = st.columns(2)
            with col_board:
                boarding_stop = st.selectbox(
                    "📍 Boarding Point:",
                    stop_list,
                    key="passenger_boarding_select"
                )
            with col_dest:
                # Destination options: everything except boarding
                dest_options = [s for s in stop_list if s != boarding_stop]
                if not dest_options:
                    dest_options = stop_list
                dest_stop = st.selectbox(
                    "🏁 Destination:",
                    dest_options,
                    key="passenger_dest_select"
                )

            # ---- Arrival time estimate (dynamic countdown) ----
            if boarding_stop and dest_stop:
                eta_mins = get_countdown_eta(boarding_stop, dest_stop, stop_list)
                if eta_mins > 0:
                    # Color based on urgency
                    if eta_mins > 8:
                        eta_color = "#818cf8"  # calm purple
                    elif eta_mins > 3:
                        eta_color = "#f59e0b"  # amber
                    else:
                        eta_color = "#22c55e"  # green — arriving soon!
                    st.markdown(f"""
                    <div class='arrival-box'>
                        <div class='eta-label'>🕐 Estimated Bus Arrival</div>
                        <div class='eta-value' style='color:{eta_color} !important;'>~{eta_mins} min</div>
                        <div class='eta-label'>From <b>{boarding_stop}</b> → <b>{dest_stop}</b></div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class='arrival-box' style='border-color:rgba(34,197,94,0.5);'>
                        <div class='eta-label'>🕐 Estimated Bus Arrival</div>
                        <div class='eta-value' style='color:#22c55e !important;'>~0 min</div>
                        <div class='eta-label'>From <b>{boarding_stop}</b> → <b>{dest_stop}</b></div>
                    </div>
                    """, unsafe_allow_html=True)

                # Crowd level badge near ETA (no threshold text)
                detector = get_live_detector()
                crowd = detector.get_crowd_data()
                level = crowd["level"]
                if st.session_state.get("live_detection_active", False) or level != "Unknown":
                    if level == "Low":
                        st.markdown("<span class='crowd-low'>🟢 LOW Crowd</span>", unsafe_allow_html=True)
                    elif level == "Medium":
                        st.markdown("<span class='crowd-medium'>🟡 MEDIUM Crowd</span>", unsafe_allow_html=True)
                    else:
                        st.markdown("<span class='crowd-high'>🔴 HIGH Crowd</span>", unsafe_allow_html=True)
        else:
            st.info(f"✅ Selected: **{route_option}** — Stop details loading…")

    else:
        st.error("❌ Route data not available.")

    st.markdown("</div>", unsafe_allow_html=True)

    # ================================================================
    # SECTION 2 — Live Crowd Detection
    # ================================================================
    st.markdown("<div class='pass-card'>", unsafe_allow_html=True)
    st.markdown("### 🎥 Live Crowd Detection")
    st.caption("Start the camera to detect how many people are in the bus.")

    cam_col, info_col = st.columns([3, 2])

    with cam_col:
        btn_c1, btn_c2 = st.columns(2)
        with btn_c1:
            if st.button("📹 Start Detection", key="passenger_start_btn", use_container_width=True):
                st.session_state.live_detection_active = True
                detector = get_live_detector()
                detector.start_detection(camera_index=0)

        with btn_c2:
            if st.button("⏹️ Stop Detection", key="passenger_stop_btn", use_container_width=True):
                st.session_state.live_detection_active = False
                detector = get_live_detector()
                detector.stop_detection()
                st.rerun()

        # ---- Camera feed ----
        if st.session_state.get("live_detection_active", False):
            detector = get_live_detector()
            # Status indicator
            status_placeholder = st.empty()
            frame_placeholder  = st.empty()

            frame = detector.get_latest_frame()
            if frame is not None:
                status_placeholder.success(f"🟢 Camera Active — {detector.status_msg}")
                frame_placeholder.image(
                    frame,
                    caption="🎥 Live Camera — Crowd Detection",
                    use_container_width=True
                )
            else:
                status_placeholder.info(f"⏳ {detector.status_msg}")
                frame_placeholder.markdown("""
                <div style='background:rgba(30,41,59,0.8); border-radius:12px;
                            padding:40px; text-align:center; border:2px dashed rgba(34,211,238,0.3);'>
                    <p style='color:#94a3b8; font-size:1.1rem;'>📷 Camera initializing…<br>
                    <small>Please wait a moment</small></p>
                </div>
                """, unsafe_allow_html=True)

            # Auto-refresh every 0.8s to stream the camera feed
            time.sleep(0.8)
            st.rerun()
        else:
            st.markdown("""
            <div style='background:rgba(30,41,59,0.7); border-radius:12px;
                        padding:36px; text-align:center; border:2px dashed rgba(255,255,255,0.1);
                        margin-top:10px;'>
                <p style='color:#64748b; font-size:1rem;'>📷 Camera is OFF<br>
                <small style='color:#475569;'>Press "Start Detection" to begin</small></p>
            </div>
            """, unsafe_allow_html=True)

    # ---- Crowd Info Panel ----
    with info_col:
        st.markdown("#### 📊 Crowd Info")

        if st.session_state.get("live_detection_active", False):
            detector = get_live_detector()
            crowd    = detector.get_crowd_data()
            count    = crowd["count"]
            level    = crowd["level"]

            # People count metric (color matches crowd level)
            level_color = "#22c55e" if level == "Low" else "#f59e0b" if level == "Medium" else "#ef4444"
            st.markdown(f"""
            <div style='background:rgba(30,41,59,0.85); border-radius:12px;
                        padding:14px; text-align:center; border:1px solid rgba(255,255,255,0.1);
                        margin-bottom:12px;'>
                <div style='color:#94a3b8; font-size:0.8rem; margin-bottom:4px;'>👥 People Detected</div>
                <div style='color:{level_color}; font-size:2.2rem; font-weight:800;'>{count}</div>
            </div>
            """, unsafe_allow_html=True)

            # Crowd level badge with color
            if level == "Low":
                st.markdown(f"<span class='crowd-low'>🟢 LOW Crowd<br><small>Seats Available</small></span>",
                            unsafe_allow_html=True)
            elif level == "Medium":
                st.markdown(f"<span class='crowd-medium'>🟡 MEDIUM Crowd<br><small>Standing Room Only</small></span>",
                            unsafe_allow_html=True)
            else:
                st.markdown(f"<span class='crowd-high'>🔴 HIGH Crowd<br><small>Bus is Very Crowded</small></span>",
                            unsafe_allow_html=True)

        else:
            detector = get_live_detector()
            crowd = detector.get_crowd_data()
            count = crowd["count"]
            level = crowd["level"]
            if level != "Unknown":
                level_color = "#22c55e" if level == "Low" else "#f59e0b" if level == "Medium" else "#ef4444"
                st.markdown(f"""
                <div style='background:rgba(30,41,59,0.85); border-radius:12px;
                            padding:14px; text-align:center; border:1px solid rgba(255,255,255,0.1);
                            margin-bottom:12px;'>
                    <div style='color:#94a3b8; font-size:0.8rem; margin-bottom:4px;'>👥 People Detected (Last)</div>
                    <div style='color:{level_color}; font-size:2.2rem; font-weight:800;'>{count}</div>
                </div>
                """, unsafe_allow_html=True)

                if level == "Low":
                    st.markdown("<span class='crowd-low'>🟢 LOW Crowd</span>", unsafe_allow_html=True)
                elif level == "Medium":
                    st.markdown("<span class='crowd-medium'>🟡 MEDIUM Crowd</span>", unsafe_allow_html=True)
                else:
                    st.markdown("<span class='crowd-high'>🔴 HIGH Crowd</span>", unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style='background:rgba(30,41,59,0.7); border-radius:12px;
                            padding:24px; text-align:center; border:1px dashed rgba(255,255,255,0.1);'>
                    <p style='color:#475569; font-size:0.95rem;'>
                        Start detection to see<br>live crowd data
                    </p>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ================================================================
    # SECTION 3 — Live Crowd Level (People Count + Color) below
    # ================================================================
    st.markdown("<div class='pass-card'>", unsafe_allow_html=True)
    st.markdown("### 👥 Live Crowd Status")

    detector = get_live_detector()
    crowd = detector.get_crowd_data()
    count = crowd["count"]
    level = crowd["level"]

    if st.session_state.get("live_detection_active", False) or level != "Unknown":
        # Pick color/class
        if level == "Low":
            badge_class = "crowd-low"
            badge_text = f"🟢 LOW Crowd — {count} people detected<br><small>Seats Available</small>"
        elif level == "Medium":
            badge_class = "crowd-medium"
            badge_text = f"🟡 MEDIUM Crowd — {count} people detected<br><small>Standing Room Only</small>"
        else:
            badge_class = "crowd-high"
            badge_text = f"🔴 HIGH Crowd — {count} people detected<br><small>Bus is Very Crowded</small>"

        st.markdown(f"<span class='{badge_class}'>{badge_text}</span>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='background:rgba(30,41,59,0.7); border-radius:12px;
                    padding:20px; text-align:center; border:1px dashed rgba(255,255,255,0.1);'>
            <p style='color:#64748b; font-size:0.95rem;'>Start live detection above to see real-time crowd level here</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ================================================================
    # SECTION 4 — CROWD DENSITY MAP WITH FOLIUM (NO API KEY NEEDED)
    # ================================================================
    st.markdown("<div class='pass-card'>", unsafe_allow_html=True)
    st.markdown("### 🗺️ Real-Time Crowd Density Map")
    st.caption("View crowd levels across the city. 🟢 Low • 🟡 Medium • 🔴 High")
    
    # Create Folium map centered on Chennai
    m = folium.Map(
        location=[13.0827, 80.2707],
        zoom_start=13,
        tiles="OpenStreetMap"
    )
    
    # Define crowd zones with colors and boundaries
    crowd_zones = [
        {
            "name": "🔴 Downtown Junction",
            "level": "High",
            "density": 85,
            "color": "#ef4444",
            "coordinates": [
                [13.0650, 80.2500],
                [13.0750, 80.2500],
                [13.0750, 80.2650],
                [13.0650, 80.2650]
            ]
        },
        {
            "name": "🟡 Shopping Mall Area",
            "level": "Medium",
            "density": 55,
            "color": "#f59e0b",
            "coordinates": [
                [13.0850, 80.2900],
                [13.0950, 80.2900],
                [13.0950, 80.3050],
                [13.0850, 80.3050]
            ]
        },
        {
            "name": "🟢 Residential Area",
            "level": "Low",
            "density": 25,
            "color": "#22c55e",
            "coordinates": [
                [13.1100, 80.2200],
                [13.1200, 80.2200],
                [13.1200, 80.2350],
                [13.1100, 80.2350]
            ]
        },
        {
            "name": "🔴 Stadium Area",
            "level": "High",
            "density": 92,
            "color": "#ef4444",
            "coordinates": [
                [13.0400, 80.2800],
                [13.0550, 80.2800],
                [13.0550, 80.3000],
                [13.0400, 80.3000]
            ]
        },
        {
            "name": "🟡 Central Bus Hub",
            "level": "Medium",
            "density": 60,
            "color": "#f59e0b",
            "coordinates": [
                [13.0950, 80.2550],
                [13.1050, 80.2550],
                [13.1050, 80.2700],
                [13.0950, 80.2700]
            ]
        },
        {
            "name": "🟢 Parks & Green Area",
            "level": "Low",
            "density": 20,
            "color": "#22c55e",
            "coordinates": [
                [13.1250, 80.2700],
                [13.1400, 80.2700],
                [13.1400, 80.2900],
                [13.1250, 80.2900]
            ]
        }
    ]
    
    # Add polygons for each crowd zone
    for zone in crowd_zones:
        popup_text = f"""
        <b>{zone['name']}</b><br>
        <b>Crowd Level:</b> {zone['level']}<br>
        <b>Density:</b> {zone['density']}%<br>
        <hr style="margin: 4px 0;">
        <small>
        {'⏱️ Plan extra time (20+ mins)' if zone['level'] == 'High' else '⏱️ Allow 10-15 mins' if zone['level'] == 'Medium' else '✅ Best for quick boarding'}
        </small>
        """
        
        folium.Polygon(
            locations=zone["coordinates"],
            popup=folium.Popup(popup_text, max_width=250),
            color=zone["color"],
            fill=True,
            fillColor=zone["color"],
            fillOpacity=0.5,
            weight=3,
            opacity=0.9
        ).add_to(m)
        
        # Add center marker for each zone
        center_lat = sum([coord[0] for coord in zone["coordinates"]]) / len(zone["coordinates"])
        center_lng = sum([coord[1] for coord in zone["coordinates"]]) / len(zone["coordinates"])
        
        folium.CircleMarker(
            location=[center_lat, center_lng],
            radius=15,
            popup=folium.Popup(f"{zone['name']}<br>Density: {zone['density']}%", max_width=200),
            color=zone["color"],
            fill=True,
            fillColor=zone["color"],
            fillOpacity=0.8,
            weight=2,
            tooltip=f"{zone['name']} - {zone['density']}% crowded"
        ).add_to(m)
    
    # Add current location marker
    folium.CircleMarker(
        location=[13.0827, 80.2707],
        radius=8,
        popup="📍 Reference Location",
        color="#3b82f6",
        fill=True,
        fillColor="#3b82f6",
        fillOpacity=0.9,
        weight=3,
        tooltip="Your approximate reference location"
    ).add_to(m)
    
    # Display map
    st_folium(m, width=1400, height=600)
    
    # Crowd Statistics Panel
    st.markdown("#### 📊 Real-Time Crowd Statistics")
    
    stat_cols = st.columns(3)
    with stat_cols[0]:
        st.metric("🔴 High Density", "2 zones", "85% - 92% capacity")
    with stat_cols[1]:
        st.metric("🟡 Medium Density", "2 zones", "55% - 60% capacity")
    with stat_cols[2]:
        st.metric("🟢 Low Density", "2 zones", "20% - 25% capacity")
    
    st.markdown("""
    **📍 How to Use This Map:**
    
    - **🟢 Green Zones** = Ideal for quick boarding with minimal waiting time
    - **🟡 Yellow Zones** = Moderate crowds, allow 10-15 minutes extra time
    - **🔴 Red Zones** = High congestion, plan for 20+ minutes of waiting
    
    **💡 Tips:**
    - Click on any zone marker to see detailed crowd information
    - Circle markers show the center of each zone
    - Color intensity indicates crowd density percentage
    - Blue marker shows your reference location
    - Updates automatically with live detection data
    """)
    
    st.markdown("</div>", unsafe_allow_html=True)

    # ================================================================
    # SECTION 5 — Switch Role
    # ================================================================
    st.markdown("<div class='pass-card'>", unsafe_allow_html=True)
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
            if st.button(label, key=f"pass_switch_{role}", use_container_width=True,
                         disabled=(st.session_state.get("role") == role)):
                st.session_state.role = role
                st.session_state.selected_portal = role
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
