Working well only problem orange and blue 
no real data 

import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import Draw
from geopy.geocoders import Nominatim
from PIL import Image, ImageDraw
from fpdf import FPDF
import datetime
import tempfile
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText

# --- Session State Initialization ---
for key in ["t1_date", "t2_date", "aoi_geojson", "pdf_bytes"]:
    if key not in st.session_state:
        st.session_state[key] = None

st.set_page_config(page_title="KshetraNetra", layout="wide")
st.title("🛰️ KshetraNetra – Satellite Change Detection System")

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

# --- 3. T1/T2 Date Selection ---
st.sidebar.header("3️⃣ Select T1 and T2 Dates")
t1_date = st.sidebar.date_input("T1 Date (Before)", key="t1_date_input")
t2_date = st.sidebar.date_input("T2 Date (After)", key="t2_date_input")

# --- 4. Simulated Satellite Images ---
st.header("🖼️ T1 and T2 Satellite Images (Simulated)")

def create_placeholder_image(color, label):
    img = Image.new('RGB', (400, 400), color=color)
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), label, fill=(255, 255, 255))
    return img

t1_img = t2_img = None
if aoi_geojson:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### T1 Image")
        t1_img = create_placeholder_image((0, 120, 255), f"T1: {t1_date}")
        st.image(t1_img, caption=f"T1 ({t1_date})", use_column_width=True)
    with col2:
        st.markdown("#### T2 Image")
        t2_img = create_placeholder_image((255, 120, 0), f"T2: {t2_date}")
        st.image(t2_img, caption=f"T2 ({t2_date})", use_column_width=True)
else:
    st.warning("Please select an AOI on the map to view T1/T2 images.")

# --- 5. Run Change Detection (Simulated) ---
st.header("🔍 Run Change Detection")
run_cd = st.button("Run Change Detection", key="run_change_detection_btn")

if run_cd:
    if not aoi_geojson or t1_img is None or t2_img is None:
        st.warning("Please select an AOI and T1/T2 dates first.")
    else:
        st.subheader("🧠 Simulated Change Detection Output")
        mask = Image.blend(t1_img, t2_img, alpha=0.5)
        st.image(mask, caption="Simulated Change Mask", use_column_width=True)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_mask:
            mask.save(tmp_mask, format="PNG")
            mask_path = tmp_mask.name

        # --- 6. Generate PDF Report ---
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "KshetraNetra Alert Report", ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"AOI Geometry: {str(aoi_geojson)[:80]}...", ln=True)
        pdf.cell(0, 10, f"T1 Date: {t1_date}", ln=True)
        pdf.cell(0, 10, f"T2 Date: {t2_date}", ln=True)
        pdf.cell(0, 10, f"Report Generated: {datetime.datetime.now().strftime('%d-%m-%Y %I:%M %p')}", ln=True)
        pdf.cell(0, 10, "Summary: Structural changes detected in AOI", ln=True)
        pdf.ln(5)
        pdf.image(mask_path, x=30, w=150)

        pdf_bytes = pdf.output(dest='S').encode('latin1')
        st.session_state["t1_date"] = str(t1_date)
        st.session_state["t2_date"] = str(t2_date)
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
            msg["Subject"] = f"KshetraNetra Alert Report"

            body = f"""Dear User,

Please find attached the official satellite change detection report for your selected AOI.

T1 Date: {st.session_state['t1_date']}
T2 Date: {st.session_state['t2_date']}

This report has been auto-generated by KshetraNetra.

Jai Hind 🇮🇳
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

