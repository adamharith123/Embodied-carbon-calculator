
import io
from datetime import datetime

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Fire Safety Embodied Carbon Calculator",
    page_icon="🔥",
    layout="wide"
)

@st.cache_data
def load_default_factors():
    return pd.DataFrame([
        {"Item": "Fire sprinklers", "Category": "Active fire protection", "Unit": "head", "Carbon Factor (kgCO2e/unit)": 4.8, "Source/Notes": "Placeholder factor - replace with verified EPD/database value"},
        {"Item": "Smoke detectors", "Category": "Detection and alarm", "Unit": "unit", "Carbon Factor (kgCO2e/unit)": 2.1, "Source/Notes": "Placeholder factor - replace with verified EPD/database value"},
        {"Item": "Fire extinguishers", "Category": "Portable equipment", "Unit": "unit", "Carbon Factor (kgCO2e/unit)": 18.0, "Source/Notes": "Placeholder factor - replace with verified EPD/database value"},
        {"Item": "Fire door system", "Category": "Passive fire protection", "Unit": "door", "Carbon Factor (kgCO2e/unit)": 120.0, "Source/Notes": "Placeholder factor - replace with verified EPD/database value"},
        {"Item": "Fire hydrant", "Category": "Water-based systems", "Unit": "unit", "Carbon Factor (kgCO2e/unit)": 150.0, "Source/Notes": "Placeholder factor - replace with verified EPD/database value"},
        {"Item": "Fire damper", "Category": "HVAC fire protection", "Unit": "unit", "Carbon Factor (kgCO2e/unit)": 30.0, "Source/Notes": "Placeholder factor - replace with verified EPD/database value"},
        {"Item": "Fire stop mortar", "Category": "Passive fire protection", "Unit": "kg", "Carbon Factor (kgCO2e/unit)": 1.1, "Source/Notes": "Placeholder factor - replace with verified EPD/database value"},
        {"Item": "Fire-rated steel pipe", "Category": "Water-based systems", "Unit": "m", "Carbon Factor (kgCO2e/unit)": 12.0, "Source/Notes": "Placeholder factor - replace with verified EPD/database value"},
        {"Item": "Fire-retardant panel", "Category": "Passive fire protection", "Unit": "m2", "Carbon Factor (kgCO2e/unit)": 18.0, "Source/Notes": "Placeholder factor - replace with verified EPD/database value"},
        {"Item": "Fire blocker", "Category": "Passive fire protection", "Unit": "unit", "Carbon Factor (kgCO2e/unit)": 8.0, "Source/Notes": "Placeholder factor - replace with verified EPD/database value"},
    ])

def calculate_row(item, quantity, factors_df):
    match = factors_df[factors_df["Item"] == item].iloc[0]
    factor = float(match["Carbon Factor (kgCO2e/unit)"])
    return {
        "Item": item,
        "Category": match["Category"],
        "Quantity": float(quantity),
        "Unit": match["Unit"],
        "Carbon Factor (kgCO2e/unit)": factor,
        "Embodied Carbon (kgCO2e)": float(quantity) * factor,
        "Source/Notes": match["Source/Notes"],
    }

def convert_df_to_csv(df):
    return df.to_csv(index=False).encode("utf-8")

def build_summary_text(project_name, asset_type, df):
    total = df["Embodied Carbon (kgCO2e)"].sum() if not df.empty else 0
    highest = "N/A"
    if not df.empty:
        highest = df.sort_values("Embodied Carbon (kgCO2e)", ascending=False).iloc[0]["Item"]

    lines = [
        "Fire Safety Embodied Carbon Summary",
        f"Project: {project_name or 'Untitled project'}",
        f"Asset type: {asset_type}",
        f"Date: {datetime.now().strftime('%d %b %Y')}",
        "",
        f"Total embodied carbon: {total:,.2f} kgCO2e",
        f"Items assessed: {len(df)}",
        f"Highest contributor: {highest}",
        "",
        "Itemised breakdown:",
    ]

    for _, row in df.iterrows():
        lines.append(
            f"- {row['Item']}: {row['Quantity']:,.2f} {row['Unit']} x "
            f"{row['Carbon Factor (kgCO2e/unit)']:,.2f} = "
            f"{row['Embodied Carbon (kgCO2e)']:,.2f} kgCO2e"
        )

    lines.append("")
    lines.append("Note: Current carbon factors are placeholders unless replaced with verified EPD/database values.")
    return "\n".join(lines).encode("utf-8")

if "assessment_rows" not in st.session_state:
    st.session_state.assessment_rows = []

if "factor_database" not in st.session_state:
    st.session_state.factor_database = load_default_factors()

st.title("🔥 Fire Safety Embodied Carbon Calculator")
st.caption("Version 2.0 prototype — simple tool for fire engineers to estimate embodied carbon of fire safety equipment and materials.")

with st.sidebar:
    st.header("Project details")
    project_name = st.text_input("Project name", value="JFC Fire Safety Assessment")
    asset_type = st.radio("Assessment type", ["Proposed new design", "Existing asset"], index=0)
    st.divider()
    st.subheader("Factor database")
    st.caption("Current values are placeholders. Replace them with verified values before formal use.")
    uploaded_factors = st.file_uploader("Upload carbon factor CSV", type=["csv"], help="Required columns: Item, Category, Unit, Carbon Factor (kgCO2e/unit), Source/Notes")
    if uploaded_factors is not None:
        try:
            new_factors = pd.read_csv(uploaded_factors)
            required_cols = {"Item", "Category", "Unit", "Carbon Factor (kgCO2e/unit)"}
            if required_cols.issubset(set(new_factors.columns)):
                if "Source/Notes" not in new_factors.columns:
                    new_factors["Source/Notes"] = "User-uploaded factor"
                st.session_state.factor_database = new_factors
                st.success("Carbon factor database loaded.")
            else:
                st.error("CSV missing required columns.")
        except Exception as e:
            st.error(f"Could not read factor CSV: {e}")

factors_df = st.session_state.factor_database
assessment_df = pd.DataFrame(st.session_state.assessment_rows)

total_carbon = assessment_df["Embodied Carbon (kgCO2e)"].sum() if not assessment_df.empty else 0
item_count = len(assessment_df)
highest_item = "N/A"
highest_value = 0

if not assessment_df.empty:
    top_row = assessment_df.sort_values("Embodied Carbon (kgCO2e)", ascending=False).iloc[0]
    highest_item = top_row["Item"]
    highest_value = top_row["Embodied Carbon (kgCO2e)"]

col1, col2, col3 = st.columns(3)
col1.metric("Total embodied carbon", f"{total_carbon:,.2f} kgCO₂e")
col2.metric("Items assessed", f"{item_count}")
col3.metric("Highest contributor", highest_item, f"{highest_value:,.2f} kgCO₂e" if item_count else None)

st.divider()

tab1, tab2, tab3, tab4 = st.tabs(["➕ Manual entry", "📂 Upload BOM", "📊 Results", "⚙️ Factor database"])

with tab1:
    st.subheader("Add fire safety item")
    st.write("Select an item, enter quantity, then add it to the assessment.")

    left, mid, right = st.columns([2, 1, 1])

    with left:
        selected_item = st.selectbox("Fire safety item", factors_df["Item"].tolist())

    selected_factor = factors_df[factors_df["Item"] == selected_item].iloc[0]

    with mid:
        quantity = st.number_input(f"Quantity ({selected_factor['Unit']})", min_value=0.0, value=1.0, step=1.0)

    with right:
        st.write("")
        st.write("")
        if st.button("Add item", type="primary", use_container_width=True):
            st.session_state.assessment_rows.append(calculate_row(selected_item, quantity, factors_df))
            st.success(f"Added {selected_item}.")

    st.info(
        f"Selected factor: {selected_factor['Carbon Factor (kgCO2e/unit)']} kgCO₂e/{selected_factor['Unit']} "
        f"— {selected_factor['Source/Notes']}"
    )

    if st.session_state.assessment_rows:
        st.subheader("Current assessment")
        st.dataframe(pd.DataFrame(st.session_state.assessment_rows), use_container_width=True, hide_index=True)

        if st.button("Clear assessment"):
            st.session_state.assessment_rows = []
            st.rerun()

with tab2:
    st.subheader("Upload Bill of Materials")
    st.write("Upload a CSV file with at least these two columns: **Item** and **Quantity**.")

    sample = pd.DataFrame({
        "Item": ["Fire sprinklers", "Smoke detectors", "Fire extinguishers"],
        "Quantity": [120, 45, 10],
    })

    st.download_button(
        "Download sample BOM template",
        data=convert_df_to_csv(sample),
        file_name="sample_fire_bom.csv",
        mime="text/csv"
    )

    bom_file = st.file_uploader("Upload BOM CSV", type=["csv"], key="bom_upload")
    if bom_file is not None:
        try:
            bom_df = pd.read_csv(bom_file)
            if {"Item", "Quantity"}.issubset(set(bom_df.columns)):
                added = 0
                missing = []
                for _, row in bom_df.iterrows():
                    item_name = str(row["Item"]).strip()
                    if item_name in factors_df["Item"].tolist():
                        st.session_state.assessment_rows.append(calculate_row(item_name, float(row["Quantity"]), factors_df))
                        added += 1
                    else:
                        missing.append(item_name)

                st.success(f"Added {added} item(s) from BOM.")
                if missing:
                    st.warning("These items were not found in the factor database: " + ", ".join(missing))
            else:
                st.error("BOM must include columns named Item and Quantity.")
        except Exception as e:
            st.error(f"Could not process BOM: {e}")

with tab3:
    st.subheader("Results summary")

    if assessment_df.empty:
        st.warning("No items added yet. Use Manual entry or Upload BOM first.")
    else:
        display_df = assessment_df.copy()
        display_df["Embodied Carbon (kgCO2e)"] = display_df["Embodied Carbon (kgCO2e)"].round(2)

        st.dataframe(display_df, use_container_width=True, hide_index=True)

        chart_df = (
            display_df.groupby("Item", as_index=False)["Embodied Carbon (kgCO2e)"]
            .sum()
            .sort_values("Embodied Carbon (kgCO2e)", ascending=False)
        )

        st.subheader("Carbon contributors")
        st.bar_chart(chart_df, x="Item", y="Embodied Carbon (kgCO2e)")

        csv_data = convert_df_to_csv(display_df)
        summary_data = build_summary_text(project_name, asset_type, display_df)

        c1, c2 = st.columns(2)
        with c1:
            st.download_button(
                "Download results CSV",
                data=csv_data,
                file_name="fire_safety_embodied_carbon_results.csv",
                mime="text/csv",
                use_container_width=True
            )
        with c2:
            st.download_button(
                "Download summary TXT",
                data=summary_data,
                file_name="fire_safety_embodied_carbon_summary.txt",
                mime="text/plain",
                use_container_width=True
            )

with tab4:
    st.subheader("Carbon factor database")
    st.write("This table controls the app calculations. For the final JFC version, replace placeholder values with verified carbon factors.")
    st.dataframe(factors_df, use_container_width=True, hide_index=True)

    st.download_button(
        "Download current factor database",
        data=convert_df_to_csv(factors_df),
        file_name="carbon_factors.csv",
        mime="text/csv"
    )

st.divider()
st.caption("Disclaimer: This prototype provides indicative calculations only. It should not be used for formal carbon reporting until all carbon factors, boundaries, and assumptions are verified.")
