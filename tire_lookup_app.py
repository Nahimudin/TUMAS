import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="TUMAS", page_icon="icon-192x192.png")

# Load your existing dataset
df = pd.read_excel("your_file.xlsx")

# Ensure consistent column names
df.columns = df.columns.str.strip().str.replace("'", "")

# --- PAGE NAVIGATION ---
page = st.sidebar.selectbox("Menu", ["Search"])

# Initialize session state for selected record
if "selected_record" not in st.session_state:
    st.session_state.selected_record = None

if page == "Search":
    st.title("🔍 Tire Lookup")

    serial = st.text_input("Search by Serial Number (SN)")
    part_no = st.text_input("Search by Part Number (P/No)")
    wo_no = st.text_input("Search by Work Order (W/O No)")

    # Filter logic
    result = df.copy()
    if serial:
        result = result[result["SN"].astype(str).str.contains(serial.strip(), case=False, na=False)]
    if part_no:
        result = result[result["P/No"].astype(str).str.contains(part_no.strip(), case=False, na=False)]
    if wo_no:
        result = result[result["W/O No"].astype(str).str.contains(wo_no.strip(), case=False, na=False)]

    # --- SHOW DETAIL VIEW IF SELECTED ---
    if st.session_state.selected_record is not None:
        row = st.session_state.selected_record
        st.success(f"✅ Showing details for {row['SN']}")
        
        # Keep your original card and chart layout below
        st.markdown(f"""
            <div style="background-color:#3C1361;padding:20px;border-radius:15px;color:white;">
                <h3>{row['Description']}</h3>
                <p><b>Date In:</b> {row['Date In']}</p>
                <p><b>Ex-Aircraft:</b> {row['Ex-Aircraft']}</p>
                <p><b>P/No:</b> {row['P/No']}</p>
                <p><b>W/O No:</b> {row['W/O No']}</p>
                <p><b>SN:</b> {row['SN']}</p>
            </div>
        """, unsafe_allow_html=True)

        # Example chart (same as your original style)
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=65,
            gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#C42454"}},
            title={'text': "Usage %"}
        ))
        st.plotly_chart(fig, use_container_width=True)

        if st.button("⬅ Back to Table"):
            st.session_state.selected_record = None
            st.rerun()

    # --- SHOW SEARCH TABLE ---
    else:
        if not result.empty:
            st.success(f"✅ Found {len(result)} record(s)")

            # Display as table with open buttons
            for i, (_, row) in enumerate(result.iterrows()):
                c1, c2, c3, c4, c5, c6, c7 = st.columns([1.3, 1.3, 2, 1.3, 1.3, 1.3, 0.8])
                c1.write(str(row["Date In"]))
                c2.write(str(row["Ex-Aircraft"]))
                c3.write(str(row["Description"]))
                c4.write(str(row["SN"]))
                c5.write(str(row["P/No"]))
                c6.write(str(row["W/O No"]))
                if c7.button("Open", key=f"open_{i}"):
                    st.session_state.selected_record = row
                    st.rerun()
        else:
            st.warning("No matching records found.")
