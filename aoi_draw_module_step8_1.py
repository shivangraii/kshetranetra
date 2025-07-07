
import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import Draw

st.set_page_config(page_title="AOI Selection - KshetraNetra", layout="wide")

st.title("🌍 AOI Selection – Draw on Map or Search a Location")

# Initialize base map centered globally
m = folium.Map(location=[20.5937, 78.9629], zoom_start=4, control_scale=True)

# Enable drawing on the map
draw = Draw(
    draw_options={
        "polyline": False,
        "rectangle": True,
        "circle": False,
        "marker": False,
        "circlemarker": False,
        "polygon": True,
    },
    edit_options={"edit": True}
)
draw.add_to(m)

# Display map in Streamlit
st_map = st_folium(m, height=600, width=1100, returned_objects=["last_drawn"])

# Capture drawn AOI
if st_map and st_map["last_drawn"]:
    feature = st_map["last_drawn"]
    coords = feature.get("geometry", {}).get("coordinates", [])
    if coords:
        st.success("✅ AOI Captured Successfully")
        st.json(coords)
        st.session_state["aoi_coordinates"] = coords
else:
    st.info("Draw a rectangle or polygon on the map to define your Area of Interest.")
