# -*- coding: utf-8 -*-
# ============================================================
#   REQUEST MANAGER MODULE
#   Explicit features for handling pickup requests
#   - Fetch requests with filters
#   - Display request details
#   - Update request status with actions
#   - Track request priority
# ============================================================

import streamlit as st
from datetime import datetime
from firebase_manager import get_firebase_manager


class RequestManager:
    """Explicit request management with clear operations."""
    
    def __init__(self):
        self.fb = get_firebase_manager()
        self.request_cache = {}
    
    # ================================================================
    # EXPLICIT FETCHING OPERATIONS
    # ================================================================
    
    def fetch_all_requests(self):
        """
        EXPLICIT: Fetch all pending pickup requests.
        Returns: List of request dictionaries
        """
        if not self.fb.initialized:
            return []
        return self.fb.get_active_requests()
    
    def fetch_requests_by_route(self, route_id):
        """
        EXPLICIT: Fetch requests for a specific route.
        Args:
            route_id: The bus route ID/number
        Returns: List of requests for that route
        """
        if not self.fb.initialized:
            return []
        return self.fb.get_active_requests(route=route_id)
    
    def fetch_request_by_id(self, request_id):
        """
        EXPLICIT: Fetch a single request by ID.
        Args:
            request_id: Unique request ID from Firebase
        Returns: Request dictionary or None
        """
        all_requests = self.fetch_all_requests()
        for req in all_requests:
            if req.get("id") == request_id:
                return req
        return None
    
    def fetch_requests_by_priority(self):
        """
        EXPLICIT: Fetch all requests sorted by priority.
        Priority: Elderly > Wheelchair > Visual > Hearing > Mobility > Other
        Returns: Sorted list of requests
        """
        requests = self.fetch_all_requests()
        
        priority_order = {
            "Elderly": 1,
            "Wheelchair User": 2,
            "Visual Impairment": 3,
            "Hearing Impairment": 4,
            "Mobility Issue": 5,
            "Other": 6
        }
        
        def get_priority(req):
            disability = req.get("disability_type", "Other")
            return priority_order.get(disability, 99)
        
        return sorted(requests, key=get_priority)
    
    def fetch_urgent_requests(self):
        """
        EXPLICIT: Fetch only urgent/high-priority requests.
        Returns: List of high-priority requests
        """
        urgent_disabilities = ["Elderly", "Wheelchair User", "Visual Impairment"]
        all_requests = self.fetch_all_requests()
        return [r for r in all_requests if r.get("disability_type") in urgent_disabilities]
    
    # ================================================================
    # EXPLICIT ACTION OPERATIONS
    # ================================================================
    
    def accept_request(self, request_id, driver_name="Driver"):
        """
        EXPLICIT: Accept a pickup request.
        Args:
            request_id: Request ID
            driver_name: Name of driver accepting
        Returns: Success boolean
        """
        success = self.fb.update_request_status(
            request_id,
            "acknowledged",
            f"Accepted by {driver_name} at {datetime.now().strftime('%H:%M:%S')}"
        )
        return success
    
    def complete_request(self, request_id, driver_name="Driver", notes=""):
        """
        EXPLICIT: Mark request as complete.
        Args:
            request_id: Request ID
            driver_name: Name of driver completing
            notes: Additional completion notes
        Returns: Success boolean
        """
        completion_note = f"Completed by {driver_name} at {datetime.now().strftime('%H:%M:%S')}"
        if notes:
            completion_note += f" - {notes}"
        
        success = self.fb.update_request_status(request_id, "completed", completion_note)
        return success
    
    def reject_request(self, request_id, driver_name="Driver", reason=""):
        """
        EXPLICIT: Reject/decline a pickup request.
        Args:
            request_id: Request ID
            driver_name: Name of driver declining
            reason: Reason for rejection
        Returns: Success boolean
        """
        rejection_note = f"Declined by {driver_name} at {datetime.now().strftime('%H:%M:%S')}"
        if reason:
            rejection_note += f" - Reason: {reason}"
        
        success = self.fb.update_request_status(request_id, "declined", rejection_note)
        return success
    
    def snooze_request(self, request_id, minutes=5):
        """
        EXPLICIT: Snooze a request for later action.
        Args:
            request_id: Request ID
            minutes: Snooze duration in minutes
        Returns: Success boolean
        """
        success = self.fb.update_request_status(
            request_id,
            "snoozed",
            f"Snoozed for {minutes} minutes until {datetime.now().strftime('%H:%M:%S')}"
        )
        return success
    
    # ================================================================
    # EXPLICIT DATA RETRIEVAL OPERATIONS
    # ================================================================
    
    def get_request_distance(self, request_id, driver_lat, driver_lng):
        """
        EXPLICIT: Calculate distance from driver to passenger.
        Args:
            request_id: Request ID
            driver_lat: Driver's latitude
            driver_lng: Driver's longitude
        Returns: Distance in km or None
        """
        request = self.fetch_request_by_id(request_id)
        if not request:
            return None
        
        passenger_lat = request.get("passenger_lat")
        passenger_lng = request.get("passenger_lng")
        
        if not passenger_lat or not passenger_lng:
            return None
        
        from math import radians, cos, sin, asin, sqrt
        
        lon1, lat1, lon2, lat2 = map(
            radians,
            [driver_lng, driver_lat, passenger_lng, passenger_lat]
        )
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371  # Radius of earth in kilometers
        return c * r
    
    def get_request_summary(self, request_id):
        """
        EXPLICIT: Get a formatted summary of a request.
        Args:
            request_id: Request ID
        Returns: Dictionary with formatted information
        """
        request = self.fetch_request_by_id(request_id)
        if not request:
            return None
        
        return {
            "id": request.get("id", "N/A"),
            "passenger_name": request.get("user_name", "Unknown"),
            "location": request.get("location", "Unknown"),
            "boarding_stop": request.get("boarding_stop", "TBD"),
            "destination_stop": request.get("destination_stop", "TBD"),
            "disability_type": request.get("disability_type", "Not specified"),
            "status": request.get("status", "pending"),
            "contact": request.get("phone", "No phone"),
            "email": request.get("email", "No email"),
            "latitude": request.get("passenger_lat"),
            "longitude": request.get("passenger_lng"),
            "maps_link": request.get("passenger_gmaps_url", ""),
            "photo_url": request.get("photo_url", None),
            "requested_at": request.get("timestamp", "")
        }
    
    # ================================================================
    # STATISTICS & ANALYTICS
    # ================================================================
    
    def get_request_stats(self):
        """
        EXPLICIT: Get summary statistics of all requests.
        Returns: Dictionary with stats
        """
        all_requests = self.fetch_all_requests()
        
        stats = {
            "total": len(all_requests),
            "pending": sum(1 for r in all_requests if r.get("status") == "pending"),
            "acknowledged": sum(1 for r in all_requests if r.get("status") == "acknowledged"),
            "completed": sum(1 for r in all_requests if r.get("status") == "completed"),
            "declined": sum(1 for r in all_requests if r.get("status") == "declined"),
            "by_disability": {}
        }
        
        # Count by disability type
        for req in all_requests:
            disability = req.get("disability_type", "Other")
            stats["by_disability"][disability] = stats["by_disability"].get(disability, 0) + 1
        
        return stats
    
    def get_driver_performance(self, driver_name=None):
        """
        EXPLICIT: Get driver performance metrics.
        Args:
            driver_name: Filter by specific driver (optional)
        Returns: Performance statistics
        """
        all_requests = self.fetch_all_requests()
        
        completed = [
            r for r in all_requests 
            if r.get("status") == "completed"
        ]
        
        return {
            "total_handled": len(completed),
            "average_completion_time": "N/A",  # Would need timestamp tracking
            "customer_satisfaction": "5/5 ⭐"  # Placeholder
        }


# ---- Cached Singleton ----

@st.cache_resource
def get_request_manager():
    """Return a shared (cached) RequestManager instance."""
    return RequestManager()
