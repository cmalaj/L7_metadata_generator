import streamlit as st
from datetime import datetime
import pytz

st.set_page_config(page_title="LogPhase 600 Metadata Generator", layout="centered")
st.title("LogPhase 600 Metadata File Generator")

st.markdown("Use this tool to generate a metadata file for your LogPhase 600 growth/kill curve run.")

# Set default time to GMT+8
tz = pytz.timezone("Asia/Singapore")  # or GMT+8 manually
now_gmt8 = datetime.now(tz)

# --- Experiment Metadata ---
st.header("Experiment Information")

with st.form("main_metadata_form"):
    exp_date = st.date_input("Experiment Date", value=now_gmt8.date())
    exp_time = st.time_input("Experiment Start Time", value=now_gmt8.time())
    technician = st.text_input("Technician Name or Initials")
    exp_type = st.selectbox("Experiment Type", ["Quality Control", "Production"])
    organism = st.text_input("Bacterial Organism", value="P. aeruginosa")

    num_plates = st.number_input("Number of Plates in this Run", min_value=1, step=1, value=4)

    notes = st.text_area("Additional Notes")
    serial_number = st.text_input("Instrument Serial Number", value="LP600-XYZ123")
    software_version = st.text_input("Software Version", value="Gen5 v3.10")

    submitted = st.form_submit_button("Next: Enter Plate Details")

# --- Plate Metadata ---
if submitted:
    st.header("Plate Metadata")

    plate_data = []

    for i in range(int(num_plates)):
        st.subheader(f"Plate {i+1}")
        plate_id = st.text_input(f"Plate {i+1} ID", key=f"plate_{i}_id")
        strains = st.text_input(f"Strain ID(s) for Plate {i+1} (comma-separated)", key=f"plate_{i}_strains")
        phages = st.text_input(f"Phage(s) for Plate {i+1} (comma-separated)", key=f"plate_{i}_phages")
        plate_data.append({
            "Plate ID": plate_id,
            "Strain ID(s)": strains,
            "Phage(s)": phages
        })

    if st.button("Generate Metadata File"):
        # Construct metadata text
        lines = [
            f"Experiment Date: {exp_date.strftime('%Y-%m-%d')}",
            f"Experiment Start Time (GMT+8): {exp_time.strftime('%I:%M %p')}",
            f"Technician: {technician}",
            f"Experiment Type: {exp_type}",
            f"Bacterial Organism: {organism}",
            f"Instrument Serial Number: {serial_number}",
            f"Software Version: {software_version}",
            f"Notes: {notes}",
            f"Number of Plates: {num_plates}",
            ""
        ]

        for i, plate in enumerate(plate_data):
            lines.append(f"--- Plate {i+1} ---")
            lines.append(f"Plate ID: {plate['Plate ID']}")
            lines.append(f"Strain ID(s): {plate['Strain ID(s)']}")
            lines.append(f"Phage(s): {plate['Phage(s)']}")
            lines.append("")

        metadata_text = "\n".join(lines)

        st.success("✅ Metadata file generated!")

        st.download_button(
            label="📥 Download metadata.txt",
            data=metadata_text,
            file_name="metadata.txt",
            mime="text/plain"
        )