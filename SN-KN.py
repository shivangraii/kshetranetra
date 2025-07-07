import streamlit as st
from PIL import Image
from fpdf import FPDF
import datetime
import io
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import tempfile

# ✅ Page Setup
st.set_page_config(page_title="KshetraNetra", layout="wide")
st.title("🛰️ KshetraNetra – Satellite Change Detection System")

# ✅ Sidebar Inputs
st.sidebar.header("🗂️ Input Panel")
aoi_name = st.sidebar.text_input("Enter AOI Name")

# --- T1 Inputs ---
st.sidebar.markdown("### T1 Image Info")
t1_file = st.sidebar.file_uploader("Upload T1", type=["jpg", "jpeg", "png"], key="t1")
t1_date = st.sidebar.date_input("T1 Date")
t1_hour = st.sidebar.selectbox("T1 Hour", list(range(1, 13)), index=1)
t1_minute = st.sidebar.selectbox("T1 Minute", list(range(0, 60, 5)), index=0)
t1_ampm = st.sidebar.radio("T1 AM/PM", ["AM", "PM"])

# --- T2 Inputs ---
st.sidebar.markdown("### T2 Image Info")
t2_file = st.sidebar.file_uploader("Upload T2", type=["jpg", "jpeg", "png"], key="t2")
t2_date = st.sidebar.date_input("T2 Date")
t2_hour = st.sidebar.selectbox("T2 Hour", list(range(1, 13)), index=10)
t2_minute = st.sidebar.selectbox("T2 Minute", list(range(0, 60, 5)), index=0)
t2_ampm = st.sidebar.radio("T2 AM/PM", ["AM", "PM"])

# ✅ Display Images
st.markdown("### 🖼️ T1 and T2 Image Viewer")
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🛰️ T1 Image")
    if t1_file:
        img1 = Image.open(t1_file)
        st.image(img1, caption="T1 Image", use_container_width=True)
        t1_time_str = f"{t1_date.strftime('%d-%m-%Y')} – {t1_hour}:{t1_minute:02d} {t1_ampm}"
        st.markdown(f"🗓️ T1 Captured: **{t1_time_str}**")
    else:
        img1 = None
        t1_time_str = ""
        st.info("Upload T1 image from sidebar.")

with col2:
    st.markdown("#### 🛰️ T2 Image")
    if t2_file:
        img2 = Image.open(t2_file)
        st.image(img2, caption="T2 Image", use_container_width=True)
        t2_time_str = f"{t2_date.strftime('%d-%m-%Y')} – {t2_hour}:{t2_minute:02d} {t2_ampm}"
        st.markdown(f"🗓️ T2 Captured: **{t2_time_str}**")
    else:
        img2 = None
        t2_time_str = ""
        st.info("Upload T2 image from sidebar.")

# ✅ Run Change Detection
if st.button("🔍 Run Change Detection"):
    if t1_file and t2_file:
        st.subheader("🧠 Simulated Change Detection Output")
        mask = img2.convert("L")
        st.image(mask, caption="Simulated Change Mask", use_container_width=True)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_mask:
            mask.save(tmp_mask, format="PNG")
            mask_path = tmp_mask.name

        try:
            pdf = FPDF()
            pdf.add_page()
            # Font handling
            font_path = os.path.join(os.path.dirname(__file__), "DejaVuSans.ttf")
            if os.path.exists(font_path):
                pdf.add_font("DejaVu", "", font_path, uni=True)
                pdf.set_font("DejaVu", "", 14)
            else:
                pdf.set_font("Arial", "", 14)
            pdf.cell(0, 10, "KshetraNetra Alert Report", ln=True)
            pdf.cell(0, 10, f"AOI Name: {aoi_name or 'Not specified'}", ln=True)
            pdf.cell(0, 10, f"T1 Captured: {t1_time_str}", ln=True)
            pdf.cell(0, 10, f"T2 Captured: {t2_time_str}", ln=True)
            pdf.cell(0, 10, f"Report Generated: {datetime.datetime.now().strftime('%d-%m-%Y %I:%M %p')}", ln=True)
            pdf.cell(0, 10, "Summary: Structural changes detected in AOI", ln=True)
            pdf.ln(5)
            pdf.image(mask_path, x=30, w=150)

            # Get PDF as bytes (fixes output error)
            pdf_bytes = pdf.output(dest='S').encode('latin1')

            st.session_state["pdf_bytes"] = pdf_bytes
            st.session_state["aoi_name"] = aoi_name
            st.session_state["t1_time_str"] = t1_time_str
            st.session_state["t2_time_str"] = t2_time_str

            st.download_button(
                label="📄 Download PDF Report",
                data=pdf_bytes,
                file_name="kshetranetra_report.pdf",
                mime="application/pdf"
            )
        finally:
            os.remove(mask_path)
    else:
        st.warning("⚠️ Please upload both T1 and T2 images.")

# 📧 Email Send Section
st.markdown("---")
st.subheader("📧 Send This Report via Email")
recipient = st.text_input("Enter recipient email address")
send_email = st.button("📨 Send Email")

if send_email:
    if not recipient:
        st.warning("⚠️ Please enter a recipient email first.")
    elif "pdf_bytes" not in st.session_state:
        st.error("❌ No PDF generated yet. Please run Change Detection first.")
    else:
        try:
            SENDER_EMAIL = "kshetranetra.alerts@gmail.com"
            APP_PASSWORD = "zznw wmyz bjri alru"  # Replace with actual App Password

            msg = MIMEMultipart()
            msg["From"] = SENDER_EMAIL
            msg["To"] = recipient
            msg["Subject"] = f"KshetraNetra Alert Report – {st.session_state['aoi_name']}"

            body = f"""Dear User,

Please find attached the official satellite change detection report for the Area of Interest (AOI): {st.session_state['aoi_name']}.

📌 Observation Summary:
• T1 Captured: {st.session_state['t1_time_str']}
• T2 Captured: {st.session_state['t2_time_str']}

This report has been auto-generated by *KshetraNetra* – an AI-based surveillance & change detection platform developed for strategic monitoring of sensitive zones across India.

━━━━━━━━━━━━━━━━━━━━━━━  
🛰️ Powered by: SudarshanNetra  
🕉️ क्षेत्रं पश्यामि, धर्मं रक्षामि  
📧 Email: kshetranetra.alerts@gmail.com  
━━━━━━━━━━━━━━━━━━━━━━━  

For technical queries or verifications, kindly contact: kshetranetra.alerts@gmail.com  

Jai Hind 🇮🇳  
SudarshanNetra
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
