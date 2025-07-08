import streamlit as st

st.set_page_config(page_title="KshetraNetra", layout="wide")
st.image("logo.png", width=140)  # Adjust width as needed
st.markdown(
    "<h1 style='margin-bottom:0; font-size:2.2rem; font-weight:700; letter-spacing:1px; color:#1a237e;'>KshetraNetra</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<span style='font-size:1.1rem; color:#555;'>Satellite Change Detection System (Demo)</span>",
    unsafe_allow_html=True
)





import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import Draw
from geopy.geocoders import Nominatim
from PIL import Image
from fpdf import FPDF
import datetime
import tempfile
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText

# --- Professional Logo at the Top ---
st.set_page_config(page_title="KshetraNetra", layout="wide")
st.image("logo.png", width=120)
st.markdown(
    "<h1 style='margin-bottom:0; font-size:2.2rem; font-weight:700; letter-spacing:1px; color:#1a237e;'>KshetraNetra</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<span style='font-size:1.1rem; color:#555;'>Satellite Change Detection System (Demo)</span>",
    unsafe_allow_html=True
)

# --- Session State Initialization ---
for key in ["t1_datetime", "t2_datetime", "aoi_geojson", "pdf_bytes"]:
    if key not in st.session_state:
        st.session_state[key] = None

# --- 1. Location Search ---
st.sidebar.header("1️⃣ Search Location")
search_query = st.sidebar.text_input("🔍 Search for a place (city, country, etc.)", key="search_input")

# --- 2. Map and AOI Drawing ---
st.sidebar.header("2️⃣ Draw AOI (Area of Interest)")
map_center = [20, 0]
zoom = 2

if search_query:
    try:
        geolocator = Nominatim(user_agent="kshetranetra_app")
        location = geolocator.geocode(search_query, timeout=10)
        if location:
            st.sidebar.success(f"Found: {location.address}")
            map_center = [location.latitude, location.longitude]
            zoom = 10
        else:
            st.sidebar.warning("Location not found.")
    except Exception:
        st.sidebar.error("Geocoding service unavailable. Try again later.")

m = folium.Map(location=map_center, zoom_start=zoom)
Draw(export=True).add_to(m)
output = st_folium(m, width=700, height=500, key="folium_map")

aoi_geojson = None
if output and output.get('last_active_drawing'):
    aoi_geojson = output['last_active_drawing']
    st.success("AOI Selected! Geometry below:")
    st.json(aoi_geojson)
else:
    st.info("Draw a polygon or rectangle on the map to select your AOI.")

# --- 3. T1/T2 Date and Time Selection ---
st.sidebar.header("3️⃣ Select T1 and T2 Date & Time")

def time_selector(label_prefix):
    date_val = st.sidebar.date_input(f"{label_prefix} Date", key=f"{label_prefix}_date")
    hour = st.sidebar.selectbox(f"{label_prefix} Hour", list(range(1, 13)), key=f"{label_prefix}_hour")
    minute = st.sidebar.selectbox(f"{label_prefix} Minute", list(range(0, 60, 5)), key=f"{label_prefix}_minute")
    ampm = st.sidebar.radio(f"{label_prefix} AM/PM", ["AM", "PM"], key=f"{label_prefix}_ampm")
    hour_24 = hour % 12 + (12 if ampm == "PM" else 0)
    dt = datetime.datetime.combine(date_val, datetime.time(hour_24, minute))
    time_str = dt.strftime("%d-%m-%Y %I:%M %p")
    return dt, time_str

t1_datetime, t1_time_str = time_selector("T1")
t2_datetime, t2_time_str = time_selector("T2")

# --- 4. Always Load and Show Demo Images ---
def load_demo_image(filename):
    return Image.open(filename)

t1_img = load_demo_image("t1.jpeg")
t2_img = load_demo_image("t2.jpeg")
mask_img = load_demo_image("mask.jpeg")

st.header("🖼️ T1 and T2 Satellite Images (Demo)")
col1, col2 = st.columns(2)
with col1:
    st.markdown("#### T1 Image")
    st.image(t1_img, caption=f"T1 ({t1_time_str})", use_column_width=True)
    st.markdown(f"🗓️ Captured: **{t1_time_str}**")
with col2:
    st.markdown("#### T2 Image")
    st.image(t2_img, caption=f"T2 ({t2_time_str})", use_column_width=True)
    st.markdown(f"🗓️ Captured: **{t2_time_str}**")

# --- 5. Run Change Detection (Demo) ---
st.header("🔍 Run Change Detection")
run_cd = st.button("Run Change Detection", key="run_change_detection_btn")

if run_cd:
    st.subheader("Simulated Change Detection Output")
    st.image(mask_img, caption="Simulated Change Mask", use_column_width=True)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpeg") as tmp_mask:
        mask_img.save(tmp_mask, format="JPEG")
        mask_path = tmp_mask.name

    # --- 6. Generate PDF Report (ASCII/Unicode-safe) ---
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "KshetraNetra Alert Report", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"AOI Geometry: {str(aoi_geojson)[:80]}...", ln=True)
    pdf.cell(0, 10, f"T1 Captured: {t1_time_str}", ln=True)
    pdf.cell(0, 10, f"T2 Captured: {t2_time_str}", ln=True)
    pdf.cell(0, 10, f"Report Generated: {datetime.datetime.now().strftime('%d-%m-%Y %I:%M %p')}", ln=True)
    pdf.cell(0, 10, "Summary: Structural changes detected in AOI", ln=True)
    pdf.ln(5)
    pdf.image(mask_path, x=30, w=150)

    pdf_bytes = pdf.output(dest='S').encode('latin1', errors='replace')
    st.session_state["t1_datetime"] = str(t1_datetime)
    st.session_state["t2_datetime"] = str(t2_datetime)
    st.session_state["aoi_geojson"] = aoi_geojson
    st.session_state["pdf_bytes"] = pdf_bytes

    st.download_button(
        label="📄 Download PDF Report",
        data=pdf_bytes,
        file_name="kshetranetra_report.pdf",
        mime="application/pdf",
        key="download_pdf_btn"
    )
    os.remove(mask_path)

# --- 7. Email Sending ---
st.header("📧 Send Report via Email")
recipient = st.text_input("Enter recipient email address", key="email_input")
send_email = st.button("Send Email", key="send_email_btn")

if send_email:
    if not recipient:
        st.warning("Please enter a recipient email first.")
    elif not st.session_state.get("pdf_bytes"):
        st.error("No PDF generated yet. Please run Change Detection first.")
    else:
        try:
            SENDER_EMAIL = "kshetranetra.alerts@gmail.com"
            APP_PASSWORD = "zznw wmyz bjri alru"  # Replace with your actual App Password

            msg = MIMEMultipart()
            msg["From"] = SENDER_EMAIL
            msg["To"] = recipient
            msg["Subject"] = "KshetraNetra Alert Report"

            body = f"""Dear User,

Please find attached the official satellite change detection report for your selected AOI.

T1 Captured: {t1_time_str}
T2 Captured: {t2_time_str}

This report has been auto-generated by KshetraNetra.

Jai Hind
"""
            msg.attach(MIMEText(body, "plain"))

            attachment = MIMEApplication(st.session_state["pdf_bytes"], _subtype="pdf")
            attachment.add_header("Content-Disposition", "attachment", filename="kshetranetra_report.pdf")
            msg.attach(attachment)

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(SENDER_EMAIL, APP_PASSWORD)
                server.send_message(msg)

            st.success(f"✅ Email successfully sent to {recipient}!")
        except Exception as e:
            st.error(f"❌ Failed to send email: {e}")
