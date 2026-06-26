
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Fire Safety Embodied Carbon Calculator", layout="centered")

st.title("🔥 Fire Safety Embodied Carbon Calculator")
st.caption("Simple prototype for JFC – replace placeholder factors with verified values.")

FACTORS = {
    "Fire sprinklers": ("head", 4.8),
    "Smoke detectors": ("unit", 2.1),
    "Fire extinguishers": ("unit", 18.0),
    "Fire door system": ("door", 120.0),
    "Fire hydrant": ("unit", 150.0),
    "Fire damper": ("unit", 30.0),
}

if "rows" not in st.session_state:
    st.session_state.rows = []

item = st.selectbox("Fire safety item", list(FACTORS.keys()))
qty = st.number_input("Quantity", min_value=0.0, value=1.0, step=1.0)

if st.button("Add item"):
    unit, factor = FACTORS[item]
    total = qty * factor
    st.session_state.rows.append({
        "Item": item,
        "Quantity": qty,
        "Unit": unit,
        "Factor (kgCO2e/unit)": factor,
        "Embodied Carbon (kgCO2e)": total
    })

if st.session_state.rows:
    df = pd.DataFrame(st.session_state.rows)
    st.subheader("Assessment")
    st.dataframe(df, use_container_width=True)
    grand = df["Embodied Carbon (kgCO2e)"].sum()
    st.metric("Total Embodied Carbon", f"{grand:,.2f} kgCO2e")
    st.download_button(
        "Download CSV",
        data=df.to_csv(index=False),
        file_name="fire_embodied_carbon_results.csv",
        mime="text/csv",
    )
else:
    st.info("Add an item to begin.")
