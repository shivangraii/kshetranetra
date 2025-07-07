import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import Draw
from geopy.geocoders import Nominatim
import requests
from PIL import Image
from io import BytesIO

# --- User credentials (replace with your Bhoonidhi username/password) ---
BHOONIDHI_USERNAME = "trixom06"
BHOONIDHI_PASSWORD = "balaji@2006"

st.set_page_config(page_title="KshetraNetra – Bhoonidhi Integration", layout="wide")
st.title("🛰️ KshetraNetra – Satellite Change Detection (Bhoonidhi API)")

# --- 1. AOI selection ---
st.sidebar.header("1️⃣ Select Area of Interest (AOI)")
search_query = st.sidebar.text_input("Search for a place (city, country, etc.)", key="search_input")

# Default map center (India)
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

aoi_geojson = None
if output and output.get('last_active_drawing'):
    aoi_geojson = output['last_active_drawing']
    st.success("AOI Selected! Geometry below:")
    st.json(aoi_geojson)
else:
    st.info("Draw a polygon or rectangle on the map to select your AOI.")

# --- 2. Date selection ---
st.sidebar.header("2️⃣ Select T1 and T2 Dates")
t1_date = st.sidebar.date_input("T1 Date (Before)", key="t1_date_input")
t2_date = st.sidebar.date_input("T2 Date (After)", key="t2_date_input")

# --- 3. Satellite/Sensor selection ---
st.sidebar.header("3️⃣ Satellite and Sensor")
satellite = st.sidebar.selectbox("Satellite", ["SENTINEL-2", "RESOURCESAT-2A", "CARTOSAT-2"], index=0)
sensor = st.sidebar.text_input("Sensor (e.g., MSI, LISS-III, PAN)", value="MSI" if satellite == "SENTINEL-2" else "")

# --- 4. Fetch images from Bhoonidhi ---
def get_bhoonidhi_token(username, password):
    url = "https://bhoonidhi-api.nrsc.gov.in/auth/token"
    payload = {"username": username, "password": password}
    r = requests.post(url, json=payload)
    if r.status_code == 200:
        return r.json()["access_token"]
    else:
        st.error("Authentication failed. Check your Bhoonidhi credentials.")
        return None

def search_bhoonidhi(token, aoi, start_date, end_date, satellite, sensor):
    url = "https://bhoonidhi-api.nrsc.gov.in/data/search"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "aoi": aoi,
        "startDate": str(start_date),
        "endDate": str(end_date),
        "satellite": satellite,
        "sensor": sensor
    }
    r = requests.post(url, json=payload, headers=headers)
    if r.status_code == 200:
        return r.json().get("products", [])
    else:
        st.error("Search failed. Please check your parameters and try again.")
        return []

def download_bhoonidhi_image(token, product_id):
    url = f"https://bhoonidhi-api.nrsc.gov.in/download/{product_id}"
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return r.content
    else:
        st.error("Download failed. The product may not be open-access or is not ready.")
        return None

def extract_bbox_from_geojson(geojson):
    # For rectangle AOI, extract the coordinates
    coords = geojson["geometry"]["coordinates"][0]
    return coords

# --- 5. Fetch and display T1 and T2 images ---
if st.button("Fetch T1 & T2 Images from Bhoonidhi") and aoi_geojson:
    with st.spinner("Authenticating and searching Bhoonidhi..."):
        token = get_bhoonidhi_token(BHOONIDHI_USERNAME, BHOONIDHI_PASSWORD)
        if token:
            aoi = {
                "type": "Polygon",
                "coordinates": aoi_geojson["geometry"]["coordinates"]
            }
            # T1 image search
            t1_products = search_bhoonidhi(token, aoi, t1_date, t1_date, satellite, sensor)
            # T2 image search
            t2_products = search_bhoonidhi(token, aoi, t2_date, t2_date, satellite, sensor)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### T1 Image")
                if t1_products:
                    t1_product_id = t1_products[0]["id"]
                    t1_img_bytes = download_bhoonidhi_image(token, t1_product_id)
                    if t1_img_bytes:
                        t1_img = Image.open(BytesIO(t1_img_bytes))
                        st.image(t1_img, caption=f"T1 ({t1_date})", use_column_width=True)
                    else:
                        st.warning("T1 image could not be downloaded.")
                else:
                    st.warning("No T1 image found for the selected AOI and date.")

            with col2:
                st.markdown("#### T2 Image")
                if t2_products:
                    t2_product_id = t2_products[0]["id"]
                    t2_img_bytes = download_bhoonidhi_image(token, t2_product_id)
                    if t2_img_bytes:
                        t2_img = Image.open(BytesIO(t2_img_bytes))
                        st.image(t2_img, caption=f"T2 ({t2_date})", use_column_width=True)
                    else:
                        st.warning("T2 image could not be downloaded.")
                else:
                    st.warning("No T2 image found for the selected AOI and date.")
else:
    st.info("Select AOI, dates, and click the button to fetch images.")

st.markdown("---")
st.markdown("**Note:** Some images may require processing or may not be open-access. If you see a download warning, try a different date or satellite/sensor combination. For best results, use small AOIs and recent dates.")

