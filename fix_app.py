#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix corrupted app.py by replacing it with clean code."""

clean_code = """# -*- coding: utf-8 -*-
import os
os.environ["TORCH_LOAD_WEIGHTS_ONLY"] = "0"
import streamlit as st
import time
from helpers import local_css, load_data
from pages import render

# Configure Streamlit
st.set_page_config(page_title="TN Smart Bus - Inclusive Transport", layout="wide", initial_sidebar_state="collapsed")

# Apply CSS and load data
local_css()
routes, stops = load_data()

# Initialize session state
if "role" not in st.session_state:
    st.session_state.role = None
if "selected_portal" not in st.session_state:
    st.session_state.selected_portal = None
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "ai_assistant_active" not in st.session_state:
    st.session_state.ai_assistant_active = False
if "ai_messages" not in st.session_state:
    st.session_state.ai_messages = []
if "show_ai_help" not in st.session_state:
    st.session_state.show_ai_help = False
if "live_detection_active" not in st.session_state:
    st.session_state.live_detection_active = False
if "bus_tracking_active" not in st.session_state:
    st.session_state.bus_tracking_active = False
if "bus_current_stop" not in st.session_state:
    st.session_state.bus_current_stop = 0
if "bus_last_update" not in st.session_state:
    st.session_state.bus_last_update = time.time()
if "detected_crowd_count" not in st.session_state:
    st.session_state.detected_crowd_count = 0
if "detected_crowd_level" not in st.session_state:
    st.session_state.detected_crowd_level = "Unknown"

# Render the app
render(routes, stops)
"""

try:
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(clean_code)
    print("✅ app.py has been cleaned successfully!")
    print(f"   File size: {len(clean_code)} bytes")
except Exception as e:
    print(f"❌ Error: {e}")
