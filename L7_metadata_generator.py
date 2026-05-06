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

# Define phage order for standard layout
PHAGE_ORDER = [
    "4TWA",
    "V1IB",
    "N5HX",
    "EUVX",
    "0VBC",
    "4NWX",
    "KPSM",
    "C7E4",
    "VKO7",
    "WDPI",
    "YK3I",
    "XMDS",
    "P71S",
    "T0U1",
    "9XQE",
    "AUV6",
    "Z6TS",
    "NC61",
    "MZOB",
    "DKQ8",
    "2CJA",
    "6281",
    "NQ4L",
    "R4QE",
    "LG65",
    "J5TC",
    "O8XK",
    "GE9K",
    "EBID"
]

# Helper function to generate standard layout based on strain, phage order, and plate number as of 14 Nov 2025
def generate_standard_layout(strain_id, plate_number):
    rows = list("ABCDEFGH")
    cols = [str(c) for c in range(1, 13)]
    layout_df = pd.DataFrame("", index=rows, columns=cols)

    base_layout = [
        [1, 9, 17, 25, 1, 9, 17, 25, 1, 9, 17, 25],
        [2, 10, 18, 26, 2, 10, 18, 26, 2, 10, 18, 26],
        [3, 11, 19, 27, 3, 11, 19, 27, 3, 11, 19, 27],
        [4, 12, 20, 28, 4, 12, 20, 28, 4, 12, 20, 28],
        [5, 13, 21, 29, 5, 13, 21, 29, 5, 13, 21, 29],
        [6, 14, 22, "LB", 6, 14, 22, "LB", 6, 14, 22, "LB"],
        [7, 15, 23, "BR1", 7, 15, 23, "BR2", 7, 15, 23, "BR3"],
        [8, 16, 24, "PAO1", 8, 16, 24, "PAO1", 8, 16, 24, "PAO1"],
    ]

    plate_control_map = {
        1: "PROP_HOST_MOI0.1_POS",
        2: "PHAGE_ONLY_NEG",
        3: "PROP_HOST_ONLY_NEG",
        4: "PROP_HOST_MOI0.01_POS",
    }

    phage_control_type = plate_control_map.get(plate_number, f"PHAGE_CONTROL_PLATE{plate_number}")

    for r_idx, row in enumerate(rows):
        for c_idx, col in enumerate(cols):
            value = base_layout[r_idx][c_idx]

            if value == "LB":
                label = "LB"
            elif value == "PAO1":
                label = "PAO1"
            elif isinstance(value, str) and value.startswith("BR"):
                label = f"{strain_id}_{value}"
            else:
                phage_id = PHAGE_ORDER[value - 1]

                if c_idx < 4:
                    label = f"{phage_id}_MOI0.01-{strain_id}"
                elif c_idx < 8:
                    label = f"{phage_id}_MOI0.1-{strain_id}"
                else:
                    label = f"{phage_id}_{phage_control_type}"

            layout_df.loc[row, col] = label

    return layout_df



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
        batch_tag = st.text_input("Brief Description / Batch Tag (used in filename)", placeholder="e.g. AST15-Run1")
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

        rows = list("ABCDEFGH")
        cols = [str(c) for c in range(1, 13)]
        layout_df = pd.DataFrame("", index=rows, columns=cols)

        if layout_mode == "Use preset layout":
            if not strain_input.strip():
                st.warning("⚠️ Please enter a bacterial strain ID.")
            else:
                layout_df = generate_standard_layout(
                    strain_id=strain_input.strip(),
                    plate_number=i + 1
                )

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
            lines.append(f"Phage(s): {', '.join(PHAGE_ORDER)}")
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
        st.rerun()