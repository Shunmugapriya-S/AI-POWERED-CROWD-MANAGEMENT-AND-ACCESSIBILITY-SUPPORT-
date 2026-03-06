# -*- coding: utf-8 -*-
# ============================================================
#   TN SMART BUS — MAIN APP (app.py)
#
#   This file only handles:
#     1. Streamlit page config & CSS
#     2. Session state initialization
#     3. Data loading (routes + stops CSV)
#     4. Login page
#     5. Navigation to the correct portal
#
#   All portal logic lives in separate modules:
#     - passenger_page.py   → Passenger Portal
#     - driver_page.py      → Driver Dashboard
#     - admin_page.py       → Admin Control Panel
#     - disabled_page.py    → Disabled / Accessibility Portal
#     - firebase_manager.py → Firebase Integration
#     - crowd_detector.py   → YOLO Crowd Detection
# ============================================================

import os
os.environ["TORCH_LOAD_WEIGHTS_ONLY"] = "0"

import base64
import time
import pandas as pd
import streamlit as st

# ---- Import Each Portal Module ----
from passenger_page import render_passenger
from driver_page    import render_driver
from admin_page     import render_admin
from disabled_page  import render_disabled


# ============================================================
# CSS & STYLING
# ============================================================

def _get_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def apply_css():
    """Inject global CSS for the whole app."""
    try:
        bg = _get_base64("background.png")
        bg_style = f"""
        background-image: linear-gradient(rgba(15,23,42,0.65), rgba(30,41,59,0.65)),
                          url(data:image/png;base64,{bg});
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        """
    except Exception:
        bg_style = "background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);"

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

    html, body, [data-testid="stAppViewContainer"] {{
        font-family: 'Outfit', sans-serif;
        {bg_style}
        color: #f8fafc;
    }}

    /* Buttons */
    .stButton>button {{
        width: 100%;
        border-radius: 12px;
        height: 3em;
        background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%);
        color: #fff !important;
        font-weight: 600;
        font-size: 1rem;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }}
    .stButton>button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(59,130,246,0.4);
        background: linear-gradient(90deg, #60a5fa 0%, #3b82f6 100%);
    }}

    /* Cards */
    .card {{
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 20px;
    }}

    /* Headings */
    h1, h2, h3 {{
        color: #22d3ee !important;
        font-weight: 800 !important;
        text-shadow: 0 0 20px rgba(34,211,238,0.3);
    }}

    /* General text - bright & readable */
    p, span, div,
    .stMarkdown p, .stMarkdown span {{
        color: #f1f5f9 !important;
    }}

    /* Input labels */
    [data-testid="stTextInput"] label,
    [data-testid="stSelectbox"] label {{
        color: #22d3ee !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }}

    /* Selectbox selected value text */
    [data-testid="stSelectbox"] div[data-baseweb="select"] span,
    [data-testid="stSelectbox"] div[data-baseweb="select"] div {{
        color: #0f172a !important;
        font-weight: 600 !important;
    }}

    /* Dropdown popup list — ALL option text must be dark */
    [data-baseweb="popover"] li,
    [data-baseweb="popover"] li span,
    [data-baseweb="popover"] li div,
    [data-baseweb="menu"] li,
    [data-baseweb="menu"] li span,
    [data-baseweb="menu"] li div,
    [role="listbox"] li,
    [role="listbox"] li span,
    [role="option"] span,
    [role="option"] div,
    ul[data-baseweb="menu"] li span {{
        color: #0f172a !important;
        font-weight: 600 !important;
    }}

    /* Dropdown popup background white */
    [data-baseweb="popover"],
    [data-baseweb="menu"] {{
        background: #ffffff !important;
    }}

    /* Hovered option in dropdown */
    [data-baseweb="menu"] li:hover,
    [role="option"]:hover {{
        background: #e0f2fe !important;
    }}
    [data-baseweb="menu"] li:hover span,
    [role="option"]:hover span {{
        color: #0369a1 !important;
    }}

    /* Text inputs readable */
    [data-testid="stTextInput"] input {{
        color: #0f172a !important;
        background: #f8fafc !important;
        font-weight: 500 !important;
    }}

    /* Login card semi-transparent dark background */
    .card {{
        background: rgba(15, 23, 42, 0.88) !important;
        backdrop-filter: blur(16px);
        border: 1px solid rgba(34,211,238,0.2) !important;
    }}

    /* Info / success / warning / error box text */
    [data-testid="stAlert"] p,
    [data-testid="stAlert"] span {{
        color: #1e293b !important;
        font-weight: 600 !important;
    }}
    </style>
    """, unsafe_allow_html=True)


# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data
def load_data():
    """Load route and stop CSV data."""
    try:
        routes = pd.read_csv("routedata1.csv")
        stops  = pd.read_csv("stopdata.csv")
        routes.columns = routes.columns.str.strip()
        stops.columns  = stops.columns.str.strip()

        # Normalize stop column names
        stop_id_col   = next((c for c in stops.columns if 'id'   in c.lower()), stops.columns[0])
        stop_name_col = next((c for c in stops.columns if 'name' in c.lower()), stops.columns[1])
        stops = stops.rename(columns={stop_id_col: "stop_id", stop_name_col: "stop_name"})

        return routes, stops
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None


# ============================================================
# SESSION STATE DEFAULTS
# ============================================================

def init_session_state():
    """Set default values for all session state keys."""
    defaults = {
        "logged_in":               False,
        "role":                    None,
        "selected_portal":         None,
        "user_email":              "",
        "user_phone":              "",
        "live_detection_active":   False,
        "bus_tracking_active":     False,
        "bus_current_stop":        0,
        "bus_last_update":         time.time(),
        "detected_crowd_count":    0,
        "detected_crowd_level":    "Unknown",
        "ai_assistant_active":     False,
        "ai_messages":             [],
        "show_ai_help":            False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


# ============================================================
# LOGIN PAGE
# ============================================================

def render_login():
    """Central login page (common for all portals)."""

    st.markdown("""
    <div style='text-align:center; padding: 20px 0 10px;'>
        <h1>🚌 TAMIL NADU SMART BUS</h1>
        <p style='font-size:1.2em; opacity:0.75;'>
            Inclusive &amp; Automated Public Transport Solution
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Login card (centered)
    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 🔐 Central Login Dashboard")
        st.markdown("---")

        # Portal selector
        portal_options = {
            "🧍 Passenger": "passenger",
            "♿ Disabled":  "disabled",
            "🚌 Driver":    "driver",
            "🛠 Admin":     "admin",
        }
        selected_label  = st.selectbox("Select Portal:", list(portal_options.keys()), key="login_portal_select")
        selected_portal = portal_options[selected_label]

        st.markdown("---")

        if selected_portal == "disabled":
            st.info("✅ Disabled portal does not require login. Click below to continue.")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("➡️ Continue to Disabled Portal", key="disabled_continue_btn"):
                st.session_state.logged_in       = True
                st.session_state.role            = selected_portal
                st.session_state.selected_portal = selected_portal
                st.session_state.user_email      = "disabled_user"
                st.session_state.user_phone      = ""
                st.success("✅ Redirecting to Disabled portal...")
                time.sleep(0.6)
                st.rerun()
        else:
            # Credentials
            email    = st.text_input("📧 Email ID",      key="login_email")
            password = st.text_input("🔑 Password",      key="login_password", type="password")
            phone    = st.text_input("📱 Phone Number",   key="login_phone", max_chars=10)

            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("✅ Login", key="login_btn"):
                if not email or not password or not phone:
                    st.error("❌ Please fill in all fields.")
                elif len(phone) != 10 or not phone.isdigit():
                    st.error("❌ Enter a valid 10-digit phone number.")
                else:
                    st.session_state.logged_in      = True
                    st.session_state.role           = selected_portal
                    st.session_state.selected_portal= selected_portal
                    st.session_state.user_email     = email
                    st.session_state.user_phone     = phone
                    st.success(f"✅ Welcome! Redirecting to {selected_label} portal...")
                    time.sleep(0.8)
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# SIDEBAR (Logout + Info)
# ============================================================

def render_sidebar():
    """Render sidebar with user info and logout button."""
    if not st.session_state.logged_in:
        return

    with st.sidebar:
        st.markdown("## 🚌 TN Smart Bus")
        st.markdown("---")
        st.markdown(f"**Logged in as:**  \n`{st.session_state.user_email}`")
        st.markdown(f"**Portal:** `{st.session_state.role.title()}`")
        st.markdown("---")

        if st.button("🔓 Logout", key="sidebar_logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


# ============================================================
# MAIN NAVIGATION ROUTER
# ============================================================

def navigate(routes, stops):
    """Route to the correct portal based on session state role."""
    if not st.session_state.logged_in:
        render_login()
        return

    role = st.session_state.role

    if role == "passenger":
        render_passenger(routes, stops)

    elif role == "disabled":
        render_disabled(routes, stops)

    elif role == "driver":
        render_driver()

    elif role == "admin":
        render_admin()

    else:
        st.error("Unknown portal role. Please log in again.")
        st.session_state.logged_in = False
        st.rerun()


# ============================================================
# APP ENTRY POINT
# ============================================================

st.set_page_config(
    page_title="TN Smart Bus — Inclusive Transport",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="collapsed"
)

apply_css()
init_session_state()
routes, stops = load_data()

render_sidebar()
navigate(routes, stops)
