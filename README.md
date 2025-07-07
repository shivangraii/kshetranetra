# 🛰️ KshetraNetra – Bidirectional Satellite Monitoring System

**KshetraNetra** is an AI-powered satellite monitoring application designed to detect structural and vegetation changes in sensitive regions such as border zones, nuclear sites, and abandoned military areas.

It performs **bidirectional change detection** — identifying both the **appearance of new structures** and the **disappearance of existing ones** — using NDVI and NDBI analysis over user-defined Areas of Interest (AOIs). The system also generates real-time alerts and visual reports.

---

## 🔧 Features

- 🗺️ AOI selection via interactive map
- 🌱 NDVI/NDBI-based vegetation and built-up analysis
- 📷 Before–after satellite image comparison
- 🔍 Detection of both new and removed structures
- ⚠️ Real-time alert and visual reporting
- 📊 Streamlit-based web dashboard

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/kshetranetra-app.git
cd kshetranetra-app
```

### 2. Install Requirements
```bash
pip install -r requirements.txt
```

### 3. Run the App
```bash
streamlit run app.py
```

---

## 🗂️ Folder Structure

```
kshetranetra-app/
├── app.py               # Main Streamlit app
├── requirements.txt     # Dependencies
├── assets/              # (Optional) Icons, overlays, etc.
├── sample_data/         # (Optional) Satellite image samples
└── README.md
```

---

## 📦 Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python (FastAPI planned)
- **Satellite Imagery**: Sentinel-2 via Bhoonidhi API
- **Preprocessing**: Rasterio, OpenCV
- **Change Detection**: UNet model
- **Indices**: NDVI, NDBI
- **Alerts**: SMTP (email)

---
## 📍 Use Case
Designed to support **strategic surveillance**, **disaster readiness**, and **national security**, especially in high-risk or sensitive geographic zones.
---

## 🧠 Contributors
- Shivang Rai https://github.com/shivangraii
- Om Tripathi https://github.com/omtripathi06
- Sheen Ambardar 
- Chaitanya
---

## 📜 License
This project is unilicensed.
