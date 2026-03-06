# -*- coding: utf-8 -*-
import os
os.environ["TORCH_LOAD_WEIGHTS_ONLY"] = "0"
import streamlit as st
import pandas as pd
import time
from datetime import datetime
from live_crowd_detector import LiveCrowdDetector
from firebase_manager import FirebaseManager


# ---------------- CUSTOM CSS ----------------
def get_base64_image(image_path):
    import base64
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


def local_css():
    try:
        bg_image = get_base64_image("background.png")
        bg_style = f"""
        background-image: linear-gradient(rgba(15, 23, 42, 0.65), rgba(30, 41, 59, 0.65)), url(data:image/png;base64,{bg_image});
        background-size: cover;
        background-position: center center;
        background-repeat: no-repeat;
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

    .stButton>button {{
        width: 100%;
        border-radius: 12px;
        height: 3em;
        background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%);
        color: #ffffff !important;
        font-weight: 600;
        font-size: 1rem;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }}

    .stButton>button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.4);
        background: linear-gradient(90deg, #60a5fa 0%, #3b82f6 100%);
    }}

    .card {{
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
    }}

    h1, h2, h3 {{
        color: #22d3ee !important;
        font-weight: 800 !important;
        text-shadow: 0 0 20px rgba(34, 211, 238, 0.3);
    }}

    p, span, div {{
        color: #e2e8f0 !important;
    }}
    </style>
    """, unsafe_allow_html=True)


# ---------------- DATA LOADING ----------------
@st.cache_data
def load_data():
    try:
        routes = pd.read_csv("routedata1.csv")
        stops = pd.read_csv("stopdata.csv")
        routes.columns = routes.columns.str.strip()
        stops.columns = stops.columns.str.strip()

        stop_id_col = next((col for col in stops.columns if 'id' in col.lower()), stops.columns[0])
        stop_name_col = next((col for col in stops.columns if 'name' in col.lower()), stops.columns[1])
        stops = stops.rename(columns={stop_id_col: "stop_id", stop_name_col: "stop_name"})

        return routes, stops
    except Exception as e:
        st.error(f"Error loading CSV files: {e}")
        return None, None


@st.cache_resource
def get_firebase_manager():
    return FirebaseManager()


@st.cache_resource
def get_live_detector():
    detector = LiveCrowdDetector()
    detector.load_model()
    fb = get_firebase_manager()
    if fb.initialized:
        detector.set_firebase_manager(fb)
    return detector


def get_ai_response(user_question, context="voice_login"):
    responses = {
        "how_to_use": """
        **🎤 How to Use Voice Login:**
        1. Click the 🎤 Speak Character button
        2. Say ONE letter or number clearly (e.g., "A", "B", "1", "2")
        3. For special characters:
           - Say "AT" for @
           - Say "DOT" for period (.)
        """,
        "what_is_this": """
        **🚌 Tamil Nadu Smart Bus System**
        This is an inclusive public transport solution with voice login and pickup requests.
        """,
    }
    q = user_question.lower()
    if "how" in q or "use" in q:
        return responses["how_to_use"]
    return responses.get("what_is_this")
