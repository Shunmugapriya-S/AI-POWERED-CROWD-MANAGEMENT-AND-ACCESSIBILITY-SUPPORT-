# -*- coding: utf-8 -*-
# ============================================================
#   DISABLED PERSON ID CARD AUTHENTICATION MODULE
#   Features:
#     - UID/ID Card verification
#     - User authentication before accessing portal
#     - ID validation and database lookup
#     - Voice & text based ID input
#     - Biometric (face recognition) support (optional)
# ============================================================

import streamlit as st
from firebase_manager import get_firebase_manager
from datetime import datetime


# ================================================================
# VERIFIED DISABLED USERS DATABASE
# ================================================================

VERIFIED_DISABLED_USERS = {
    "UID001": {
        "name": "Rajini K",
        "email": "rajini.k@example.com",
        "phone": "+91 9876543210",
        "disability_type": "Mobility Impairment",
        "verification_status": "verified",
        "registration_date": "2025-01-15"
    },
    "UID002": {
        "name": "Arjun S",
        "email": "arjun.s@example.com",
        "phone": "+91 8765432109",
        "disability_type": "Visual Impairment",
        "verification_status": "verified",
        "registration_date": "2025-01-20"
    },
    "UID003": {
        "name": "Priya Devi",
        "email": "priya.devi@example.com",
        "phone": "+91 7654321098",
        "disability_type": "Hearing Impairment",
        "verification_status": "verified",
        "registration_date": "2025-02-01"
    },
    "UID004": {
        "name": "Vikram Kumar",
        "email": "vikram.kumar@example.com",
        "phone": "+91 6543210987",
        "disability_type": "Hand Disability",
        "verification_status": "verified",
        "registration_date": "2025-02-05"
    },
    "UID005": {
        "name": "Lakshmi N",
        "email": "lakshmi.n@example.com",
        "phone": "+91 5432109876",
        "disability_type": "Elderly",
        "verification_status": "verified",
        "registration_date": "2025-02-10"
    },
}


class DisabledIDAuthenticator:
    """
    Authentication system for disabled persons using UID/ID cards.
    Verifies identity before granting access to the accessibility portal.
    """
    
    def __init__(self):
        self.fb = get_firebase_manager()
        self.verified_users = VERIFIED_DISABLED_USERS
    
    # ================================================================
    # ID VERIFICATION OPERATIONS
    # ================================================================
    
    def verify_uid(self, uid):
        """
        EXPLICIT: Verify UID against database.
        Args:
            uid: UID/ID card number
        Returns: User data if found and verified, None otherwise
        """
        if not uid:
            return None
        
        uid = uid.strip().upper()
        
        # Check in verified users database
        if uid in self.verified_users:
            user = self.verified_users[uid].copy()
            user["uid"] = uid
            user["verified"] = True
            user["verification_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return user
        
        # Try Firebase (future: for dynamic user registration)
        if self.fb.initialized:
            try:
                # Could add Firebase lookup here
                pass
            except Exception as e:
                print(f"[Auth] Firebase lookup error: {e}")
        
        return None
    
    def validate_uid_format(self, uid):
        """
        EXPLICIT: Validate UID format.
        Args:
            uid: UID/ID card string
        Returns: True if format valid, False otherwise
        """
        if not uid:
            return False
        
        uid_clean = uid.strip().upper()
        
        # Check format: UID followed by digits (e.g., UID001, UID002)
        if len(uid_clean) >= 5:
            if uid_clean.startswith("UID") and uid_clean[3:].isdigit():
                return True
        
        # Accept plain numbers too
        if uid_clean.isdigit() and len(uid_clean) >= 3:
            uid_formatted = f"UID{uid_clean.zfill(3)}"
            return uid_formatted in self.verified_users
        
        return False
    
    def login_with_uid(self, uid, password=None):
        """
        EXPLICIT: Authenticate user with UID.
        Args:
            uid: UID/ID card number
            password: Optional password (for extra security)
        Returns: Tuple (success: bool, user_data: dict, message: str)
        """
        if not uid:
            return False, None, "❌ UID cannot be empty"
        
        # Validate format
        if not self.validate_uid_format(uid):
            return False, None, "❌ Invalid UID format (use UID001, UID002, etc.)"
        
        # Verify UID
        user = self.verify_uid(uid)
        
        if not user:
            return False, None, f"❌ UID '{uid}' not found in system"
        
        # Check verification status
        if user.get("verification_status") != "verified":
            return False, None, "❌ This ID is not verified. Please contact administration."
        
        # Success
        message = f"✅ Welcome {user.get('name')}! Login successful."
        return True, user, message
    
    def get_user_by_uid(self, uid):
        """
        EXPLICIT: Get user information by UID.
        Args:
            uid: UID/ID card number
        Returns: User dictionary or None
        """
        user = self.verify_uid(uid)
        return user
    
    def log_login_attempt(self, uid, success):
        """
        EXPLICIT: Log login attempt for audit trail.
        Args:
            uid: UID/ID card number
            success: Whether login was successful
        Returns: None (logging only)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "SUCCESS" if success else "FAILED"
        print(f"[Auth Log] {timestamp} - UID: {uid} - Status: {status}")
        
        # Could save to Firebase for audit
        if self.fb.initialized and success:
            try:
                user = self.verify_uid(uid)
                if user:
                    ref = self.fb.db.reference('disabled_login_logs')
                    ref.push({
                        'uid': uid,
                        'user_name': user.get('name'),
                        'timestamp': {'.sv': 'timestamp'},
                        'status': 'success'
                    })
            except Exception as e:
                print(f"[Auth] Logging error: {e}")
    
    # ================================================================
    # FACE RECOGNITION (Optional/Future)
    # ================================================================
    
    def verify_face_match(self, face_image_path):
        """
        EXPLICIT: Verify face against stored photo (future implementation).
        Args:
            face_image_path: Path to captured face image
        Returns: Match confidence (0-1) or None
        """
        # Placeholder for future face recognition
        # Would use face_recognition or similar library
        return None
    
    # ================================================================
    # UTILITY FUNCTIONS
    # ================================================================
    
    def get_all_verified_users_count(self):
        """Get total count of verified disabled users."""
        return len(self.verified_users)
    
    def get_users_by_disability(self, disability_type):
        """Get all users with specific disability type."""
        return [
            user for user in self.verified_users.values()
            if user.get("disability_type") == disability_type
        ]
    
    def is_valid_session(self, uid):
        """Check if a UID is currently in valid session."""
        if "authenticated_uid" in st.session_state:
            return st.session_state.authenticated_uid == uid
        return False


# ================================================================
# SINGLETON INSTANCE
# ================================================================

# Global instance for the authenticator
_authenticator_instance = None

def get_id_authenticator():
    """Return a shared DisabledIDAuthenticator instance."""
    global _authenticator_instance
    if _authenticator_instance is None:
        _authenticator_instance = DisabledIDAuthenticator()
    return _authenticator_instance
