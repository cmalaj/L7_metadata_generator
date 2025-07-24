import streamlit as st
from datetime import datetime
import pytz

st.set_page_config(page_title="LogPhase 600 Metadata Generator", layout="centered")
st.title("LogPhase 600 Metadata File Generator")

st.markdown("Use this tool to generate a metadata file for your LogPhase 600 growth/kill curve run.")

# Set default time to GMT+8
tz = pytz.timezone("Asia/Singapore")
now_gmt8 = datetime.now(tz)

# --- Initialize session state for progression ---
if "form_submitted" not in st.session_state:
    st.session_state.form_submitted = False

# --- Experiment Metadata Form ---
if not st.session_state.form_submitted:
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

        if submitted:
            # Save to session state
            st.session_state.form_submitted = True
            st.session_state.exp_date = exp_date
            st.session_state.exp_time = exp_time
            st.session_state.technician = technician
            st.session_state.exp_type = exp_type
            st.session_state.organism = organism
            st.session_state.num_plates = int(num_plates)
            st.session_state.notes = notes
            st.session_state.serial_number = serial_number
            st.session_state.software_version = software_version

# --- Plate Metadata Form ---
if st.session_state.form_submitted:
    st.header("Plate Metadata")
    plate_data = []

    for i in range(st.session_state.num_plates):
        st.subheader(f"Plate {i+1}")
        plate_id = st.text_input(f"Plate {i+1} ID", key=f"plate_{i}_id")
        strains = st.text_input(f"Strain ID(s) for Plate {i+1}", key=f"plate_{i}_strains")
        phages = st.text_input(f"Phage(s) for Plate {i+1}", key=f"plate_{i}_phages")

        plate_data.append({
            "Plate ID": plate_id,
            "Strain ID(s)": strains,
            "Phage(s)": phages
        })

    if st.button("Generate Metadata File"):
        lines = [
            f"Experiment Date: {st.session_state.exp_date.strftime('%Y-%m-%d')}",
            f"Experiment Start Time (GMT+8): {st.session_state.exp_time.strftime('%I:%M %p')}",
            f"Technician: {st.session_state.technician}",
            f"Experiment Type: {st.session_state.exp_type}",
            f"Bacterial Organism: {st.session_state.organism}",
            f"Instrument Serial Number: {st.session_state.serial_number}",
            f"Software Version: {st.session_state.software_version}",
            f"Notes: {st.session_state.notes}",
            f"Number of Plates: {st.session_state.num_plates}",
            ""
        ]

        for i, plate in enumerate(plate_data):
            lines.append(f"--- Plate {i+1} ---")
            lines.append(f"Plate ID: {plate['Plate ID']}")
            lines.append(f"Strain ID(s): {plate['Strain ID(s)']}")
            lines.append(f"Phage(s): {plate['Phage(s)']}")
            lines.append("")

        metadata_text = "\n".join(lines)

        st.success("Metadata file generated!")

        st.download_button(
            label="📥 Download metadata.txt",
            data=metadata_text,
            file_name="metadata.txt",
            mime="text/plain"
        )