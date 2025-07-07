import streamlit as st
from PIL import Image
from fpdf import FPDF
import datetime
import tempfile
import os

st.set_page_config(page_title="KshetraNetra Demo", layout="wide")
st.title("🛰️ KshetraNetra – Satellite Change Detection System (Demo)")

# --- Always load demo images ---
def load_demo_image(filename):
    return Image.open(filename)

t1_img = load_demo_image("t1.jpeg")
t2_img = load_demo_image("t2.jpeg")
mask_img = load_demo_image("mask.jpeg")

# --- Date and time selection (for realism) ---
import datetime
st.sidebar.header("Select T1 and T2 Date & Time")

def time_selector(label):
    date_val = st.sidebar.date_input(f"{label} Date")
    hour = st.sidebar.selectbox(f"{label} Hour", list(range(1, 13)))
    minute = st.sidebar.selectbox(f"{label} Minute", list(range(0, 60, 5)))
    ampm = st.sidebar.radio(f"{label} AM/PM", ["AM", "PM"])
    hour_24 = hour % 12 + (12 if ampm == "PM" else 0)
    dt = datetime.datetime.combine(date_val, datetime.time(hour_24, minute))
    time_str = dt.strftime("%d-%m-%Y – %I:%M %p")
    return dt, time_str

t1_datetime, t1_time_str = time_selector("T1")
t2_datetime, t2_time_str = time_selector("T2")

# --- Display T1 and T2 images ---
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

# --- Run Change Detection ---
st.header("🔍 Run Change Detection")
run_cd = st.button("Run Change Detection")

if run_cd:
    st.subheader("🧠 Simulated Change Detection Output")
    st.image(mask_img, caption="Simulated Change Mask", use_column_width=True)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpeg") as tmp_mask:
        mask_img.save(tmp_mask, format="JPEG")
        mask_path = tmp_mask.name

    # --- Generate PDF Report ---
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "KshetraNetra Alert Report", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"T1 Captured: {t1_time_str}", ln=True)
    pdf.cell(0, 10, f"T2 Captured: {t2_time_str}", ln=True)
    pdf.cell(0, 10, f"Report Generated: {datetime.datetime.now().strftime('%d-%m-%Y %I:%M %p')}", ln=True)
    pdf.cell(0, 10, "Summary: Structural changes detected", ln=True)
    pdf.ln(5)
    pdf.image(mask_path, x=30, w=150)

    pdf_bytes = pdf.output(dest='S').encode('latin1')
    st.download_button(
        label="📄 Download PDF Report",
        data=pdf_bytes,
        file_name="kshetranetra_report.pdf",
        mime="application/pdf"
    )
    os.remove(mask_path)
