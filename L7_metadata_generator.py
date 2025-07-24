import streamlit as st
import pandas as pd
from datetime import datetime
import io

st.set_page_config(page_title="LogPhase 600 Metadata Generator", layout="centered")

st.title("🧬 LogPhase 600 Metadata File Generator")

st.markdown("Fill in the details below to generate your `metadata.txt` file for an experiment.")

# Form
with st.form("metadata_form"):
    exp_date = st.date_input("Experiment Date", value=datetime.today())
    exp_time = st.time_input("Experiment Start Time", value=datetime.now().time())
    technician = st.text_input("Technician Name or Initials")
    exp_type = st.selectbox("Experiment Type", ["Quality Control", "Production"])
    organism = st.text_input("Organism / Strain", value="E. coli MG1655")
    plate_id = st.text_input("Plate ID", placeholder="e.g. Plate_001_20250724")
    notes = st.text_area("Additional Notes")
    serial_number = st.text_input("Instrument Serial Number", value="LP600-XYZ123")
    software_version = st.text_input("Software Version", value="Gen5 v3.10")
    
    submitted = st.form_submit_button("Generate Metadata File")

if submitted:
    metadata_dict = {
        "Experiment Date": exp_date.strftime('%Y-%m-%d'),
        "Experiment Start Time": exp_time.strftime('%I:%M %p'),
        "Technician": technician,
        "Experiment Type": exp_type,
        "Organism / Strain": organism,
        "Plate ID": plate_id,
        "Notes": notes,
        "Instrument Serial Number": serial_number,
        "Software Version": software_version
    }

    metadata_str = "\n".join(f"{key}: {value}" for key, value in metadata_dict.items())

    st.success("Metadata file generated successfully!")

    st.download_button(
        label="📥 Download metadata.txt",
        data=metadata_str,
        file_name="metadata.txt",
        mime="text/plain"
    )