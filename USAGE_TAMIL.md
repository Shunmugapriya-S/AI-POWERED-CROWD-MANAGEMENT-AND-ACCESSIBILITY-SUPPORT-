# 🚌 தமிழ்நாடு ஸ்மார்ட் பஸ் - பயன்பாட்டு வழிகாட்டி

## 🎯 Crowd Detection எப்படி பயன்படுத்துவது?

### படி 1: App-ஐ திறக்கவும்
```bash
streamlit run app.py
```

Browser-ல் தானாக திறக்கும்: http://localhost:8501

### படி 2: Passenger Role தேர்வு செய்யவும்
- முதல் பக்கத்தில் **"🧍 Passenger"** button-ஐ click செய்யவும்

### படி 3: Route தேர்வு செய்யவும்
- உங்கள் bus route-ஐ dropdown-ல் இருந்து தேர்வு செய்யவும்
- Boarding stop மற்றும் destination-ஐ select செய்யவும்

### படி 4: Crowd Detection பயன்படுத்தவும்

#### 📸 Mobile-ல் இருந்து Photo Upload செய்ய:

1. **"🎥 Live Crowd Detection"** section-க்கு scroll செய்யவும்

2. **"Upload Bus Image"** option-ஐ select செய்யவும்

3. **"Browse files"** button-ஐ click செய்யவும்

4. உங்கள் mobile-ல் இருந்து bus interior photo-வை select செய்யவும்

5. System தானாக:
   - Bus-ல் உள்ள அனைத்து பேரையும் detect செய்யும்
   - ஒவ்வொருவரையும் green box-ல் காட்டும்
   - மொத்த எண்ணிக்கையை count செய்யும்
   - Crowd level-ஐ சொல்லும் (Low/Medium/High)

### 📊 Crowd Level என்றால் என்ன?

- **🟢 Low (0-9 பேர்)**: நிறைய இருக்கைகள் available
- **🟡 Medium (10-29 பேர்)**: நிற்க இடம் உள்ளது
- **🔴 High (30+ பேர்)**: Bus நிரம்பியுள்ளது

### 💡 Tips:

1. **Clear photo எடுக்கவும்**: மக்கள் தெளிவாக தெரிய வேண்டும்
2. **நல்ல வெளிச்சம்**: பகல் நேரம் அல்லது bus light இருக்கும் போது
3. **Multiple angles**: பல கோணங்களில் photo எடுத்து try செய்யலாம்
4. **Internet வேண்டாம்**: முதல் முறை மட்டும் model download ஆகும், பிறகு offline-ல் வேலை செய்யும்

## 🎥 எந்த மாதிரி Photo எடுக்கணும்?

### ✅ நல்ல Photos:
- Bus-க்குள் இருந்து எடுத்த photo
- மக்கள் தெளிவாக தெரியும் photo
- நல்ல lighting உள்ள photo
- Front/side angle-ல் இருந்து எடுத்த photo

### ❌ தவிர்க்க வேண்டிய Photos:
- மிகவும் இருட்டாக உள்ள photo
- மக்கள் தெரியாத அளவுக்கு தூரத்தில் இருந்து எடுத்த photo
- Blurry/unclear photos

## 🔧 முதல் முறை Setup

### Requirements Install செய்ய:
```bash
pip install -r requirements.txt
```

### YOLO Model Download:
- முதல் முறை run செய்யும் போது தானாக download ஆகும்
- Size: ~6.2 MB
- Internet connection தேவை (முதல் முறை மட்டும்)
- Download location: Project folder-ல் `yolov8n.pt` என்ற file

## 📱 Mobile-ல் பயன்படுத்த:

1. Same WiFi network-ல் mobile மற்றும் computer இருக்க வேண்டும்

2. App run செய்யும் போது காட்டும் **Network URL**-ஐ mobile browser-ல் திறக்கவும்
   ```
   Network URL: http://10.83.49.240:8501
   ```

3. Mobile-ல் photo எடுத்து direct-ஆ upload செய்யலாம்

## 🎯 Example Workflow:

1. App-ஐ open செய்யவும்
2. "Passenger" role select செய்யவும்
3. Route: "21G - Chennai Central to Tambaram" select செய்யவும்
4. Boarding: "Guindy" select செய்யவும்
5. Destination: "Tambaram" select செய்யவும்
6. "Upload Bus Image" click செய்து photo upload செய்யவும்
7. System detect செய்து count காட்டும்
8. "Get Live Status" click செய்து full details பார்க்கவும்

## ❓ Common Issues & Solutions:

### Issue 1: "YOLO model failed to load"
**Solution**: 
- Internet connection check செய்யவும்
- `python test_detector.py` run செய்து test செய்யவும்

### Issue 2: "Cannot detect people"
**Solution**:
- Photo clear-ஆ இருக்கிறதா check செய்யவும்
- Lighting நல்லா இருக்கிறதா பார்க்கவும்
- வேறு photo-வை try செய்யவும்

### Issue 3: Count தவறாக இருக்கிறது
**Solution**:
- மக்கள் overlap ஆகாமல் இருக்கும் photo எடுக்கவும்
- நல்ல angle-ல் இருந்து photo எடுக்கவும்
- Multiple photos try செய்யவும்

## 🚀 Advanced Features:

### Test Detector:
```bash
python test_detector.py
```
இது YOLO model சரியாக வேலை செய்கிறதா என்று check செய்யும்

### Custom Settings:
`crowd_detector.py` file-ல் இவற்றை மாற்றலாம்:
- Confidence threshold (line 31)
- Crowd level thresholds (lines 40-45)

## 📞 Support:

Issues இருந்தால்:
1. `test_detector.py` run செய்து பார்க்கவும்
2. README.md file-ஐ படிக்கவும்
3. Error messages-ஐ note செய்து வைக்கவும்

---

**Made with ❤️ for Tamil Nadu**

**குறிப்பு**: இந்த system முழுவதும் AI-powered. YOLO v8 model பயன்படுத்தி real-time-ல் மக்களை detect செய்கிறது!
