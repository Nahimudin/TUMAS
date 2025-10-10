import streamlit as st
import pandas as pd
import base64
import plotly.graph_objects as go
import json
import streamlit.components.v1 as components

# ================== PAGE SETUP ==================
st.set_page_config(page_title="TUMAS", page_icon="icon-192x192.png")
st.header("")

# Hide Streamlit style
hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    body {background-color: #2C004E;}
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# ================== LOGIN SYSTEM ==================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

users = {
    "nahim": "123",
    "kamil": "456",
    "admin": "batik"
}

if not st.session_state.logged_in:
    st.markdown("<h3 style='text-align:center; color:white;'>🔒 Login to TUMAS</h3>", unsafe_allow_html=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in users and password == users[username]:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()
        else:
            st.error("❌ Invalid username or password")
    st.stop()

# ================== MAIN APP ==================
st.markdown(f"<h3 style='color:white;'>👋 Welcome, {st.session_state.username.upper()}</h3>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("📁 Upload Excel File", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Search inputs
    st.markdown("<h4 style='color:#C42454;'>🔍 Search Tyre Records</h4>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        sn = st.text_input("Search by Serial Number (SN)")
    with col2:
        part_no = st.text_input("Search by Part Number (P/No)")
    with col3:
        wo_no = st.text_input("Search by W/O No")

    search_button = st.button("Search")

    if "search_results" not in st.session_state:
        st.session_state.search_results = None

    if search_button:
        query = df.copy()
        if sn:
            query = query[query["SN"].astype(str).str.contains(sn, case=False, na=False)]
        if part_no:
            query = query[query["P/No"].astype(str).str.contains(part_no, case=False, na=False)]
        if wo_no:
            query = query[query["W/O No"].astype(str).str.contains(wo_no, case=False, na=False)]

        if not query.empty:
            st.session_state.search_results = query
        else:
            st.session_state.search_results = pd.DataFrame()
            st.warning("⚠️ No matching records found.")

    # ================== TABLE DISPLAY ==================
    if st.session_state.search_results is not None and not st.session_state.search_results.empty:
        result = st.session_state.search_results
        st.success(f"✅ Found {len(result)} matching record(s).")

        # Black background table container
        st.markdown("""
        <div style="background-color: black; padding: 15px 25px; border-radius: 12px; margin: 25px 0;">
            <div style="display: grid; grid-template-columns: 1.2fr 1.2fr 1.2fr 1.5fr 1fr 1fr 1fr 0.8fr; 
                        gap: 10px; padding: 10px; border-bottom: 2px solid #C42454;">
                <div style="color: white; font-weight: bold;">Date In</div>
                <div style="color: white; font-weight: bold;">Date Out</div>
                <div style="color: white; font-weight: bold;">Ex-Aircraft</div>
                <div style="color: white; font-weight: bold;">Description</div>
                <div style="color: white; font-weight: bold;">W/O No</div>
                <div style="color: white; font-weight: bold;">P/No</div>
                <div style="color: white; font-weight: bold;">SN</div>
                <div style="color: white; font-weight: bold;">Action</div>
            </div>
        """, unsafe_allow_html=True)

        # Data rows with "Open" expanders (kept functional)
        for idx, row in result.iterrows():
            st.markdown(f"""
            <div style="display: grid; grid-template-columns: 1.2fr 1.2fr 1.2fr 1.5fr 1fr 1fr 1fr 0.8fr; 
                        gap: 10px; padding: 8px 10px; background-color: black; border-bottom: 1px solid #444;">
                <div style="color: white;">{row.get('Date In', 'N/A')}</div>
                <div style="color: white;">{row.get('DATE OUT', 'N/A')}</div>
                <div style="color: white;">{row.get('Ex-Aircraft', 'N/A')}</div>
                <div style="color: white;">{row.get('Description', 'N/A')}</div>
                <div style="color: white;">{row.get('W/O No', 'N/A')}</div>
                <div style="color: white;">{row.get('P/No', 'N/A')}</div>
                <div style="color: white;">{row.get('SN', 'N/A')}</div>
                <div style="color: white;">⬇️</div>
            </div>
            """, unsafe_allow_html=True)

            with st.expander(f"🔧 Open Details for {row.get('Description', 'Record')}"):
                st.markdown(f"""
                <div style="background-color:black; padding:15px; border-radius:10px; color:white;">
                    <b>Date In:</b> {row.get('Date In', 'N/A')}<br>
                    <b>Date Out:</b> {row.get('DATE OUT', 'N/A')}<br>
                    <b>Ex-Aircraft:</b> {row.get('Ex-Aircraft', 'N/A')}<br>
                    <b>Description:</b> {row.get('Description', 'N/A')}<br>
                    <b>W/O No:</b> {row.get('W/O No', 'N/A')}<br>
                    <b>P/No:</b> {row.get('P/No', 'N/A')}<br>
                    <b>SN:</b> {row.get('SN', 'N/A')}<br>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

else:
    st.info("📂 Please upload an Excel file to begin.")
