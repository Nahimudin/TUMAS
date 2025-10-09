import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import base64

st.set_page_config(page_title="TUMAS", page_icon="icon-192x192.png")

# Hide Streamlit default UI
hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

st.title("🛞 Tire Usage Monitoring Application System (TUMAS)")

# Load Excel
@st.cache_data
def load_data():
    return pd.read_excel("tire_data.xlsx")

df = load_data()

# Clean up column names
df.columns = df.columns.str.strip().str.replace("'", "").str.replace('"', '')
df = df.applymap(lambda x: str(x).strip() if isinstance(x, str) else x)

# Sidebar navigation
page = st.sidebar.radio("Navigate", ["Search", "About"])

if "selected_row" not in st.session_state:
    st.session_state.selected_row = None
if "last_results" not in st.session_state:
    st.session_state.last_results = None

if page == "Search":
    st.header("🔍 Tire Lookup")

    with st.form("search_form"):
        serial = st.text_input("Search by Serial Number (SN):")
        part_no = st.text_input("Search by Part Number (P/No):")
        wo_no = st.text_input("Search by Work Order Number (W/O No):")
        submitted = st.form_submit_button("Search")

    if submitted:
        result = df.copy()
        if serial:
            result = result[result['SN'].astype(str).str.contains(serial.strip(), case=False, na=False)]
        if part_no:
            result = result[result['P/No'].astype(str).str.contains(part_no.strip(), case=False, na=False)]
        if wo_no:
            result = result[result['W/O No'].astype(str).str.contains(wo_no.strip(), case=False, na=False)]

        if result.empty:
            st.warning("No results found. Please check your search inputs.")
        else:
            st.session_state.last_results = result
            st.session_state.selected_row = None

    # Display table view if not showing a specific record
    if st.session_state.last_results is not None and st.session_state.selected_row is None:
        result = st.session_state.last_results

        st.write("### Search Results")
        show_df = result[['Date In', 'Ex-Aircraft', 'Description', 'SN', 'P/No', 'W/O No']].copy()

        # Add Open button for each row
        for i in range(len(show_df)):
            c1, c2, c3, c4, c5, c6, c7 = st.columns([1.5, 1.5, 3, 2, 2, 2, 1])
            c1.write(show_df.iloc[i]['Date In'])
            c2.write(show_df.iloc[i]['Ex-Aircraft'])
            c3.write(show_df.iloc[i]['Description'])
            c4.write(show_df.iloc[i]['SN'])
            c5.write(show_df.iloc[i]['P/No'])
            c6.write(show_df.iloc[i]['W/O No'])
            if c7.button("Open", key=f"open_{i}"):
                st.session_state.selected_row = show_df.iloc[i]['SN']
                st.rerun()

    # Display full record if "Open" is clicked
    elif st.session_state.selected_row is not None:
        full_record = df[df['SN'] == st.session_state.selected_row]
        if not full_record.empty:
            row = full_record.iloc[0]

            st.markdown(f"""
                <div style='background-color:#F8F3F8;padding:20px;border-radius:15px;'>
                    <h3 style='color:#C42454;'>{row['Description']}</h3>
                    <p><b style='color:#C42454;'>📌 Tire On:</b> {row['Ex-Aircraft']}</p>
                    <p><b style='color:#C42454;'>📆 Date In:</b> {row['Date In']}</p>
                    <p><b style='color:#C42454;'>⚙️ P/No:</b> {row['P/No']}</p>
                    <p><b style='color:#C42454;'>🔢 SN:</b> {row['SN']}</p>
                    <p><b style='color:#C42454;'>🧾 W/O No:</b> {row['W/O No']}</p>
                    <p><b style='color:#C42454;'>🛠️ RO Repair Order No:</b> {row['RO Repair Order No']}</p>
                    <p><b style='color:#C42454;'>📄 TC Remark:</b> {row['TC Remark']}</p>
                    <p><b style='color:#C42454;'>📊 Cycles Since Installed:</b> {row['Cycles Since Installed']}</p>
                </div>
            """, unsafe_allow_html=True)

            # Example chart (if you have data)
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=['Cycles Since Installed'],
                y=[int(row['Cycles Since Installed']) if str(row['Cycles Since Installed']).isdigit() else 0],
                marker_color='#C42454'
            ))
            fig.update_layout(title="Tire Usage Chart", showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

            if st.button("⬅ Back to Table"):
                st.session_state.selected_row = None
                st.rerun()

if page == "About":
    st.header("📘 About TUMAS")
    st.write("""
    Tire Usage Monitoring Application System (TUMAS) helps record and monitor
    aircraft tire usage, replacement, and service details to improve maintenance
    efficiency and traceability.
    """)
