# -*- coding: utf-8 -*-
# ============================================================
#   DRIVER REQUEST FEATURES MODULE
#   Enhanced request management UI for driver dashboard
#   - Request cards with explicit details
#   - Action buttons (accept, complete, snooze, reject)
#   - Request filtering by priority/status
#   - Distance calculation and display
# ============================================================

import streamlit as st
import streamlit.components.v1 as components
from request_manager import get_request_manager
from firebase_manager import get_firebase_manager
from datetime import datetime


def render_request_action_buttons(request_id, request_data):
    """
    Render explicit action buttons for a single request.
    
    Actions:
    - ACCEPT: Acknowledge and accept the request
    - COMPLETE: Mark pickup as completed
    - SNOOZE: Snooze for later
    - REJECT: Decline the request
    """
    col1, col2, col3, col4 = st.columns(4)
    
    request_mgr = get_request_manager()
    
    with col1:
        if st.button(
            "✅ ACCEPT",
            key=f"accept_{request_id}",
            use_container_width=True,
            help="Accept this pickup request"
        ):
            driver_name = st.session_state.get("driver_name", "Driver")
            if request_mgr.accept_request(request_id, driver_name):
                st.success(f"✅ Request {request_id[:8]} accepted!")
                st.rerun()
            else:
                st.error("Failed to update request")
    
    with col2:
        if st.button(
            "🏁 COMPLETE",
            key=f"complete_{request_id}",
            use_container_width=True,
            help="Mark pickup as completed"
        ):
            driver_name = st.session_state.get("driver_name", "Driver")
            if request_mgr.complete_request(request_id, driver_name):
                st.success(f"✅ Request {request_id[:8]} completed!")
                st.rerun()
            else:
                st.error("Failed to complete request")
    
    with col3:
        if st.button(
            "⏱️ SNOOZE",
            key=f"snooze_{request_id}",
            use_container_width=True,
            help="Snooze request for 5 minutes"
        ):
            if request_mgr.snooze_request(request_id, minutes=5):
                st.info(f"⏱️ Request {request_id[:8]} snoozed for 5 minutes")
                st.rerun()
            else:
                st.error("Failed to snooze request")
    
    with col4:
        if st.button(
            "❌ REJECT",
            key=f"reject_{request_id}",
            use_container_width=True,
            help="Decline this request"
        ):
            driver_name = st.session_state.get("driver_name", "Driver")
            if request_mgr.reject_request(request_id, driver_name, reason="Driver unavailable"):
                st.warning(f"❌ Request {request_id[:8]} declined")
                st.rerun()
            else:
                st.error("Failed to decline request")


def render_request_card(request_data, driver_lat=None, driver_lng=None):
    """
    Render a single request as an enhanced card with all details.
    
    Displays:
    - Passenger name, contact info
    - Location, stops, disability type
    - Distance to passenger
    - Live location map
    - Action buttons
    """
    request_mgr = get_request_manager()
    request_id = request_data.get("id", "UNKNOWN")
    
    # Get formatted summary
    summary = request_mgr.get_request_summary(request_id)
    if not summary:
        st.error("Failed to load request details")
        return
    
    # Get priority color
    disability_priority = {
        "Elderly": "🔴",
        "Wheelchair User": "🟠",
        "Visual Impairment": "🟡",
        "Hearing Impairment": "🟡",
        "Mobility Issue": "🟢",
        "Other": "⚪"
    }
    
    priority_icon = disability_priority.get(summary["disability_type"], "⚪")
    
    # Calculate distance if driver location available
    distance_km = None
    if driver_lat and driver_lng:
        distance_km = request_mgr.get_request_distance(request_id, driver_lat, driver_lng)
    
    status = summary["status"]
    status_color = {
        "pending": "#ef4444",     # Red
        "acknowledged": "#f59e0b",  # Orange
        "completed": "#22c55e",     # Green
        "declined": "#6b7280",      # Gray
        "snoozed": "#3b82f6"        # Blue
    }.get(status, "#94a3b8")
    
    # Request Card Header
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(30,41,59,0.9), rgba(15,23,42,0.95));
                border-left: 6px solid {status_color};
                border-radius: 12px;
                padding: 18px;
                margin: 12px 0;
                border: 1px solid rgba(34,211,238,0.2);
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
            <div>
                <div style="color: #22d3ee; font-size: 1.3rem; font-weight: 800;">
                    {priority_icon} {summary['passenger_name']}
                </div>
                <div style="color: #94a3b8; font-size: 0.85rem; margin-top: 4px;">
                    Request ID: <code style="color: #f1f5f9;">{request_id[:12]}</code>
                </div>
            </div>
            <div style="text-align: right;">
                <div style="background: {status_color}; color: #fff; padding: 6px 12px; 
                           border-radius: 20px; font-weight: 700; font-size: 0.85rem;">
                    {status.upper()}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Details Grid
    grid1a, grid2a = st.columns(2)
    
    with grid1a:
        st.markdown(f"""
        <div style="background: rgba(30,41,59,0.6); padding: 12px; border-radius: 8px; 
                   border: 1px solid rgba(34,211,238,0.15); margin-bottom: 12px;">
            <div style="color: #94a3b8; font-size: 0.8rem; margin-bottom: 4px;">🧍 Passenger Name</div>
            <div style="color: #f1f5f9; font-size: 1rem; font-weight: 600;">
                {summary['passenger_name']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="background: rgba(30,41,59,0.6); padding: 12px; border-radius: 8px; 
                   border: 1px solid rgba(34,211,238,0.15); margin-bottom: 12px;">
            <div style="color: #94a3b8; font-size: 0.8rem; margin-bottom: 4px;">♿ Accessibility Need</div>
            <div style="color: #f1f5f9; font-size: 1rem; font-weight: 600;">
                {summary['disability_type']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="background: rgba(30,41,59,0.6); padding: 12px; border-radius: 8px; 
                   border: 1px solid rgba(34,211,238,0.15); margin-bottom: 12px;">
            <div style="color: #94a3b8; font-size: 0.8rem; margin-bottom: 4px;">📞 Contact</div>
            <div style="color: #f1f5f9; font-size: 0.95rem; font-family: monospace;">
                <div>☎️ {summary['contact']}</div>
                <div>📧 {summary['email']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with grid2a:
        st.markdown(f"""
        <div style="background: rgba(30,41,59,0.6); padding: 12px; border-radius: 8px; 
                   border: 1px solid rgba(34,211,238,0.15); margin-bottom: 12px;">
            <div style="color: #94a3b8; font-size: 0.8rem; margin-bottom: 4px;">🛫 Boarding Stop</div>
            <div style="color: #f1f5f9; font-size: 1rem; font-weight: 600;">
                {summary['boarding_stop']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="background: rgba(30,41,59,0.6); padding: 12px; border-radius: 8px; 
                   border: 1px solid rgba(34,211,238,0.15); margin-bottom: 12px;">
            <div style="color: #94a3b8; font-size: 0.8rem; margin-bottom: 4px;">🏁 Destination</div>
            <div style="color: #f1f5f9; font-size: 1rem; font-weight: 600;">
                {summary['destination_stop'] or 'Not specified'}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Distance display
        if distance_km:
            distance_color = "#22c55e" if distance_km < 5 else "#f59e0b" if distance_km < 15 else "#ef4444"
            st.markdown(f"""
            <div style="background: rgba(30,41,59,0.6); padding: 12px; border-radius: 8px; 
                       border: 1px solid rgba(34,211,238,0.15); margin-bottom: 12px;">
                <div style="color: #94a3b8; font-size: 0.8rem; margin-bottom: 4px;">📍 Distance</div>
                <div style="color: {distance_color}; font-size: 1.2rem; font-weight: 800;">
                    {distance_km:.2f} km away
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Location Map
    if summary['latitude'] and summary['longitude']:
        st.markdown("#### 🗺️ Passenger Location")
        
        map_html = f"""
        <iframe width="100%" height="300" 
                style="border-radius: 12px; border: 2px solid rgba(34,211,238,0.3);"
                src="https://maps.google.com/maps?q={summary['latitude']},{summary['longitude']}&z=17&output=embed"></iframe>
        """
        st.markdown(map_html, unsafe_allow_html=True)
        
        if summary['maps_link']:
            st.link_button(
                "🔗 Open Full Map",
                summary['maps_link'],
                use_container_width=True
            )
    
    # Action Buttons
    st.markdown("#### ⚡ Actions")
    render_request_action_buttons(request_id, request_data)


def render_requests_by_filter(filter_type="all", driver_lat=None, driver_lng=None):
    """
    Render requests filtered by different criteria.
    
    Filter types:
    - "all": All pending requests
    - "urgent": High-priority requests  
    - "priority": Sorted by priority
    - "nearby": Sorted by distance
    """
    request_mgr = get_request_manager()
    
    if filter_type == "all":
        requests = request_mgr.fetch_all_requests()
        title = "📋 All Requests"
    elif filter_type == "urgent":
        requests = request_mgr.fetch_urgent_requests()
        title = "🚨 Urgent Requests"
    elif filter_type == "priority":
        requests = request_mgr.fetch_requests_by_priority()
        title = "🏆 Requests by Priority"
    elif filter_type == "nearby":
        requests = request_mgr.fetch_all_requests()
        # Sort by distance if driver location available
        if driver_lat and driver_lng:
            requests_with_distance = []
            for req in requests:
                dist = request_mgr.get_request_distance(req.get("id"), driver_lat, driver_lng)
                requests_with_distance.append((req, dist or float('inf')))
            requests = [r[0] for r in sorted(requests_with_distance, key=lambda x: x[1])]
        title = "📍 Requests by Distance"
    else:
        requests = []
        title = "Unknown Filter"
    
    st.markdown(f"### {title}")
    
    if not requests:
        st.info("ℹ️ No requests match this filter")
        return
    
    # Display stats
    total = len(requests)
    pending = sum(1 for r in requests if r.get("status") == "pending")
    acknowledged = sum(1 for r in requests if r.get("status") == "acknowledged")
    completed = sum(1 for r in requests if r.get("status") == "completed")
    
    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
    with stat_col1:
        st.metric("Total", total)
    with stat_col2:
        st.metric("Pending", pending, delta="🔴" if pending > 0 else None)
    with stat_col3:
        st.metric("Acknowledged", acknowledged)
    with stat_col4:
        st.metric("Completed", completed)
    
    # Render each request
    for i, request in enumerate(requests):
        st.divider()
        render_request_card(request, driver_lat, driver_lng)


def render_driver_request_panel():
    """
    Main panel for driver to view and manage all requests.
    Accessible from the driver dashboard.
    """
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(34,211,238,0.15), rgba(59,130,246,0.1));
                border: 2px solid rgba(34,211,238,0.3);
                border-radius: 16px;
                padding: 20px;
                margin: 20px 0;">
        <div style="color: #22d3ee; font-size: 1.8rem; font-weight: 800; margin-bottom: 8px;">
            🚍 Driver Request Management Panel
        </div>
        <div style="color: #94a3b8; font-size: 0.95rem;">
            View, filter, and manage all pickup requests with explicit actions
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize driver location session state if needed (NO DEFAULTS - driver must provide location)
    if "driver_lat" not in st.session_state:
        st.session_state.driver_lat = None
    if "driver_lng" not in st.session_state:
        st.session_state.driver_lng = None
    
    # Filter Tabs
    view_tab, stats_tab, history_tab = st.tabs(["📋 View Requests", "📊 Statistics", "📜 History"])
    
    with view_tab:
        st.markdown("#### Filter by:")
        
        filter_cols = st.columns(4)
        with filter_cols[0]:
            if st.button("📋 All Requests", use_container_width=True, key="filter_all"):
                st.session_state.request_filter = "all"
        with filter_cols[1]:
            if st.button("🚨 Urgent Only", use_container_width=True, key="filter_urgent"):
                st.session_state.request_filter = "urgent"
        with filter_cols[2]:
            if st.button("🏆 By Priority", use_container_width=True, key="filter_priority"):
                st.session_state.request_filter = "priority"
        with filter_cols[3]:
            if st.button("📍 By Distance", use_container_width=True, key="filter_distance"):
                st.session_state.request_filter = "nearby"
        
        # Get current filter
        current_filter = st.session_state.get("request_filter", "all")
        
        # Render filtered requests
        render_requests_by_filter(
            current_filter,
            st.session_state.driver_lat,
            st.session_state.driver_lng
        )
    
    with stats_tab:
        st.markdown("#### 📊 Request Statistics")
        
        request_mgr = get_request_manager()
        stats = request_mgr.get_request_stats()
        
        # Stats grid
        sg1, sg2, sg3, sg4 = st.columns(4)
        with sg1:
            st.metric("📊 Total Requests", stats["total"])
        with sg2:
            st.metric("🔴 Pending", stats["pending"])
        with sg3:
            st.metric("✅ Acknowledged", stats["acknowledged"])
        with sg4:
            st.metric("🏁 Completed", stats["completed"])
        
        st.divider()
        
        # By disability type
        st.markdown("#### By Accessibility Need:")
        disability_stats = stats.get("by_disability", {})
        
        if disability_stats:
            for disability, count in sorted(disability_stats.items(), key=lambda x: x[1], reverse=True):
                st.write(f"**{disability}**: {count}")
        else:
            st.info("No requests yet")
    
    with history_tab:
        st.markdown("#### 📜 Activity Log")
        st.info("📝 Activity tracking coming soon!")
