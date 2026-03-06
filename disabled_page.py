# -*- coding: utf-8 -*-
# ============================================================
#   DISABLED / ACCESSIBILITY PORTAL
#   Features:
#     - Audio welcome prompt (TTS) asking disability type
#     - Voice YES/NO detection → switch to voice or text mode
#     - Real-time Speech-to-Text via Web Speech API (browser)
#     - Voice login (email + password spoken aloud → displayed)
#     - Normal text login for deaf / leg-disabled users
#     - Route & stop selection with ETA
#     - Pickup request submission to Firebase
# ============================================================

import time
import random
import difflib
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, timedelta
from firebase_manager import get_firebase_manager
from accessibility_alerts import AccessibilityAlerts, alert_request_sent
from disabled_id_auth import get_id_authenticator
from disabled_id_login_ui import render_id_card_login, render_authenticated_user_info


# ================================================================
# SESSION STATE INIT
# ================================================================

def init_disabled_state():
    defaults = {
        # ID Authentication
        "authenticated_uid":   None,       # UID of authenticated user
        "authenticated_user":  None,       # User data from ID auth
        
        # Portal Mode
        "dis_mode":          "id_login",   # id_login → ask → voice_login / text_login → welcome → routes
        "dis_voice_mode":    False,        # True = voice, False = text
        "dis_email":         "",
        "dis_password":      "",
        "dis_name":          "",
        "dis_type":          "",           # blind / hand_disabled / leg_disabled / deaf
        "dis_spoken_text":   "",           # latest speech recognition result
        "dis_voice_field":   "email",      # which field is being spoken: email / password
        "dis_yesno_done":    False,        # prevent repeated yes/no auto-trigger
        "dis_last_request":  None,
        "dis_live_coords_input": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ================================================================
# JAVASCRIPT HELPERS
# ================================================================

def speak_js(text):
    """Inject TTS via browser SpeechSynthesis."""
    safe = text.replace("'", "\\'").replace("\n", " ")
    components.html(f"""
    <script>
    (function() {{
        window.speechSynthesis.cancel();
        var u = new SpeechSynthesisUtterance('{safe}');
        u.lang  = 'en-IN';
        u.rate  = 0.92;
        u.pitch = 1.0;
        window.speechSynthesis.speak(u);
    }})();
    </script>
    """, height=0)


def normalize_spelled_input(text):
    """Convert letter-by-letter speech into a usable string."""
    if not text or not isinstance(text, str):
        return ""
    raw = text.strip().lower()
    if not raw:
        return ""
    # Common spoken tokens
    token_map = {
        "at": "@",
        "dot": ".",
        "period": ".",
        "underscore": "_",
        "under score": "_",
        "dash": "-",
        "hyphen": "-",
        "space": "",
    }
    parts = raw.split()
    # If user spelled letters/tokens, rebuild
    if len(parts) >= 2 and all(len(p) == 1 or p in token_map for p in parts):
        return "".join(token_map.get(p, p) for p in parts)
    # Fallback: remove spaces for normal speech like "john doe"
    return raw.replace(" ", "")


def speech_to_text_component(field_key, placeholder_text, target_label=None, target_placeholder=None, mirror_label=None):
    """
    Render a mic button + live transcript display using
    browser Web Speech API. Returns the spoken text via
    a hidden Streamlit text_input that gets auto-filled by JS.
    """
    unique = field_key.replace(" ", "_")
    target_label_js = (target_label or "").replace("'", "\\'")
    target_placeholder_js = (target_placeholder or "").replace("'", "\\'")
    mirror_label_js = (mirror_label or "").replace("'", "\\'")
    html_code = f"""
    <style>
      .mic-btn {{
        background: linear-gradient(135deg,#7c3aed,#4f46e5);
        color:#fff; border:none; border-radius:50px;
        padding:12px 28px; font-size:1rem; font-weight:700;
        cursor:pointer; margin:6px 0; transition:all .2s;
        box-shadow:0 4px 14px rgba(124,58,237,.4);
      }}
      .mic-btn:hover {{ transform:scale(1.05); }}
      .mic-btn.listening {{
        background:linear-gradient(135deg,#dc2626,#ef4444);
        animation: pulse 1s infinite;
      }}
      @keyframes pulse {{
        0%,100%{{ box-shadow:0 0 0 0 rgba(239,68,68,.6); }}
        50%{{ box-shadow:0 0 0 12px rgba(239,68,68,0); }}
      }}
      .transcript-box {{
        background:rgba(15,23,42,.9); color:#22d3ee;
        border:1.5px solid #4f46e5; border-radius:12px;
        padding:12px 16px; margin:8px 0;
        font-size:1.05rem; min-height:42px; word-break:break-all;
        font-weight:600;
      }}
      .status-lbl {{ color:#94a3b8; font-size:.82rem; margin-top:4px; }}
    </style>

    <button class="mic-btn" id="micBtn_{unique}" onclick="toggleMic_{unique}()">
      🎤 Speak {placeholder_text}
    </button>
    <div class="status-lbl">Mic button is at the middle-left of the screen. Press it to start speaking.</div>
    <div class="transcript-box" id="transcript_{unique}">
      <span style="color:#475569;">🗣 {placeholder_text} here will appear…</span>
    </div>
    <div class="status-lbl" id="status_{unique}">Press the button and start speaking</div>

    <script>
    var recognition_{unique} = null;
    var isListening_{unique} = false;
    var shouldRestart_{unique} = false;

    function setStreamlitInput_{unique}(val) {{
      try {{
        var doc = window.parent.document;
        var mirrorLabel = '{mirror_label_js}';
        if (mirrorLabel) {{
          var mirrorInput = doc.querySelector('input[aria-label=\"' + mirrorLabel + '\"]');
          if (mirrorInput) {{
            mirrorInput.value = val;
            mirrorInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
          }}
        }}

        var targetPlaceholder = '{target_placeholder_js}';
        if (targetPlaceholder) {{
          var pInput = doc.querySelector('input[placeholder=\"' + targetPlaceholder + '\"]');
          if (pInput) {{
            pInput.value = val;
            pInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
            return;
          }}
          // contains match fallback
          var allInputs = doc.querySelectorAll('input[type=\"text\"], input[type=\"password\"]');
          for (var j = 0; j < allInputs.length; j++) {{
            var ph = allInputs[j].getAttribute('placeholder') || '';
            if (ph && ph.toLowerCase().includes(targetPlaceholder.toLowerCase())) {{
              allInputs[j].value = val;
              allInputs[j].dispatchEvent(new Event('input', {{ bubbles: true }}));
              return;
            }}
          }}
        }}
        var targetLabel = '{target_label_js}';
        if (targetLabel) {{
          var targetInput = doc.querySelector('input[aria-label=\"' + targetLabel + '\"]');
          if (targetInput) {{
            targetInput.value = val;
            targetInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
            return;
          }}
        }}
        // Fallback: find first input whose label contains "Spoken"
        var inputs = doc.querySelectorAll('input[type=\"text\"], input[type=\"password\"]');
        for (var i = 0; i < inputs.length; i++) {{
          if (inputs[i].previousElementSibling &&
              inputs[i].previousElementSibling.textContent &&
              inputs[i].previousElementSibling.textContent.includes(\"Spoken\")) {{
            inputs[i].value = val;
            inputs[i].dispatchEvent(new Event('input', {{ bubbles: true }}));
            break;
          }}
        }}
      }} catch (e) {{}}
    }}

    function toggleMic_{unique}() {{
      if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {{
        document.getElementById('status_{unique}').innerText =
          '❌ Your browser does not support speech recognition. Use Chrome.';
        return;
      }}
      if (isListening_{unique}) {{
        shouldRestart_{unique} = false;
        recognition_{unique}.stop();
        return;
      }}
      var SR = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognition_{unique} = new SR();
      recognition_{unique}.lang = 'en-IN';
      recognition_{unique}.continuous = true;
      recognition_{unique}.interimResults = true;
      shouldRestart_{unique} = true;

      recognition_{unique}.onstart = function() {{
        isListening_{unique} = true;
        document.getElementById('micBtn_{unique}').classList.add('listening');
        document.getElementById('micBtn_{unique}').innerText = '🔴 Listening… (click to stop)';
        document.getElementById('status_{unique}').innerText = '🎙 Listening…';
      }};

      recognition_{unique}.onresult = function(e) {{
        var interim = '', final = '';
        for (var i = e.resultIndex; i < e.results.length; i++) {{
          if (e.results[i].isFinal) final += e.results[i][0].transcript;
          else interim += e.results[i][0].transcript;
        }}
        document.getElementById('transcript_{unique}').innerText =
          (final || interim) || '…';
        if (final) {{
          // Push to Streamlit via postMessage
          window.parent.postMessage({{
            type:'streamlit:setComponentValue',
            value: final.trim()
          }}, '*');
          setStreamlitInput_{unique}(final.trim());
          document.getElementById('status_{unique}').innerText =
            '✅ Captured: "' + final.trim() + '"';
        }}
      }};

      recognition_{unique}.onend = function() {{
        if (shouldRestart_{unique}) {{
          try {{ recognition_{unique}.start(); }} catch (e) {{}}
          return;
        }}
        isListening_{unique} = false;
        document.getElementById('micBtn_{unique}').classList.remove('listening');
        document.getElementById('micBtn_{unique}').innerText = '🎤 Speak {placeholder_text}';
        document.getElementById('status_{unique}').innerText = 'Click mic to speak again';
      }};

      recognition_{unique}.onerror = function(e) {{
        document.getElementById('status_{unique}').innerText = '⚠️ Error: ' + e.error;
        isListening_{unique} = false;
        document.getElementById('micBtn_{unique}').classList.remove('listening');
        document.getElementById('micBtn_{unique}').innerText = '🎤 Speak {placeholder_text}';
      }};

      recognition_{unique}.start();
    }}
    </script>
    """
    return components.html(html_code, height=160)


def capture_location_component(field_key, target_label=None, target_placeholder=None):
    """Capture current GPS location and write `lat,lng` into a Streamlit input."""
    unique = field_key.replace(" ", "_")
    target_label_js = (target_label or "").replace("'", "\\'")
    target_placeholder_js = (target_placeholder or "").replace("'", "\\'")
    html_code = f"""
    <style>
      .loc-box {{
        background:rgba(15,23,42,.9);
        border:1px solid rgba(34,211,238,.35);
        border-radius:12px;
        padding:12px 14px;
        margin:8px 0;
      }}
      .loc-status {{ color:#94a3b8; font-size:.9rem; }}
      .loc-value {{ color:#22d3ee; font-weight:700; margin-top:4px; }}
    </style>
    <div class="loc-box">
      <div class="loc-status" id="locStatus_{unique}">Requesting location permission...</div>
      <div class="loc-value" id="locValue_{unique}">Waiting for GPS...</div>
    </div>
    <script>
    function setStreamlitLocation_{unique}(val) {{
      try {{
        var doc = window.parent.document;
        var targetPlaceholder = '{target_placeholder_js}';
        if (targetPlaceholder) {{
          var pInput = doc.querySelector('input[placeholder=\"' + targetPlaceholder + '\"]');
          if (pInput) {{
            pInput.value = val;
            pInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
            return;
          }}
        }}
        var targetLabel = '{target_label_js}';
        if (targetLabel) {{
          var targetInput = doc.querySelector('input[aria-label=\"' + targetLabel + '\"]');
          if (targetInput) {{
            targetInput.value = val;
            targetInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
          }}
        }}
      }} catch (e) {{}}
    }}

    function updateLoc_{unique}(pos) {{
      var lat = pos.coords.latitude;
      var lng = pos.coords.longitude;
      var coords = lat.toFixed(6) + ',' + lng.toFixed(6);
      document.getElementById('locStatus_{unique}').innerText = 'Location detected';
      document.getElementById('locStatus_{unique}').style.color = '#22c55e';
      document.getElementById('locValue_{unique}').innerText = coords;
      setStreamlitLocation_{unique}(coords);
    }}

    function locErr_{unique}(err) {{
      var msg = {{1:'Permission denied',2:'Position unavailable',3:'Timeout'}}[err.code] || 'Location error';
      document.getElementById('locStatus_{unique}').innerText = msg;
      document.getElementById('locStatus_{unique}').style.color = '#ef4444';
    }}

    if ('geolocation' in navigator) {{
      navigator.geolocation.getCurrentPosition(updateLoc_{unique}, locErr_{unique}, {{
        enableHighAccuracy: true,
        timeout: 15000,
        maximumAge: 5000
      }});
    }} else {{
      document.getElementById('locStatus_{unique}').innerText = 'Geolocation not supported';
      document.getElementById('locStatus_{unique}').style.color = '#ef4444';
    }}
    </script>
    """
    return components.html(html_code, height=95)


# ================================================================
# STEP 0 - ASK MODE (Audio prompt + YES/NO)
# ================================================================

def render_ask_mode():
    st.markdown("""
    <div style='text-align:center; padding:20px 0;'>
        <div style='font-size:3rem;'>♿</div>
        <h2 style='color:#22d3ee;'>Welcome to the Accessibility Portal</h2>
        <p style='color:#94a3b8;'>This portal supports <b>voice-based</b> assistance for blind / hand-disabled users
        and <b>standard text</b> input for deaf / leg-disabled users.</p>
    </div>
    """, unsafe_allow_html=True)

    # Auto-play TTS welcome
    speak_js(
        "Welcome to the Tamil Nadu Smart Bus Accessibility Portal. "
        "Are you blind or hand disabled and need voice-based assistance? "
        "If yes, click the YES button. Otherwise click NO to use text input."
    )

    st.markdown("""
    <div style='background:rgba(15,23,42,.85); border:1px solid rgba(34,211,238,.25);
                border-radius:18px; padding:24px; text-align:center; margin:10px 0;'>
        <p style='color:#f1f5f9; font-size:1.1rem; margin-bottom:18px;'>
            🔊 <b>Listening question:</b><br>
            <i>"Are you blind or hand-disabled? Do you want voice-based interface?"</i>
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Voice yes/no (for users without hands)
    st.markdown("#### 🎙️ Say YES or NO")
    speech_to_text_component("ask_yesno", "yes or no")
    spoken_yesno = st.text_input(
        "Spoken answer (auto-filled by mic above, or type here):",
        key="dis_yesno_input",
        placeholder="yes / no"
    )
    if spoken_yesno and not st.session_state.get("dis_yesno_done"):
        said = spoken_yesno.strip().lower()
        if "yes" in said:
            st.session_state.dis_voice_mode = True
            st.session_state.dis_mode = "select_type"
            st.session_state.dis_yesno_done = True
            speak_js("Voice mode selected. Please choose your disability type.")
            st.rerun()
        elif "no" in said:
            st.session_state.dis_voice_mode = False
            st.session_state.dis_mode = "text_login"
            st.session_state.dis_yesno_done = True
            st.rerun()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ YES - I want Voice Mode", key="dis_yes_btn",
                     use_container_width=True, type="primary"):
            st.session_state.dis_voice_mode = True
            st.session_state.dis_mode = "select_type"
            speak_js("Voice mode selected. Please choose your disability type.")
            st.rerun()
    with col2:
        if st.button("⌨️ NO - I'll Type Normally", key="dis_no_btn",
                     use_container_width=True):
            st.session_state.dis_voice_mode = False
            st.session_state.dis_mode = "text_login"
            st.rerun()


# ================================================================
# STEP 0.5 - SELECT DISABILITY TYPE
# ================================================================

def render_select_type():
    st.markdown("### 🏷️ Select Your Accessibility Need")
    speak_js("Please select your disability type.")

    dtype = st.radio(
        "What best describes you?",
        options=["blind", "hand_disabled", "leg_disabled", "deaf"],
        format_func=lambda x: {
            "blind":        "👁️ Blind / Visual Impairment",
            "hand_disabled":"🤚 Hand Disabled (No Hands)",
            "leg_disabled": "🦽 Leg Disabled / Wheelchair",
            "deaf":         "🔇 Deaf / Hard of Hearing",
        }[x],
        key="dis_type_radio"
    )

    if st.button("✅ Confirm & Continue", key="dis_type_confirm",
                 use_container_width=True, type="primary"):
        st.session_state.dis_type = dtype
        if dtype in ("blind", "hand_disabled"):
            st.session_state.dis_mode  = "voice_login"
            st.session_state.dis_voice_mode = True
            speak_js("Voice login selected. Please speak your email address when prompted.")
        else:
            st.session_state.dis_mode  = "text_login"
            st.session_state.dis_voice_mode = False
        st.rerun()


# ================================================================
# STEP 1A - VOICE LOGIN (Speech-to-Text via Web Speech API)
# ================================================================

def render_voice_login():
    st.markdown("""
    <div style='text-align:center; margin-bottom:16px;'>
        <h3 style='color:#22d3ee;'>🎤 Voice Login</h3>
        <p style='color:#94a3b8;'>Press the mic button and speak. Your words will appear on screen.</p>
    </div>
    """, unsafe_allow_html=True)

    speak_js("Voice login. Press the mic button and speak your email address clearly.")

    # ---- Email by voice ----
    st.markdown("#### 📧 Speak your Email")
    st.markdown(f"""
    <div style='background:rgba(15,23,42,.85); border:1px solid #4f46e5;
                border-radius:12px; padding:14px; margin-bottom:8px;'>
        <span style='color:#94a3b8; font-size:.85rem;'>Current Email:</span><br>
        <span style='color:#22d3ee; font-size:1.2rem; font-weight:700;'>
            {st.session_state.dis_email if st.session_state.dis_email else "( not set yet )"}
        </span>
    </div>
    """, unsafe_allow_html=True)

    st.text_input("voice_email_value", key="voice_email_value", label_visibility="collapsed")
    st.markdown("""
    <style>
    input[aria-label="voice_email_value"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

    speech_to_text_component(
        "email_voice",
        "your email",
        target_label="Spoken email (auto-filled by mic above, or type here):",
        target_placeholder="e.g. user@gmail.com",
        mirror_label="voice_email_value"
    )

    spoken_email = st.text_input(
        "Spoken email (auto-filled by mic above, or type here):",
        key="dis_spoken_email_input",
        placeholder="e.g. user@gmail.com"
    )
    if spoken_email:
        normalized = normalize_spelled_input(spoken_email)
        if "@" not in normalized:
            normalized = f"{normalized}@gmail.com"
        st.session_state.dis_spoken_email_input = normalized
        st.session_state.dis_email = normalized

    ec1, ec2 = st.columns(2)
    with ec1:
        if st.button("⌫ Clear Email", key="dis_clear_email"):
            st.session_state.dis_email = ""
            st.rerun()
    with ec2:
        if st.button("✅ Set Email", key="dis_set_email"):
            if st.session_state.get("dis_spoken_email_input"):
                st.session_state.dis_email = st.session_state.dis_spoken_email_input.strip()
            st.rerun()

    st.markdown("---")

    # ---- Password by voice ----
    st.markdown("#### 🔑 Speak your Password")
    st.markdown(f"""
    <div style='background:rgba(15,23,42,.85); border:1px solid #4f46e5;
                border-radius:12px; padding:14px; margin-bottom:8px;'>
        <span style='color:#94a3b8; font-size:.85rem;'>Current Password:</span><br>
        <span style='color:#22d3ee; font-size:1.2rem; font-weight:700;'>
            {"•" * len(st.session_state.dis_password) if st.session_state.dis_password else "( not set yet )"}
        </span>
    </div>
    """, unsafe_allow_html=True)

    st.text_input("voice_pass_value", key="voice_pass_value", label_visibility="collapsed")
    st.markdown("""
    <style>
    input[aria-label="voice_pass_value"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

    speech_to_text_component(
        "pass_voice",
        "your password",
        target_label="Spoken password (auto-filled by mic above, or type here):",
        target_placeholder="Speak clearly...",
        mirror_label="voice_pass_value"
    )

    spoken_pass = st.text_input(
        "Spoken password (auto-filled by mic above, or type here):",
        key="dis_spoken_pass_input",
        type="password",
        placeholder="Speak clearly..."
    )
    if spoken_pass:
        normalized = normalize_spelled_input(spoken_pass)
        st.session_state.dis_spoken_pass_input = normalized
        st.session_state.dis_password = normalized

    pc1, pc2 = st.columns(2)
    with pc1:
        if st.button("⌫ Clear Password", key="dis_clear_pass"):
            st.session_state.dis_password = ""
            st.rerun()
    with pc2:
        if st.button("✅ Set Password", key="dis_set_pass"):
            if st.session_state.get("dis_spoken_pass_input"):
                st.session_state.dis_password = st.session_state.dis_spoken_pass_input.strip()
            st.rerun()

    st.markdown("---")

    if st.button("🚀 Login with Voice", key="dis_voice_login_btn",
                 use_container_width=True, type="primary"):
        # Use spoken inputs if available
        if st.session_state.get("voice_email_value"):
            st.session_state.dis_email = st.session_state.voice_email_value.strip()
        elif st.session_state.get("dis_spoken_email_input"):
            st.session_state.dis_email = st.session_state.dis_spoken_email_input.strip()
        if st.session_state.get("voice_pass_value"):
            st.session_state.dis_password = st.session_state.voice_pass_value.strip()
        elif st.session_state.get("dis_spoken_pass_input"):
            st.session_state.dis_password = st.session_state.dis_spoken_pass_input.strip()

        if not st.session_state.dis_email:
            st.session_state.dis_email = "voice_user"
        if not st.session_state.dis_password:
            st.session_state.dis_password = "voice_pass"

        st.session_state.dis_name = st.session_state.dis_email.split("@")[0].title()
        st.session_state.dis_mode = "welcome"
        speak_js(f"Login successful! Welcome {st.session_state.dis_name}!")
        st.rerun()

    if st.button("🔙 Back", key="dis_back_from_voice"):
        st.session_state.dis_mode = "ask"
        st.rerun()


# ================================================================
# STEP 1B - TEXT LOGIN (for deaf / leg-disabled)
# ================================================================

def render_text_login():
    st.markdown("""
    <div style='text-align:center; margin-bottom:16px;'>
        <h3 style='color:#22d3ee;'>⌨️ Standard Login</h3>
        <p style='color:#94a3b8;'>Type your email and password below - fully keyboard accessible.</p>
    </div>
    """, unsafe_allow_html=True)

    dtype_display = {
        "leg_disabled": "🦽 Leg Disabled",
        "deaf":         "🔇 Deaf / Hard of Hearing",
    }.get(st.session_state.dis_type, "♿ Accessibility User")

    st.info(f"**Access Mode:** {dtype_display} - Text Input")

    email    = st.text_input("📧 Email Address", key="dis_text_email",
                             placeholder="enter your email")
    password = st.text_input("🔑 Password",      key="dis_text_pass",
                             type="password", placeholder="enter your password")

    dtype = st.selectbox("♿ Disability Type",
                         ["leg_disabled", "deaf", "blind", "hand_disabled"],
                         format_func=lambda x: {
                             "leg_disabled": "🦽 Leg Disabled",
                             "deaf":         "🔇 Deaf",
                             "blind":        "👁️ Blind",
                             "hand_disabled":"🤚 Hand Disabled"
                         }[x],
                         key="dis_text_dtype")

    if st.button("✅ Login", key="dis_text_login_btn",
                 use_container_width=True, type="primary"):
        if not email or not password:
            st.error("❌ Please fill in all fields.")
        else:
            st.session_state.dis_email    = email
            st.session_state.dis_password = password
            st.session_state.dis_type     = dtype
            st.session_state.dis_name     = email.split("@")[0].title()
            st.session_state.dis_mode     = "welcome"
            st.rerun()

    if st.button("🔙 Back", key="dis_back_from_text"):
        st.session_state.dis_mode = "ask"
        st.rerun()


# ================================================================
# STEP 2 - WELCOME
# ================================================================

def render_disabled_welcome():
    name  = st.session_state.dis_name
    dtype = st.session_state.dis_type
    label = {
        "blind":        "👁️ Visual Impairment",
        "hand_disabled":"🤚 Hand Disability",
        "leg_disabled": "🦽 Mobility Impairment",
        "deaf":         "🔇 Deaf / Hard of Hearing",
    }.get(dtype, "♿ Accessibility User")

    st.markdown(f"""
    <div style='background:rgba(15,23,42,.88); border:1px solid rgba(34,211,238,.3);
                border-radius:18px; padding:28px; text-align:center; margin-bottom:18px;'>
        <div style='font-size:3rem;'>👋</div>
        <h2 style='color:#22d3ee;'>Welcome, {name}!</h2>
        <div style='background:rgba(34,211,238,.12); border-radius:10px; padding:10px 20px;
                    display:inline-block; margin:10px 0;'>
            <span style='color:#22d3ee; font-weight:700;'>{label}</span>
        </div>
        <p style='color:#94a3b8;'>Logged in at {datetime.now().strftime("%I:%M %p")}</p>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.get("dis_voice_mode"):
        speak_js(f"Welcome {name}! You are now logged in. Press the button to select your journey.")

    if st.button("📍 Select My Journey", key="dis_goto_routes",
                 use_container_width=True, type="primary"):
        st.session_state.dis_mode = "routes"
        if st.session_state.get("dis_voice_mode"):
            speak_js("Please select your bus route, boarding point and destination.")
        st.rerun()

    if st.button("🔙 Logout", key="dis_logout"):
        for k in ["dis_mode","dis_email","dis_password","dis_name","dis_type","dis_voice_mode","dis_last_request","dis_live_coords_input","authenticated_uid","authenticated_user"]:
            st.session_state[k] = "" if k not in ("dis_mode","dis_voice_mode") else ("id_login" if k=="dis_mode" else False)
        st.rerun()


# ================================================================
# STEP 3 - ROUTE SELECTION & PICKUP REQUEST
# ================================================================

def render_disabled_routes(routes, stops):
    name = st.session_state.dis_name

    st.markdown(f"### 🚌 Your Journey - {name}")

    if routes is None or routes.empty:
        st.error("❌ Route data not available.")
        return

    route_option = st.selectbox("🚌 Select Bus Route:",
                                routes["bus_details"].unique(),
                                key="dis_route_select")

    route_row     = routes[routes["bus_details"] == route_option].iloc[0]
    try:
        route_stop_ids = list(map(int, str(route_row["route"]).split()))
        route_stops    = stops[stops["stop_id"].isin(route_stop_ids)].copy()
        route_stops["order"] = route_stops["stop_id"].apply(
            lambda x: route_stop_ids.index(x) if x in route_stop_ids else 9999
        )
        route_stops = route_stops.sort_values("order")
    except Exception:
        st.error("Stop data error.")
        return

    stop_names = route_stops["stop_name"].unique().tolist()

    def _normalize_stop_text(text):
        if not text:
            return ""
        cleaned = str(text).lower().strip()
        for w in ["bus stop", "busstand", "bus stand", "stop", "boarding", "destination", "point"]:
            cleaned = cleaned.replace(w, " ")
        cleaned = "".join(ch for ch in cleaned if ch.isalnum() or ch.isspace())
        return " ".join(cleaned.split())

    def _match_stop(spoken, candidates):
        if not spoken:
            return None
        s = _normalize_stop_text(spoken)
        for name in candidates:
            n = _normalize_stop_text(name)
            if s and (s in n or n in s):
                return name
        normalized_pairs = [(_normalize_stop_text(c), c) for c in candidates]
        normalized_names = [n for n, _ in normalized_pairs]
        matches = difflib.get_close_matches(s, normalized_names, n=1, cutoff=0.6)
        if not matches:
            return None
        matched_norm = matches[0]
        for norm_name, original in normalized_pairs:
            if norm_name == matched_norm:
                return original
        return None

    st.markdown("#### 🎙️ Speak Boarding & Destination Stops")
    speech_to_text_component(
        "dis_board_voice",
        "boarding stop",
        target_label="Spoken boarding stop:",
        target_placeholder="say boarding stop"
    )
    spoken_board = st.text_input(
        "Spoken boarding stop:",
        key="dis_spoken_boarding",
        placeholder="say boarding stop"
    )

    speech_to_text_component(
        "dis_dest_voice",
        "destination stop",
        target_label="Spoken destination stop:",
        target_placeholder="say destination stop"
    )
    spoken_dest = st.text_input(
        "Spoken destination stop:",
        key="dis_spoken_destination",
        placeholder="say destination stop"
    )

    from_stop_voice = _match_stop(spoken_board, stop_names)
    to_stop_voice = _match_stop(spoken_dest, stop_names)

    if spoken_board and not from_stop_voice:
        st.warning("⚠️ Boarding stop not matched. Please speak again slowly.")
    if spoken_dest and not to_stop_voice:
        st.warning("⚠️ Destination stop not matched. Please speak again slowly.")

    board_default_idx = stop_names.index(from_stop_voice) if from_stop_voice in stop_names else 0
    dest_default_idx = stop_names.index(to_stop_voice) if to_stop_voice in stop_names else min(board_default_idx + 1, len(stop_names) - 1)

    st.markdown("#### ✅ Confirm Stops")
    cc1, cc2 = st.columns(2)
    with cc1:
        from_stop = st.selectbox(
            "Boarding stop (confirm):",
            stop_names,
            index=board_default_idx,
            key="dis_boarding_confirm"
        )
    with cc2:
        to_stop = st.selectbox(
            "Destination stop (confirm):",
            stop_names,
            index=dest_default_idx,
            key="dis_destination_confirm"
        )

    from_data = route_stops[route_stops["stop_name"] == from_stop]
    to_data   = route_stops[route_stops["stop_name"] == to_stop]

    if from_stop and to_stop and not from_data.empty and not to_data.empty:
        from_idx = from_data["order"].values[0]
        to_idx   = to_data["order"].values[0]

        if from_idx == to_idx:
            st.error("❌ Boarding and destination cannot be the same stop.")
        else:
            reverse_journey = from_idx > to_idx
            remaining  = abs(to_idx - from_idx)
            eta_mins   = int(max(3, min(14, remaining * random.randint(2, 3))))
            arrival    = datetime.now() + timedelta(minutes=int(eta_mins))

            st.markdown("---")
            m1, m2, m3 = st.columns(3)
            m1.metric("🚏 Stops Away", remaining)
            m2.metric("⏱️ ETA",        f"{eta_mins} min")
            m3.metric("🕐 Arrives",    arrival.strftime("%I:%M %p"))
            if reverse_journey:
                st.warning("⚠️ Destination appears before boarding in this route order. Request will still be sent to driver.")

            # Crowd level
            st.markdown("### 👥 Expected Crowd")

            # SEND REQUEST SECTION - MOVED UP FOR VISIBILITY
            st.markdown("""
            <div style='background:linear-gradient(135deg,rgba(34,211,238,.15),rgba(59,130,246,.15)); 
                        border:2px solid #22d3ee; border-radius:14px; padding:18px; margin:16px 0;'>
                <div style='color:#22d3ee; font-size:1.2rem; font-weight:800; margin-bottom:10px;'>
                    📨 SEND ACCESSIBILITY REQUEST TO DRIVER
                </div>
                <div style='color:#94a3b8; font-size:0.95rem;'>
                    Your accessibility request will be visible to the driver immediately.
                    The driver will acknowledge your assistance needs.
                </div>
            </div>
            """, unsafe_allow_html=True)
            if remaining <= 3:
                st.markdown("<span class='crowd-low'>🟢 LOW - Seats Available</span>",
                            unsafe_allow_html=True)
            elif remaining <= 6:
                st.markdown("<span class='crowd-medium'>🟡 MEDIUM - Standing Room</span>",
                            unsafe_allow_html=True)
            else:
                st.markdown("<span class='crowd-high'>🔴 HIGH - Very Crowded</span>",
                            unsafe_allow_html=True)

            if st.session_state.get("dis_voice_mode"):
                speak_js(f"Bus {route_option} will arrive in {eta_mins} minutes. Crowd level is "
                         f"{'low' if remaining<=3 else 'medium' if remaining<=6 else 'high'}.")

            st.markdown("---")

            # LOCATION SECTION
            st.markdown("#### 📡 Share Current Location")
            st.info("📍 **GPS is being detected automatically**. Allow location permission in your browser for accurate pickup.")
            capture_location_component(
                "dis_current_location",
                target_label="Passenger live location (lat,lng):",
                target_placeholder="auto-detected from GPS"
            )
            live_coords = st.text_input(
                "Passenger live location (lat,lng):",
                key="dis_live_coords_input",
                placeholder="auto-detected from GPS"
            )

            passenger_lat, passenger_lng = None, None
            if live_coords and "," in live_coords:
                try:
                    parts = [p.strip() for p in live_coords.split(",")]
                    passenger_lat = float(parts[0])
                    passenger_lng = float(parts[1])
                    st.success(f"✅ **GPS Detected:** Latitude {passenger_lat:.6f}, Longitude {passenger_lng:.6f}")
                    print(f"[Disabled Portal] 📍 GPS Location captured: LAT={passenger_lat}, LNG={passenger_lng}")
                except Exception as e:
                    st.warning("⚠️ GPS format invalid. Allow location permission and retry.")
                    print(f"[Disabled Portal] ⚠️ GPS parsing error: {e}")
            else:
                st.warning("⏳ **Waiting for GPS...**  Please allow location permission in your browser popup. Refresh page if needed.")

            def _send_request_to_driver():
                if passenger_lat is None or passenger_lng is None:
                    st.error("❌ Current location required. Please allow GPS and try again.")
                    return

                request_signature = (
                    route_option,
                    from_stop,
                    to_stop,
                    f"{passenger_lat:.6f},{passenger_lng:.6f}"
                )
                if st.session_state.get("dis_last_request") == request_signature:
                    st.info("ℹ️ This request is already sent.")
                    return

                fb = get_firebase_manager()
                if not fb.initialized:
                    st.error("❌ Firebase not connected. Request not sent.")
                    return

                print(f"[Disabled Portal] 🚀 Sending request to driver...")
                print(f"[Disabled Portal] 📍 Passenger Location: LAT={passenger_lat}, LNG={passenger_lng}")
                print(f"[Disabled Portal] 🚌 Route: {route_option}, From: {from_stop}, To: {to_stop}")
                
                req_id = fb.send_pickup_request(
                    user_name=name,
                    location=from_stop,
                    route=route_option,
                    disability_type=st.session_state.dis_type,
                    email=st.session_state.get("dis_email", ""),
                    phone=st.session_state.get("user_phone", ""),
                    boarding_stop=from_stop,
                    destination_stop=to_stop,
                    passenger_lat=passenger_lat,
                    passenger_lng=passenger_lng
                )
                if req_id:
                    st.session_state.dis_last_request = request_signature
                    disability_type_text = st.session_state.dis_type.replace("_", " ").title()
                    
                    # SEND APPROPRIATE ALERTS BASED ON DISABILITY TYPE
                    if st.session_state.dis_type == "deaf":
                        # VISUAL ALERT FOR DEAF USERS
                        AccessibilityAlerts.show_request_sent_alert_deaf(
                            route=route_option,
                            from_stop=from_stop,
                            to_stop=to_stop,
                            arrival_time=arrival.strftime('%I:%M %p'),
                            disability_type=disability_type_text,
                            passenger_lat=passenger_lat,
                            passenger_lng=passenger_lng
                        )
                        st.info("📍 Your GPS location has been shared with drivers for precise pickup")
                        st.caption("✅ Look for status updates on this screen. Drivers will show confirmations here.")
                    elif st.session_state.dis_type == "blind":
                        # VOICE ALERT FOR BLIND USERS
                        AccessibilityAlerts.show_request_sent_alert_blind(
                            route=route_option,
                            from_stop=from_stop,
                            to_stop=to_stop,
                            arrival_time=arrival.strftime('%I:%M %p'),
                            disability_type=disability_type_text
                        )
                        st.success("✅ Your accessibility request has been sent!")
                        st.info("📍 Your GPS location has been shared with drivers for precise pickup")
                        st.caption("🔊 This screen will announce driver updates. Keep your device audio ON.")
                    else:
                        # DEFAULT ALERT FOR OTHER ACCESSIBILITY NEEDS
                        AccessibilityAlerts.show_visual_alert_deaf(
                            title="REQUEST SENT TO DRIVERS",
                            message=f"""
🚌 Route: <strong>{route_option}</strong><br>
🛫 Boarding: <strong>{from_stop}</strong><br>
🏁 Going to: <strong>{to_stop}</strong><br>
⏱️ Arrival: <strong>{arrival.strftime('%I:%M %p')}</strong><br>
♿ Support Type: <strong>{disability_type_text}</strong>
                            """,
                            alert_type="success"
                        )
                        st.info("📍 Your GPS location has been shared with drivers for precise pickup")
                    
                    # Show accessibility support info
                    AccessibilityAlerts.show_accessibility_support_active_deaf(st.session_state.dis_type)
                    
                    st.info("💬 The driver will acknowledge your request shortly. Please wait at the designated boarding point.")
                    
                    st.session_state.dis_request_confirm_voice = ""
                else:
                    st.error("❌ Failed to send request. Please retry.")

            # PROMINENT REQUEST CONFIRMATION SECTION
            st.markdown("""
            <div style='background:linear-gradient(135deg,rgba(34,211,238,.2),rgba(59,130,246,.2)); 
                        border:2px solid #22d3ee; border-radius:14px; padding:20px; margin:20px 0;
                        box-shadow: 0 0 20px rgba(34,211,238,.25);'>
                <div style='color:#22d3ee; font-size:1.3rem; font-weight:800; margin-bottom:12px;'>
                    ✅ READY TO SEND REQUEST?
                </div>
                <div style='color:#f1f5f9; font-size:0.95rem; line-height:1.6;'>
                    <div>🚌 <strong>Route:</strong> {route_}</div>
                    <div>🛫 <strong>From:</strong> {from_}</div>
                    <div>🏁 <strong>To:</strong> {to_}</div>
                    <div>⏱️ <strong>Arrival in:</strong> {eta_} minutes</div>
                </div>
            </div>
            """.format(route_=route_option, from_=from_stop, to_=to_stop, eta_=eta_mins), unsafe_allow_html=True)

            st.markdown("#### 📨 Confirm Send Request to Driver")
            st.caption("👉 Tap YES to notify the driver of your accessibility needs")

            spoken_confirm = ""
            if st.session_state.get("dis_voice_mode"):
                speech_to_text_component(
                    "dis_send_confirm_voice",
                    "yes or no",
                    target_label="Confirm send request (yes/no):",
                    target_placeholder="yes / no"
                )
                spoken_confirm = st.text_input(
                    "Confirm send request (yes/no):",
                    key="dis_request_confirm_voice",
                    placeholder="yes / no"
                ).strip().lower()

            yes_clicked, no_clicked = False, False
            
            # LARGE PROMINENT SEND BUTTON FOR ACCESSIBILITY
            st.markdown("""
            <div style='margin-top:20px; margin-bottom:20px;'>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                yes_clicked = st.button(
                    "✅ YES - SEND REQUEST",
                    key="dis_send_request_yes_btn",
                    use_container_width=True,
                    type="primary",
                    help="Tap here to send your accessibility request to nearby drivers"
                )
            with col2:
                no_clicked = st.button(
                    "❌ NO - CANCEL",
                    key="dis_send_request_no_btn",
                    use_container_width=True,
                    help="Tap here to cancel and go back"
                )
            
            st.markdown("</div>", unsafe_allow_html=True)

            said_yes = bool(spoken_confirm) and "yes" in spoken_confirm
            said_no = bool(spoken_confirm) and "no" in spoken_confirm

            if yes_clicked or said_yes:
                _send_request_to_driver()
            elif no_clicked or said_no:
                st.info("Request cancelled.")
                if st.session_state.get("dis_voice_mode"):
                    speak_js("Request cancelled.")

    if st.button("🔙 Back", key="dis_back_from_routes"):
        st.session_state.dis_mode = "welcome"
        st.rerun()


# ================================================================
# MAIN RENDER
# ================================================================

def render_disabled(routes, stops):
    # ---- CSS for crowd badges ----
    st.markdown("""
    <style>
    .crowd-low    { background:linear-gradient(90deg,#16a34a,#22c55e); color:#fff !important;
                    padding:10px 20px; border-radius:12px; font-size:1.1rem; font-weight:700;
                    display:block; text-align:center; margin:8px 0;
                    box-shadow:0 4px 12px rgba(34,197,94,.4); }
    .crowd-medium { background:linear-gradient(90deg,#d97706,#f59e0b); color:#fff !important;
                    padding:10px 20px; border-radius:12px; font-size:1.1rem; font-weight:700;
                    display:block; text-align:center; margin:8px 0;
                    box-shadow:0 4px 12px rgba(245,158,11,.4); }
    .crowd-high   { background:linear-gradient(90deg,#dc2626,#ef4444); color:#fff !important;
                    padding:10px 20px; border-radius:12px; font-size:1.1rem; font-weight:700;
                    display:block; text-align:center; margin:8px 0;
                    box-shadow:0 4px 12px rgba(239,68,68,.4); }
    [data-testid="stTextInput"] input {{ color:#0f172a !important; background:#f8fafc !important; }}
    [data-testid="stTextInput"] label {{ color:#22d3ee !important; font-weight:600 !important; }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='text-align:center; margin-bottom:16px;'>
        <h2 style='color:#22d3ee;'>♿ Inclusive Accessibility Portal</h2>
        <p style='color:#94a3b8;'>Voice-assisted & text-based access for differently-abled users</p>
        <div style='background:rgba(34,211,238,.1); border:1px solid rgba(34,211,238,.3); 
                    border-radius:12px; padding:12px; margin:12px 0;'>
            <p style='color:#f1f5f9; margin:0;'>
                🚌 <strong>Your accessibility request will be sent to drivers at Madhavaram Bus Depot</strong><br>
                📍 Your GPS location will be shared for precise pickup<br>
                🔊 Drivers will receive voice alerts about your accessibility needs
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    init_disabled_state()

    mode = st.session_state.dis_mode
    
    # ================================================================
    # STEP 0: ID CARD AUTHENTICATION (REQUIRED FIRST)
    # ================================================================
    if mode == "id_login":
        render_id_card_login()
        return  # Stop here until authenticated
    
    # ================================================================
    # VERIFY AUTHENTICATION BEFORE PROCEEDING
    # ================================================================
    if not st.session_state.get("authenticated_uid"):
        st.error("❌ You must authenticate with your ID card first.")
        if st.button("🔓 Back to Login"):
            st.session_state.dis_mode = "id_login"
            st.rerun()
        return
    
    # Show authenticated user info
    render_authenticated_user_info()
    
    # ================================================================
    # CONTINUE WITH PORTAL MODES (ONLY IF AUTHENTICATED)
    # ================================================================
    if   mode == "ask":          render_ask_mode()
    elif mode == "select_type":  render_select_type()
    elif mode == "voice_login":  render_voice_login()
    elif mode == "text_login":   render_text_login()
    elif mode == "welcome":      render_disabled_welcome()
    elif mode == "routes":       render_disabled_routes(routes, stops)

    # ---- Switch Role ----
    st.markdown("""
    <div style='background:rgba(15,23,42,.88); border:1px solid rgba(34,211,238,.25);
                border-radius:18px; padding:20px; margin-top:24px;'>
    """, unsafe_allow_html=True)
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
            if st.button(label, key=f"dis_switch_{role}", use_container_width=True,
                         disabled=(st.session_state.get("role") == role)):
                st.session_state.role = role
                st.session_state.selected_portal = role
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
