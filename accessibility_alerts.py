# -*- coding: utf-8 -*-
# ============================================================
#   ACCESSIBILITY ALERTS MODULE
#   Provides specialized alert systems for deaf and blind users:
#     - DEAF: Visual alerts with animations and high contrast
#     - BLIND: Voice/audio alerts via text-to-speech
# ============================================================

import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime


class AccessibilityAlerts:
    """Handle alerts for deaf and blind passengers"""
    
    @staticmethod
    def speak_alert(text, speed=0.9):
        """Play audio alert using browser Text-to-Speech"""
        safe = text.replace("'", "\\'").replace("\n", " ")
        components.html(f"""
        <script>
        (function() {{
            window.speechSynthesis.cancel();
            var u = new SpeechSynthesisUtterance('{safe}');
            u.lang = 'en-IN';
            u.rate = {speed};
            u.pitch = 1.0;
            u.volume = 1.0;
            window.speechSynthesis.speak(u);
        }})();
        </script>
        """, height=0)
    
    @staticmethod
    def show_visual_alert_deaf(title, message, alert_type="success"):
        """
        Show HIGH CONTRAST visual alert for deaf users.
        alert_type: success / info / warning / error
        """
        colors = {
            "success": {"bg": "#10b981", "border": "#059669", "icon": "✅"},
            "info": {"bg": "#3b82f6", "border": "#1e40af", "icon": "ℹ️"},
            "warning": {"bg": "#f59e0b", "border": "#d97706", "icon": "⚠️"},
            "error": {"bg": "#ef4444", "border": "#991b1b", "icon": "❌"},
        }
        
        style = colors.get(alert_type, colors["info"])
        
        st.markdown(f"""
        <div style='
            background-color: {style["bg"]};
            border: 4px solid {style["border"]};
            border-radius: 12px;
            padding: 24px;
            margin: 20px 0;
            box-shadow: 0 0 30px {style["bg"]}40;
            text-align: center;
        '>
            <div style='
                font-size: 2.5rem;
                margin-bottom: 16px;
                font-weight: bold;
            '>{style["icon"]}</div>
            <div style='
                color: #ffffff;
                font-size: 1.5rem;
                font-weight: 900;
                margin-bottom: 12px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            '>{title}</div>
            <div style='
                color: #ffffff;
                font-size: 1.1rem;
                font-weight: 600;
                line-height: 1.8;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
            '>{message}</div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def show_request_sent_alert_deaf(route, from_stop, to_stop, arrival_time, disability_type, passenger_lat, passenger_lng):
        """Visual alert for deaf users when request is sent"""
        AccessibilityAlerts.show_visual_alert_deaf(
            title="REQUEST SENT TO DRIVERS",
            message=f"""
🚌 Route: <strong>{route}</strong><br>
🛫 Boarding: <strong>{from_stop}</strong><br>
🏁 Going to: <strong>{to_stop}</strong><br>
⏱️ Arrival: <strong>{arrival_time}</strong><br>
♿ Support Type: <strong>{disability_type}</strong><br>
📍 Location shared with drivers
            """,
            alert_type="success"
        )
    
    @staticmethod
    def show_request_sent_alert_blind(route, from_stop, to_stop, arrival_time, disability_type):
        """Audio alert for blind users when request is sent"""
        message = f"Your accessibility request has been sent successfully. You requested {disability_type} support on route {route}. Boarding at {from_stop} and going to {to_stop}. The bus is estimated to arrive at {arrival_time}. Please wait at the boarding point."
        AccessibilityAlerts.speak_alert(message, speed=0.85)
    
    @staticmethod
    def show_driver_acknowledged_alert_deaf(driver_name, driver_eta, driver_vehicle):
        """Visual alert for deaf users when driver acknowledges"""
        AccessibilityAlerts.show_visual_alert_deaf(
            title="DRIVER ACKNOWLEDGED YOUR REQUEST!",
            message=f"""
✅ Driver <strong>{driver_name}</strong> has confirmed<br>
🚗 Vehicle: <strong>{driver_vehicle}</strong><br>
⏱️ Arriving in: <strong>{driver_eta} minutes</strong><br>
📍 Driver is on the way to pick you up
            """,
            alert_type="success"
        )
    
    @staticmethod
    def show_driver_acknowledged_alert_blind(driver_name, driver_eta, driver_vehicle):
        """Audio alert for blind users when driver acknowledges"""
        message = f"Great news! Driver {driver_name} has acknowledged your request and is on the way. The vehicle is {driver_vehicle}. They will arrive in approximately {driver_eta} minutes. Please prepare to board."
        AccessibilityAlerts.speak_alert(message, speed=0.85)
    
    @staticmethod
    def show_driver_nearby_alert_deaf(driver_name, distance_meters):
        """Visual alert for deaf users when driver is nearby"""
        AccessibilityAlerts.show_visual_alert_deaf(
            title="DRIVER IS NEARBY!",
            message=f"""
🚨 <strong>{driver_name}</strong> is only <strong>{distance_meters}m away</strong><br>
🔔 Please be ready at the boarding point<br>
👀 Look for the vehicle<br>
🤝 Wave or signal to the driver
            """,
            alert_type="warning"
        )
    
    @staticmethod
    def show_driver_nearby_alert_blind(driver_name, distance_meters):
        """Audio alert for blind users when driver is nearby"""
        message = f"Alert! Driver {driver_name} is very close, only {distance_meters} meters away. Get ready at the boarding point. Your driver will be here in just a moment. Please be prepared."
        AccessibilityAlerts.speak_alert(message, speed=0.75)
    
    @staticmethod
    def show_driver_arrived_alert_deaf(driver_name, vehicle_color, vehicle_number):
        """Visual alert for deaf users when driver arrives"""
        AccessibilityAlerts.show_visual_alert_deaf(
            title="DRIVER HAS ARRIVED!",
            message=f"""
🎉 <strong>{driver_name}</strong> has arrived at your location<br>
🚗 <strong>{vehicle_color}</strong> bus<br>
🏷️ Number: <strong>{vehicle_number}</strong><br>
👋 Please get in the bus
            """,
            alert_type="success"
        )
    
    @staticmethod
    def show_driver_arrived_alert_blind(driver_name, vehicle_color, vehicle_number):
        """Audio alert for blind users when driver arrives"""
        message = f"Excellent! Your driver {driver_name} has arrived at your location. It is a {vehicle_color} bus, number {vehicle_number}. Please board the bus now."
        AccessibilityAlerts.speak_alert(message, speed=0.85)
    
    @staticmethod
    def show_tracking_status_deaf(driver_location_status, minutes_away):
        """Show live tracking status for deaf users"""
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, rgba(59,130,246,0.15), rgba(34,211,238,0.15));
            border: 3px solid #3b82f6;
            border-radius: 12px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 0 20px rgba(59,130,246,0.2);
        '>
            <div style='color: #3b82f6; font-size: 1.3rem; font-weight: 900; margin-bottom: 10px;'>
                📍 LIVE TRACKING
            </div>
            <div style='color: #1e293b; font-size: 1.1rem; font-weight: 700;'>
                {driver_location_status}
            </div>
            <div style='color: #475569; font-size: 1rem; margin-top: 8px;'>
                ⏱️ Arriving in <strong>{minutes_away}</strong> minutes
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def show_tracking_status_blind(driver_location_description, minutes_away):
        """Announce live tracking status for blind users"""
        message = f"Tracking update: {driver_location_description}. Your driver is arriving in {minutes_away} minutes."
        AccessibilityAlerts.speak_alert(message, speed=0.9)
    
    @staticmethod
    def show_accessibility_support_active_deaf(support_type):
        """Show confirmation that accessibility support is active - for deaf users"""
        support_icons = {
            "blind": "👁️",
            "deaf": "👂",
            "hand_disabled": "✋",
            "leg_disabled": "🦵"
        }
        icon = support_icons.get(support_type, "♿")
        
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, rgba(16,185,129,0.15), rgba(6,182,212,0.15));
            border: 3px solid #10b981;
            border-radius: 12px;
            padding: 16px;
            margin: 16px 0;
            text-align: center;
        '>
            <div style='font-size: 2rem; margin-bottom: 8px;'>{icon}</div>
            <div style='color: #10b981; font-size: 1rem; font-weight: 900;'>
                ✅ ACCESSIBILITY SUPPORT ACTIVE
            </div>
            <div style='color: #047857; font-size: 0.95rem; margin-top: 8px; font-weight: 600;'>
                Driver will provide special assistance for your needs
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def show_accessibility_support_active_blind(support_type):
        """Announce that accessibility support is active - for blind users"""
        support_names = {
            "blind": "blind",
            "deaf": "deaf",
            "hand_disabled": "hand disability",
            "leg_disabled": "mobility"
        }
        support_name = support_names.get(support_type, "accessibility")
        message = f"Your {support_name} support is now active. The driver will provide you with special assistance."
        AccessibilityAlerts.speak_alert(message, speed=0.9)


# Helper functions for easy integration

def alert_request_sent(disability_type, route, from_stop, to_stop, arrival_time, passenger_lat, passenger_lng):
    """
    Send appropriate alert based on disability type
    """
    if disability_type == "deaf":
        AccessibilityAlerts.show_request_sent_alert_deaf(
            route, from_stop, to_stop, arrival_time, "Deaf", passenger_lat, passenger_lng
        )
    elif disability_type == "blind":
        AccessibilityAlerts.show_request_sent_alert_blind(
            route, from_stop, to_stop, arrival_time, "Blind"
        )


def alert_driver_acknowledged(disability_type, driver_name, driver_eta, driver_vehicle):
    """
    Alert when driver acknowledges the request
    """
    if disability_type == "deaf":
        AccessibilityAlerts.show_driver_acknowledged_alert_deaf(
            driver_name, driver_eta, driver_vehicle
        )
    elif disability_type == "blind":
        AccessibilityAlerts.show_driver_acknowledged_alert_blind(
            driver_name, driver_eta, driver_vehicle
        )


def alert_driver_nearby(disability_type, driver_name, distance_meters):
    """
    Alert when driver is approaching
    """
    if disability_type == "deaf":
        AccessibilityAlerts.show_driver_nearby_alert_deaf(driver_name, distance_meters)
    elif disability_type == "blind":
        AccessibilityAlerts.show_driver_nearby_alert_blind(driver_name, distance_meters)


def alert_driver_arrived(disability_type, driver_name, vehicle_color, vehicle_number):
    """
    Alert when driver has arrived
    """
    if disability_type == "deaf":
        AccessibilityAlerts.show_driver_arrived_alert_deaf(driver_name, vehicle_color, vehicle_number)
    elif disability_type == "blind":
        AccessibilityAlerts.show_driver_arrived_alert_blind(driver_name, vehicle_color, vehicle_number)
