import streamlit as st
import pandas as pd
import base64
import json
import streamlit.components.v1 as components

st.set_page_config(page_title="TUMAS", page_icon="icon-192x192.png")
st.header("")
hide_st_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""

# --- Helper to load logo as base64 ---
def get_base64_image(img_path):
    try:
        with open(img_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        st.error(f"⚠️ Logo file '{img_path}' not found.")
        return ""

logo_base64 = get_base64_image("batik_logo_transparent.png")

# --- Load user database ---
USERS_FILE = "users.xlsx"
try:
    users_df = pd.read_excel(USERS_FILE)
    users_df['Username'] = users_df['Username'].astype(str).str.strip()
    users_df['Password'] = users_df['Password'].astype(str).str.strip()
    USER_CREDENTIALS = dict(zip(users_df["Username"], users_df["Password"]))
except Exception as e:
    st.error(f"⚠️ Could not load '{USERS_FILE}': {e}")
    USER_CREDENTIALS = {}

# --- Session State ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "search_results" not in st.session_state:
    st.session_state.search_results = None
if "selected_row" not in st.session_state:
    st.session_state.selected_row = None

# --- CSS Styling ---
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #5C246E, #C42454); background-attachment: fixed; }
section[data-testid="stSidebar"] { background-color: #5C246E !important; }
section[data-testid="stSidebar"] .stRadio label { color: white !important; font-weight: bold; }
.result-card {
    background-color: white;
    border-radius: 15px;
    padding: 25px;
    margin-top: 20px;
    box-shadow: 0px 6px 18px rgba(0,0,0,0.15);
}
.footer { text-align: center; color: white; font-size: 14px; margin-top: 60px; opacity: 0.8; }
table { width: 100%; border-collapse: collapse; background-color: white; border-radius: 10px; overflow: hidden; }
th, td { text-align: left; padding: 10px; border-bottom: 1px solid #ddd; }
th { background-color: #5C246E; color: white; }
tr:hover { background-color: #f5f5f5; }
button { background-color: #5C246E; color: white; border: none; padding: 5px 10px; border-radius: 5px; cursor: pointer; }
button:hover { background-color: #C42454; }
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
            if username.strip() in USER_CREDENTIALS and USER_CREDENTIALS[username.strip()] == password.strip():
                st.session_state.logged_in = True
                st.session_state.username = username.strip()
                st.success("✅ Login successful!")
                st.rerun()
            else:
                st.error("❌ Incorrect username or password")

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
        st.session_state.search_results = None
        st.session_state.selected_row = None
        st.rerun()

    # --- SEARCH PAGE ---
    elif page == "Search":
        st.subheader("🔍 Search Tire Record")
        FILE = "TUMAS-DATABASE.xlsx"

        try:
            df = pd.read_excel(FILE, sheet_name="Sheet1", header=0)
            df.columns = df.columns.astype(str).str.strip()
        except Exception as e:
            st.error(f"⚠️ Could not load tire database: {e}")
            df = pd.DataFrame()

        # --- SEARCH FORM ---
        if st.session_state.selected_row is None:
            with st.form("search_form"):
                col1, col2, col3 = st.columns(3)
                serial = col1.text_input("🔧 Serial Number (SN)")
                part_no = col2.text_input("🧩 Part Number (P/No)")
                wo_no = col3.text_input("📄 Work Order No (W/O No)")
                submitted = st.form_submit_button("Search")

            if submitted:
                if not df.empty:
                    mask = pd.Series([True] * len(df))
                    if serial:
                        mask &= df['SN'].astype(str).str.contains(serial, case=False, na=False)
                    if part_no:
                        mask &= df['P/No'].astype(str).str.contains(part_no, case=False, na=False)
                    if wo_no:
                        mask &= df['W/O No'].astype(str).str.contains(wo_no, case=False, na=False)
                    result = df[mask]
                    st.session_state.search_results = result
                else:
                    st.error("⚠️ No data found.")

            if st.session_state.search_results is not None and not st.session_state.search_results.empty:
                result = st.session_state.search_results
                st.markdown("<h4 style='color:white;'>Search Results:</h4>", unsafe_allow_html=True)
                html_table = "<table><tr><th>Date In</th><th>Ex-Aircraft</th><th>Description</th><th>SN</th><th>P/No</th><th>W/O No</th><th>Open</th></tr>"
                for idx, row in result.iterrows():
                    html_table += f"<tr><td>{row.get('Date In','')}</td><td>{row.get('Ex-Aircraft','')}</td><td>{row.get('Description','')}</td><td>{row.get('SN','')}</td><td>{row.get('P/No','')}</td><td>{row.get('W/O No','')}</td><td><button onclick=\"window.parent.postMessage({{'index':{idx}}}, '*')\">Open</button></td></tr>"
                html_table += "</table>"
                components.html(html_table + """
                <script>
                window.addEventListener('message', (event) => {
                    if (event.data.index !== undefined) {
                        window.parent.postMessage(event.data, '*');
                    }
                });
                </script>
                """, height=400)
                msg = st.experimental_get_query_params().get("open_index", [None])[0]

        else:
            row = st.session_state.selected_row
            st.markdown("<h4 style='color:white;'>Tire Details:</h4>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class="result-card">
                <h3 style="color:#5C246E;">{row.get('Description','N/A')}</h3>
                <p><b>Date In:</b> {row.get('Date In','N/A')}</p>
                <p><b>Ex-Aircraft:</b> {row.get('Ex-Aircraft','N/A')}</p>
                <p><b>SN:</b> {row.get('SN','N/A')}</p>
                <p><b>P/No:</b> {row.get('P/No','N/A')}</p>
                <p><b>W/O No:</b> {row.get('W/O No','N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("⬅️ Back to Results"):
                st.session_state.selected_row = None
                st.rerun()

    elif page == "About":
        st.markdown(f"""
            <div class="result-card">
                <img src="data:image/png;base64,{logo_base64}" width="150" style="display:block; margin:auto;">
                <h3 style="text-align:center;color:#5C246E;">About TUMS</h3>
                <p style="text-align:justify;">The <b>Tire Usage Monitoring System (TUMS)</b> helps Batik Air Technical Services manage aircraft tire life efficiently by tracking cycles, retreads, and usage history.</p>
            </div>
        """, unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("""
<div class="footer">
© 2025 Batik Air • Technical Services • Support Workshop <br>
Developed for Internship Project (TUMS)
</div>
""", unsafe_allow_html=True)
