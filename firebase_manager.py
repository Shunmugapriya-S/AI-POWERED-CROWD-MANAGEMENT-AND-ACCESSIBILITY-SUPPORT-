# -*- coding: utf-8 -*-
# ============================================================
#   FIREBASE MANAGER MODULE
#   Handles:
#     - Firebase Admin SDK initialization
#     - Crowd status updates for buses
#     - Pickup request CRUD (create, read, update)
#     - FCM push notifications to drivers
# ============================================================

import os
import time
import firebase_admin
import streamlit as st
from firebase_admin import credentials, db, storage, messaging

DATABASE_URL = 'https://busminiproj-default-rtdb.firebaseio.com/'
CERT_PATH = 'firebase_key.json'


class FirebaseManager:
    def __init__(self, cert_path=CERT_PATH):
        self.app = None
        self.cert_path = cert_path
        self.initialized = False
        self.storage_bucket = None
        self._initialize()

    def _initialize(self):
        """Initialize Firebase Admin SDK."""
        try:
            if not os.path.exists(self.cert_path):
                print(f"[Firebase] Key not found: {self.cert_path}. Running in OFFLINE mode.")
                return False

            if not firebase_admin._apps:
                cred = credentials.Certificate(self.cert_path)
                # Auto-detect storage bucket from database URL
                bucket = None
                try:
                    host = DATABASE_URL.split('//')[-1].split('/')[0]
                    project = host.split('.')[0]
                    project = project.replace('-default-rtdb', '').replace('-rtdb', '')
                    bucket = f"{project}.appspot.com"
                except Exception:
                    bucket = None

                init_kwargs = {'databaseURL': DATABASE_URL}
                if bucket:
                    init_kwargs['storageBucket'] = bucket

                self.app = firebase_admin.initialize_app(cred, init_kwargs)
                self.storage_bucket = bucket
            else:
                self.app = firebase_admin.get_app()

            self.initialized = True
            print("[Firebase] Initialized successfully.")
            return True
        except Exception as e:
            print(f"[Firebase] Error initializing: {e}")
            return False

    # ---- Crowd Status ----

    def update_crowd_status(self, bus_id, count, level):
        """Push live crowd data for a bus to Firebase."""
        if not self.initialized:
            return False
        try:
            ref = db.reference(f'buses/{bus_id}/crowd')
            ref.update({
                'count': count,
                'level': level,
                'last_update': {'.sv': 'timestamp'}
            })
            return True
        except Exception as e:
            print(f"[Firebase] Error updating crowd: {e}")
            return False

    # ---- Photo Upload ----

    def _upload_photo_bytes(self, photo_bytes, dest_path):
        """Upload image bytes to Firebase Storage."""
        if not self.initialized or not self.storage_bucket:
            return None
        try:
            bucket = storage.bucket()
            blob = bucket.blob(dest_path)
            blob.upload_from_string(photo_bytes, content_type='image/jpeg')
            try:
                blob.make_public()
                return blob.public_url
            except Exception:
                return f'gs://{bucket.name}/{dest_path}'
        except Exception as e:
            print(f"[Firebase] Error uploading photo: {e}")
            return None

    # ---- Pickup Requests ----

    def send_pickup_request(
        self,
        user_name,
        location,
        route,
        disability_type,
        photo_url=None,
        email=None,
        phone=None,
        boarding_stop=None,
        destination_stop=None,
        passenger_lat=None,
        passenger_lng=None
    ):
        """Submit a new pickup request to Firebase Realtime DB."""
        if not self.initialized:
            return False
        try:
            gmaps_url = ""
            if passenger_lat is not None and passenger_lng is not None:
                gmaps_url = f"https://www.google.com/maps?q={passenger_lat},{passenger_lng}"
                print(f"[Firebase] 📍 Storing passenger location: LAT={passenger_lat}, LNG={passenger_lng}")
            else:
                print(f"[Firebase] ⚠️ WARNING: Passenger location missing - LAT={passenger_lat}, LNG={passenger_lng}")

            ref = db.reference('pickup_requests').push()
            ref.set({
                'user_name': user_name,
                'email': email or "",
                'phone': phone or "",
                'location': location,
                'route': route,
                'disability_type': disability_type,
                'boarding_stop': boarding_stop or location,
                'destination_stop': destination_stop or "",
                'passenger_lat': passenger_lat,
                'passenger_lng': passenger_lng,
                'passenger_gmaps_url': gmaps_url,
                'photo_url': photo_url,
                'status': 'pending',
                'timestamp': {'.sv': 'timestamp'}
            })
            request_key = ref.key
            print(f"[Firebase] ✅ Request created with ID: {request_key}")

            # Send FCM push notification to drivers
            try:
                topic = f"drivers_{route}" if route else 'drivers'
                message = messaging.Message(
                    notification=messaging.Notification(
                        title='🚌 New Pickup Request',
                        body=f'Pickup at {location} for route {route}'
                    ),
                    topic=topic,
                    data={'request_id': request_key, 'route': str(route) if route else ''}
                )
                messaging.send(message)
                print(f"[Firebase] FCM sent to topic: {topic}")
            except Exception as e:
                print(f"[Firebase] FCM warning: {e}")

            return request_key
        except Exception as e:
            print(f"[Firebase] Error sending pickup request: {e}")
            return False

    def get_active_requests(self, route=None):
        """Fetch all pending pickup requests (optionally filtered by route)."""
        if not self.initialized:
            return []
        try:
            ref = db.reference('pickup_requests')
            query = ref.order_by_child('status').equal_to('pending').get()
            if not query:
                return []
            result = []
            for key, val in query.items():
                if route is None or val.get('route') == route:
                    val['id'] = key
                    # Log location data
                    lat = val.get('passenger_lat')
                    lng = val.get('passenger_lng')
                    if lat and lng:
                        print(f"[Firebase] 📍 Request {key} has location: {lat}, {lng}")
                    else:
                        print(f"[Firebase] ⚠️ Request {key} missing location data - LAT={lat}, LNG={lng}")
                    result.append(val)
            print(f"[Firebase] ✅ Retrieved {len(result)} active requests")
            return result
        except Exception as e:
            print(f"[Firebase] Error getting active requests: {e}")
            return []

    def get_all_requests(self):
        """Fetch all pickup requests (for admin use)."""
        if not self.initialized:
            return []
        try:
            ref = db.reference('pickup_requests')
            query = ref.get()
            if not query:
                return []
            result = []
            for key, val in query.items():
                val['id'] = key
                result.append(val)
            try:
                result.sort(key=lambda r: r.get('timestamp', 0), reverse=True)
            except Exception:
                pass
            return result
        except Exception as e:
            print(f"[Firebase] Error getting all requests: {e}")
            return []

    def update_request_status(self, request_id, status, admin_note=None):
        """Update a pickup request's status and optionally add an admin note."""
        if not self.initialized:
            return False
        try:
            ref = db.reference(f'pickup_requests/{request_id}')
            update_data = {
                'status': status,
                'last_update': {'.sv': 'timestamp'}
            }
            if admin_note:
                update_data['admin_note'] = admin_note
            ref.update(update_data)
            return True
        except Exception as e:
            print(f"[Firebase] Error updating status: {e}")
            return False


# ---- Cached Singleton ----

@st.cache_resource
def get_firebase_manager():
    """Return a shared (cached) FirebaseManager instance."""
    return FirebaseManager()
