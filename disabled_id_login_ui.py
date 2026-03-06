# -*- coding: utf-8 -*-
# ============================================================
#   DISABLED PERSON ID CARD LOGIN UI
#   Features:
#     - Visual ID card login form
#     - Barcode/QR code scanning (future)
#     - Voice-based UID input
#     - Manual UID entry
#     - Authentication feedback
# ============================================================

import streamlit as st
import streamlit.components.v1 as components
from disabled_id_auth import get_id_authenticator
from accessibility_alerts import AccessibilityAlerts


def render_id_card_login():
    """
    Render ID card authentication screen for disabled persons.
    Provides multiple input methods for accessibility.
    """
    
    st.markdown("""
    <div style='text-align:center; padding:20px 0;'>
        <div style='font-size:4rem;'>🆔</div>
        <h1 style='color:#22d3ee;'>Disabled Person Portal</h1>
        <p style='color:#94a3b8; font-size:1.1rem;'>🔐 ID Card Verification Required</p>
    </div>
    """, unsafe_allow_html=True)
    
    authenticator = get_id_authenticator()
    
    # Introduction
    st.markdown("""
    <div style='background:rgba(34,211,238,0.1); border:2px solid rgba(34,211,238,0.3);
                border-radius:12px; padding:18px; margin:20px 0;'>
        <div style='color:#22d3ee; font-weight:700; margin-bottom:12px;'>🆔 ID Card Authentication</div>
        <div style='color:#f1f5f9; line-height:1.6;'>
            <ul>
                <li>✅ Verified disabled persons can login with their ID card</li>
                <li>✅ UID format: UID001, UID002, etc.</li>
                <li>✅ Multiple input methods available (text, voice)</li>
                <li>✅ Your information is secure and encrypted</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs for different input methods
    tab1, tab2, tab3 = st.tabs(["📝 Manual Entry", "🎤 Voice Input", "📱 QR Code (Future)"])
    
    # ================================================================
    # TAB 1: MANUAL UID ENTRY
    # ================================================================
    with tab1:
        st.markdown("### 📝 Enter Your Details")
        st.caption("⚠️ Both fields are required - provide your UID and full name")
        
        # Ensure fields are empty by default (no pre-filled values)
        if "manual_uid_input" not in st.session_state:
            st.session_state.manual_uid_input = ""
        if "manual_name_input" not in st.session_state:
            st.session_state.manual_name_input = ""
        
        col1, col2 = st.columns(2)
        with col1:
            uid_input = st.text_input(
                "UID / ID Card Number *",
                key="manual_uid_input",
                placeholder="UID001",
                help="Required: Enter your unique disability ID card number (e.g., UID001, UID002, etc.)"
            )
        with col2:
            name_input = st.text_input(
                "Your Full Name *",
                key="manual_name_input",
                placeholder="Enter your name",
                help="Required: Enter your full name as you wish to be addressed"
            )
        
        if st.button("🔓 Verify & Login", use_container_width=True, type="primary", key="verify_manual"):
            # Validate both fields are provided
            if not uid_input or not uid_input.strip():
                st.error("❌ UID is required. Please enter your ID card number.")
            elif not name_input or not name_input.strip():
                st.error("❌ Name is required. Please enter your full name.")
            elif uid_input and name_input:
                success, user, message = authenticator.login_with_uid(uid_input)
                
                # Log attempt
                authenticator.log_login_attempt(uid_input, success)
                
                if success:
                    st.success(f"✅ Welcome {name_input}! Login successful.")
                    st.session_state.authenticated_uid = uid_input
                    # Use user-provided name instead of database name
                    st.session_state.authenticated_user = {
                        "uid": uid_input,
                        "name": name_input,
                        "verified": True,
                        "verification_status": "verified"
                    }
                    st.session_state.dis_mode = "welcome"
                    st.balloons()
                    st.rerun()
                else:
                    st.error(message)
                    # Voice alert for blind users
                    AccessibilityAlerts.speak_alert(f"Authentication failed. {message}")
            else:
                st.error("❌ Please enter both your UID and name")
    
    # ================================================================
    # TAB 2: VOICE-BASED UID INPUT
    # ================================================================
    with tab2:
        st.markdown("### 🎤 Speak Your UID")
        st.caption("Click the mic button and say your UID (e.g., 'UID 001' or '001')")
        
        # Voice input component
        voice_html = """
        <style>
            .mic-btn-large {
                background: linear-gradient(135deg, #22c55e, #16a34a);
                color: #fff;
                border: none;
                border-radius: 50%;
                width: 120px;
                height: 120px;
                font-size: 2.5rem;
                cursor: pointer;
                margin: 20px auto;
                display: block;
                transition: all 0.3s;
                box-shadow: 0 8px 24px rgba(34, 197, 94, 0.4);
            }
            .mic-btn-large:hover {
                transform: scale(1.1);
                box-shadow: 0 12px 32px rgba(34, 197, 94, 0.6);
            }
            .mic-btn-large.listening {
                background: linear-gradient(135deg, #ef4444, #dc2626);
                animation: pulse-mic 1s infinite;
            }
            @keyframes pulse-mic {
                0%, 100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
                50% { box-shadow: 0 0 0 20px rgba(239, 68, 68, 0); }
            }
            .voice-transcript {
                background: rgba(15, 23, 42, 0.9);
                color: #22d3ee;
                border: 2px solid #22d3ee;
                border-radius: 12px;
                padding: 20px;
                text-align: center;
                font-size: 1.3rem;
                font-weight: 700;
                margin: 20px 0;
                min-height: 60px;
            }
            .voice-status {
                color: #94a3b8;
                font-size: 0.95rem;
                text-align: center;
                margin: 10px 0;
            }
        </style>
        
        <button class="mic-btn-large" id="voiceMicBtn" onclick="toggleVoiceInput()">🎤</button>
        <div class="voice-status" id="voiceStatus">🎤 Press the microphone button and speak your UID</div>
        <div class="voice-transcript" id="voiceTranscript">Waiting for input...</div>
        
        <script>
        var voiceRecognition = null;
        var isVoiceListening = false;
        
        function toggleVoiceInput() {
            if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
                alert('Speech recognition not supported. Use Chrome/Edge.');
                return;
            }
            
            if (isVoiceListening) {
                voiceRecognition.stop();
                return;
            }
            
            var SR = window.SpeechRecognition || window.webkitSpeechRecognition;
            voiceRecognition = new SR();
            voiceRecognition.lang = 'en-IN';
            voiceRecognition.continuous = false;
            voiceRecognition.interimResults = true;
            
            voiceRecognition.onstart = function() {
                isVoiceListening = true;
                document.getElementById('voiceMicBtn').classList.add('listening');
                document.getElementById('voiceMicBtn').innerText = '🔴';
                document.getElementById('voiceStatus').innerText = '🎙 Listening... Please say your UID';
                document.getElementById('voiceTranscript').innerText = 'Listening...';
            };
            
            voiceRecognition.onresult = function(e) {
                var final = '';
                for (var i = e.resultIndex; i < e.results.length; i++) {
                    if (e.results[i].isFinal) {
                        final += e.results[i][0].transcript;
                    }
                }
                if (final) {
                    document.getElementById('voiceTranscript').innerText = final.toUpperCase();
                    window.parent.postMessage({
                        type: 'streamlit:setComponentValue',
                        value: final.trim()
                    }, '*');
                }
            };
            
            voiceRecognition.onend = function() {
                isVoiceListening = false;
                document.getElementById('voiceMicBtn').classList.remove('listening');
                document.getElementById('voiceMicBtn').innerText = '🎤';
                document.getElementById('voiceStatus').innerText = '✅ Processing your UID';
            };
            
            voiceRecognition.onerror = function(e) {
                document.getElementById('voiceStatus').innerText = '⚠️ Error: ' + e.error;
                isVoiceListening = false;
                document.getElementById('voiceMicBtn').classList.remove('listening');
            };
            
            voiceRecognition.start();
        }
        </script>
        """
        
        components.html(voice_html, height=300)
        
        # Ensure fields are empty by default
        if "voice_uid_input" not in st.session_state:
            st.session_state.voice_uid_input = ""
        if "voice_name_input" not in st.session_state:
            st.session_state.voice_name_input = ""
        
        # Text input for voice result
        voice_uid = st.text_input(
            "Recognized UID (auto-filled by voice input above) *",
            key="voice_uid_input",
            placeholder="UID001",
            help="Required: Speak your UID in the box above OR type it manually"
        )
        
        # Name input for voice auth
        voice_name = st.text_input(
            "Your Full Name *",
            key="voice_name_input",
            placeholder="Enter your name",
            help="Required: Enter your full name as you wish to be addressed"
        )
        
        st.caption("💡 Tips: Speak clearly, pause between syllables (U-I-D, zero-zero-one)")
        
        if st.button("🔓 Verify Voice & Login", use_container_width=True, type="primary", key="verify_voice"):
            # Validate both fields are provided
            if not voice_uid or not voice_uid.strip():
                st.error("❌ UID is required. Please speak or type your ID card number.")
            elif not voice_name or not voice_name.strip():
                st.error("❌ Name is required. Please enter your full name.")
            elif voice_uid and voice_name:
                # Process voice input (remove spaces, normalize)
                uid_clean = voice_uid.strip().upper().replace(" ", "")
                if "UID" not in uid_clean:
                    uid_clean = "UID" + uid_clean
                
                success, user, message = authenticator.login_with_uid(uid_clean)
                authenticator.log_login_attempt(uid_clean, success)
                
                if success:
                    st.success(f"✅ Welcome {voice_name}! Login successful.")
                    st.session_state.authenticated_uid = uid_clean
                    # Use user-provided name instead of database name
                    st.session_state.authenticated_user = {
                        "uid": uid_clean,
                        "name": voice_name,
                        "verified": True,
                        "verification_status": "verified"
                    }
                    st.session_state.dis_mode = "welcome"
                    st.balloons()
                    st.rerun()
                else:
                    st.error(message)
                    AccessibilityAlerts.speak_alert(message)
    
    # ================================================================
    # TAB 3: QR CODE (FUTURE)
    # ================================================================
    with tab3:
        st.markdown("### 📱 QR Code Scanner (Coming Soon)")
        st.info("""
        🚧 **Future Feature**
        
        Will support:
        - Scan ID card QR code
        - Automatic UID recognition
        - Faster authentication
        
        Coming in next version!
        """)
    
    # ================================================================
    # DEMO CREDENTIALS
    # ================================================================
    st.divider()
    
    with st.expander("ℹ️ Available Test UIDs", expanded=False):
        st.markdown("""
        **Valid UIDs for testing (you must provide your own name):**
        
        - **UID001** - Valid UID for testing
        - **UID002** - Valid UID for testing
        - **UID003** - Valid UID for testing
        - **UID004** - Valid UID for testing
        - **UID005** - Valid UID for testing
        
        **How to test:**
        1. Switch to "Manual Entry" or "Voice Input" tab
        2. Enter a valid UID (e.g., UID001)
        3. **Enter your own name** in the name field
        4. Click "Verify & Login"
        5. System will authenticate and greet you by your provided name
        """)
        
        # Show Firebase connection status
        auth = get_id_authenticator()
        
        st.write(f"✅ **Verified UIDs in System:** {auth.get_all_verified_users_count()}")
        
        # Show system stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🆔 Total UIDs", auth.get_all_verified_users_count())
        with col2:
            st.metric("🔐 Security", "Enabled")
        with col3:
            st.metric("✓ Status", "Active")


def render_authenticated_user_info():
    """
    Display authenticated user information and session details.
    Shows user-provided name and UID.
    """
    if "authenticated_user" not in st.session_state or not st.session_state.authenticated_user:
        return
    
    user = st.session_state.authenticated_user
    
    st.markdown("""
    <div style='background:rgba(34,211,238,0.1); border-left:4px solid #22d3ee;
                border-radius:8px; padding:16px; margin:20px 0;'>
        <div style='color:#22d3ee; font-weight:700; margin-bottom:12px;'>
            ✅ Authenticated Session
        </div>
        <div style='color:#f1f5f9; line-height:1.8;'>
    """, unsafe_allow_html=True)
    
    st.write(f"**🆔 UID:** {user.get('uid')}")
    st.write(f"**👤 Name (Provided by You):** {user.get('name')}")
    st.write(f"**✓ Status:** {user.get('verification_status').upper()}")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Logout button
    if st.button("🔐 Logout", use_container_width=True, key="login_ui_logout"):
        st.session_state.authenticated_uid = None
        st.session_state.authenticated_user = None
        st.session_state.dis_mode = "id_login"
        st.rerun()
