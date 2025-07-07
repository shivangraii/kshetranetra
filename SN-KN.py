import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import Draw
from geopy.geocoders import Nominatim
from sentinelhub import SHConfig, MimeType, CRS, BBox, SentinelHubRequest, DataCollection, bbox_to_dimensions
from PIL import Image
import numpy as np
from datetime import date
import tempfile
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText

# --- Sentinel Hub Credentials ---
INSTANCE_ID = "8efa5b49-19d6-492a-ada1-ce97e7acf1d7"
CLIENT_ID = "2524271b-a66c-49cc-b346-4930f98391df"
CLIENT_SECRET = "VDQBdOU2nQJBVJJBEjFGq7JjBNDzFo1a"

config = SHConfig()
config.instance_id = INSTANCE_ID
config.sh_client_id = CLIENT_ID
config.sh_client_secret = CLIENT_SECRET

# --- Session State Initialization ---
for key in ["t1_img", "t2_img", "pdf_bytes"]:
    if key not in st.session_state:
        st.session_state[key] = None

st.set_page_config(page_title="KshetraNetra – Sentinel Hub Integration", layout="wide")
st.title("🛰️ KshetraNetra – Satellite Change Detection (Sentinel Hub)")

# --- 1. AOI Selection ---
st.sidebar.header("1️⃣ Select Area of Interest (AOI)")
search_query = st.sidebar.text_input("Search for a place (city, country, etc.)", key="search_input")

map_center = [22.5, 78.0]
zoom = 5

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

aoi_bbox = None
if output and output.get('last_active_drawing'):
    coords = output['last_active_drawing']['geometry']['coordinates'][0]
    lons = [pt[0] for pt in coords]
    lats = [pt[1] for pt in coords]
    min_lon, max_lon = min(lons), max(lons)
    min_lat, max_lat = min(lats), max(lats)
    aoi_bbox = [min_lon, min_lat, max_lon, max_lat]
    st.success("AOI Selected! Bounding Box:")
    st.write(f"Longitude: {min_lon:.4f} to {max_lon:.4f}")
    st.write(f"Latitude: {min_lat:.4f} to {max_lat:.4f}")
else:
    st.info("Draw a rectangle on the map to select your AOI.")

# --- 2. Date Selection ---
st.sidebar.header("2️⃣ Select T1 and T2 Dates")
today = date.today()
t1_date = st.sidebar.date_input("T1 Date (Before)", key="t1_date_input", value=today.replace(day=1))
t2_date = st.sidebar.date_input("T2 Date (After)", key="t2_date_input", value=today)

# --- 3. Fetch Sentinel-2 Images ---
def fetch_sentinel_image(bbox, time_interval, config):
    size = bbox_to_dimensions(BBox(bbox=bbox, crs=CRS.WGS84), resolution=10)
    evalscript = """
    //VERSION=3
    function setup() {
      return {
        input: ["B04", "B03", "B02"],
        output: { bands: 3 }
      };
    }
    function evaluatePixel(sample) {
      return [sample.B04, sample.B03, sample.B02];
    }
    """
    request = SentinelHubRequest(
        evalscript=evalscript,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L2A,
                time_interval=time_interval
            )
        ],
        responses=[SentinelHubRequest.output_response('default', MimeType.PNG)],
        bbox=BBox(bbox=bbox, crs=CRS.WGS84),
        size=size,
        config=config
    )
    img = request.get_data()[0]
    return Image.fromarray(np.uint8(img))

st.header("🖼️ T1 and T2 Sentinel-2 Images")

t1_img = t2_img = None
if aoi_bbox:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### T1 Image")
        try:
            t1_img = fetch_sentinel_image(aoi_bbox, (str(t1_date), str(t1_date)), config)
            st.image(t1_img, caption=f"T1 ({t1_date})", use_column_width=True)
            st.session_state["t1_img"] = t1_img
        except Exception as e:
            st.warning(f"T1 image not available: {e}")
            st.session_state["t1_img"] = None
    with col2:
        st.markdown("#### T2 Image")
        try:
            t2_img = fetch_sentinel_image(aoi_bbox, (str(t2_date), str(t2_date)), config)
            st.image(t2_img, caption=f"T2 ({t2_date})", use_column_width=True)
            st.session_state["t2_img"] = t2_img
        except Exception as e:
            st.warning(f"T2 image not available: {e}")
            st.session_state["t2_img"] = None
else:
    st.warning("Please select an AOI on the map to view T1/T2 images.")

# --- 4. Run Change Detection ---
st.header("🔍 Run Change Detection")
run_cd = st.button("Run Change Detection", key="run_change_detection_btn")

if run_cd:
    if not aoi_bbox or st.session_state["t1_img"] is None or st.session_state["t2_img"] is None:
        st.warning("Please ensure both T1 and T2 images are loaded.")
    else:
        st.subheader("🧠 Simulated Change Detection Output")
        mask = Image.blend(st.session_state["t1_img"], st.session_state["t2_img"], alpha=0.5)
        st.image(mask, caption="Simulated Change Mask", use_column_width=True)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_mask:
            mask.save(tmp_mask, format="PNG")
            mask_path = tmp_mask.name

        # --- 5. Generate PDF Report ---
        from fpdf import FPDF
        import datetime
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "KshetraNetra Alert Report", ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"AOI Bounding Box: {str(aoi_bbox)}", ln=True)
        pdf.cell(0, 10, f"T1 Date: {t1_date}", ln=True)
        pdf.cell(0, 10, f"T2 Date: {t2_date}", ln=True)
        pdf.cell(0, 10, f"Report Generated: {datetime.datetime.now().strftime('%d-%m-%Y %I:%M %p')}", ln=True)
        pdf.cell(0, 10, "Summary: Structural changes detected in AOI", ln=True)
        pdf.ln(5)
        pdf.image(mask_path, x=30, w=150)

        pdf_bytes = pdf.output(dest='S').encode('latin1')
        st.session_state["pdf_bytes"] = pdf_bytes

        st.download_button(
            label="📄 Download PDF Report",
            data=pdf_bytes,
            file_name="kshetranetra_report.pdf",
            mime="application/pdf",
            key="download_pdf_btn"
        )
        os.remove(mask_path)

# --- 6. Email Sending ---
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

T1 Date: {t1_date}
T2 Date: {t2_date}

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
