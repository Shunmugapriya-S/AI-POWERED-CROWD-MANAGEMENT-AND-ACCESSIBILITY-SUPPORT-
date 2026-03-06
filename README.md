# 🚌 Tamil Nadu Smart Bus - Live Crowd Detection

## ✨ Features

### 🎥 Live Crowd Detection (Railway Obstacle Detection மாதிரி)
- **Real-time camera feed** with YOLO detection
- **Live people counting** with bounding boxes
- **Automatic crowd level** classification (Low/Medium/High)
- **Background threading** for smooth performance

### 🚌 Live Bus Tracking
- **Current bus location** tracking
- **ETA (Estimated Time of Arrival)** to your stop
- **Progress indicator** showing bus journey
- **Real-time status** updates

### 👥 Multi-Role Portal
- **Passenger**: Live detection + Bus tracking
- **Disabled**: Accessibility features
- **Driver**: Priority pickup requests
- **Admin**: System monitoring

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the App
```bash
streamlit run app.py
```

### 3. Open Browser
```
http://localhost:8501
```

---

## 📱 How to Use

### Passenger Portal:

1. **Select "Passenger" role** from landing page

2. **Choose your route** and stops:
   - Select bus route
   - Choose boarding stop
   - Choose destination

3. **Start Live Detection**:
   - Click "📹 Start Live Detection"
   - Camera will open automatically
   - See live people count and crowd level
   - Railway obstacle detection மாதிரி!

4. **Track Bus**:
   - Click "🔍 Track Bus Location"
   - See current bus location
   - Get ETA to your stop
   - View crowd level in bus

---

## 🎯 Live Detection Features

### Like Railway Obstacle Detection:
- ✅ Live camera feed
- ✅ Real-time YOLO detection
- ✅ Bounding boxes around people
- ✅ Live count display
- ✅ Background processing
- ✅ Smooth video feed

### Crowd Levels:
- 🟢 **Low** (0-9 people): Plenty of seats
- 🟡 **Medium** (10-29 people): Standing available
- 🔴 **High** (30+ people): Crowded

---

## 📊 Bus Tracking

### Real-time Information:
- 📍 **Current Location**: Where the bus is now
- ⏱️ **ETA**: Time to reach your stop
- 🚦 **Status**: On time / Delayed
- 👥 **Crowd Level**: Live or simulated

---

## 🔧 Configuration

### Change Camera:
Edit `live_crowd_detector.py` line 34:
```python
self.cap = cv2.VideoCapture(0)  # 0 = default camera
```

### Adjust Crowd Thresholds:
Edit `live_crowd_detector.py` lines 61-67:
```python
if count < 10:
    self.crowd_level = "Low"
elif count < 30:
    self.crowd_level = "Medium"
else:
    self.crowd_level = "High"
```

---

## 📁 Project Structure

```
smart bus/
├── app.py                      # Main Streamlit app
├── live_crowd_detector.py      # Live detection module
├── routedata1.csv             # Bus routes
├── stopdata.csv               # Bus stops
├── background.png             # Background image
├── *.png                      # Role images
└── requirements.txt           # Dependencies
```

---

## 🐛 Troubleshooting

### Camera not opening:
- Check if camera is connected
- Try different camera index (0, 1, 2...)
- Check camera permissions

### Detection not working:
- Ensure YOLO model is downloaded
- Check internet connection (first run)
- Verify camera feed is showing

### App not loading:
- Check all dependencies installed
- Ensure CSV files exist
- Restart Streamlit server

---

## 💡 Tips

1. **Good Lighting**: Works best in well-lit areas
2. **Camera Position**: Point camera at people
3. **Stop Detection**: Click "Stop" when done to free camera
4. **Multiple Cameras**: Change camera index for different cameras

---

## 🎓 How It Works

### Architecture:
```
Camera → YOLO Detection → Background Thread → Live Display
                ↓
         People Count → Crowd Level → Stats Panel
```

### Threading:
- Main thread runs Streamlit UI
- Background thread runs YOLO detection
- Shared state for live updates

---

## 📝 Tamil Guide

### பயன்படுத்தும் முறை:

1. **App-ஐ run செய்யவும்**: `streamlit run app.py`
2. **Passenger select செய்யவும்**
3. **Route தேர்வு செய்யவும்**
4. **"Start Live Detection" click செய்யவும்**
5. **Camera தானாக open ஆகும்**
6. **Live-ஆ people count பார்க்கலாம்**
7. **"Track Bus" click செய்து bus location பார்க்கலாம்**

---

## ✅ Status

**System**: 🟢 READY
**Detection**: 🟢 LIVE
**Tracking**: 🟢 ACTIVE

---

**Run**: `streamlit run app.py`
**Access**: http://localhost:8501

**Made with ❤️ for Tamil Nadu**
