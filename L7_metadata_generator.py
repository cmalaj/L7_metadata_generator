import streamlit as st
from datetime import datetime
import pytz
import pandas as pd

# Setup
st.set_page_config(page_title="LogPhase 600 Metadata Generator", layout="centered")
st.title("LogPhase 600 Metadata File Generator")
st.markdown("Use this tool to generate a metadata file for your LogPhase 600 growth/kill curve run.")

# Set default time to GMT+8
tz = pytz.timezone("Asia/Singapore")
now_gmt8 = datetime.now(tz)

# Session State Init
if "form_submitted" not in st.session_state:
    st.session_state.form_submitted = False

# --- EXPERIMENT METADATA FORM ---
if not st.session_state.form_submitted:
    st.header("Experiment Information")

    with st.form("main_metadata_form"):
        exp_date = st.date_input("Experiment Date", value=now_gmt8.date())
        exp_time = st.time_input("Experiment Start Time (GMT+8)", value=now_gmt8.time())
        technician = st.text_input("Technician Name or Initials")
        exp_type = st.selectbox("Experiment Type", ["Quality Control", "Production"])
        organism = st.text_input("Bacterial Organism", value="P. aeruginosa")
        batch_tag = st.text_input("Brief Description / Batch Tag (used in filename)", placeholder="e.g. AST15_Prod_Run1")
        num_plates = st.number_input("Number of Plates in this Run", min_value=1, step=1, value=4)
        notes = st.text_area("Additional Notes")
        serial_number = st.text_input("Instrument Serial Number", value="LP600-XYZ123")
        software_version = st.text_input("Software Version", value="Gen5 v3.10")
        submitted = st.form_submit_button("Next: Enter Plate Details")

        if submitted:
            st.session_state.form_submitted = True
            st.session_state.exp_date = exp_date
            st.session_state.exp_time = exp_time
            st.session_state.technician = technician
            st.session_state.exp_type = exp_type
            st.session_state.organism = organism
            st.session_state.batch_tag = batch_tag
            st.session_state.num_plates = int(num_plates)
            st.session_state.notes = notes
            st.session_state.serial_number = serial_number
            st.session_state.software_version = software_version

# --- PLATE METADATA SECTION ---
if st.session_state.form_submitted:
    st.header("Plate Metadata")

    plate_data = []

    for i in range(st.session_state.num_plates):
        st.subheader(f"Plate {i + 1}")

        layout_mode = st.radio(
            f"Layout Mode for Plate {i+1}",
            ["Use preset layout", "Start with empty layout"],
            key=f"layout_mode_{i}",
            horizontal=True
        )

        plate_id = st.text_input(f"Plate {i+1} ID", key=f"plate_{i}_id")
        strain_input = st.text_input(f"Bacterial Strain ID", key=f"plate_{i}_strain")
        phages = st.text_input(f"Phage(s) for Plate {i+1} (comma-separated, e.g. P1,P2,P3,P4)", key=f"plate_{i}_phages")

        rows = list("ABCDEFGH")
        cols = [str(c) for c in range(1, 13)]
        layout_df = pd.DataFrame("", index=rows, columns=cols)

        if layout_mode == "Use preset layout":
            phage_list = [p.strip() for p in phages.split(",") if p.strip()]
            tech_reps = ["T1", "T2"]
            batches = ["B1", "B2", "B3"]

            if len(phage_list) != 4:
                st.warning("⚠️ Please enter exactly 4 phage IDs.")
            else:
                for row_idx, row_letter in enumerate(rows):
                    phage_id = phage_list[row_idx // 2]
                    tech_rep = tech_reps[row_idx % 2]

                    # Columns 1–9
                    well_values = []
                    for moi in ["MOI1", "MOI0.5", "MOI0.1"]:
                        for batch in batches:
                            label = f"{phage_id}_{moi}-{strain_input}_{batch}-{tech_rep}"
                            well_values.append(label)

                    # Columns 10–12 — match original layout
                    if row_idx == 0:
                        well_values += [phage_id, "BROTH", f"{strain_input}_B1"]
                    elif row_idx == 1:
                        well_values += [phage_id, "VEHICLE", f"{strain_input}_B1"]
                    elif row_idx == 2:
                        well_values += [phage_id, "PAO1", "EMPTY"]
                    elif row_idx == 3:
                        well_values += [phage_id, "EMPTY", f"{strain_input}_B2"]
                    elif row_idx == 4:
                        well_values += [phage_id, "BROTH", f"{strain_input}_B2"]
                    elif row_idx == 5:
                        well_values += [phage_id, "VEHICLE", "EMPTY"]
                    elif row_idx == 6:
                        well_values += [phage_id, "PAO1", f"{strain_input}_B3"]
                    elif row_idx == 7:
                        well_values += [phage_id, "EMPTY", f"{strain_input}_B3"]

                    layout_df.loc[row_letter, :] = well_values

        # Editable grid
        st.markdown(f"**Customize Layout for Plate {i+1} (optional)**")
        layout_df = st.data_editor(
            layout_df,
            key=f"plate_{i}_layout_editor",
            use_container_width=True,
            num_rows="fixed",
            column_config={col: st.column_config.TextColumn() for col in cols},
            hide_index=False
        )

        plate_data.append({
            "Plate ID": plate_id,
            "Strain ID(s)": strain_input,
            "Phage(s)": phages,
            "Layout": layout_df
        })

    # Generate metadata file
    if st.button("📄 Generate Metadata File"):
        lines = [
            f"Experiment Date: {st.session_state.exp_date.strftime('%Y-%m-%d')}",
            f"Experiment Start Time (GMT+8): {st.session_state.exp_time.strftime('%I:%M %p')}",
            f"Technician: {st.session_state.technician}",
            f"Experiment Type: {st.session_state.exp_type}",
            f"Bacterial Organism: {st.session_state.organism}",
            f"Batch Tag: {st.session_state.batch_tag}",
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
            lines.append("Plate Layout:")
            lines.append(plate["Layout"].to_csv(sep="\t", index=True))
            lines.append("")

        metadata_text = "\n".join(lines)

        # Format filename
        exp_type_short = "QC" if st.session_state.exp_type == "Quality Control" else "PROD"
        filename_base = f"{st.session_state.exp_date.strftime('%Y-%m-%d')}_{st.session_state.technician}_{exp_type_short}_{st.session_state.batch_tag}"
        safe_filename = filename_base.replace(" ", "_").replace("/", "-")

        st.success("Metadata file generated!")
        st.download_button(
            label="Download metadata.txt",
            data=metadata_text,
            file_name=f"{safe_filename}.txt",
            mime="text/plain"
        )

    if st.button("🔄 Start Over"):
        st.session_state.clear()
        st.experimental_rerun()