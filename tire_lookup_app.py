import streamlit as st
import pandas as pd
import base64
import json
import streamlit.components.v1 as components

# --- Page setup ---
st.set_page_config(page_title="TUMAS", page_icon="icon-192x192.png")
st.header("")

# --- Hide Streamlit UI ---
hide_st_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- Helper: load image as base64 ---
def get_base64_image(img_path):
    try:
        with open(img_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        st.error(f"⚠️ Logo file '{img_path}' not found.")
        return ""

logo_base64 = get_base64_image("batik_logo_transparent.png")

# --- Load user credentials ---
USERS_FILE = "users.xlsx"
try:
    users_df = pd.read_excel(USERS_FILE)
    users_df['Username'] = users_df['Username'].astype(str).str.strip()
    users_df['Password'] = users_df['Password'].astype(str).str.strip()
    USER_CREDENTIALS = dict(zip(users_df["Username"], users_df["Password"]))
except Exception as e:
    st.error(f"⚠️ Could not load '{USERS_FILE}': {e}")
    USER_CREDENTIALS = {}

# --- Session state setup ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "selected_index" not in st.session_state:
    st.session_state.selected_index = None

# --- CSS ---
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #5C246E, #C42454); background-attachment: fixed; }
section[data-testid="stSidebar"] { background-color: #5C246E !important; }
.result-card {
    background-color: white; border-radius: 15px;
    padding: 25px; margin: 20px auto;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.2);
}
.footer { text-align:center; color:white; font-size:14px; margin-top:60px; opacity:0.8; }
</style>
""", unsafe_allow_html=True)

# --- LOGIN PAGE ---
if not st.session_state.logged_in:
    st.markdown(f"""
        <div style="text-align:center; margin-top:80px;">
            <img src="data:image/png;base64,{logo_base64}" width="200">
            <h1 style="color:white;">TIRE USAGE MONITORING APPLICATION SYSTEM</h1>
        </div>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        username = st.text_input("👤 Username")
        password = st.text_input("🔑 Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            username_input = username.strip()
            password_input = password.strip()
            if username_input in USER_CREDENTIALS:
                if USER_CREDENTIALS[username_input] == password_input:
                    st.session_state.logged_in = True
                    st.session_state.username = username_input
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error("❌ Incorrect password")
            else:
                st.error("❌ Username not found")

# --- MAIN APP ---
else:
    st.markdown(f"""
        <div style="text-align:center; margin-bottom:20px;">
            <img src="data:image/png;base64,{logo_base64}" width="120">
            <h3 style='color:white;'>Welcome, {st.session_state.username} 👋</h3>
        </div>
    """, unsafe_allow_html=True)

    page = st.radio("", ["Search", "About", "🔒 Logout"], horizontal=True)

    # --- Logout ---
    if page == "🔒 Logout":
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.selected_index = None
        st.rerun()

    # --- SEARCH PAGE ---
    elif page == "Search":
        st.subheader("🔍 Search Tire Record")

        FILE = "TUMAS-DATABASE.xlsx"
        try:
            df = pd.read_excel(FILE, sheet_name="Sheet1", header=0)
            df.columns = (
                df.columns.astype(str)
                .str.strip()
                .str.replace('"', '')
                .str.replace("'", '')
                .str.replace('\n', ' ')
            )
        except Exception as e:
            st.error(f"⚠️ Could not load tire database: {e}")
            df = pd.DataFrame()

        # --- Search form ---
        with st.form("search_form"):
            col1, col2, col3 = st.columns(3)
            serial = col1.text_input("🔧 Serial Number (SN)")
            part_no = col2.text_input("🧩 Part Number (P/No)")
            wo_no = col3.text_input("📄 Work Order No (W/O No)")
            submitted = st.form_submit_button("Search")

        if submitted:
            if df.empty:
                st.error("❌ Database is empty or not loaded.")
            else:
                mask = pd.Series([True] * len(df))
                if serial:
                    mask &= df["SN"].astype(str).str.contains(serial.strip(), case=False, na=False)
                if part_no:
                    mask &= df["P/No"].astype(str).str.contains(part_no.strip(), case=False, na=False)
                if wo_no:
                    mask &= df["W/O No"].astype(str).str.contains(wo_no.strip(), case=False, na=False)

                result = df[mask].reset_index(drop=True)

                if not result.empty:
                    st.success(f"✅ Found {len(result)} record(s).")

                    # --- Display summary table ---
                    summary_cols = ["Date In", "W/O No", "P/No", "SN", "Ex-Aircraft", "Cycles Since Installed"]
                    display_df = result[summary_cols].copy()

                    selected_row = st.data_editor(
                        display_df,
                        hide_index=True,
                        use_container_width=True,
                        key="data_table",
                        disabled=True,
                    )

                    # --- User selects a specific record ---
                    row_index = st.selectbox("Select record to view details:", range(len(result)), format_func=lambda i: f"{result.loc[i, 'SN']} — {result.loc[i, 'P/No']}")

                    st.session_state.selected_index = row_index

                else:
                    st.warning("⚠️ No matching records found.")

        # --- Detailed Record View ---
        if st.session_state.selected_index is not None and not df.empty:
            i = st.session_state.selected_index
            try:
                row = df.iloc[i]
                st.markdown(f"<hr>", unsafe_allow_html=True)
                st.subheader(f"📋 Detailed Record for SN: {row.get('SN','N/A')}")
                st.markdown(f"""
                <div class="result-card">
                    <p><b>📆 Date In:</b> {row.get('Date In','N/A')}</p>
                    <p><b>📆 Date Out:</b> {row.get('DATE OUT','N/A')}</p>
                    <p><b>📋 W/O No:</b> {row.get('W/O No','N/A')}</p>
                    <p><b>🧩 Part No:</b> {row.get('P/No','N/A')}</p>
                    <p><b>🔧 Serial No:</b> {row.get('SN','N/A')}</p>
                    <p><b>🛠️ TC Remark:</b> {row.get('TC Remark','N/A')}</p>
                    <p><b>📅 Removal Date:</b> {row.get('Removal Date','N/A')}</p>
                    <p><b>✈️ Ex-Aircraft:</b> {row.get('Ex-Aircraft','N/A')}</p>
                    <p><b>🔢 AJL No:</b> {row.get('AJL No','N/A')}</p>
                    <p><b>🔄 Cycles Since Installed:</b> {row.get('Cycles Since Installed','0')}</p>
                </div>
                """, unsafe_allow_html=True)
            except Exception:
                st.error("⚠️ Could not display details for selected record.")

    # --- ABOUT PAGE ---
    elif page == "About":
        st.markdown(f"""
            <div style="background:white;padding:30px;border-radius:15px;max-width:850px;margin:auto;">
                <img src="data:image/png;base64,{logo_base64}" width="150" style="display:block;margin:auto;">
                <h2 style="text-align:center;color:#5C246E;">About TUMS</h2>
                <p style="font-size:16px;color:#444;text-align:justify;">
                    The <b>Tire Usage Monitoring System (TUMS)</b> is developed for <b>Batik Air Technical Services – Support Workshop</b>.
                    It helps track tire cycles, replacements, and usage efficiency.
                </p>
                <p style="font-size:16px;color:#444;text-align:justify;">
                    Built as part of the <b>2025 Internship Project</b>, it supports better documentation, analysis, and
                    operational decision-making for aircraft tire maintenance.
                </p>
            </div>
        """, unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("""
<div class="footer">
    © 2025 Batik Air • Technical Services • Support Workshop <br>
    Developed for Internship Project (TUMS)
</div>
""", unsafe_allow_html=True)
