# 🎯 ACCESSIBILITY ALERTS IMPLEMENTATION GUIDE

## Overview

The system now provides **specialized accessibility alerts** for deaf and blind users:

- **👁️ DEAF USERS**: Receive **HIGH-CONTRAST VISUAL ALERTS** with large text, bright colors, and animations
- **🔊 BLIND USERS**: Receive **VOICE/AUDIO ALERTS** via Text-to-Speech (TTS) with clear spoken instructions

---

## 📁 New Module Created

### `accessibility_alerts.py`

Main module handling all accessibility alert systems.

**Features:**

- `AccessibilityAlerts` class with static methods for different alert types
- Specialized alert functions for deaf users (visual)
- Specialized alert functions for blind users (audio)
- Helper functions for easy integration

---

## 🎙️ Alert Types

### 1️⃣ **REQUEST SENT ALERTS**

When a passenger sends an accessibility request:

#### For DEAF Users:

```python
AccessibilityAlerts.show_request_sent_alert_deaf(
    route="Route 5A",
    from_stop="Central Station",
    to_stop="Airport",
    arrival_time="02:30 PM",
    disability_type="Deaf Support",
    passenger_lat=13.1234,
    passenger_lng=80.5678
)
```

✅ **Display**: High-contrast visual card with:

- 🟢 Bright green background (#10b981)
- 🔤 Large, bold white text
- 📍 GPS coordinates clearly displayed
- 🗺️ Google Maps reference

#### For BLIND Users:

```python
AccessibilityAlerts.show_request_sent_alert_blind(
    route="Route 5A",
    from_stop="Central Station",
    to_stop="Airport",
    arrival_time="02:30 PM",
    disability_type="Blind"
)
```

🔊 **Audio Output**: Clear spoken announcement:

> "Your accessibility request has been sent successfully. You requested Blind support on route Route 5A. Boarding at Central Station and going to Airport. The bus is estimated to arrive at 02:30 PM. Please wait at the boarding point."

---

### 2️⃣ **DRIVER ACKNOWLEDGED ALERTS**

When driver confirms they're responding to request:

#### For DEAF Users:

```python
AccessibilityAlerts.show_driver_acknowledged_alert_deaf(
    driver_name="Arjun",
    driver_eta="8",
    driver_vehicle="Tamil Nadu Bus No. 5A"
)
```

✅ **Display**: Green success card with driver name, vehicle, and ETA

#### For BLIND Users:

```python
AccessibilityAlerts.show_driver_acknowledged_alert_blind(
    driver_name="Arjun",
    driver_eta="8",
    driver_vehicle="Tamil Nadu Bus No. 5A"
)
```

🔊 **Audio**: Confirms driver is on the way

---

### 3️⃣ **DRIVER NEARBY ALERTS**

When driver is approaching (within 500m):

#### For DEAF Users:

```python
AccessibilityAlerts.show_driver_nearby_alert_deaf(
    driver_name="Arjun",
    distance_meters=450
)
```

✅ **Display**: Orange warning card - "DRIVER IS NEARBY!"

#### For BLIND Users:

```python
AccessibilityAlerts.show_driver_nearby_alert_blind(
    driver_name="Arjun",
    distance_meters=450
)
```

🔊 **Audio**: "Alert! Driver Arjun is very close, only 450 meters away..."

---

### 4️⃣ **DRIVER ARRIVED ALERTS**

When driver reaches passenger location:

#### For DEAF Users:

```python
AccessibilityAlerts.show_driver_arrived_alert_deaf(
    driver_name="Arjun",
    vehicle_color="Red",
    vehicle_number="TN-05-AB-2023"
)
```

✅ **Display**: Bright green card - "DRIVER HAS ARRIVED!"

#### For BLIND Users:

```python
AccessibilityAlerts.show_driver_arrived_alert_blind(
    driver_name="Arjun",
    vehicle_color="Red",
    vehicle_number="TN-05-AB-2023"
)
```

🔊 **Audio**: "Excellent! Your driver Arjun has arrived..."

---

### 5️⃣ **ACCESSIBILITY SUPPORT ACTIVE**

Confirmation that support mode is enabled:

#### For DEAF Users:

```python
AccessibilityAlerts.show_accessibility_support_active_deaf(
    support_type="deaf"
)
```

✅ **Display**: Green badge with accessibility icon

#### For BLIND Users:

```python
AccessibilityAlerts.show_accessibility_support_active_blind(
    support_type="blind"
)
```

🔊 **Audio**: Announces support status

---

## 🔌 Integration Points

### In `disabled_page.py` - Passenger Portal

When request is sent, the system now calls:

```python
from accessibility_alerts import AccessibilityAlerts

if st.session_state.dis_type == "deaf":
    # Visual alert for deaf users
    AccessibilityAlerts.show_request_sent_alert_deaf(...)

elif st.session_state.dis_type == "blind":
    # Voice alert for blind users
    AccessibilityAlerts.show_request_sent_alert_blind(...)
```

### In `driver_page.py` - Driver Portal

When showing pending requests, specialized alerts are shown:

```python
from accessibility_alerts import AccessibilityAlerts

if disability == "deaf":
    AccessibilityAlerts.show_visual_alert_deaf(
        title="DEAF PASSENGER ALERT",
        message="...",
        alert_type="warning"
    )

elif disability == "blind":
    AccessibilityAlerts.speak_alert("...")
```

---

## 🎨 Visual Alert Design

### For DEAF Users - HIGH CONTRAST

```
┌─────────────────────────────────┐
│ ✅  (Large Icon)                │
│ BOLD TITLE TEXT                 │
│                                 │
│ 🚌 Route: <strong>name</strong> │
│ 🛫 Boarding: <strong>stop</strong>
│ 🏁 Destination: <strong>stop</strong>
│                                 │
│ Colors: Bright (Green/Blue/Red) │
│ Shadow: Strong box-shadow       │
│ Font: Bold, Large (1.5rem+)     │
│ Border: 4px thick, bright color │
└─────────────────────────────────┘
```

### For BLIND Users - AUDIO

```
Text-to-Speech (TTS) Properties:
- Language: English (en-IN - Indian accent)
- Speed: 0.75-0.9 (slower for clarity)
- Pitch: 1.0 (normal)
- Volume: 1.0 (maximum)
```

---

## 💡 Special Features

### 1. High Contrast for Deaf Users

```css
/* Bright, distinct colors */
background-color: #10b981; /* Green */
border: 4px solid #059669;
color: #ffffff; /* Pure white text */
font-weight: 900;
font-size: 1.5rem;
box-shadow: 0 0 30px rgba color;
```

### 2. Clear Voice for Blind Users

```python
def speak_alert(text, speed=0.9):
    """
    Mobile-friendly TTS that:
    - Cancels previous speech
    - Uses Indian English accent
    - Slow speed (0.75-0.9) for clarity
    - Maximum volume
    """
```

### 3. Accessibility Support Status

```python
AccessibilityAlerts.show_accessibility_support_active_deaf(
    support_type="deaf/blind/hand_disabled/leg_disabled"
)
```

Shows passenger/driver that special assistance is active.

---

## 📱 Integration Workflow

### Passenger Journey - DEAF USER

```
1. Login → Select Disability: "Deaf"
2. Select Route & Stops
3. Send Request
   ↓
4. VISUAL ALERT: "REQUEST SENT TO DRIVERS"
   - Bright cyan/blue high-contrast display
   - Shows route, stops, GPS coordinates
   ↓
5. Driver acknowledges
   ↓
6. VISUAL ALERT: "DRIVER HAS ACKNOWLEDGED"
   - Shows driver name, vehicle details
   ↓
7. Driver nearby (500m)
   ↓
8. VISUAL ALERT: "DRIVER IS NEARBY!"
   - Orange warning with distance
   ↓
9. Driver arrived
   ↓
10. VISUAL ALERT: "DRIVER HAS ARRIVED!"
    - Green success with vehicle details
```

### Passenger Journey - BLIND USER

```
1. Login → Select Disability: "Blind"
2. Select Route & Stops
3. Send Request
   ↓
4. VOICE ALERT: "Your request has been sent..."
   - TTS reads all request details
   ↓
5. Driver acknowledges
   ↓
6. VOICE ALERT: "Driver has acknowledged..."
   - TTS announces driver details
   ↓
7. Driver nearby
   ↓
8. VOICE ALERT: "Driver is very close..."
   - TTS gives distance information
   ↓
9. Driver arrived
   ↓
10. VOICE ALERT: "Driver has arrived..."
    - TTS gives final instructions
```

### Driver Journey - PENDING REQUEST ARRIVES

```
1. New accessibility request from passenger
   ↓
2. Check disability type:

   IF DEAF PASSENGER:
   - Show BRIGHT RED/ORANGE visual alert
   - Display: "DEAF PASSENGER ALERT"
   - Instructions: Use visual signals, lights, signs
   - Screen communication only

   IF BLIND PASSENGER:
   - Play VOICE ALERT via TTS
   - Message: Clear instructions with passenger details
   - Instructions: Use voice + honk clearly
   - Prepare for voice communication

   IF OTHER:
   - Play standard voice alert
   - Show normal visual alert
```

---

## 🚀 Usage Examples

### Example 1: Send Request (Passenger)

```python
# In disabled_page.py - _send_request_to_driver()
if st.session_state.dis_type == "deaf":
    AccessibilityAlerts.show_request_sent_alert_deaf(
        route=route_option,
        from_stop=from_stop,
        to_stop=to_stop,
        arrival_time=arrival.strftime('%I:%M %p'),
        disability_type=disability_type_text,
        passenger_lat=passenger_lat,
        passenger_lng=passenger_lng
    )
elif st.session_state.dis_type == "blind":
    AccessibilityAlerts.show_request_sent_alert_blind(
        route=route_option,
        from_stop=from_stop,
        to_stop=to_stop,
        arrival_time=arrival.strftime('%I:%M %p'),
        disability_type=disability_type_text
    )
```

### Example 2: Show Pending Request Alerts (Driver)

```python
# In driver_page.py - render_driver_requests()
if disability == "deaf":
    AccessibilityAlerts.show_visual_alert_deaf(
        title=f"DEAF PASSENGER ALERT - {user_name.upper()}",
        message=f"...",
        alert_type="warning"
    )
elif disability == "blind":
    AccessibilityAlerts.speak_alert(blind_alert_msg)
```

---

## ⚙️ Configuration

### Text-to-Speech Settings

```python
# Language & speed can be customized:
u.lang = 'en-IN'    # Indian English
u.rate = 0.85       # 0.5 (slow) to 2 (fast)
u.pitch = 1.0       # 0.5 to 2
u.volume = 1.0      # 0 to 1
```

### Alert Colors

```python
colors = {
    "success": {"bg": "#10b981", "border": "#059669", "icon": "✅"},
    "info": {"bg": "#3b82f6", "border": "#1e40af", "icon": "ℹ️"},
    "warning": {"bg": "#f59e0b", "border": "#d97706", "icon": "⚠️"},
    "error": {"bg": "#ef4444", "border": "#991b1b", "icon": "❌"},
}
```

---

## 📊 Testing Checklist

### Test for DEAF Users

- [ ] Request sent → Visual alert displays (bright colors, high contrast)
- [ ] Driver acknowledges → Visual update shows on screen
- [ ] Driver nearby → Orange warning alert appears
- [ ] Driver arrives → Green success alert displays
- [ ] All text is readable (font size > 1.1rem, bold)
- [ ] Colors are distinct and accessible
- [ ] Alert updates happen without sound

### Test for BLIND Users

- [ ] Request sent → Voice announces all details clearly
- [ ] Driver acknowledges → Voice confirms driver is coming
- [ ] Driver nearby → Voice announces distance/time
- [ ] Driver arrives → Voice gives final boarding instructions
- [ ] Audio is clear and at normal volume
- [ ] Speech rate is appropriate (~0.85)
- [ ] Announcements are in logical order

### Test for ALL Disabilities

- [ ] Accessibility support status shows
- [ ] GPS coordinates are accurate
- [ ] Request sent without errors
- [ ] Firebase integration works
- [ ] Device audio/visual settings respected

---

## 🔍 Troubleshooting

### Issue: No voice output for blind users

**Solution**:

- Check browser has audio permission
- Verify `window.speechSynthesis` is available
- Test in Chrome (best compatibility)

### Issue: Visual alerts not showing for deaf users

**Solution**:

- Clear browser cache
- Check CSS is loading correctly
- Verify Streamlit version supports unsafe_allow_html

### Issue: TTS stops working after first alert

**Solution**:

```python
window.speechSynthesis.cancel()  # Always cancel before new speech
```

---

## 📝 Files Modified

1. **`accessibility_alerts.py`** (NEW)
   - Complete accessibility alert system

2. **`disabled_page.py`** (MODIFIED)
   - Added import: `from accessibility_alerts import...`
   - Updated: `_send_request_to_driver()` function
   - Added: Specialized alerts for deaf/blind passengers

3. **`driver_page.py`** (MODIFIED)
   - Added import: `from accessibility_alerts import...`
   - Updated: Pending request alert handling
   - Added: Specialized alerts for deaf/blind passengers

---

## 🎯 Future Enhancements

- [ ] SMS alerts for deaf users (text-based backup)
- [ ] Haptic feedback for deaf users (vibration alerts)
- [ ] Real-time caption generation for audio alerts
- [ ] Multi-language support (Tamil, Hindi, etc.)
- [ ] Customizable alert preferences
- [ ] Alert history/logging
- [ ] Integration with accessibility devices

---
