# 🎤 Driver Voice Assistant Portal - Disability Pickups

## Overview

The Voice Assistant Portal has been added to the Driver Dashboard to provide real-time voice announcements and position updates for all accessibility-related passenger pickups.

## Features

### 📍 Position-Based Announcements

- **Real-time Distance Calculation**: Automatically calculates distance of each pickup from Madhavaram Depot
- **GPS Coordinates**: Displays exact latitude and longitude of each passenger location
- **Sorted by Proximity**: Requests are automatically sorted by distance (nearest first)

### 🎤 Voice Announcements

The driver can use several announcement options:

1. **Announce All Pickups** - Lists all pending disability pickups with positions
   - Announces total number of requests
   - Details for each pickup with location and distance

2. **Announce Nearest Pickup** - Only announces the closest disability pickup
   - Useful when the driver wants to focus on the nearest passenger

3. **Position Announcement** - Announces the position of a specific pickup
   - Can be triggered for any individual pickup request
   - Includes passenger name, location, distance, and disability type

4. **Navigation Instructions** - Provides voice guidance to reach the pickup location
   - Includes distance from depot
   - Provides accessibility guidance for the specific disability type

### ♿ Accessibility Communication Guidance

Built-in guidelines for communicating with passengers with different disabilities:

**👁️ BLIND Passengers:**

- Use clear voice communication when arriving
- Honk loudly and distinctly
- Announce arrival verbally
- Verbally guide to bus entrance
- Describe obstacles clearly

**🔇 DEAF Passengers:**

- Use visual signals (lights, signs)
- Flash headlights when arriving
- Use hand signals to guide
- Display boarding information visibly
- Write messages if needed

**🦽 MOBILITY IMPAIRMENT Patients:**

- Arrive at exact location
- Allow extra boarding time
- Offer assistance as needed
- Ensure wheelchair accessibility
- Park close to boarding point

**🤚 HAND DISABILITY Passengers:**

- Park close to boarding point
- Allow extra boarding time
- Offer assistance if needed
- Be patient with boarding process

## Implementation Details

### New Files Created

- **driver_voice_assistant.py**: Main module for voice assistant portal functionality

### Modified Files

- **driver_page.py**: Added tabs to access voice assistant and modified to import voice assistant module

### Key Functions

#### `speak_announcement(text)`

Uses browser's Web Speech API for text-to-speech announcements in English (Indian accent).

#### `announce_pickup_position(passenger_name, location, distance_km, disability_type, boarding_stop)`

Creates formatted voice announcements for individual pickups with disability-specific guidance.

#### `render_voice_assistant_portal()`

Main rendering function that displays:

- Voice announcement controls
- Position-based pickup list
- GPS coordinates
- Action buttons for each pickup
- Accessibility communication guidelines

## Position Data

Each pickup displays:

- **Passenger Name**: Who is waiting
- **Boarding Location**: Where they will board
- **Distance**: Calculated in km from Madhavaram Depot (13.1180°N, 80.2350°E)
- **GPS Coordinates**: Exact latitude and longitude (6 decimal places precision)
- **Disability Type**: Specific accessibility need
- **Status**: Pending or Acknowledged

## How to Access

1. Log in as Driver to the Driver Dashboard
2. Click on the **"🎤 Voice Assistant - Disability Pickups"** tab
3. Use voice announcement buttons to hear pickup information
4. See real-time position updates
5. Acknowledge or complete each pickup

## Integration

The Voice Assistant is seamlessly integrated into the existing Driver Dashboard:

- **Dashboard Tab**: Original driver features (location, requests, real-time updates)
- **Voice Assistant Tab**: New voice-based pickup management with position announcements

## Status Updates

✅ Voice announcements working with Web Speech API
✅ Position calculations accurate
✅ Accessibility guidelines integrated
✅ Real-time distance sorting
✅ Integration with Firebase for live data

## Notes

- Voice announcements use English (Indian) language setting
- Distance calculated using Haversine formula
- All GPS coordinates accurate to 6 decimal places
- Voice assistant respects Firebase connection status
